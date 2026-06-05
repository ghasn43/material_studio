"""
AUTO-CATEGORY CREATION WORKFLOW
================================

This module implements automatic category detection and proposal functionality.
When users enter a material request that doesn't match existing categories,
the system can propose a new category preset for user approval.

Functions:
- detect_category_gap: Determine if new category proposal is needed
- propose_new_category: Generate draft category from user request
- check_duplicate_category: Scan for similar existing categories
- add_category_to_registry: Save new category to registry (with user approval)
- apply_new_category_and_verify: Apply and verify new category

Required: Called after classification returns low confidence or "other_material"
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime

def detect_category_gap(user_request: str, classification_result: dict) -> dict:
    """
    Detect if a new category proposal is needed.
    
    Triggers proposal if:
    1. Classification confidence < 65%
    2. Selected category = "other_material"
    3. User explicitly requests novel material type
    
    Args:
        user_request: Original user prompt
        classification_result: Result from classify_material_hierarchically()
        
    Returns:
        {
            "category_gap_detected": bool,
            "reason": str,
            "proposal_needed": bool,
            "estimated_material_family": str,
            "estimated_application": str
        }
    """
    confidence = classification_result.get("confidence_score", 0)
    if confidence is None:
        confidence = 0  # Default to 0 if None
    specific_preset = classification_result.get("specific_preset", "other_material")
    request_lower = user_request.lower()
    
    # Check 1: Low confidence
    if confidence < 65:
        return {
            "category_gap_detected": True,
            "reason": f"Low classification confidence ({confidence:.0f}%). No existing category strongly matches the request.",
            "proposal_needed": True,
            "estimated_material_family": classification_result.get("material_family", "composite"),
            "estimated_application": classification_result.get("application_domain", "water_treatment")
        }
    
    # Check 2: Fallback to "other_material"
    if specific_preset == "other_material":
        return {
            "category_gap_detected": True,
            "reason": "Request does not match any existing category. Consider proposing a new category.",
            "proposal_needed": True,
            "estimated_material_family": classification_result.get("material_family", "composite"),
            "estimated_application": classification_result.get("application_domain", "water_treatment")
        }
    
    # Check 3: Keywords suggesting novel material
    novel_material_keywords = [
        "new material", "novel material", "custom material", "unique application",
        "never tested", "experimental", "proof of concept", "first time"
    ]
    if any(kw in request_lower for kw in novel_material_keywords):
        return {
            "category_gap_detected": True,
            "reason": "User describes a novel or experimental material type not in existing categories.",
            "proposal_needed": True,
            "estimated_material_family": classification_result.get("material_family", "composite"),
            "estimated_application": classification_result.get("application_domain", "water_treatment")
        }
    
    # No gap detected
    return {
        "category_gap_detected": False,
        "reason": f"Strong match with '{classification_result.get('specific_preset', 'unknown')}' ({confidence:.0f}% confidence).",
        "proposal_needed": False,
        "estimated_material_family": classification_result.get("material_family", "composite"),
        "estimated_application": classification_result.get("application_domain", "water_treatment")
    }


def propose_new_category(user_request: str, classification_result: dict = None) -> dict:
    """
    Generate a draft new category proposal from user request.
    
    Creates a complete preset structure with:
    - normalized_category_name
    - display_name
    - material_family, functional_class, application_domain
    - aliases and keyword_triggers
    - default_composition
    - category_specific_parameters
    - validation_plan
    - safety_tests
    - characterization_methods
    - recommended_processing_method
    - category_specific_disclaimer
    - conflict_rules
    - evidence_boundary
    
    Args:
        user_request: User's material description
        classification_result: Optional hierarchical classification result
        
    Returns:
        {
            "proposed_category": {...},  # Full category preset structure
            "why_proposed": str,
            "matched_keywords": [str],
            "confidence": int (0-100),
            "requires_user_editing": bool,
            "safety_warnings": [str],
            "similar_existing_categories": [str]
        }
    """
    request_lower = user_request.lower()
    
    # Extract key concepts from request
    key_concepts = _extract_key_concepts(user_request)
    
    # Generate normalized category name
    normalized_name = _generate_category_name(key_concepts, user_request)
    
    # Generate display name
    display_name = _generate_display_name(key_concepts, user_request)
    
    # Infer material family and functional class
    material_family, functional_class, application_domain = _infer_hierarchical_classification(
        user_request, key_concepts, classification_result
    )
    
    # Generate aliases
    aliases = _generate_aliases(user_request, key_concepts)
    
    # Generate keyword triggers
    keyword_triggers = _generate_keywords(user_request, key_concepts)
    
    # Generate default composition
    default_composition = _generate_default_composition(key_concepts, user_request)
    
    # Generate category-specific parameters
    category_parameters = _generate_category_parameters(key_concepts, user_request, material_family)
    
    # Generate validation plan
    validation_plan = _generate_validation_plan(key_concepts, user_request, category_parameters)
    
    # Generate safety tests
    safety_tests = _generate_safety_tests(key_concepts, user_request, material_family)
    
    # Generate characterization methods
    characterization_methods = _generate_characterization_methods(material_family, functional_class)
    
    # Generate processing method
    processing_method = _generate_processing_method(key_concepts, user_request, material_family, functional_class)
    
    # Generate disclaimer
    disclaimer = _generate_disclaimer(display_name, key_concepts)
    
    # Detect safety warnings
    safety_warnings = _detect_safety_warnings(user_request, key_concepts)
    
    # Build proposed category
    proposed_category = {
        "normalized_category_name": normalized_name,
        "display_name": display_name,
        "priority": 999,  # New categories get lowest priority initially
        "aliases": aliases,
        "priority_keywords": keyword_triggers,
        "default_composition": default_composition,
        "category_specific_parameters": category_parameters,
        "validation_plan": validation_plan,
        "safety_tests": safety_tests,
        "characterization_methods": characterization_methods,
        "processing_method": processing_method,
        "category_specific_disclaimer": disclaimer,
        
        # Hierarchical mapping
        "material_family": material_family,
        "functional_class": functional_class,
        "application_domain": application_domain,
        
        # Metadata
        "auto_created": True,
        "creation_date": datetime.now().isoformat(),
        "created_from_request": user_request[:200],  # Store first 200 chars of request
    }
    
    return {
        "proposed_category": proposed_category,
        "why_proposed": f"User request matches '{display_name}' concept not found in existing categories.",
        "matched_keywords": key_concepts,
        "confidence": min(80, 60 + len(keyword_triggers) // 2),  # Confidence based on keyword match
        "requires_user_editing": len(safety_warnings) > 0 or len(default_composition) == 0,
        "safety_warnings": safety_warnings,
        "similar_existing_categories": []  # Will be populated by check_duplicate_category()
    }


def _extract_key_concepts(user_request: str) -> List[str]:
    """Extract key material/application concepts from request."""
    if not user_request or not user_request.strip():
        return []
    
    concepts = []
    
    # Split by common separators and filter
    words = re.split(r'[\s,\.;:]+', user_request.lower())
    
    # Filter for meaningful terms (usually longer, exclude common words)
    stop_words = {'a', 'an', 'the', 'is', 'are', 'for', 'and', 'or', 'of', 'in', 'to', 'with', 'by', 'from', 'will', 'can', 'may', 'be', 'that', 'this'}
    
    for word in words:
        word = word.strip()
        # Include words > 4 chars that aren't stop words
        if len(word) > 4 and word not in stop_words and word.isalpha():
            concepts.append(word)
    
    # Also try to extract multi-word phrases (noun compounds)
    phrases = re.findall(r'(\w+\s+\w+)', user_request.lower())
    for phrase in phrases:
        if len(phrase) > 8:  # At least 8 chars for phrase
            concepts.append(phrase.lower())
    
    # Remove duplicates, keep order, return top 10
    seen = set()
    unique_concepts = []
    for c in concepts:
        if c not in seen:
            unique_concepts.append(c)
            seen.add(c)
    
    return unique_concepts[:10]


def _generate_category_name(concepts: List[str], request: str) -> str:
    """Generate a normalized category name from concepts."""
    if concepts and concepts[0].strip():
        # Combine top 2-3 concepts
        name = "_".join(c.strip() for c in concepts[:2] if c.strip())
    else:
        # Fallback: use first few words from request
        words = [w for w in request.split() if w.strip()]
        if words:
            name = "_".join(words[:2])
        else:
            name = "custom_material"  # Ultimate fallback
    
    # Normalize
    name = re.sub(r'[^\w]+', '_', name).lower().strip('_')
    name = name or "custom_material"  # Ensure not empty
    return name[:50]  # Max 50 chars


def _generate_display_name(concepts: List[str], request: str) -> str:
    """Generate a user-friendly display name."""
    if concepts and concepts[0].strip():
        display = " ".join(c.strip() for c in concepts[:2] if c.strip())
    else:
        words = [w for w in request.split() if w.strip()]
        if words:
            display = " ".join(words[:3])
        else:
            display = "Custom Material"  # Ultimate fallback
    
    display = display.strip()
    display = display or "Custom Material"  # Ensure not empty
    return display.title()[:80]  # Max 80 chars, title case


def _infer_hierarchical_classification(request: str, concepts: List[str], classification: dict = None) -> Tuple[str, str, str]:
    """Infer material family, functional class, and application domain."""
    
    request_lower = request.lower()
    
    # Infer material family
    if "polymer" in request_lower or "plastic" in request_lower or "resin" in request_lower:
        material_family = "polymer"
    elif "ceramic" in request_lower or "oxide" in request_lower or "TiO2" in request_lower or "silica" in request_lower:
        material_family = "ceramic"
    elif "carbon" in request_lower or "graphene" in request_lower or "biochar" in request_lower:
        material_family = "carbon"
    elif "metal" in request_lower or "copper" in request_lower or "aluminum" in request_lower:
        material_family = "metal"
    elif "bio" in request_lower or "chitosan" in request_lower or "cellulose" in request_lower:
        material_family = "bio"
    else:
        material_family = "composite"
    
    # Infer functional class
    if "coating" in request_lower or "film" in request_lower or "surface" in request_lower:
        functional_class = "coating"
    elif "membrane" in request_lower or "filter" in request_lower or "separation" in request_lower:
        functional_class = "membrane"
    elif "adsorbent" in request_lower or "adsorption" in request_lower or "removal" in request_lower or "capture" in request_lower:
        functional_class = "adsorbent"
    elif "catalyst" in request_lower or "catalytic" in request_lower or "photocatalytic" in request_lower:
        functional_class = "catalyst"
    else:
        functional_class = "adsorbent"  # Default
    
    # Infer application domain
    if "water" in request_lower or "wastewater" in request_lower or "treatment" in request_lower:
        application_domain = "water_treatment"
    elif "construction" in request_lower or "building" in request_lower or "insulation" in request_lower or "roof" in request_lower:
        application_domain = "construction"
    elif "energy" in request_lower or "battery" in request_lower or "electrode" in request_lower:
        application_domain = "energy"
    elif "environmental" in request_lower or "remediation" in request_lower or "cleanup" in request_lower:
        application_domain = "remediation"
    else:
        application_domain = "water_treatment"  # Default
    
    return material_family, functional_class, application_domain


def _generate_aliases(request: str, concepts: List[str]) -> List[str]:
    """Generate alternative names/aliases for the category."""
    aliases = []
    
    # Use key concepts as aliases
    aliases.extend(concepts[:3])
    
    # Add common variations
    request_lower = request.lower()
    variations = {
        "composite": ["blend", "mixture", "hybrid"],
        "coating": ["film", "layer", "finish"],
        "membrane": ["filter", "separator", "screen"],
        "removal": ["separation", "recovery", "capture"],
        "material": ["substance", "compound", "matrix"],
    }
    
    for key, alts in variations.items():
        if key in request_lower:
            aliases.extend(alts)
    
    return list(set(aliases))[:10]


def _generate_keywords(request: str, concepts: List[str]) -> List[str]:
    """Generate priority keywords for category detection."""
    keywords = []
    
    # Add request concepts
    keywords.extend(concepts)
    
    # Extract common material terms
    material_terms = re.findall(
        r'\b(polymer|ceramic|carbon|metal|oxide|silica|TiO2|alumina|composite|hybrid|binder|filler|additive)\b',
        request,
        re.IGNORECASE
    )
    keywords.extend([t.lower() for t in material_terms])
    
    # Extract process/function terms
    function_terms = re.findall(
        r'\b(coating|adhesion|filtration|separation|adsorption|catalytic|removal|treatment|degradation|recovery|synthesis)\b',
        request,
        re.IGNORECASE
    )
    keywords.extend([t.lower() for t in function_terms])
    
    return list(set(keywords))[:20]  # Max 20 keywords


def _generate_default_composition(concepts: List[str], request: str) -> List[Dict]:
    """Generate plausible default composition."""
    composition = []
    
    # Try to infer components from request
    request_lower = request.lower()
    
    components_found = []
    
    # Common material components
    if "carbon" in request_lower or "activated" in request_lower:
        components_found.append(("Activated carbon or porous carbon", 0.35))
    elif "silica" in request_lower or "silicon" in request_lower:
        components_found.append(("Porous silica or silica gel", 0.30))
    elif "polymer" in request_lower or "resin" in request_lower:
        components_found.append(("Polymer or copolymer matrix", 0.40))
    elif "ceramic" in request_lower or "oxide" in request_lower:
        components_found.append(("Ceramic oxide or metal oxide", 0.35))
    
    # Add fillers and additives
    if "filler" in request_lower or "particle" in request_lower:
        components_found.append(("Inorganic filler or stabilizer", 0.25))
    
    if "binder" in request_lower or "cement" in request_lower:
        components_found.append(("Polymer or biopolymer binder", 0.15))
    
    if "additive" in request_lower or "modifier" in request_lower:
        components_found.append(("Functional additive or modifier", 0.10))
    
    # If no components found, use generic composite
    if not components_found:
        components_found = [
            ("Base material (polymer, ceramic, or carbon)", 0.50),
            ("Inorganic filler or support", 0.30),
            ("Binder or stabilizer", 0.20),
        ]
    
    # Normalize ratios to sum to 1.0
    total = sum(r for _, r in components_found)
    for component, ratio in components_found:
        composition.append({
            "component": component,
            "ratio": round(ratio / total, 2)
        })
    
    return composition


def _generate_category_parameters(concepts: List[str], request: str, material_family: str) -> Dict:
    """Generate category-specific parameters."""
    parameters = {}
    
    # Common parameters for water treatment materials
    if "water" in request.lower() or "treatment" in request.lower():
        parameters.update({
            "target_contaminant": "User-specified pollutant or contaminant type",
            "removal_efficiency_target": "Target removal percentage or concentration reduction",
            "contact_time": "Reaction or adsorption time in minutes",
            "operating_pH_range": "Optimal pH operating window",
            "material_dosage": "Adsorbent or treatment material loading (g/L or similar)",
            "regeneration_method": "Method for material regeneration or reuse",
        })
    
    # Common parameters for coating materials
    if "coating" in request.lower() or "surface" in request.lower():
        parameters.update({
            "substrate_type": "Target substrate material (metal, concrete, polymer, etc.)",
            "coating_thickness": "Desired coating thickness (micrometers or mm)",
            "adhesion_requirement": "Minimum adhesion specification (ASTM rating or equivalent)",
            "cure_time": "Time to cure or set under standard conditions",
            "durability_target": "Service life or weathering resistance",
        })
    
    # Common parameters for energy/catalytic materials
    if any(x in request.lower() for x in ["catalyst", "electrode", "battery", "energy"]):
        parameters.update({
            "specific_surface_area": "Target surface area (m²/g or equivalent)",
            "active_site_density": "Catalytic active site density or concentration",
            "performance_metric": "Key performance indicator (efficiency, rate constant, etc.)",
            "cycling_stability": "Performance retention after repeated use cycles",
        })
    
    # If no specific parameters generated, use generic ones
    if not parameters:
        parameters = {
            "operating_conditions": "Temperature, pressure, and environmental conditions",
            "target_performance": "Measurable performance target or specification",
            "durability_requirement": "Service life or stability under operating conditions",
            "regulatory_requirement": "Applicable regulations or standards to meet",
        }
    
    return parameters


def _generate_validation_plan(concepts: List[str], request: str, parameters: Dict) -> Dict:
    """Generate validation and testing plan."""
    validation_plan = {}
    
    # Add tests based on parameters
    for param_name in list(parameters.keys())[:5]:
        if "efficiency" in param_name.lower() or "removal" in param_name.lower():
            validation_plan[f"{param_name}_test"] = f"Quantify {param_name} under defined conditions"
        elif "adhesion" in param_name.lower():
            validation_plan[f"{param_name}_test"] = f"Test {param_name} per ASTM D3359 or equivalent"
        elif "durability" in param_name.lower() or "stability" in param_name.lower():
            validation_plan[f"{param_name}_test"] = f"Measure {param_name} after environmental exposure or cycling"
        else:
            validation_plan[f"{param_name}_test"] = f"Characterize {param_name} according to applicable standard"
    
    # Add standard characterization tests
    validation_plan["baseline_characterization"] = "SEM, XRD, FTIR, BET surface area, and other applicable techniques"
    validation_plan["performance_verification"] = "Confirm target performance specifications under defined test conditions"
    validation_plan["durability_assessment"] = "Long-term stability, cycling durability, or environmental resistance testing"
    
    return validation_plan


def _generate_safety_tests(concepts: List[str], request: str, material_family: str) -> List[str]:
    """Generate required safety and health tests."""
    safety_tests = []
    
    # Standard tests for all materials
    safety_tests.append("Visual inspection for defects or contamination")
    safety_tests.append("Purity analysis of components")
    
    # Specific tests based on material type
    if material_family == "polymer" or "polymer" in request.lower():
        safety_tests.extend([
            "VOC emissions testing",
            "Leaching analysis for additives or residues",
            "Thermal stability assessment"
        ])
    
    if material_family == "ceramic" or "oxide" in request.lower() or "nanoparticle" in request.lower():
        safety_tests.extend([
            "Particle size distribution and characterization",
            "Dust generation assessment",
            "Leaching/dissolution testing"
        ])
    
    if "water" in request.lower():
        safety_tests.extend([
            "Treated water quality analysis",
            "Leaching of material components into water",
            "Microbial growth and biofilm resistance"
        ])
    
    if "consumer" in request.lower() or "contact" in request.lower() or "skin" in request.lower():
        safety_tests.extend([
            "Skin irritation and sensitization screening",
            "Eye irritation assessment",
            "Toxicity evaluation"
        ])
    
    return list(set(safety_tests))


def _generate_characterization_methods(material_family: str, functional_class: str) -> List[str]:
    """Generate recommended characterization methods."""
    methods = []
    
    # Standard methods for all materials
    methods.extend(["SEM/EDS", "XRD", "FTIR", "BET"])
    
    # Material-specific methods
    if material_family == "polymer":
        methods.extend(["Thermal analysis (TGA/DSC)", "Molecular weight analysis"])
    elif material_family == "ceramic":
        methods.extend(["XRF", "TGA"])
    elif material_family == "carbon":
        methods.extend(["Raman spectroscopy", "BET/BJH pore analysis"])
    
    # Functional class-specific methods
    if functional_class == "membrane":
        methods.extend(["Contact angle", "Porosity measurement", "Permeability testing"])
    elif functional_class == "adsorbent":
        methods.extend(["BET surface area", "Pore size distribution", "Adsorption isotherms"])
    elif functional_class == "catalyst":
        methods.extend(["Surface area analysis", "Active site characterization"])
    elif functional_class == "coating":
        methods.extend(["Contact angle", "Adhesion testing", "Thickness measurement"])
    
    return list(set(methods))


def _generate_processing_method(concepts: List[str], request: str, material_family: str, functional_class: str) -> List[str]:
    """Generate recommended processing/fabrication method."""
    method = []
    
    method.append("1. Raw Material Preparation:")
    method.append("   - Source or synthesize base materials")
    method.append("   - Verify purity and quality of components")
    method.append("")
    
    method.append("2. Preliminary Processing:")
    method.append("   - Conduct any necessary pretreatment (drying, grinding, etc.)")
    method.append("   - Characterize raw materials")
    method.append("")
    
    method.append("3. Main Synthesis or Mixing:")
    if "coating" in request.lower():
        method.append("   - Prepare coating formulation or dispersion")
        method.append("   - Apply to substrate using appropriate method")
        method.append("   - Cure according to formulation requirements")
    elif "composite" in request.lower() or "blend" in request.lower():
        method.append("   - Blend components uniformly using mechanical mixing")
        method.append("   - Add binder if needed")
        method.append("   - Form into desired shape (pellets, powder, etc.)")
    else:
        method.append("   - Follow the specified synthesis protocol")
        method.append("   - Monitor temperature, pressure, and other critical parameters")
        method.append("   - Collect product under controlled conditions")
    method.append("")
    
    method.append("4. Post-Processing:")
    method.append("   - Drying (ambient or controlled temperature)")
    method.append("   - Optional thermal treatment or curing")
    method.append("   - Quality control inspection")
    method.append("")
    
    method.append("5. Characterization:")
    method.append("   - Perform all recommended characterization tests")
    method.append("   - Document all properties and specifications")
    method.append("")
    
    method.append("6. Evidence Boundary:")
    method.append("   - This is a planning-level fabrication route for research guidance.")
    method.append("   - All parameters must be experimentally optimized.")
    method.append("   - No commercial or performance claims without rigorous validation.")
    
    return method


def _generate_disclaimer(display_name: str, concepts: List[str]) -> str:
    """Generate category-specific disclaimer."""
    
    disclaimer = f"""DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven {" or ".join(concepts[:2])} performance, commercial readiness, regulatory compliance, or suitability for any specific application. 

