"""
SUGGESTED CATEGORY WORKFLOW
===========================

Implements intelligent category suggestion system to prevent incorrect mappings.
When a user request doesn't strongly match existing categories, this module
generates 2-5 suggested categories for user review before proceeding.

Functions:
- detect_category_conflict: Identify if selected category conflicts with request
- propose_candidate_categories: Generate 2-5 suggested categories
- score_category_match: Score how well a category matches the request
- extract_request_domain: Identify material domain from request
- should_show_suggestions: Determine if suggestion panel is needed
"""

import re
from typing import Dict, List, Tuple, Optional
from category_registry import CATEGORY_REGISTRY


# ==============================================================================
# DOMAIN & KEYWORD DETECTION
# ==============================================================================

DOMAIN_KEYWORDS = {
    "fabric_cleaning": {
        "keywords": [
            "cotton clothing", "cotton fabric", "fabric-safe", "oil-stain removal",
            "grease stain", "cooking oil", "laundry", "pre-treatment", "pre-wash",
            "colorfastness", "rinsability", "skin-contact residue", "washing-machine",
            "garment", "textile", "cloth", "stain removal from fabric", "fabric stain",
            "fabric safe", "laundry stain", "clothing stain"
        ],
        "negative_keywords": ["heavy metal", "lead", "cadmium", "arsenic", "chromium", "Pb", "Cd", "As", "Cr"],
        "category_template": {
            "material_family": "hybrid cleaning composite",
            "functional_class": "fabric stain remover",
            "application_domain": "textile cleaning"
        }
    },
    "water_treatment": {
        "keywords": [
            "water treatment", "water purification", "wastewater", "contamination removal",
            "pollution removal", "water quality", "water cleaning", "aqueous"
        ],
        "negative_keywords": [],
        "category_template": {
            "material_family": "composite",
            "functional_class": "adsorbent",
            "application_domain": "water_treatment"
        }
    },
    "photocatalytic": {
        "keywords": [
            "photocatalytic", "photodegradation", "UV light", "visible light",
            "TiO2", "self-cleaning", "light activated", "light-driven"
        ],
        "negative_keywords": [],
        "category_template": {
            "material_family": "ceramic",
            "functional_class": "photocatalyst",
            "application_domain": "water_treatment"
        }
    },
    "thermal_insulation": {
        "keywords": [
            "thermal insulation", "heat insulation", "thermal resistance", "thermal barrier",
            "insulation material", "insulating", "thermal protection", "R-value",
            "thermal performance", "building insulation", "roof", "wall"
        ],
        "negative_keywords": [],
        "category_template": {
            "material_family": "composite",
            "functional_class": "insulation",
            "application_domain": "construction"
        }
    },
    "water_repellent": {
        "keywords": [
            "waterproof", "water-resistant", "water repellent", "moisture barrier",
            "water blocking", "hydrophobic", "water protection", "leak prevention",
            "damp prevention", "water blocking"
        ],
        "negative_keywords": [],
        "category_template": {
            "material_family": "polymer",
            "functional_class": "coating",
            "application_domain": "construction"
        }
    }
}


def extract_request_domain(user_request: str) -> List[Tuple[str, float]]:
    """
    Identify material domains from user request.
    
    Args:
        user_request: User's material description
        
    Returns:
        List of (domain_name, confidence) tuples sorted by confidence
    """
    request_lower = user_request.lower()
    domain_scores = {}
    
    for domain, config in DOMAIN_KEYWORDS.items():
        # Count positive keyword matches
        positive_matches = sum(
            1 for kw in config["keywords"]
            if kw.lower() in request_lower
        )
        
        # Count negative keyword matches (penalize)
        negative_matches = sum(
            1 for kw in config["negative_keywords"]
            if kw.lower() in request_lower
        )
        
        # Calculate confidence
        if positive_matches > 0:
            confidence = (positive_matches * 10) - (negative_matches * 20)
            domain_scores[domain] = max(0, confidence)
    
    # Sort by confidence
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_domains


def detect_category_conflict(user_request: str, selected_category_key: str) -> dict:
    """
    Detect if selected category conflicts with request content.
    
    Args:
        user_request: User's material description
        selected_category_key: Key of selected category from registry
        
    Returns:
        {
            "conflict_detected": bool,
            "conflict_reason": str,
            "suggested_domain": str,
            "category_description": str
        }
    """
    request_lower = user_request.lower()
    
    # Get category info
    category = CATEGORY_REGISTRY.get(selected_category_key, {})
    category_keywords = category.get("priority_keywords", [])
    category_keywords_lower = [kw.lower() for kw in category_keywords]
    
    # Special case: Heavy Metal Adsorbent without heavy metal mention
    if selected_category_key == "adsorbent_heavy_metals":
        heavy_metal_keywords = ["lead", "cadmium", "arsenic", "chromium", "pb", "cd", "as", "cr", "heavy metal"]
        has_heavy_metal = any(kw in request_lower for kw in heavy_metal_keywords)
        
        if not has_heavy_metal:
            # Check if request is about fabric/laundry instead
            if any(kw in request_lower for kw in DOMAIN_KEYWORDS["fabric_cleaning"]["keywords"]):
                return {
                    "conflict_detected": True,
                    "conflict_reason": "Request describes fabric/laundry stain removal but Heavy Metal Adsorbent category was selected. No heavy metals mentioned.",
                    "suggested_domain": "fabric_cleaning",
                    "category_description": "Request strongly indicates textile/laundry application, not water treatment for heavy metals."
                }
            
            # Check if request is about water treatment (generic)
            if any(kw in request_lower for kw in DOMAIN_KEYWORDS["water_treatment"]["keywords"]):
                return {
                    "conflict_detected": True,
                    "conflict_reason": "Heavy Metal Adsorbent selected but request doesn't mention heavy metals. Generic water treatment mentioned instead.",
                    "suggested_domain": "water_treatment",
                    "category_description": "Request indicates general water treatment, not specifically heavy metal removal."
                }
    
    # Check keyword match percentage
    matched_keywords = sum(1 for kw in category_keywords_lower if kw in request_lower)
    match_percentage = matched_keywords / len(category_keywords_lower) if category_keywords_lower else 0
    
    # If match is very low, check for domain mismatch
    if match_percentage < 0.3:  # Less than 30% keyword match
        detected_domains = extract_request_domain(user_request)
        if detected_domains and detected_domains[0][1] > 30:  # Strong domain detection
            domain_name = detected_domains[0][0]
            return {
                "conflict_detected": True,
                "conflict_reason": f"Selected category '{category.get('display_name')}' has poor keyword match ({match_percentage*100:.0f}%). Request appears to be {domain_name.replace('_', ' ')}.",
                "suggested_domain": domain_name,
                "category_description": f"Request strongly indicates {domain_name.replace('_', ' ')} application."
            }
    
    return {
        "conflict_detected": False,
        "conflict_reason": "",
        "suggested_domain": None,
        "category_description": ""
    }


def score_category_match(user_request: str, category_key: str, category_data: dict) -> float:
    """
    Score how well a category matches the user request (0-100).
    
    Args:
        user_request: User's material description
        category_key: Category key from registry
        category_data: Category data from registry
        
    Returns:
        Confidence score 0-100
    """
    request_lower = user_request.lower()
    
    score = 0.0
    
    # 1. Keyword matching (max 60 points)
    keywords = category_data.get("priority_keywords", [])
    if keywords:
        matched = sum(1 for kw in keywords if kw.lower() in request_lower)
        keyword_score = (matched / len(keywords)) * 60
        score += keyword_score
    
    # 2. Aliases matching (max 20 points)
    aliases = category_data.get("aliases", [])
    if aliases:
        matched_aliases = sum(1 for alias in aliases if alias.lower() in request_lower)
        alias_score = (matched_aliases / len(aliases)) * 20
        score += alias_score
    
    # 3. Display name matching (max 10 points)
    display_name = category_data.get("display_name", "").lower()
    words_in_display = display_name.split()
    if words_in_display:
        matched_words = sum(1 for word in words_in_display if word in request_lower)
        name_score = (matched_words / len(words_in_display)) * 10
        score += name_score
    
    # 4. Negative penalty for conflicting content
    negative_keywords = {
        "adsorbent_heavy_metals": ["fabric", "laundry", "stain", "cotton", "textile", "clothing"],
        "fabric_oil_stain_removal_composite": ["lead", "cadmium", "arsenic", "heavy metal"],
        "photocatalytic_coating": ["fabric", "laundry", "clothing"],
    }
    
    if category_key in negative_keywords:
        conflicting = sum(1 for neg_kw in negative_keywords[category_key] if neg_kw in request_lower)
        if conflicting > 0:
            score -= conflicting * 15
    
    return max(0, min(100, score))