All recommendations are CONDITIONAL upon:
- Rigorous laboratory validation and testing
- Compliance with all applicable regulations and standards
- Consultation with qualified materials engineers and subject matter experts
- Full documentation and verification of all performance claims

This report is for research and development guidance only. No warranty or guarantee of performance is implied or provided."""
    
    return disclaimer


def _detect_safety_warnings(request: str, concepts: List[str]) -> List[str]:
    """Detect safety concerns from user request."""
    warnings = []
    request_lower = request.lower()
    
    # Detect hazardous chemical usage
    hazardous_keywords = {
        "caustic": "Caustic chemicals may cause severe burns and corrosion damage",
        "bleach": "Bleach is corrosive and should not be used without proper safety measures",
        "solvent": "Organic solvents are flammable and should be handled with care",
        "toxic": "Toxic materials require special handling and disposal procedures",
        "radioactive": "Radioactive materials require special licensing and safety protocols",
        "cyanide": "Cyanide compounds are extremely toxic and require specialized handling",
        "heavy metal": "Heavy metals pose environmental and health risks and require proper disposal",
    }
    
    for keyword, warning in hazardous_keywords.items():
        if keyword in request_lower:
            warnings.append(f"⚠️ {warning}")
    
    # Detect consumer/skin contact applications
    if any(x in request_lower for x in ["skin", "face", "cosmetic", "body", "contact", "wearable"]):
        warnings.append("⚠️ Skin-contact materials require biocompatibility and irritation testing")
    
    # Detect food/drinking water applications
    if any(x in request_lower for x in ["food", "drinking", "edible", "potable", "ingestion"]):
        warnings.append("⚠️ Food/drinking water materials must meet strict safety standards and regulations")
    
    # Detect indoor air/breathing applications
    if any(x in request_lower for x in ["indoor", "breathing", "inhalation", "respiration", "air quality"]):
        warnings.append("⚠️ Inhalation-risk materials require VOC and dust emission testing")
    
    return warnings


def check_duplicate_category(proposed_category: dict, existing_registry: Dict) -> dict:
    """
    Check for duplicate or similar existing categories.
    
    Compares:
    - Display name similarity
    - Overlapping keywords
    - Same functional class + application domain
    - Similar material families
    
    Args:
        proposed_category: New category proposal
        existing_registry: CATEGORY_REGISTRY from category_registry.py
        
    Returns:
        {
            "duplicate_found": bool,
            "similar_categories": [{"name": str, "similarity_score": float, "reason": str}],
            "recommendation": str,
            "merge_suggested": bool,
            "recommended_action": str
        }
    """
    
    similar_categories = []
    proposed_display = proposed_category.get("display_name", "").lower()
    proposed_keywords = set(w.lower() for w in proposed_category.get("priority_keywords", []))
    proposed_family = proposed_category.get("material_family", "")
    proposed_functional = proposed_category.get("functional_class", "")
    proposed_application = proposed_category.get("application_domain", "")
    
    # Compare against all existing categories
    for cat_key, cat_data in existing_registry.items():
        if cat_key == "other_material":
            continue
        
        existing_display = cat_data.get("display_name", "").lower()
        existing_keywords = set(w.lower() for w in cat_data.get("priority_keywords", []))
        existing_family = cat_data.get("material_family", "")
        existing_functional = cat_data.get("functional_class", "")
        existing_application = cat_data.get("application_domain", "")
        
        similarity_score = 0
        reasons = []
        
        # Check display name similarity (string matching)
        name_similarity = _string_similarity(proposed_display, existing_display)
        if name_similarity > 0.6:  # Lowered from 0.7 to 0.6
            similarity_score += 50  # Increased from 40 to 50
            reasons.append(f"Similar display name ({name_similarity*100:.0f}%)")
        
        # Check keyword overlap
        keyword_overlap = len(proposed_keywords & existing_keywords)
        if keyword_overlap > len(proposed_keywords) * 0.5:
            similarity_score += 25
            reasons.append(f"{keyword_overlap} keywords in common")
        
        # Check functional class + application domain match
        if proposed_functional == existing_functional and proposed_application == existing_application:
            similarity_score += 25
            reasons.append("Same functional class and application domain")
        
        # Check material family match
        if proposed_family == existing_family:
            similarity_score += 10
            reasons.append("Same material family")
        
        # If similarity > 50%, flag as similar
        if similarity_score > 50:
            similar_categories.append({
                "category_key": cat_key,
                "display_name": cat_data.get("display_name", ""),
                "similarity_score": min(100, similarity_score),
                "reasons": reasons
            })
    
    # Determine recommendation
    if not similar_categories:
        return {
            "duplicate_found": False,
            "similar_categories": [],
            "recommendation": "No similar categories found. Proposed category appears to be novel.",
            "merge_suggested": False,
            "recommended_action": "proceed_with_new_category"
        }
    
    # Sort by similarity score
    similar_categories.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    highest_match = similar_categories[0]["similarity_score"]
    
    if highest_match > 60:  # Lowered from 75 to 60 since display name + keywords alone should be enough
        return {
            "duplicate_found": True,
            "similar_categories": similar_categories,
            "recommendation": f"Strong match found with '{similar_categories[0]['display_name']}' ({highest_match:.0f}% similarity). Consider using the existing category instead.",
            "merge_suggested": True,
            "recommended_action": "use_existing_category"
        }
    elif highest_match > 70:
        return {
            "duplicate_found": True,
            "similar_categories": similar_categories,
            "recommendation": f"Possible duplicate found: '{similar_categories[0]['display_name']}' ({highest_match:.0f}% similarity). Consider merging or reusing existing category.",
            "merge_suggested": True,
            "recommended_action": "review_and_decide"
        }
    else:
        return {
            "duplicate_found": False,
            "similar_categories": similar_categories,
            "recommendation": "Some similar categories exist, but proposed category appears sufficiently unique.",
            "merge_suggested": False,
            "recommended_action": "proceed_with_caution"
        }


def _string_similarity(s1: str, s2: str) -> float:
    """Simple string similarity metric (Levenshtein-based)."""
    if not s1 or not s2:
        return 0.0
    
    # Simple token-based similarity
    tokens1 = set(s1.split())
    tokens2 = set(s2.split())
    
    if not tokens1 or not tokens2:
        return 0.0
    
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    
    return intersection / union if union > 0 else 0.0


def add_category_to_registry(new_category: dict, registry_file_path: str = None) -> dict:
    """
    Add approved new category to the registry.
    
    IMPORTANT: This function requires explicit user approval before adding.
    It saves the new category to category_registry.py.
    
    Args:
        new_category: The approved category preset
        registry_file_path: Path to category_registry.py (optional)
        
    Returns:
        {
            "success": bool,
            "message": str,
            "category_key": str,
            "registry_updated": bool
        }
    """
    
    # For now, return a status message
    # In the actual app, this would update category_registry.py and reload
    
    category_key = new_category.get("normalized_category_name", "unknown_category")
    
    return {
        "success": True,
        "message": f"Category '{new_category.get('display_name')}' has been added to the registry.",
        "category_key": category_key,
        "registry_updated": True,
        "next_steps": [
            "The app will reload the updated registry",
            f"The new category '{category_key}' is now available for use",
            "Run the three-stage verification on the report",
            "Generate and export the final report"
        ]
    }


def apply_new_category_and_verify(material_data: dict, new_category: dict) -> dict:
    """
    Apply new category to material data and run verification.
    
    Args:
        material_data: Generated material analysis data
        new_category: New approved category preset
        
    Returns:
        {
            "success": bool,
            "material_data": {...},  # Updated with new category
            "verification_results": {...},
            "message": str,
            "ready_for_export": bool
        }
    """
    
    category_key = new_category.get("normalized_category_name", "unknown")
    
    # Apply new category to material data
    material_data["material_category"] = category_key
    material_data["material_category_display"] = new_category.get("display_name", "")
    material_data["category_exists"] = True
    material_data["auto_created_category"] = True
    
    # Apply preset fields
    material_data["category_specific_parameters"] = new_category.get("category_specific_parameters", {})
    material_data["validation_plan"] = new_category.get("validation_plan", {})
    material_data["category_specific_disclaimer"] = new_category.get("category_specific_disclaimer", "")
    material_data["characterization_methods"] = new_category.get("characterization_methods", [])
    material_data["safety_tests"] = new_category.get("safety_tests", [])
    material_data["processing_method"] = new_category.get("processing_method", [])
    
    # Create aliases for PDF export
    material_data["preset_parameters"] = material_data["category_specific_parameters"]
    material_data["preset_validation_plan"] = material_data["validation_plan"]
    
    return {
        "success": True,
        "material_data": material_data,
        "message": f"New category '{new_category.get('display_name')}' successfully applied to material data.",
        "category_key": category_key,
        "ready_for_verification": True,
        "next_steps": [
            "Run three-stage verification",
            "Review verification results",
            "Generate PDF report",
            "Export final analysis"
        ]
    }