def propose_candidate_categories(user_request: str, existing_registry: Dict = None) -> List[dict]:
    """
    Generate 2-5 candidate categories based on user request.
    
    Combines:
    1. Existing categories that partially match
    2. Newly proposed categories based on detected domain
    
    Args:
        user_request: User's material description
        existing_registry: CATEGORY_REGISTRY (optional, uses global if not provided)
        
    Returns:
        List of suggested categories with highest confidence first:
        [
            {
                "display_name": str,
                "normalized_category_name": str,
                "material_family": str,
                "functional_class": str,
                "application_domain": str,
                "matched_keywords": [str],
                "reason": str,
                "exists_in_registry": bool,
                "confidence": int (0-100)
            },
            ...
        ]
    """
    if existing_registry is None:
        existing_registry = CATEGORY_REGISTRY
    
    candidates = []
    
    # Step 1: Score all existing categories
    existing_candidates = []
    for cat_key, cat_data in existing_registry.items():
        if cat_key == "other_material":
            continue
        
        score = score_category_match(user_request, cat_key, cat_data)
        
        if score > 20:  # Only include if some match
            request_lower = user_request.lower()
            matched_kw = [kw for kw in cat_data.get("priority_keywords", []) if kw.lower() in request_lower]
            
            existing_candidates.append({
                "display_name": cat_data.get("display_name", cat_key),
                "normalized_category_name": cat_key,
                "material_family": cat_data.get("material_family", "unknown"),
                "functional_class": cat_data.get("functional_class", "unknown"),
                "application_domain": cat_data.get("application_domain", "unknown"),
                "matched_keywords": matched_kw[:5],
                "reason": f"Existing category with {score:.0f}% keyword match",
                "exists_in_registry": True,
                "confidence": int(score)
            })
    
    # Step 2: Generate new suggested categories based on detected domain
    detected_domains = extract_request_domain(user_request)
    
    new_suggested = []
    for domain_name, domain_confidence in detected_domains[:2]:  # Top 2 domains
        if domain_confidence >= 20:  # Include if confidence >= 20 (lowered from > 20)
            template = DOMAIN_KEYWORDS[domain_name]["category_template"]
            
            # Generate category name from request
            if domain_name == "fabric_cleaning":
                # Special handling for fabric cleaning
                display_name = "Fabric Oil-Stain Removal Composite"
                normalized_name = "fabric_oil_stain_removal_composite"
                reason = "Request describes fabric/laundry stain removal with mentions of cotton, oil stains, and washing compatibility."
            else:
                display_name = " ".join(word.capitalize() for word in domain_name.split("_"))
                normalized_name = domain_name
                reason = f"Detected strong {domain_name.replace('_', ' ')} application domain in request."
            
            new_suggested.append({
                "display_name": display_name,
                "normalized_category_name": normalized_name,
                "material_family": template.get("material_family", "hybrid"),
                "functional_class": template.get("functional_class", "unknown"),
                "application_domain": template.get("application_domain", "unknown"),
                "matched_keywords": [kw for kw in DOMAIN_KEYWORDS[domain_name]["keywords"] if kw.lower() in user_request.lower()][:5],
                "reason": reason,
                "exists_in_registry": normalized_name in existing_registry,
                "confidence": int(domain_confidence)
            })
    
    # Step 3: Combine and sort by confidence
    all_candidates = existing_candidates + new_suggested
    all_candidates.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Step 4: Return top 2-5 candidates
    return all_candidates[:5]


def should_show_suggestions(confidence_score: int, selected_category_key: str, user_request: str) -> bool:
    """
    Determine if suggestion panel should be shown.
    
    Shows suggestions if:
    - Confidence < 85%
    - Conflict detected
    - Multiple strong domain matches
    
    Args:
        confidence_score: Classification confidence (0-100)
        selected_category_key: Selected category key
        user_request: User's material description
        
    Returns:
        bool - True if suggestions should be shown
    """
    # Show if confidence is low
    if confidence_score < 85:
        return True
    
    # Show if conflict detected
    conflict = detect_category_conflict(user_request, selected_category_key)
    if conflict.get("conflict_detected"):
        return True
    
    # Show if multiple strong domain matches
    domains = extract_request_domain(user_request)
    if len(domains) >= 2 and domains[0][1] - domains[1][1] < 20:  # Close scores
        return True
    
    return False


# ==============================================================================
# HELPER: Generate complete category preset
# ==============================================================================

def generate_suggested_category_preset(suggested_category: dict, user_request: str) -> dict:
    """
    Generate a complete category preset from a suggested category.
    
    This converts a suggestion into a full category preset ready to add to registry.
    
    Args:
        suggested_category: Suggested category dict from propose_candidate_categories()
        user_request: Original user request
        
    Returns:
        Complete category preset dict ready for registry
    """
    from auto_category_creation import (
        _generate_aliases,
        _generate_keywords,
        _generate_default_composition,
        _generate_category_parameters,
        _generate_validation_plan,
        _generate_safety_tests,
        _generate_characterization_methods,
        _generate_processing_method,
        _generate_disclaimer,
        _detect_safety_warnings
    )
    
    # Extract concepts from suggested category
    concepts = suggested_category["matched_keywords"]
    
    return {
        "normalized_category_name": suggested_category["normalized_category_name"],
        "display_name": suggested_category["display_name"],
        "material_family": suggested_category["material_family"],
        "functional_class": suggested_category["functional_class"],
        "application_domain": suggested_category["application_domain"],
        "aliases": _generate_aliases(user_request, concepts),
        "priority_keywords": _generate_keywords(user_request, concepts),
        "default_composition": _generate_default_composition(concepts, user_request),
        "category_specific_parameters": _generate_category_parameters(concepts, user_request, suggested_category["material_family"]),
        "validation_plan": _generate_validation_plan(concepts, user_request, {}),
        "safety_tests": _generate_safety_tests(concepts, user_request, suggested_category["material_family"]),
        "characterization_methods": _generate_characterization_methods(suggested_category["material_family"], suggested_category["functional_class"]),
        "processing_method": _generate_processing_method(concepts, user_request, suggested_category["material_family"], suggested_category["functional_class"]),
        "category_specific_disclaimer": _generate_disclaimer(suggested_category["display_name"], concepts),
        "safety_warnings": _detect_safety_warnings(user_request, concepts)
    }
