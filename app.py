# -*- coding: utf-8 -*-
"""
Materials Science AI with Intelligent Category Presets
=======================================================
Detects material categories (AWH, photocatalysis, etc.) and enriches
analysis with category-specific parameters and validation plans.

Architecture: Central Category Registry
- Single source of truth for all categories
- Priority-based classification to prevent conflicts
- Unified preset management and application
- Scientific label protection for PDF export
"""

import streamlit as st
from anthropic import Anthropic, APIError, RateLimitError
import json
import os
import time
from datetime import datetime
from fpdf import FPDF
from io import BytesIO
from dotenv import load_dotenv

# Import the central category registry
from category_registry import (
    CATEGORY_REGISTRY,
    CATEGORY_PRIORITY_ORDER,
    HIERARCHICAL_PRESETS,
    MATERIAL_FAMILIES,
    FUNCTIONAL_CLASSES,
    APPLICATION_DOMAINS,
    classify_material_category,
    classify_material_hierarchically,
    get_category_preset,
    apply_category_preset,
    validate_required_fields,
    format_scientific_label,
    export_report,
    get_category_display_name,
    validate_category_exists,
    clear_previous_preset_fields,
    run_three_stage_verification,
    normalize_category_name,  # NEW: for normalizing category names
    validate_composition_components,  # NEW: validate composition doesn't contain substrates
    clean_composition_components,  # NEW: remove substrate/environment items from composition
)

# Import scientific dataset verification
try:
    from scientific_data_connectors import format_verification_for_pdf
    SCIENTIFIC_VERIFICATION_AVAILABLE = True
except ImportError:
    SCIENTIFIC_VERIFICATION_AVAILABLE = False

# Import auto-category creation and helper
from auto_category_creation import (
    detect_category_gap,
    propose_new_category,
    check_duplicate_category,
    add_category_to_registry,
    apply_new_category_and_verify
)
from streamlit_auto_category_ui import (
    show_category_gap_detection_ui,
    show_category_editing_ui,
    show_category_approval_panel
)
from app_integration_helper import (
    init_auto_category_session,
    add_auto_category_sidebar_toggle,
    handle_auto_category_workflow,
    apply_auto_category_to_material,
    reset_auto_category_state
)

# Import auto-category creation and helper
from auto_category_creation import (
    detect_category_gap,
    propose_new_category,
    check_duplicate_category,
    add_category_to_registry,
    apply_new_category_and_verify
)
from streamlit_auto_category_ui import (
    show_category_gap_detection_ui,
    show_category_editing_ui,
    show_category_approval_panel
)
from app_integration_helper import (
    init_auto_category_session,
    add_auto_category_sidebar_toggle,
    handle_auto_category_workflow,
    apply_auto_category_to_material,
    reset_auto_category_state
)

# Import suggested category workflow
from suggested_category_workflow import (
    detect_category_conflict,
    propose_candidate_categories,
    should_show_suggestions,
    generate_suggested_category_preset
)
from suggested_categories_ui import (
    show_suggested_categories_panel,
    show_category_comparison
)

# Local definitions (workaround for Streamlit import caching issues)
PROTECTED_LABEL_MAP = {
    # pH terms
    "ph working range": "pH Working Range",
    "ph dependence": "pH Dependence",
    "relative pH operating window": "Relative pH Operating Window",
    
    # Potassium selectivity and ratios
    "k na selectivity": "K+/Na+ Selectivity",
    "k mg selectivity": "K+/Mg2+ Selectivity",
    "k ca selectivity": "K+/Ca2+ Selectivity",
    "sodium to potassium ratio": "Sodium-to-Potassium Ratio",
    "magnesium to potassium ratio": "Magnesium-to-Potassium Ratio",
    "k na mg ca interference": "K+/Na+/Mg2+/Ca2+ Interference Resistance",
    
    # Ion and chemical terms
    "pb2+ removal capacity": "Pb2+ Removal Capacity",
    "cd2+ removal capacity": "Cd2+ Removal Capacity",
    "as3+ and as5+ removal": "As3+ and As5+ Removal",
    "cr3+ and cr6+ removal": "Cr3+ and Cr6+ Removal",
    "cl- or no3- co-ion": "Cl- or NO3- Co-ion",
    "so4^2- or po4-p anion": "SO4^2- or PO4-P Anion",
    "co2 leaching": "CO2 Leaching",
    
    # Membrane and coating terms
    "tio2 photocatalyst": "TiO2 Photocatalyst",
    "zno additive": "ZnO Additive",
    "uv-a and uv-b": "UV-A and UV-B",
    
    # Fouling and stability terms
    "scaling fouling resistance": "Scaling / Fouling Resistance",
    "leaching safety and mechanical stability": "Leaching Safety & Mechanical Stability",
    "bacterial growth inhibition": "Bacterial Growth Inhibition",
    
    # Analytical methods - preserve as-is
    "icp-oes analysis": "ICP-OES Analysis",
    "icp-ms analysis": "ICP-MS Analysis",
    "sem eds imaging": "SEM/EDS Imaging",
    "xrd characterization": "XRD Characterization",
    "ftir spectroscopy": "FTIR Spectroscopy",
    "xps surface": "XPS Surface",
    "bet analysis": "BET Analysis",
    
    # General technical terms
    "initial potassium concentration": "Initial Potassium Concentration",
    "potassium spike concentration": "Potassium Spike Concentration",
    "potassium recovery efficiency": "Potassium Recovery Efficiency",
    "ion exchange capacity": "Ion Exchange Capacity",
}

def format_parameter_label(key: str) -> str:
    """Format a parameter key into a display label, preserving scientific notation."""
    label = key.replace("_", " ").lower()
    if label in PROTECTED_LABEL_MAP:
        return PROTECTED_LABEL_MAP[label]
    return key.replace("_", " ").title()


# LOCAL VERIFICATION FUNCTIONS (Workaround for Streamlit caching)
def detect_category_conflicts(user_request: str, selected_category: str) -> dict:
    """Detect hard category conflicts using explicit conflict rules."""
    request_lower = user_request.lower()
    
    # CRITICAL RULE: Fabric/Laundry → NEVER classify as Heavy Metal Adsorbent
    fabric_keywords = ["fabric", "cotton", "clothing", "laundry", "garment", "textile",
                       "oil stain", "grease stain", "pre-treat", "pre-wash", "washing machine",
                       "stain removal", "laundry stain", "fabric stain"]
    heavy_metal_keywords = ["lead", "cadmium", "arsenic", "chromium", "pb", "cd", "as", "cr", "toxic metal"]
    
    if any(kw.lower() in request_lower for kw in fabric_keywords):
        # Only flag as conflict if there are NO heavy metal keywords
        if not any(hm.lower() in request_lower for hm in heavy_metal_keywords):
            if selected_category == "adsorbent_heavy_metals":
                return {
                    "conflict_detected": True,
                    "conflict_reason": "🚨 CRITICAL CONFLICT: Request is about fabric stain removal (laundry), NOT heavy metal removal. Category MUST be Fabric Oil-Stain Removal Composite.",
                    "recommended_category": "fabric_oil_stain_removal_composite",
                    "blocked_export": True  # BLOCK export - this is a critical misclassification
                }
            elif selected_category not in ["fabric_oil_stain_removal_composite", "other_material"]:
                # Suggest fabric category if wrong category is selected
                return {
                    "conflict_detected": True,
                    "conflict_reason": "Request appears to be about fabric/laundry stain removal. Better category available: Fabric Oil-Stain Removal Composite.",
                    "recommended_category": "fabric_oil_stain_removal_composite",
                    "blocked_export": True
                }
    
    # Roof Waterproofing Thermal Insulation Coating Rule (NEW)
    # If prompt is about roof waterproofing, prefer roof_waterproofing_thermal_insulation_coating over thermal_insulation_composite
    roof_waterproofing_keywords = [
        "roof", "rooftop", "roof-applied", "roof coating", "roof waterproofing",
        "water leakage", "rainwater", "waterproof", "concrete roof"
    ]
    
    if any(kw.lower() in request_lower for kw in roof_waterproofing_keywords):
        if selected_category == "thermal_insulation_composite":
            # Check if there are strong thermal insulation keywords without roof keywords
            thermal_only_keywords = ["thermal insulation", "insulation composite", "temperature reduction"]
            roof_only_keywords = ["roof", "rooftop", "waterproof", "water leakage", "rainwater"]
            
            has_roof_keywords = any(kw.lower() in request_lower for kw in roof_only_keywords)
            has_thermal_keywords = any(kw.lower() in request_lower for kw in thermal_only_keywords)
            
            # If has roof keywords (more specific), suggest roof coating instead
            if has_roof_keywords and has_thermal_keywords:
                return {
                    "conflict_detected": True,
                    "conflict_reason": "Request appears to describe a roof waterproofing & thermal insulation coating. Roof Waterproofing & Thermal Insulation Coating is more specific than generic Thermal Insulation Composite.",
                    "recommended_category": "roof_waterproofing_thermal_insulation_coating",
                    "blocked_export": False  # Suggest, don't block - user can override
                }
    
    # Self-Cleaning Building Coating + AWH Conflict Rule (NEW)
    # Detect when user describes a self-cleaning building coating but selects AWH
    self_cleaning_coating_keywords = [
        "self-cleaning", "self cleaning", "self-cleaning coating", "exterior coating",
        "building coating", "facade coating", "photocatalytic nanoparticles",
        "photocatalytic dirt degradation", "surface organic dirt", "sunlight degradation",
        "dust accumulation", "uv aging", "adhesion", "abrasion resistance",
        "color stability", "weather resistance", "algae resistance", "biofilm resistance"
    ]
    awh_only_keywords = [
        "atmospheric water harvesting", "water vapor capture", "moisture capture for water",
        "harvested water", "hygroscopic salt", "salt leaching", "collected water quality",
        "desorption for water", "water-harvesting cycles"
    ]
    
    if any(kw.lower() in request_lower for kw in self_cleaning_coating_keywords):
        if selected_category == "atmospheric_water_harvesting_material":
            # Only flag as conflict if there are NO AWH-specific keywords
            if not any(kw.lower() in request_lower for kw in awh_only_keywords):
                return {
                    "conflict_detected": True,
                    "conflict_reason": "Potential Conflict Detected: Request describes a self-cleaning photocatalytic building coating, but selected category is Atmospheric Water Harvesting Material. These are incompatible.",
                    "recommended_category": "self_cleaning_building_coating",
                    "blocked_export": True
                }
    
    # CO2 Conflict Rule
    co2_keywords = [
        "co2 capture", "co₂ capture", "carbon dioxide capture", "flue gas",
        "direct air capture", "amine-functionalized silica", "co₂ uptake",
        "co2/n2 selectivity", "water vapor selectivity", "amine loss"
    ]
    if any(kw.lower() in request_lower for kw in co2_keywords):
        if selected_category == "photocatalytic_coating":
            return {
                "conflict_detected": True,
                "conflict_reason": "Request mentions CO₂ capture, but selected category is Photocatalytic Coating. These are incompatible.",
                "recommended_category": "co2_capture_material",
                "blocked_export": True
            }
    
    # Membrane Conflict Rule
    membrane_keywords = [
        "membrane", "anti-fouling", "permeability", "water flux",
        "rejection efficiency", "filtration cycles", "cleaning recovery"
    ]
    heavy_metal_keywords = ["lead", "cadmium", "arsenic", "chromium", "mercury", "heavy metal"]
    
    if any(kw.lower() in request_lower for kw in membrane_keywords):
        if selected_category == "adsorbent_heavy_metals":
            if not any(kw.lower() in request_lower for kw in heavy_metal_keywords):
                return {
                    "conflict_detected": True,
                    "conflict_reason": "Request mentions membrane/filtration, but selected category is Heavy Metal Adsorbent.",
                    "recommended_category": "membrane_water_treatment",
                    "blocked_export": True
                }
    
    # Desalination Pre-Treatment Conflict Rule (NEW)
    desalination_keywords = [
        "desalination pre-treatment", "desalination pretreatment", "desal pretreatment",
        "pre-treatment media", "seawater treatment", "membrane pre-treatment",
        "osmosis pre-treatment"
    ]
    if any(kw.lower() in request_lower for kw in desalination_keywords):
        if selected_category in ["membrane_water_treatment", "adsorbent_heavy_metals", "other_material"]:
            return {
                "conflict_detected": True,
                "conflict_reason": "Request mentions desalination pre-treatment. Correct category: Desalination Pre-Treatment Media.",
                "recommended_category": "desalination_pretreatment_media",
                "blocked_export": True
            }
    
    # AWH Conflict Rule (STRENGTHENED)
    # Only match AWH if there are strong AWH-specific keywords, not just generic moisture keywords
    awh_specific_keywords = [
        "atmospheric water harvesting", "water vapor capture", "moisture capture for water",
        "water uptake", "harvested water", "hygroscopic salt", "salt leaching",
        "collected water quality", "desorption for water", "wet/dry cycles", "awh", "desiccant"
    ]
    generic_categories = ["other_material", "generic_composite"]
    
    if any(kw.lower() in request_lower for kw in awh_specific_keywords):
        if selected_category in generic_categories:
            return {
                "conflict_detected": True,
                "conflict_reason": "Request mentions atmospheric water harvesting, but selected category is too generic.",
                "recommended_category": "atmospheric_water_harvesting_material",
                "blocked_export": True
            }
    
    # Phosphate Conflict Rule
    phosphate_keywords = [
        "phosphate recovery", "phosphate ions", "phosphate", "fertilizer reuse",
        "nutrient recovery", "p recovery"
    ]
    if any(kw.lower() in request_lower for kw in phosphate_keywords):
        if selected_category == "other_material":
            return {
                "conflict_detected": True,
                "conflict_reason": "Request mentions phosphate recovery, but no category preset was selected.",
                "recommended_category": "phosphate_recovery_material",
                "blocked_export": True
            }
    
    # Potassium Brine Conflict Rule
    potassium_keywords = [
        "potassium salts", "k+ recovery", "mineral-rich brine",
        "potash brine", "sodium and magnesium competition", "k+ selectivity"
    ]
    if any(kw.lower() in request_lower for kw in potassium_keywords):
        if selected_category in ["other_material", "adsorbent_heavy_metals"]:
            return {
                "conflict_detected": True,
                "conflict_reason": "Request mentions potassium recovery from brine, but selected category doesn't match.",
                "recommended_category": "potassium_brine_separation_material",
                "blocked_export": True
            }
    
    return {"conflict_detected": False, "conflict_reason": "", "recommended_category": selected_category, "blocked_export": False}


def verify_material_decision(user_request: str, selected_category: str, material_data: dict) -> dict:
    """Verify that the selected category is consistent with the user request and material data."""
    conflict_result = detect_category_conflicts(user_request, selected_category)
    
    if conflict_result["blocked_export"]:
        return {
            "verification_status": "fail",
            "conflict_detected": True,
            "conflict_reason": conflict_result["conflict_reason"],
            "recommended_category": conflict_result["recommended_category"],
            "blocked_export": True,
            "user_confirmation_required": False,
            "details": f"Hard conflict detected: {conflict_result['conflict_reason']}"
        }
    
    return {
        "verification_status": "pass",
        "conflict_detected": False,
        "conflict_reason": "",
        "recommended_category": selected_category,
        "blocked_export": False,
        "user_confirmation_required": False,
        "details": "Verification passed: category is consistent with request and preset"
    }


def apply_new_category(category_key: str, result: dict, user_prompt: str) -> dict:
    """
    Apply a new category to the result and regenerate parameters.
    
    Steps:
    1. Clear all old preset-specific fields
    2. Set new category
    3. Apply new preset parameters
    4. Update hierarchical classification
    """
    # Step 1: Clear old preset fields to avoid contamination
    result = clear_previous_preset_fields(result)
    
    # Step 2: Update the category
    result["material_category"] = category_key
    result["material_category_display"] = CATEGORY_REGISTRY.get(category_key, {}).get("display_name", category_key)
    
    # Step 3: Apply the new preset
    preset_data = get_category_preset(category_key)
    
    # Merge preset data into result
    result["category_specific_parameters"] = preset_data.get("category_specific_parameters", {})
    result["validation_plan"] = preset_data.get("validation_plan", {})
    result["characterization_methods"] = preset_data.get("characterization_methods", [])
    result["safety_tests"] = preset_data.get("safety_tests", [])
    result["category_specific_disclaimer"] = preset_data.get("category_specific_disclaimer", "")
    result["default_composition"] = preset_data.get("default_composition", [])
    
    # Create aliases for backward compatibility with UI and PDF export
    result["preset_parameters"] = result["category_specific_parameters"]
    result["preset_validation_plan"] = result["validation_plan"]
    result["category_disclaimer"] = result["category_specific_disclaimer"]
    
    # Step 4: Update hierarchical classification to match
    hier_classification = classify_material_hierarchically(user_prompt)
    result["hierarchical_classification"] = hier_classification
    
    return result


def regenerate_conflict_check(user_prompt: str, category_key: str) -> dict:
    """Re-run conflict detection with new category."""
    return detect_category_conflicts(user_prompt, category_key)

# Load environment variables
load_dotenv()

# Try to get API key from Streamlit Secrets first (for Streamlit Cloud)
# Fall back to environment variables (for local development)
try:
    ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY")
except (AttributeError, KeyError):
    ANTHROPIC_API_KEY = None

# If not in Streamlit Secrets, try environment variables
if not ANTHROPIC_API_KEY:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if ANTHROPIC_API_KEY:
    claude_client = Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    claude_client = None

# ============================================================================
# BACKWARD COMPATIBILITY: Keep old MATERIAL_PRESETS reference
# (Updated to use registry data)
# ============================================================================

MATERIAL_PRESETS = {
    category_key: {
        "display_name": data.get("display_name"),
        "keywords": data.get("priority_keywords", []),
        "parameters": data.get("category_specific_parameters", {}),
        "validation_plan": data.get("validation_plan", {}),
        "category_disclaimer": data.get("category_specific_disclaimer", ""),
    }
    for category_key, data in CATEGORY_REGISTRY.items()
}

MATERIAL_PRESETS = {
    "atmospheric_water_harvesting_material": {
        "display_name": "Atmospheric Water Harvesting Material",
        "keywords": ["atmospheric water harvesting", "moisture capture", "hygroscopic salt", "water from air", "wet/dry cycles", "salt leaching", "collected water quality"],
        "parameters": {
            "relative_humidity_range": "40-90% RH (optimal moisture capture window)",
            "water_uptake_target": "0.3-0.8 g water per g dry material",
            "adsorption_time": "4-12 hours under ambient conditions",
            "desorption_temperature": "50-80 degrees C (thermal or solar regeneration)",
            "regeneration_method": "Sunlight-assisted heating or low-grade thermal (waste heat compatible)",
            "cycling_target": "50-100 wet/dry cycles minimum (durability benchmark)",
            "salt_leaching_test_method": "Immersion test + chloride/conductivity measurement per cycle",
            "collected_water_quality_test": "pH, TDS, conductivity, trace metals (ICP), microbial screening"
        },
        "validation_plan": {
            "water_uptake_capacity": "Quantified at 40%, 60%, 80% RH via gravimetric analysis",
            "rh_working_range": "Minimum RH (material saturation limit) and maximum RH (hygroscopic plateau)",
            "adsorption_kinetics": "Time to reach 90% equilibrium saturation (breakthrough curve)",
            "desorption_kinetics": "Time to release >80% absorbed water during thermal cycle",
            "regeneration_energy": "Thermal input (kWh) required per kg water recovered",
            "cycling_durability": "Retained water uptake (%) after 50 and 100 wet/dry cycles",
            "salt_leaching": "Salt mass balance per cycle; acceptable levels per end-use water standard",
            "collected_water_quality": "pH, TDS, conductivity, chloride (mg/L), trace metals, and microbial count per applicable standard; research-stage target: chloride <100 mg/L preliminary screening"
        },
        "category_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven water-harvesting performance, potable-water safety, commercial readiness, or suitability for any specific application. All recommendations are CONDITIONAL upon rigorous laboratory validation, field testing, compliance with applicable water-quality standards, and consultation with qualified materials engineers and water-quality specialists. This report is for research and development guidance only."
    },
    "photocatalytic_coating": {
        "display_name": "Photocatalytic Coating",
        "keywords": ["photocatalytic", "photodegradation", "TiO2", "visible light", "UV light", "pollutant degradation"],
        "parameters": {
            "substrate_type": "Glass, ceramic, or polymer",
            "coating_thickness": "0.5-5 micrometers",
            "curing_temperature": "Room temperature or 60-150 C",
            "light_source": "UV-A, UV-B, or visible light (wavelength specification)",
            "target_pollutant": "Dyes, volatile organic compounds, or bacterial spores",
            "pollutant_concentration": "ppm or mg/L range",
            "catalyst_loading": "mg/cm2 or wt%"
        },
        "validation_plan": {
            "pollutant_degradation_efficiency": ">80% degradation at 90 min under specified light",
            "reaction_kinetics": "First-order rate constant (k) in min-1",
            "catalyst_stability": "Activity retention after 10 cycles",
            "leaching_test": "ICP-MS or atomic absorption spectroscopy for metal ion release",
            "characterization_methods": ["SEM", "XRD", "FTIR", "UV-Vis DRS", "BET"],
            "toxicity_safety_review": "Leachate non-toxic; no hazardous byproducts"
        },
        "category_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven photocatalytic degradation efficiency, coating durability, treated-water safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, leaching analysis, toxicity testing, durability testing, field testing where appropriate, and consultation with qualified materials engineers and water-quality specialists. This report is for research and development guidance only."
    },
    "phosphate_recovery_material": {
        "display_name": "Phosphate Recovery Material",
        "keywords": ["phosphate recovery", "phosphate ions", "phosphorus recovery", "nutrient recovery", "fertilizer reuse", "agricultural wastewater", "industrial wastewater phosphate", "calcium-based minerals", "iron oxide phosphate adsorption"],
        "parameters": {
            "target_phosphate_species": "Orthophosphate / PO4-P",
            "initial_phosphate_concentration": "1–100 mg/L PO4-P for screening",
            "ph_working_range": "5–9",
            "contact_time": "30–240 minutes",
            "adsorbent_dosage": "0.5–5 g/L",
            "competing_ions": "nitrate, sulfate, carbonate, chloride, calcium, magnesium",
            "regeneration_method": "alkaline, acidic, or salt-based desorption depending on material stability",
            "recovery_pathway": "concentrated phosphate solution or solid nutrient-loaded material for fertilizer evaluation",
            "nutrient_release_test": "water and soil-simulant release testing",
            "leaching_safety_test": "Fe, Ca, binder residues, trace metals, pH, conductivity"
        },
        "validation_plan": {
            "phosphate_uptake_capacity": "mg PO4-P / g adsorbent (Langmuir saturation)",
            "removal_efficiency": "preliminary target >60–80% under screening conditions",
            "regeneration_efficiency": ">50–80% phosphate recovery after desorption",
            "cycling_stability": "5–10 adsorption/desorption cycles minimum",
            "competing_ion_tolerance": "performance measured in synthetic and real wastewater",
            "fertilizer_reuse_potential": "nutrient release tested before circular-economy claim",
            "characterization_methods": ["SEM/EDS", "XRD", "FTIR", "BET", "ICP-OES", "colorimetric phosphate analysis"],
            "adsorption_kinetics": "pseudo-first-order or pseudo-second-order rate fitting",
            "isotherm_fitting": "Langmuir/Freundlich model parameters",
            "ph_dependence": "uptake vs pH profile",
            "cycling_durability": "retained capacity after 5-10 cycles",
            "leaching_analysis": "trace metals, Fe, Ca, binder residues by ICP-MS",
            "ecotoxicity_review": "environmental safety assessment",
            "wastewater_testing": "performance in real agricultural or industrial wastewater"
        },
        "category_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven phosphate recovery performance, fertilizer suitability, environmental safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, leaching analysis, nutrient-release testing, ecotoxicity assessment, wastewater testing, and consultation with qualified materials engineers, environmental specialists, and fertilizer/regulatory experts. This report is for research and development guidance only."
    },
    "potassium_brine_separation_material": {
        "display_name": "Potassium Brine Separation Material",
        "keywords": ["potassium recovery", "potassium salt recovery", "potassium capture", "K+ recovery", "potash brine", "mineral-rich brine", "selective separation from brine", "sodium and magnesium competition", "ion-exchange groups", "crown ether", "functionalized porous silica", "brine selectivity"],
        "parameters": {
            "target_ion": "K+",
            "competing_ions": "Na+, Mg2+, Ca2+, Cl-, SO4²-",
            "brine_matrix": "synthetic mineral brine, seawater brine, potash brine, or Dead Sea-type brine",
            "initial_potassium_concentration": "100–10,000 mg/L K+ (screening range depends on brine source)",
            "sodium_to_potassium_ratio": "measured and reported for each brine type",
            "magnesium_to_potassium_ratio": "measured and reported for each brine type",
            "ph_working_range": "6–9 (unless material chemistry requires otherwise)",
            "contact_time": "30–240 minutes",
            "adsorbent_dosage": "0.5–5 g/L",
            "selectivity_coefficients": "K+/Na+, K+/Mg2+, and K+/Ca2+ selectivity values",
            "adsorption_capacity": "mg K+ / g adsorbent",
            "regeneration_method": "salt, acid, base, or water-based elution depending on resin stability",
            "regeneration_efficiency": "% K+ recovered after desorption",
            "fouling_scaling_test": "evaluate Mg/Ca precipitation, salt scaling, and pore blockage resistance",
            "cycling_target": "10–50 adsorption/desorption cycles minimum",
            "product_quality_test": "recovered potassium purity and contamination by Na, Mg, Ca"
        },
        "validation_plan": {
            "potassium_uptake_capacity": "mg K+ / g material at saturation",
            "adsorption_kinetics": "time-dependent K+ uptake profile and equilibration time",
            "adsorption_isotherm": "Langmuir, Freundlich, or Dubinin-Radushkevich model fitting",
            "k_na_selectivity": "K+/Na+ selectivity coefficient and uptake comparison",
            "k_mg_selectivity": "K+/Mg2+ selectivity coefficient and uptake comparison",
            "k_ca_selectivity": "K+/Ca2+ selectivity coefficient and uptake comparison",
            "regeneration_efficiency": ">50–80% K+ recovery target after desorption",
            "cycling_durability": ">80% capacity retention after 10 cycles for early screening",
            "scaling_fouling_resistance": "stable capacity under repeated high-salinity brine exposure",
            "real_brine_testing": "performance in authentic mineral, seawater, or potash brine samples",
            "product_purity_analysis": "recovered potassium salt composition by ICP-OES or ion chromatography",
            "leaching_safety_and_mechanical_stability": "binder, silica, resin, and additive leaching plus wet cycling durability"
        },
        "category_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven potassium recovery performance, ion selectivity, brine compatibility, regeneration efficiency, product purity, environmental safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, real-brine testing, ion-selectivity analysis, regeneration studies, scaling/fouling assessment, leaching analysis, and consultation with qualified materials engineers, water-treatment specialists, and mineral-processing experts. This report is for research and development guidance only."
    },
    "membrane_water_treatment": {
        "display_name": "Membrane Water Treatment Material",
        "keywords": ["membrane", "anti-fouling", "polymer membrane matrix", "PVDF", "PES", "PSf", "water flux", "permeability", "rejection efficiency", "filtration cycles", "cleaning recovery", "pore size", "molecular weight cut-off", "MWCO", "microfiltration", "ultrafiltration", "nanofiltration", "mixed-matrix membrane"],
        "parameters": {
            "membrane_type": "Microfiltration, ultrafiltration, nanofiltration, or mixed-matrix membrane",
            "water_flux_target": "L/m²·h under defined pressure",
            "operating_pressure": "0.1–10 bar depending on membrane type (UF typically 2–5 bar)",
            "rejection_target": "% rejection for turbidity, dyes, organics, salts, or selected contaminants",
            "fouling_resistance": "flux decline under organic foulant challenge (e.g., humic acid, BSA, oil emulsion)",
            "cleaning_recovery_target": "% flux recovery after physical or chemical cleaning",
            "pore_size_or_mwco": "Pore size in µm or molecular weight cut-off in Da/kDa",
            "contact_angle": "Hydrophilicity measurement (degrees); typically <80° for hydrophilic membranes",
            "nanoparticle_leaching_test": "Silica, carbon, antimicrobial additive release into treated water",
            "mechanical_durability": "Tensile strength, burst pressure, or compaction resistance",
            "filtration_cycling_target": "Repeated filtration/cleaning cycles before performance degradation"
        },
        "validation_plan": {
            "pure_water_permeability": "L/m²·h·bar baseline permeability",
            "flux_under_model_wastewater": "Flux under standard test conditions (e.g., 0.5 mg/L humic acid solution)",
            "contaminant_rejection_efficiency": "% rejection for target contaminants (turbidity, dyes, salts, organics)",
            "fouling_resistance_test": "Flux profile over time using humic acid, BSA, oil emulsion, or real wastewater challenge",
            "cleaning_recovery_test": "Flux recovery after physical rinsing, chemical backwashing, or chemical cleaning (e.g., NaOH, citric acid)",
            "long_term_filtration_stability": "Flux retention over extended operation (50–100 hours minimum)",
            "nanoparticle_additive_leaching": "Silica, carbon, antimicrobial (Ag, ZnO, TiO2) release by ICP-OES or IC",
            "mechanical_durability_testing": "Tensile strength, burst pressure, or compaction resistance under operating pressure",
            "sem_cross_section_morphology": "SEM imaging of membrane cross-section and surface; EDS elemental mapping if needed",
            "porosity_and_pore_size_distribution": "Mercury porosimetry, gas adsorption, or SEM-based pore analysis",
            "contact_angle_hydrophilicity": "Water contact angle measurement before and after fouling/cleaning cycles",
            "antimicrobial_testing": "Bacterial/algal growth inhibition if antimicrobial stabilizers (Ag, ZnO, TiO2, clay) are incorporated",
            "treated_water_safety_and_ecotoxicity": "Residual contaminant levels, pH, conductivity, microbial safety, and toxicity assessment if additives used"
        },
        "category_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven membrane permeability, contaminant rejection, anti-fouling performance, cleaning recovery, treated-water safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, long-term filtration testing, leaching analysis, mechanical durability testing, treated-water quality analysis, and consultation with qualified materials engineers, membrane specialists, and water-treatment experts. This report is for research and development guidance only."
    },
    "adsorbent_heavy_metals": {
        "display_name": "Heavy Metal Adsorbent",
        "keywords": ["heavy metals", "lead", "cadmium", "arsenic", "chromium", "Pb", "Cd", "As", "Cr", "wastewater adsorption", "modified biochar", "iron oxide nanoparticles", "metal ion removal", "leaching safety"],
        "parameters": {
            "target_ions": "Pb2+, Cd2+, As3+/As5+, Cr3+/Cr6+",
            "initial_metal_concentration": "1–100 mg/L for screening",
            "ph_working_range": "3–9",
            "contact_time": "30–240 minutes",
            "adsorbent_dosage": "0.5–5 g/L",
            "competing_ions": "Ca2+, Mg2+, Na+, Cl-, SO4²-, nitrate",
            "adsorption_capacity": "mg metal / g adsorbent",
            "removal_efficiency_target": ">70–90% under screening conditions",
            "regeneration_method": "acid, base, salt, or chelating-agent desorption depending on material stability",
            "regeneration_efficiency": "% metal recovered or % capacity restored",
            "separation_method": "filtration, sedimentation, or magnetic separation if iron oxide content sufficient",
            "leaching_safety_test": "Fe, silica, binder residues, trace contaminants, pH, conductivity",
            "water_matrix": "deionized water for screening, followed by synthetic and real wastewater"
        },
        "validation_plan": {
            "heavy_metal_uptake_capacity": "mg metal / g adsorbent at saturation",
            "adsorption_kinetics": "time-dependent metal uptake profile and equilibration time",
            "adsorption_isotherm": "Langmuir, Freundlich model fitting for single and multi-metal systems",
            "ph_dependence": "uptake vs pH profile for target metals",
            "competing_ion_selectivity": "metal removal in presence of Ca2+, Mg2+, Na+ interference",
            "multi_metal_performance": "simultaneous Pb, Cd, As, Cr removal efficiency",
            "regeneration_efficiency": "% metal recovered after acid, base, or chelating-agent desorption",
            "cycling_durability": "capacity retention after 5–10 adsorption/desorption cycles",
            "leaching_safety": "Fe, silica, binder, and additive leaching by ICP-OES; pH and conductivity of eluates",
            "treated_water_quality": "residual Pb, Cd, As, Cr by ICP-OES; comparison to drinking-water standards",
            "real_wastewater_testing": "performance in synthetic and authentic industrial or mine wastewater",
            "ecotoxicity_assessment": "toxicity of treated water and spent adsorbent disposal pathway"  
        },
        "category_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven heavy-metal removal performance, adsorption selectivity, regeneration efficiency, treated-water safety, environmental safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, real-wastewater testing, metal-ion analysis, leaching studies, regeneration testing, toxicity/ecotoxicity assessment, safe-disposal evaluation, and consultation with qualified materials engineers, water-treatment specialists, and environmental/regulatory experts. This report is for research and development guidance only."
    }
    # Add more presets as needed
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def apply_missing_preset_fields_local(material_data: dict, category_name: str) -> dict:
    """
    Apply only the missing fields from category preset.
    Local implementation to workaround Streamlit import caching issues.
    """
    preset = get_category_preset(category_name)
    
    # Add missing parameters
    expected_params = preset.get("category_specific_parameters", {})
    generated_params = material_data.get("category_specific_parameters", {})
    for param_name, param_spec in expected_params.items():
        if param_name not in generated_params:
            generated_params[param_name] = param_spec
    material_data["category_specific_parameters"] = generated_params
    
    # Add missing validation items
    expected_validation = preset.get("validation_plan", {})
    generated_validation = material_data.get("validation_plan", {})
    for val_name, val_spec in expected_validation.items():
        if val_name not in generated_validation:
            generated_validation[val_name] = val_spec
    material_data["validation_plan"] = generated_validation
    
    return material_data


def detect_material_category(user_prompt):
    """
    Detect material category using hierarchical classification.
    Returns hierarchical classification data with confidence scoring and alternatives.
    
    Returns:
        Hierarchical classification dict with all levels and confidence info
    """
    return classify_material_hierarchically(user_prompt)


def generate_fallback_composition(preset_key):
    """
    Generate default composition from the central registry.
    
    Uses the category registry's default_composition.
    """
    preset = get_category_preset(preset_key)
    return preset.get("default_composition", [])


def generate_fallback_result(user_prompt):
    """
    Generate a basic analysis from local presets when API fails.
    Uses the hierarchical category registry to ensure consistent preset application.
    """
    hier_classification = detect_material_category(user_prompt)
    preset_key = hier_classification.get("specific_preset", "other_material")
    display_name = CATEGORY_REGISTRY.get(preset_key, {}).get("display_name", preset_key)
    
    result = {
        "material_category": preset_key,
        "material_category_display": display_name,
        "target_application": "Research and development guidance (generated from local preset defaults)",
        "composition": generate_fallback_composition(preset_key),
        "user_defined_parameters": {},
        "user_defined_validation": {},
        "is_fallback": True,  # Mark this as fallback-generated
    }
    
    # Apply category preset to ensure all fields are populated
    result = apply_category_preset(result, preset_key)
    
    # Add validation warnings if using Other category
    if preset_key == "other_material":
        result["classification_warning"] = "No category-specific preset exists for this material. The report may be incomplete."
    
    return result


def validate_api_key():
    """Check if Anthropic API key is configured."""
    return ANTHROPIC_API_KEY is not None and claude_client is not None


def call_claude(prompt):
    """Call Claude API and parse JSON response. Returns structured result dict."""
    system_prompt = """You are a materials science expert. Given a user's description, return ONLY valid JSON with this structure:

{
  "material_category": "string (preset key or 'other_material')",
  "target_application": "brief description",
  "composition": [{"component": "string", "ratio": float}],
  "user_defined_parameters": {},
  "user_defined_validation": {}
}

CRITICAL RULES FOR COMPOSITION:

1. AWH (Atmospheric Water Harvesting) Detection:
   - If user mentions: moisture capture, water from air, salt leaching, wet/dry cycles, hygroscopic, thermal regeneration, water harvesting, solar-regenerated, atmospheric water
   - THEN set material_category to "atmospheric_water_harvesting_material"
   - THEN use EXACTLY this 6-component composition (percentages must sum to 1.0):
     * Activated carbon or porous carbon: 0.30
     * Porous silica or silica gel: 0.25
     * Aluminum oxide, inorganic stabilizer, or clay: 0.15
     * Calcium chloride or controlled hygroscopic salt: 0.15
     * Cellulose, polymer binder, or structural polymer: 0.10
     * Titanium dioxide, biochar, or carbon black (photothermal): 0.05
   - NEVER deviate from these percentages for AWH materials
   - Include all 6 components in every AWH composition
   - NEVER let photothermal exceed 10% for AWH
   - ALWAYS include stabilizer and binder for AWH (these are critical for handling, cycling, and durability)

2. Photocatalytic Coating Detection:
   - If user mentions: photocatalysis, photodegradation, TiO2, UV light, visible light, pollutant degradation
   - THEN set material_category to "photocatalytic_coating"
   - Adjust composition based on specific catalyst and substrate mentioned

3. Phosphate Recovery Material Detection:
   - If user mentions: phosphate recovery, phosphate ions, phosphorus recovery, nutrient recovery, fertilizer reuse, agricultural wastewater, industrial wastewater phosphate, calcium-based minerals, iron oxide phosphate adsorption
   - THEN set material_category to "phosphate_recovery_material"
   - THEN use EXACTLY this 5-component composition (percentages must sum to 1.0):
     * Calcium hydroxide or calcium-based mineral: 0.35
     * Iron oxide or iron hydroxide: 0.25
     * Porous activated carbon or biochar: 0.20
     * Bentonite clay or inorganic stabilizer: 0.10
     * Polymer or biopolymer binder: 0.10
   - NEVER deviate from these percentages for phosphate recovery materials
   - Include all 5 components in every phosphate recovery composition
   - ALWAYS include both calcium minerals and iron oxide (both are critical for phosphate adsorption)
   - ALWAYS include stabilizer and binder (critical for cycling durability and handling)

4. Potassium Brine Separation Material Detection:
   - If user mentions: potassium salt recovery, potassium capture, K+ recovery, potash brine, mineral-rich brine, selective separation from brine, sodium and magnesium competition, ion-exchange groups, crown ether, functionalized porous silica, brine selectivity
   - THEN set material_category to "potassium_brine_separation_material"
   - THEN use EXACTLY this 6-component composition (percentages must sum to 1.0):
     * Functionalized porous silica: 0.40
     * Potassium-selective ion-exchange resin or crown ether groups: 0.25
     * Zeolite or alumina stabilizer: 0.15
     * Water-stable polymer binder (PVA, PVDF, or cellulose): 0.10
     * Graphene oxide, biochar, or anti-fouling additive: 0.05
     * Optional inert porosity modifier: 0.05
   - NEVER deviate from these percentages for potassium brine separation materials
   - Include all 6 components in every potassium brine composition
   - ALWAYS include both functionalized silica and selective ion-exchange groups (both are critical for K+/Na+/Mg2+ selectivity)
   - ALWAYS include stabilizer and binder (critical for wet cycling durability under brine conditions)

5. Heavy Metal Adsorbent Detection:
   - If user mentions: heavy metals, lead, cadmium, arsenic, chromium, Pb, Cd, As, Cr, wastewater adsorption, modified biochar, iron oxide nanoparticles, metal ion removal, leaching safety
   - THEN set material_category to "adsorbent_heavy_metals"
   - THEN use EXACTLY this 5-component composition (percentages must sum to 1.0):
     * Modified biochar or activated carbon: 0.35
     * Porous silica or silica gel: 0.25
     * Iron oxide nanoparticles or iron hydroxide: 0.20
     * Bentonite clay or alumina stabilizer: 0.10
     * Natural polymer or biopolymer binder: 0.10
   - NEVER deviate from these percentages for heavy metal adsorbents
   - Include all 5 components in every heavy metal composition
   - ALWAYS include both biochar/carbon and iron oxide (both are critical for metal adsorption and separation)
   - ALWAYS include stabilizer and binder (critical for cycling durability and handling under acidic conditions)

6. Membrane Water Treatment Detection (PRIORITY: Check BEFORE Heavy Metal Adsorbent):
   - If user mentions: membrane, anti-fouling, polymer membrane matrix, PVDF, PES, PSf, water flux, permeability, rejection efficiency, filtration cycles, cleaning recovery, pore size, molecular weight cut-off, MWCO, microfiltration, ultrafiltration, nanofiltration, mixed-matrix membrane
   - THEN set material_category to "membrane_water_treatment"
   - THEN use EXACTLY this 6-component composition (percentages must sum to 1.0):
     * Polymer membrane matrix (PVDF, PES, PSf, or cellulose acetate): 0.50
     * Hydrophilic additive (PEG, PVP, or zwitterionic polymer): 0.15
     * Silica nanoparticles or hydrophilic inorganic filler: 0.15
     * Activated carbon, biochar, or MOF additive: 0.10
     * Antimicrobial or stabilizing additive (ZnO, TiO2, Ag, clay, or alumina): 0.05
     * Crosslinker or casting modifier: 0.05
   - NEVER deviate from these percentages for membrane water-treatment materials
   - Include all 6 components in every membrane composition
   - ALWAYS include polymer matrix and hydrophilic additive (both are critical for water flux and contaminant rejection)
   - ALWAYS include stabilizer/antimicrobial (critical for long-term membrane stability)
   - IMPORTANT: Membrane presets should NEVER include heavy-metal-specific fields (Pb2+, Cd2+, As3+, Cr3+, Cr6+) unless the user explicitly asks for heavy-metal removal in the membrane
   - If request mentions both membrane AND heavy metals explicitly, then create a specialized membrane with metal-removal capability, NOT a standard adsorbent

7. General Rules:
   - Composition ratios must sum to 1.0
   - For preset categories, use exact preset key
   - If no preset matches, set category to "other_material"
   - Return ONLY valid JSON, no extra text"""

    # Retry logic for transient errors (500, 429, etc.) with exponential backoff and jitter
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            response = claude_client.messages.create(
                model="claude-opus-4-1",
                max_tokens=1500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.content[0].text.strip()
            
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                content = content[json_start:json_end]
            
            data = json.loads(content)
            return {
                "success": True,
                "data": data,
                "error": None,
                "is_fallback": False
            }
        except RateLimitError as e:
            error_msg = f"Rate limit error on attempt {attempt + 1}/{max_retries}"
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt) + (time.time() % 1)  # Add jitter
                time.sleep(wait_time)
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": "Claude rate limit exceeded. Please try again in a few minutes.",
                    "is_fallback": False,
                    "technical_error": error_msg
                }
        except APIError as e:
            error_str = str(e)
            # Check if it's a transient server error (429, 500, 502, 503, 504)
            if any(code in error_str for code in ['429', '500', '502', '503', '504', 'server_error', 'overloaded']):
                error_msg = f"Server error on attempt {attempt + 1}/{max_retries}: {error_str}"
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt) + (time.time() % 1)  # Add jitter
                    time.sleep(wait_time)
                else:
                    return {
                        "success": False,
                        "data": None,
                        "error": "The AI service is temporarily unavailable. Your design input has been saved. Please try again.",
                        "is_fallback": False,
                        "technical_error": error_msg
                    }
            else:
                # Non-transient API error
                return {
                    "success": False,
                    "data": None,
                    "error": f"API error: {error_str[:100]}",
                    "is_fallback": False,
                    "technical_error": error_str
                }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "data": None,
                "error": "Failed to parse AI response. Please try again.",
                "is_fallback": False,
                "technical_error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": f"Unexpected error: {str(e)[:100]}",
                "is_fallback": False,
                "technical_error": str(e)
            }
    
    return {
        "success": False,
        "data": None,
        "error": "Unknown error after retries",
        "is_fallback": False
    }


def enrich_with_preset(user_prompt, ai_result):
    """
    Merge AI result with category preset using the central registry.
    Ensures consistent preset application across all material categories.
    
    Process:
    1. Classify the material using hierarchical classification
    2. Apply the category preset to ai_result
    3. Add classification warnings if using fallback category
    """
    hier_classification = detect_material_category(user_prompt)
    preset_key = hier_classification.get("specific_preset", "other_material")
    display_name = CATEGORY_REGISTRY.get(preset_key, {}).get("display_name", preset_key)
    
    # Apply category preset from registry
    ai_result = apply_category_preset(ai_result, preset_key)
    
    # Add warning if not in registry (Other category)
    if preset_key == "other_material":
        ai_result["classification_warning"] = "No category-specific preset exists for this material. The report may be incomplete."
    
    return ai_result


def get_generic_disclaimer():
    """Return a generic R&D disclaimer for materials without a category-specific one."""
    return (
        "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults "
        "based on materials science knowledge. These recommendations are CONDITIONAL upon rigorous laboratory validation, "
        "field testing, characterization, and consultation with qualified materials engineers and domain specialists. "
        "This report is for research and development guidance only."
    )


def sanitize_for_pdf(text):
    """
    Convert text to PDF-compatible ASCII format.
    
    Note: PDF generation uses ASCII-only output to ensure compatibility with
    fpdf2's helvetica font. Scientific labels are preserved in ASCII notation
    (K+, SO4^2-, etc.) for readability.
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Replace problematic Unicode characters that PDF doesn't handle well
    replacements = {
        '–': '-',      # en-dash to hyphen
        '—': '-',      # em-dash to hyphen
        '−': '-',      # minus sign to hyphen
        '"': '"',      # fancy left quote
        '"': '"',      # fancy right quote
        ''': "'",      # fancy apostrophe
        ''': "'",      # fancy apostrophe
        '→': '->',     # arrow
        '✓': 'OK',     # checkmark
        '✅': 'OK',    # checkmark emoji
        '❌': 'X',     # X mark emoji
        '⚠': '!',      # warning
        # Comparison operators
        '≥': '>=',     # greater than or equal
        '≤': '<=',     # less than or equal
        '≠': '!=',     # not equal
        '≈': '~',      # approximately equal
        # Superscript/subscript
        '⁺': '+',      # superscript plus
        '⁻': '-',      # superscript minus
        '²': '2',      # superscript 2
        '³': '3',      # superscript 3
        '₂': '2',      # subscript 2
        '₃': '3',      # subscript 3
        '₄': '4',      # subscript 4
        # Special symbols
        '°': ' deg',   # degree symbol
        'µ': 'u',      # micro
        '×': 'x',      # multiplication sign
        '÷': '/',      # division sign
        '§': 'Sec',    # section sign
        '†': '+',      # dagger
        '‡': '++',     # double dagger
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    # As a fallback, encode to ASCII and ignore any remaining non-ASCII characters
    # This ensures we never pass problematic characters to fpdf
    try:
        text = text.encode('ascii', errors='ignore').decode('ascii')
    except Exception:
        pass
    
    return text


def generate_pdf(user_prompt, result, three_stage_result=None):
    """Generate professional PDF report with preset parameters and validation plan."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    # Title
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, txt="Materials Science Recommendation Report", ln=True, align='C')
    
    # Generated date
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(5)

    # User Request
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, txt="User Request:", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, txt=sanitize_for_pdf(user_prompt))
    pdf.ln(4)

    # Material Category
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, txt="Material Category:", ln=True)
    pdf.set_font("Helvetica", size=11)
    category_display = result.get("material_category_display", result.get("material_category", "N/A"))
    pdf.cell(0, 6, txt=sanitize_for_pdf(category_display), ln=True)
    pdf.ln(2)

    # Target Application
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, txt="Target Application:", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, txt=sanitize_for_pdf(result.get("target_application", "N/A")))
    pdf.ln(4)

    # Composition Table
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, txt="Composition:", ln=True)
    pdf.set_font("Helvetica", size=10)
    
    comp = result.get("composition", [])
    if comp:
        pdf.set_fill_color(100, 150, 200)
        pdf.set_text_color(255, 255, 255)
        # Optimized column widths: component 140, ratio 25, percent 25 (total 190 fits page)
        pdf.cell(140, 8, "Component", 1, 0, 'L', 1)
        pdf.cell(25, 8, "Ratio", 1, 0, 'C', 1)
        pdf.cell(25, 8, "Percent", 1, 1, 'C', 1)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", size=8)
        for item in comp:
            # Increased character limit to 100 to prevent truncation of long names
            component = sanitize_for_pdf(item.get("component", "N/A")[:100])
            ratio = float(item.get('ratio', 0))
            percent = ratio * 100
            pdf.cell(140, 8, component, 1)
            pdf.cell(25, 8, f"{ratio:.3f}", 1, 0, 'C')
            pdf.cell(25, 8, f"{percent:.1f}%", 1, 1, 'C')
        pdf.set_font("Helvetica", size=10)
    else:
        pdf.cell(0, 6, txt="No composition data available.", ln=True)
    pdf.ln(4)

    # Recommended Processing / Fabrication Method
    processing_method = result.get("processing_method", [])
    if processing_method and len(processing_method) > 0:
        # Validate processing method is not empty
        has_content = any(str(step).strip() for step in processing_method)
        
        if has_content:
            # ALWAYS add page break before processing method to ensure clean space
            pdf.add_page()
            
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 8, txt="Recommended Processing / Fabrication Method:", ln=True)
            pdf.ln(2)
            
            # Use small font for processing method content
            pdf.set_font("Helvetica", size=8)
            
            # Track current font style for headers vs content
            current_font_bold = False
            
            for i, step in enumerate(processing_method):
                step_text = str(step).strip()
                
                # Skip empty lines but add minimal spacing
                if not step_text:
                    pdf.ln(0.3)
                    continue
                
                # Sanitize the text - critical for FPDF compatibility
                step_str = sanitize_for_pdf(step_text)
                
                # Check if this is a main step header (starts with number 1-8)
                is_header = any(step_str.startswith(f"{j}.") for j in range(1, 9))
                
                # Check if this is a substep (starts with spaces and dash)
                is_substep = step_str.startswith("   -") or step_str.startswith("  -")
                
                # Clean up substep markers
                if is_substep:
                    # Remove leading spaces and dash, keep bullet
                    step_str = step_str.lstrip()
                    if step_str.startswith("-"):
                        step_str = step_str[1:].strip()
                
                try:
                    if is_header:
                        # Main step header - bold, slightly larger
                        if not current_font_bold:
                            pdf.set_font("Helvetica", 'B', 8)
                            current_font_bold = True
                        pdf.multi_cell(0, 3, txt=step_str, ln=True)
                        pdf.ln(0.2)
                    else:
                        # Content line - regular font, indented
                        if current_font_bold:
                            pdf.set_font("Helvetica", '', 8)
                            current_font_bold = False
                        
                        # Add bullet point for substeps
                        if is_substep:
                            step_str = "  " + chr(149) + " " + step_str  # Use bullet character
                        
                        pdf.multi_cell(0, 2.8, txt=step_str, ln=True)
                
                except Exception as e:
                    # If rendering fails, try a simpler approach
                    try:
                        pdf.set_font("Helvetica", '', 8)
                        pdf.multi_cell(0, 2.8, txt=step_str[:500], ln=True)  # Limit line length
                    except:
                        pass  # Skip this step if it fails
            
            pdf.ln(1)

    # Category-Specific Parameters (preset) - Try both field names
    preset_params = result.get("preset_parameters") or result.get("category_specific_parameters", {})
    if preset_params:
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, txt="Category-Specific Parameters & Targets:", ln=True)
        pdf.set_font("Helvetica", size=10)
        
        for key, value in preset_params.items():
            label = format_parameter_label(key)
            value_str = sanitize_for_pdf(str(value)) if not isinstance(value, dict) else sanitize_for_pdf(str(value))
            pdf.cell(70, 6, f"{label}:", 0)
            pdf.cell(0, 6, f" {value_str}", ln=True)
        pdf.ln(4)

    # Validation Plan (preset) - Try both field names
    preset_val = result.get("preset_validation_plan") or result.get("validation_plan", {})
    if preset_val:
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, txt="Validation Plan:", ln=True)
        pdf.set_font("Helvetica", size=10)
        
        for key, value in preset_val.items():
            label = format_parameter_label(key)
            if isinstance(value, list):
                value_str = ", ".join([sanitize_for_pdf(v) for v in value])
            else:
                value_str = sanitize_for_pdf(str(value))
            pdf.cell(70, 6, f"{label}:", 0)
            pdf.cell(0, 6, f" {value_str}", ln=True)
        pdf.ln(4)

    # Safety / Regulatory Tests
    safety_tests = result.get("safety_tests", [])
    if safety_tests:
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, txt="Safety & Regulatory Tests:", ln=True)
        pdf.set_font("Helvetica", size=10)
        
        for i, test in enumerate(safety_tests, 1):
            test_str = sanitize_for_pdf(str(test))
            pdf.cell(10, 6, f"{i}. ", 0)
            pdf.cell(0, 6, f"{test_str}", ln=True)
        pdf.ln(4)

    # Scientific Dataset Verification Summary (Stage 4)
    if three_stage_result and "stage_4_result" in three_stage_result and SCIENTIFIC_VERIFICATION_AVAILABLE:
        stage_4 = three_stage_result.get("stage_4_result", {})
        
        if stage_4.get("status") != "unavailable":
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 8, txt="Scientific Dataset Verification Summary:", ln=True)
            pdf.set_font("Helvetica", size=9)
            
            # Datasets queried
            datasets = stage_4.get("datasets_queried", [])
            if datasets:
                datasets_str = ", ".join(datasets)
                pdf.multi_cell(0, 5, txt=f"Datasets Queried: {sanitize_for_pdf(datasets_str)}")
            else:
                pdf.cell(0, 5, txt="External dataset verification was not completed. Report relies on internal category registry and preset library.", ln=True)
            
            # Components verification
            components_checked = stage_4.get("components_checked", 0)
            components_verified = stage_4.get("components_verified", 0)
            pdf.cell(0, 5, txt=f"Components Verified: {components_verified}/{components_checked}", ln=True)
            
            # Materials found
            materials_found = stage_4.get("materials_found", 0)
            pdf.cell(0, 5, txt=f"Materials/Properties Found: {materials_found}", ln=True)
            
            # Literature hits
            literature_hits = stage_4.get("literature_hits", 0)
            pdf.cell(0, 5, txt=f"Supporting Literature Found: {literature_hits} papers", ln=True)
            
            # Evidence summary
            evidence = stage_4.get("evidence_summary", "")
            if evidence:
                pdf.set_font("Helvetica", size=8)
                pdf.multi_cell(0, 4, txt=f"Evidence: {sanitize_for_pdf(evidence)}")
            
            pdf.ln(2)
        else:
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 8, txt="Scientific Dataset Verification Summary:", ln=True)
            pdf.set_font("Helvetica", size=9)
            pdf.cell(0, 5, txt="External dataset verification was not completed. Report relies on internal category registry and preset library.", ln=True)
            pdf.ln(2)
    else:
        # Show fallback message if no three_stage_result
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, txt="Scientific Dataset Verification Summary:", ln=True)
        pdf.set_font("Helvetica", size=9)
        pdf.cell(0, 5, txt="External dataset verification was not completed. Report relies on internal category registry and preset library.", ln=True)
        pdf.ln(2)

    # Verification Summary (if available from three_stage_result)
    if three_stage_result:
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, txt="Verification Summary:", ln=True)
        pdf.set_font("Helvetica", size=9)
        
        # Category selected
        material_category = result.get("material_category", "N/A")
        category_display = result.get("material_category_display", material_category)
        pdf.cell(0, 5, txt=f"Category Selected: {sanitize_for_pdf(category_display)}", ln=True)
        
        # Stage 1: Category Keyword Verification
        s1 = three_stage_result.get("stage_1_result", {})
        s1_status = s1.get("status", "unknown").upper()
        keyword_match = s1.get("keyword_match_percentage", 0)
        pdf.cell(0, 5, txt=f"Stage 1 - Category Keyword Verification: {s1_status} ({keyword_match:.0f}% match)", ln=True)
        
        # Stage 2: Preset Field Compatibility
        s2 = three_stage_result.get("stage_2_result", {})
        s2_status = s2.get("status", "unknown").upper()
        pdf.cell(0, 5, txt=f"Stage 2 - Preset Field Compatibility: {s2_status}", ln=True)
        
        # Stage 3: Scientific Consistency
        s3 = three_stage_result.get("stage_3_result", {})
        s3_status = s3.get("status", "unknown").upper()
        pdf.cell(0, 5, txt=f"Stage 3 - Scientific Consistency: {s3_status}", ln=True)
        
        # Export status
        overall_status = three_stage_result.get("overall_status", "unknown").upper()
        if overall_status == "PASS":
            export_status = "Passed"
        elif overall_status == "WARNING":
            export_status = "Warning"
        else:
            export_status = "Failed"
        pdf.cell(0, 5, txt=f"Export Status: {export_status}", ln=True)
        
        pdf.ln(2)

    # Disclaimer (category-specific or generic)
    pdf.set_font("Helvetica", 'I', 8)
    disclaimer_text = result.get("category_specific_disclaimer") or result.get("category_disclaimer") or get_generic_disclaimer()
    pdf.multi_cell(0, 4, txt=sanitize_for_pdf(disclaimer_text))

    # Return PDF as bytes (using BytesIO to avoid file locking issues)
    pdf_bytes_io = BytesIO()
    pdf.output(pdf_bytes_io)
    return pdf_bytes_io.getvalue()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# ============================================================================
# STREAMLIT UI
# ============================================================================

st.set_page_config(
    page_title="Materials Science AI (AWH + Presets)",
    page_icon="🧪",
    layout="centered"
)

st.title("🧪 Materials Science Assistant (Claude-Powered)")
st.markdown("""
Describe the material you need. The app will detect specialized categories 
like **atmospheric water harvesting** and include all specific parameters, 
targets, and validation protocols.

*Powered by Claude AI via Anthropic*
""")

# Check API key
if not validate_api_key():
    st.error(
        "❌ **Anthropic API Key Not Found**\n\n"
        "**For Streamlit Cloud:**\n"
        "1. Go to your app settings (gear icon)\n"
        "2. Click 'Secrets'\n"
        "3. Add: `ANTHROPIC_API_KEY=your-api-key-here`\n"
        "4. Redeploy the app\n\n"
        "**For Local Development:**\n"
        "1. Create a `.env` file in the app directory\n"
        "2. Add: `ANTHROPIC_API_KEY=your-api-key-here`\n"
        "3. Restart the app\n\n"
        "Get your API key from https://console.anthropic.com"
    )
    st.stop()

# Initialize auto-category session state
init_auto_category_session()

# Initialize suggested category session state
if "show_suggestions_panel" not in st.session_state:
    st.session_state.show_suggestions_panel = False
if "suggestions_list" not in st.session_state:
    st.session_state.suggestions_list = None
if "suggestion_action" not in st.session_state:
    st.session_state.suggestion_action = None
if "suggested_category_selected" not in st.session_state:
    st.session_state.suggested_category_selected = None
if "category_approved_for_export" not in st.session_state:
    st.session_state.category_approved_for_export = False

# Sidebar with instructions
with st.sidebar:
    st.markdown("### 📋 Instructions")
    st.markdown("""
    1. Describe your material or coating need
    2. Include intended application and requirements
    3. Click 'Analyze'
    4. View AI analysis + category-specific parameters
    5. Generate PDF report with all details
    """)
    
    st.markdown("### 💡 Example Prompts")
    st.markdown("""
    **Atmospheric Water Harvesting:**
    - "Design a low-cost porous composite for atmospheric water harvesting using activated carbon, porous silica, hygroscopic salt, stabilizers, and polymer binder"
    
    **Photocatalytic Coating:**
    - "Photocatalytic TiO2 coating for water purification using UV light"
    
    **General Material:**
    - "High-performance aerospace aluminum alloy"
    """)
    
    # Add auto-category toggle
    enable_auto_category = add_auto_category_sidebar_toggle()

# Input section
st.markdown("### 📝 Material or Coating Request")

user_prompt = st.text_area(
    label="Describe the material or coating you need:",
    placeholder="Example: A porous material for atmospheric water harvesting that can capture moisture and release clean water...",
    height=150,
    key="material_input"
)

# Submit button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🔍 Analyze", use_container_width=True, type="primary")

# Process request
if analyze_button:
    if not user_prompt.strip():
        st.warning("⚠️ Please enter a material description before analyzing.")
    else:
        with st.spinner("🤖 Claude is analyzing your request..."):
            api_result = call_claude(user_prompt)
            
            # Store user prompt always (for retry and fallback)
            st.session_state['user_prompt'] = user_prompt
            
            if api_result.get("success"):
                # API call succeeded
                ai_data = api_result["data"]
                enriched = enrich_with_preset(user_prompt, ai_data)
                st.session_state['result'] = enriched
                st.session_state['show_result'] = True
                st.session_state['api_error'] = None
                st.rerun()
            else:
                # API call failed
                st.session_state['api_error'] = api_result.get("error", "Unknown error")
                st.session_state['technical_error'] = api_result.get("technical_error", "")
                st.session_state['show_result'] = False

# Display API error with retry/fallback options
if st.session_state.get('api_error'):
    st.error(st.session_state['api_error'])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Retry Claude Generation", use_container_width=True):
            # Retry button directly calls the API again
            with st.spinner("🤖 Retrying Claude analysis..."):
                api_result = call_claude(st.session_state['user_prompt'])
                
                if api_result.get("success"):
                    # API call succeeded this time
                    ai_data = api_result["data"]
                    enriched = enrich_with_preset(st.session_state['user_prompt'], ai_data)
                    st.session_state['result'] = enriched
                    st.session_state['show_result'] = True
                    st.session_state['api_error'] = None
                    st.rerun()
                else:
                    # Still failed, update error message
                    st.session_state['api_error'] = api_result.get("error", "Unknown error")
                    st.error("Retry failed. Please try again later or use local preset.")
    
    with col2:
        if st.button("📋 Generate Using Local Preset", use_container_width=True):
            # Generate fallback from local presets
            fallback_result = generate_fallback_result(st.session_state['user_prompt'])
            enriched = enrich_with_preset(st.session_state['user_prompt'], fallback_result)
            st.session_state['result'] = enriched
            st.session_state['show_result'] = True
            st.session_state['api_error'] = None
            st.rerun()

# Display results
if "show_result" in st.session_state and st.session_state.get("show_result"):
    result = st.session_state['result']
    user_prompt = st.session_state['user_prompt']
    
    st.markdown("---")
    
    # Show notice if this was generated from fallback
    if result.get("is_fallback"):
        st.info("📋 **Local Preset Report** - Generated from category defaults. To get AI-enhanced analysis, use 'Retry AI Generation' when service is available.")
    
    st.markdown("### 📊 Analysis Results")
    
    # Get hierarchical classification for reasoning
    hier_classification = detect_material_category(user_prompt)
    
    # ===== AUTO-CATEGORY WORKFLOW (NEW) =====
    enable_auto_category_current = st.session_state.get("enable_auto_category", False)
    if enable_auto_category_current and hier_classification:
        # Run auto-category workflow
        auto_cat_result = handle_auto_category_workflow(
            user_prompt,
            hier_classification,
            CATEGORY_REGISTRY
        )
        
        # Handle workflow result
        if auto_cat_result["should_stop_rendering"]:
            # Stop and wait for user action
            st.stop()
        
        # Apply new category if approved
        if auto_cat_result.get("action") == "approve" and auto_cat_result.get("new_category"):
            new_cat = auto_cat_result["new_category"]
            st.info(f"✅ Applying new category: {new_cat.get('display_name')}")
            
            # Apply to material data
            result = apply_auto_category_to_material(result, new_cat, user_prompt)
            st.session_state['result'] = result
            
            # Update material category for rest of workflow
            material_category = new_cat.get("normalized_category_name", "other_material")
            hier_classification["specific_preset"] = material_category
            
            st.success("New category applied! Regenerating report with new preset...")
            st.rerun()
        
        # Use fallback if rejected
        elif auto_cat_result.get("action") == "reject":
            material_category = "other_material"
            result["material_category"] = material_category
            st.session_state['result'] = result
    # ===== END AUTO-CATEGORY WORKFLOW =====
    
    # ===== SUGGESTED CATEGORY WORKFLOW (NEW) =====
    # Check if suggestions panel should be shown
    material_category = result.get("material_category", "other_material")
    confidence_score = hier_classification.get("confidence_score", 0) if hier_classification else 0
    
    # First check if suggestions are needed
    if should_show_suggestions(confidence_score, material_category, user_prompt):
        # Check for conflict between selected category and request
        conflict = detect_category_conflict(user_prompt, material_category)
        
        if conflict.get("conflict_detected") or confidence_score < 85:
            # Generate suggestions
            if st.session_state.suggestions_list is None:
                with st.spinner("🔍 Analyzing material request for better category matches..."):
                    st.session_state.suggestions_list = propose_candidate_categories(user_prompt, CATEGORY_REGISTRY)
            
            # Show suggestion panel
            if st.session_state.suggestions_list:
                st.markdown("---")
                st.markdown("### 🚨 Category Mismatch Detected")
                if conflict.get("conflict_detected"):
                    st.warning(f"⚠️ {conflict.get('conflict_reason', 'Category conflict detected')}")
                else:
                    st.warning(f"⚠️ Low confidence classification ({confidence_score:.0f}%). Showing suggestions...")
                
                # Show comparison
                show_category_comparison(material_category, st.session_state.suggestions_list, user_prompt)
                
                # Show suggestion panel and get user action
                suggestion_result = show_suggested_categories_panel(
                    st.session_state.suggestions_list,
                    user_prompt,
                    result
                )
                
                # Handle suggestion panel result
                if suggestion_result.get("action") == "use_suggested":
                    selected_cat = suggestion_result["selected_category"]
                    final_cat = suggestion_result["final_category"]
                    
                    # Apply to result
                    result["material_category"] = final_cat
                    result["material_category_display"] = selected_cat.get("display_name", final_cat)
                    
                    # If should add to registry
                    if suggestion_result.get("should_add_to_registry") and not selected_cat.get("exists_in_registry"):
                        st.info(f"📝 Adding '{selected_cat.get('display_name')}' to registry...")
                        # Generate full preset
                        full_preset = generate_suggested_category_preset(selected_cat, user_prompt)
                        result["new_category_preset"] = full_preset
                    
                    # Update session and mark as approved for export
                    st.session_state['result'] = result
                    st.session_state.category_approved_for_export = True
                    material_category = final_cat
                    
                    st.success(f"✅ Category updated to: {selected_cat.get('display_name')}")
                    st.rerun()
                
                elif suggestion_result.get("action") == "cancel":
                    st.warning("Category suggestion cancelled. Proceeding with current category.")
                    st.session_state.category_approved_for_export = False
                    st.stop()
                
                elif suggestion_result.get("action") == "waiting":
                    st.stop()  # Wait for user action
    # ===== END SUGGESTED CATEGORY WORKFLOW =====
    
    # Material Category
    category_display = result.get("material_category_display", result.get("material_category", "N/A"))
    st.markdown(f"**Material Category:** `{category_display}`")
    
    # Target Application
    st.markdown("**Target Application:**")
    st.info(result.get("target_application", "N/A"))
    
    # Composition
    if result.get("composition"):
        st.markdown("**Composition:**")
        comp_table = []
        for item in result["composition"]:
            comp_table.append({
                "Component": item.get("component", "N/A"),
                "Ratio": f"{item.get('ratio', 0):.3f}",
                "Percentage": f"{item.get('ratio', 0)*100:.1f}%"
            })
        st.table(comp_table)
    
    # Display hierarchical classification and reasoning
    st.markdown("---")
    st.markdown("### 🔍 Why This Category Was Selected")
    
    if hier_classification:
        # Display confidence and reasoning
        confidence = hier_classification.get("confidence_score", 0)
        confidence_emoji = "✅" if confidence >= 80 else "⚠️" if confidence >= 60 else "❌"
        st.markdown(f"**Confidence Score:** {confidence_emoji} {confidence}%")
        
        # Hierarchical breakdown
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            material_family = hier_classification.get("material_family", "Unknown")
            family_name = MATERIAL_FAMILIES.get(material_family, {}).get("name", material_family)
            st.metric("Material Family", family_name)
        with col2:
            functional_class = hier_classification.get("functional_class", "Unknown")
            class_name = FUNCTIONAL_CLASSES.get(functional_class, {}).get("name", functional_class)
            st.metric("Functional Class", class_name)
        with col3:
            app_domain = hier_classification.get("application_domain", "Unknown")
            domain_name = APPLICATION_DOMAINS.get(app_domain, {}).get("name", app_domain)
            st.metric("Application Domain", domain_name)
        with col4:
            st.metric("Preset", hier_classification.get("specific_preset", "N/A"))
        
        # Matched keywords
        matched = hier_classification.get("matched_keywords", [])
        if matched:
            st.markdown(f"**Matched Keywords:** {', '.join(matched[:8])}")
        
        # Run conflict detection and show interactive resolution panel
        material_category = result.get("material_category", "other_material")
        conflict_check = detect_category_conflicts(user_prompt, material_category)
        
        # Display improved classification summary with readable layout
        st.markdown("### 🔍 Why This Category Was Selected")
        
        # Get hierarchical classification info
        material_family = hier_classification.get("material_family", "Unknown")
        functional_class = hier_classification.get("functional_class", "Unknown")
        application_domain = hier_classification.get("application_domain", "Unknown")
        preset = hier_classification.get("specific_preset", "Unknown")  # Changed from "preset" to "specific_preset"
        confidence_score = hier_classification.get("confidence_score", 0)
        matched_keywords = hier_classification.get("matched_keywords", [])
        
        # Convert preset key to human-readable format
        preset_display_names = {
            "membrane_water_treatment": "Membrane Water Treatment",
            "atmospheric_water_harvesting_material": "Atmospheric Water Harvesting Material",
            "photocatalytic_coating": "Photocatalytic Coating",
            "phosphate_recovery_material": "Phosphate Recovery Material",
            "potassium_brine_separation_material": "Potassium Brine Separation Material",
            "adsorbent_heavy_metals": "Adsorbent for Heavy Metals",
            "co2_capture_material": "Carbon Dioxide Capture Material",
            "thermal_insulation_composite": "Thermal Insulation Composite",
            "self_cleaning_building_coating": "Self-Cleaning Photocatalytic Building Coating",
            "other_material": "Other Material"
        }
        display_preset_name = preset_display_names.get(preset, preset)
        
        # Display as readable vertical layout with tooltips
        st.markdown(f"""
#### Classification Details:

**Material Family:** `{material_family}`  
<small>*The chemical/material family (e.g., ceramic, polymer, carbon)*</small>

**Functional Class:** `{functional_class}`  
<small>*What the material does (e.g., coating, adsorbent, membrane)*</small>

**Application Domain:** `{application_domain}`  
<small>*Where it will be used (e.g., water treatment, energy, construction)*</small>

**Selected Preset:** `{display_preset_name}`  
<small>*Category-specific template with validation requirements*</small>

**Confidence Score:** {confidence_score}%  
<small>*Classification accuracy based on keyword matching*</small>

**Matched Keywords:**  
{', '.join(matched_keywords) if matched_keywords else '(none)'}  
<small>*Key terms from your request that triggered this category*</small>
        """)
        
        # Add manual category testing option (for testing conflict panel)
        with st.expander("🔧 Debug: Test Category Override (for testing conflict detection)"):
            st.markdown("**Temporarily override category to test conflict detection:**")
            available_cats = [(k, v.get("display_name", k)) for k, v in CATEGORY_REGISTRY.items() if k != "other_material"]
            available_cats.sort(key=lambda x: x[1])
            
            test_cat_idx = st.selectbox(
                "Override to category:", 
                range(len(available_cats)),
                format_func=lambda i: available_cats[i][1],
                key="test_override"
            )
            
            if st.button("Test This Category", key="btn_test_override"):
                test_cat_key, test_cat_display = available_cats[test_cat_idx]
                temp_result = dict(result)
                temp_result["material_category"] = test_cat_key
                
                # Check for conflicts
                test_conflict = detect_category_conflicts(user_prompt, test_cat_key)
                if test_conflict["conflict_detected"]:
                    st.error(f"✅ Conflict detected! {test_conflict['conflict_reason']}")
                    st.info(f"Recommended: {CATEGORY_REGISTRY.get(test_conflict['recommended_category'], {}).get('display_name', '')}")
                else:
                    st.success("No conflict with this category")
        
        # Now show the actual conflict panel if there's a real conflict
        if conflict_check["conflict_detected"]:
            st.markdown("---")
            st.error(f"🚨 **CONFLICT DETECTED**")
            st.markdown(f"**Issue:** {conflict_check['conflict_reason']}")
            
            # Show why this conflict was detected
            if conflict_check["conflict_reason"]:
                st.info(f"💡 {conflict_check['conflict_reason']}")
            
            # Initialize session state for conflict resolution
            if "conflict_resolution" not in st.session_state:
                st.session_state.conflict_resolution = None
            
            st.markdown("### 🔄 How would you like to proceed?")
            
            # Create columns for decision buttons
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            
            with col1:
                if st.button("✅ Use Suggested Category", use_container_width=True, key="use_suggested"):
                    # Switch to suggested category
                    suggested_cat = conflict_check["recommended_category"]
                    suggested_display = CATEGORY_REGISTRY.get(suggested_cat, {}).get("display_name", suggested_cat)
                    
                    # Apply new category
                    result = apply_new_category(suggested_cat, result, user_prompt)
                    st.session_state['result'] = result
                    st.session_state.conflict_resolution = "suggested"
                    
                    # Re-run verification
                    new_conflict = regenerate_conflict_check(user_prompt, suggested_cat)
                    if not new_conflict["conflict_detected"]:
                        st.success(f"✅ Switched to {suggested_display}. Re-analyzing...")
                        st.rerun()
                    else:
                        st.error("This category also has conflicts. Try another option.")
            
            with col2:
                if st.button("⚠️ Keep Current Category", use_container_width=True, key="keep_current"):
                    # Show confirmation warning
                    st.warning("You are proceeding with a category that has potential conflicts. The report may contain inconsistent fields.")
                    
                    if st.checkbox("I understand and want to proceed anyway", key="confirm_override"):
                        st.session_state.conflict_resolution = "override"
                        result["category_override_note"] = "User manually overrode category suggestion due to detected conflict."
                        st.session_state['result'] = result
                        st.rerun()
            
            with col3:
                if st.button("📋 Choose Another Category", use_container_width=True, key="choose_another"):
                    st.session_state.show_category_chooser = True
                    st.rerun()
            
            with col4:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_analysis"):
                    st.session_state['show_result'] = False
                    st.session_state['result'] = None
                    st.session_state.conflict_resolution = "cancelled"
                    st.info("Analysis cancelled. You can start a new analysis.")
                    st.rerun()
            
            # Show category chooser if user selected "Choose Another"
            if st.session_state.get("show_category_chooser"):
                st.markdown("---")
                st.markdown("### 📚 Select a Different Category")
                
                available_categories = [
                    (key, cat_data.get("display_name", key))
                    for key, cat_data in CATEGORY_REGISTRY.items()
                    if key != "other_material"
                ]
                available_categories.sort(key=lambda x: x[1])
                
                selected_idx = st.selectbox(
                    "Available Material Categories:",
                    range(len(available_categories)),
                    format_func=lambda i: available_categories[i][1],
                    key="category_selector"
                )
                
                chosen_key, chosen_display = available_categories[selected_idx]
                
                if st.button(f"Apply {chosen_display}", use_container_width=True, key="apply_chosen"):
                    result = apply_new_category(chosen_key, result, user_prompt)
                    st.session_state['result'] = result
                    
                    # Re-run verification
                    new_conflict = regenerate_conflict_check(user_prompt, chosen_key)
                    if not new_conflict["conflict_detected"]:
                        st.success(f"✅ Changed to {chosen_display}. Regenerating report...")
                        st.session_state.show_category_chooser = False
                        st.rerun()
                    else:
                        st.warning(f"⚠️ {chosen_display} also has potential conflicts: {new_conflict.get('conflict_reason', 'Unknown')}")
            
            st.stop()  # Stop rendering until user makes a decision
        
        # Show alternatives if confidence is low or close call
        if hier_classification.get("requires_user_confirmation"):
            st.warning("⚠️ **Classification Uncertainty**")
            if hier_classification.get("close_call"):
                st.info("Multiple categories have similar scores. Please verify the selection is appropriate.")
            
            # Show alternatives
            alternatives = hier_classification.get("top_3_categories", [])
            if len(alternatives) > 1:
                st.markdown("**Alternative Categories:**")
                for i, alt in enumerate(alternatives[1:3], 1):
                    st.markdown(f"{i}. {alt['display_name']} (Score: {alt['score']})")
    
    # Category-Specific Parameters (Preset)
    preset_params = result.get("preset_parameters", {})
    if preset_params:
        st.markdown("---")
        st.markdown("### 📋 Category-Specific Parameters & Targets")
        for key, value in preset_params.items():
            label = format_parameter_label(key)
            st.markdown(f"**{label}:** {value}")
    
    # Validation Plan (Preset)
    preset_val = result.get("preset_validation_plan", {})
    if preset_val:
        st.markdown("---")
        st.markdown("### ✅ Validation Plan")
        for key, value in preset_val.items():
            label = format_parameter_label(key)
            if isinstance(value, list):
                value_str = ", ".join(value)
            else:
                value_str = str(value)
            st.markdown(f"**{label}:** {value_str}")
    
    # PDF Generation
    st.markdown("---")
    st.markdown("### 📄 Generate Report")
    
    # Run verification before export
    material_category = result.get("material_category", "other_material")
    
    # Extract stored confidence from hier_classification (if available)
    stored_confidence = hier_classification.get("confidence_score", None) if hier_classification else None
    
    # Run the three-stage verification system with stored confidence to avoid re-checking if initially confident
    three_stage_result = run_three_stage_verification(user_prompt, material_category, result, stored_confidence=stored_confidence)
    
    # Display overall verification result
    st.markdown("### 🔐 Pre-Export Verification")
    
    if three_stage_result["overall_status"] == "fail":
        st.error("❌ **Verification Failed - Export Blocked**")
        st.markdown(three_stage_result["verification_message"])
        
        # Show which stages failed
        with st.expander("View Detailed Verification Results"):
            st.markdown("#### Stage 1: Category Keyword Verification")
            s1 = three_stage_result["stage_1_result"]
            st.markdown(f"**Status:** {s1['status'].upper()}")
            st.markdown(f"**Keyword Match:** {s1['keyword_match_percentage']:.0f}%")
            st.markdown(f"**Reason:** {s1['reason']}")
            if s1['matched_keywords']:
                st.markdown(f"✅ Matched: {', '.join(s1['matched_keywords'][:5])}")
            
            st.markdown("#### Stage 2: Preset-Field Compatibility")
            s2 = three_stage_result["stage_2_result"]
            st.markdown(f"**Status:** {s2['status'].upper()}")
            st.markdown(f"**Reason:** {s2['reason']}")
            if s2['missing_expected_fields']:
                st.markdown(f"❌ Missing Fields: {', '.join(s2['missing_expected_fields'][:5])}")
            
            st.markdown("#### Stage 3: Disclaimer Compatibility")
            s3 = three_stage_result["stage_3_result"]
            st.markdown(f"**Status:** {s3['status'].upper()}")
            st.markdown(f"**Reason:** {s3['reason']}")
            
            # Stage 4: Scientific Dataset Verification
            if "stage_4_result" in three_stage_result:
                s4 = three_stage_result["stage_4_result"]
                st.markdown("#### Stage 4: Scientific Dataset Verification")
                st.markdown(f"**Status:** {s4['status'].upper()}")
                st.markdown(f"**Reason:** {s4['reason']}")
                
                if s4['status'] != "unavailable":
                    st.markdown(f"**Datasets Queried:** {', '.join(s4['datasets_queried'])}")
                    st.markdown(f"**Components Verified:** {s4['components_verified']}/{s4['components_checked']}")
                    st.markdown(f"**Materials/Properties Found:** {s4['materials_found']}")
                    st.markdown(f"**Literature References:** {s4['literature_hits']} papers found")
                    
                    if s4['evidence_summary']:
                        st.markdown("**Evidence Summary:**")
                        st.info(s4['evidence_summary'])
        
        # ========== CORRECTION PANEL ==========
        st.markdown("---")
        st.markdown("### 🔧 Correction Options")
        
        s1_status = three_stage_result["stage_1_result"]["status"]
        s2_status = three_stage_result["stage_2_result"]["status"]
        
        # Logic: If Stage 1 passes but Stage 2 fails for the SAME category, offer to apply missing fields
        if s1_status == "pass" and s2_status != "pass":
            st.markdown("**Category appears correct, but the preset is incomplete. Fix it:**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Apply Missing Thermal Preset Fields", use_container_width=True, key="apply_missing_fields"):
                    # Apply missing fields from the preset
                    st.session_state['result'] = apply_missing_preset_fields_local(result, material_category)
                    st.session_state['correction_applied'] = "missing_fields"
                    st.success("✅ Applied missing preset fields. Re-running verification...")
                    st.rerun()
            
            with col2:
                if st.button("🔄 Cancel & Go Back", use_container_width=True, key="cancel_correction"):
                    st.session_state['correction_applied'] = None
                    st.info("Correction cancelled. Please review your selection.")
        
        # Always offer category change
        st.markdown("**Or choose a different category:**")
        
        category_options = [
            ("Atmospheric Water Harvesting Material", "atmospheric_water_harvesting_material"),
            ("Photocatalytic Coating", "photocatalytic_coating"),
            ("Membrane Water Treatment Material", "membrane_water_treatment"),
            ("Heavy Metal Adsorbent", "adsorbent_heavy_metals"),
            ("Phosphate Recovery Material", "phosphate_recovery_material"),
            ("Potassium Brine Separation Material", "potassium_brine_separation_material"),
            ("Carbon Dioxide Capture Material", "co2_capture_material"),
            ("Thermal Insulation Composite", "thermal_insulation_composite"),
            ("Self-Cleaning Building Coating", "self_cleaning_building_coating"),
            ("Other Custom Material", "other_material"),
        ]
        
        selected_display = next((d for d, k in category_options if k == material_category), material_category)
        selected_category_dropdown = st.selectbox(
            "Choose a category:",
            options=[d for d, _ in category_options],
            index=next((i for i, (d, _) in enumerate(category_options) if d == selected_display), 0),
            key="category_dropdown"
        )
        
        selected_category_key = next((k for d, k in category_options if d == selected_category_dropdown), "other_material")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Use Selected Category", use_container_width=True, key="use_selected_category"):
                if selected_category_key != material_category:
                    # Clear old preset fields and apply new category
                    st.session_state['result'] = clear_previous_preset_fields(result)
                    st.session_state['result'] = apply_category_preset(st.session_state['result'], selected_category_key)
                    st.session_state['correction_applied'] = "category_changed"
                    st.success(f"✅ Changed to {selected_category_dropdown}. Re-running verification...")
                    st.rerun()
                else:
                    st.info("Category is already selected.")
        
        with col2:
            if st.button("🔄 Cancel & Go Back", use_container_width=True, key="cancel_category"):
                st.session_state['correction_applied'] = None
                st.info("Category change cancelled. Please review your selection.")
        
        # Option to override with warning
        st.markdown("---")
        st.markdown("**Advanced: Keep current category with warning (not recommended)**")
        
        if st.checkbox("⚠️ I understand the risks and want to keep the current category anyway", key="override_checkbox"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⚠️ Keep Current Category & Export", use_container_width=True, key="keep_current_override"):
                    st.session_state['result']['verification_override_warning'] = "User manually overrode verification failure."
                    st.warning("⚠️ This report may not match the selected category. Export with caution.")
                    st.session_state['allow_export_override'] = True
                    st.rerun()
    
    elif three_stage_result["overall_status"] == "warning":
        st.warning("⚠️ **Verification Warning - Review Before Export**")
        st.markdown(three_stage_result["verification_message"])
        
        with st.expander("View Verification Details"):
            s1 = three_stage_result["stage_1_result"]
            s2 = three_stage_result["stage_2_result"]
            s3 = three_stage_result["stage_3_result"]
            
            if s1["status"] == "warning":
                st.markdown("**⚠️ Stage 1:** Some category keywords don't match the request. Verify classification is correct.")
            if s2["status"] == "warning":
                st.markdown("**⚠️ Stage 2:** Some expected preset fields are missing. Report may be incomplete.")
            if s3["status"] == "warning":
                st.markdown("**⚠️ Stage 3:** Disclaimer may not fully cover all category requirements.")
        
        # For warnings, offer to apply missing fields if Stage 2 is the issue
        if three_stage_result["stage_2_result"]["status"] == "warning":
            st.markdown("---")
            st.markdown("### 🔧 Optional Fixes")
            if st.button("✅ Apply Missing Preset Fields to Complete Report", use_container_width=True, key="apply_missing_warning"):
                st.session_state['result'] = apply_missing_preset_fields_local(result, material_category)
                st.session_state['correction_applied'] = "missing_fields_warning"
                st.success("✅ Applied missing preset fields. Re-running verification...")
                st.rerun()
        
        st.markdown("**You can proceed with export, but review the analysis above first.**")
    
    else:  # status == "pass"
        st.success("✅ **Verification Passed** - Report is ready for export")
        st.markdown("All three verification stages completed successfully.")
    
    # Validate processing method before export (if it exists)
    processing_method = result.get("processing_method", [])
    has_processing_method = len(processing_method) > 0
    processing_method_incomplete = False
    
    if has_processing_method:
        # Check if processing method has actual content (not just headers)
        content_lines = [str(step).strip() for step in processing_method if str(step).strip()]
        # Should have headers (8 steps) plus at least 2-3 bullet points per step = ~24+ lines minimum
        if len(content_lines) < 8:
            processing_method_incomplete = True
        else:
            # Check that headers aren't the only content
            header_count = sum(1 for line in content_lines if any(line.startswith(f"{j}.") for j in range(1, 9)))
            if header_count == len(content_lines):  # Only headers, no content
                processing_method_incomplete = True
    
    # Export button logic
    can_export = three_stage_result["overall_status"] != "fail" and not processing_method_incomplete
    export_disabled_reason = ""
    
    # Check composition validation
    composition_validation = result.get("composition_validation", {})
    composition_invalid = not composition_validation.get("is_valid", True)
    composition_invalid_items = composition_validation.get("invalid_items", [])
    
    if three_stage_result["overall_status"] == "fail":
        export_disabled_reason = "Verification failed"
    elif processing_method_incomplete:
        export_disabled_reason = "Processing method incomplete"
    elif composition_invalid:
        export_disabled_reason = "Invalid substrate/environment objects in composition"
        can_export = False
    elif confidence_score < 85 and not st.session_state.get("category_approved_for_export", False):
        # Block export if low confidence and not approved
        can_export = False
        export_disabled_reason = "Category not approved for export (low confidence)"
    
    if st.button("📥 Generate PDF Report", use_container_width=True, type="secondary", disabled=not can_export):
        if three_stage_result["overall_status"] == "fail":
            st.error("Cannot export: Verification failed. Please use the correction options above.")
        elif processing_method_incomplete:
            st.error("❌ Processing method incomplete. Please apply processing preset before export.")
        elif composition_invalid:
            st.error(f"❌ Invalid substrate/environment objects found in composition: {', '.join(composition_invalid_items)}. "
                    f"These items have been removed. Please review the Composition table below.")
        elif confidence_score < 85 and not st.session_state.get("category_approved_for_export", False):
            st.error("⚠️ Category has low confidence. Please approve via the suggestion panel before exporting.")
        else:
            with st.spinner("Creating PDF..."):
                try:
                    pdf_bytes = generate_pdf(user_prompt, result, three_stage_result)
                    st.success("✅ PDF Report Generated Successfully!")
                    if result.get('verification_override_warning'):
                        st.warning(result['verification_override_warning'])
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"material_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
    
    # Disclaimer
    st.markdown("""
    ---
    💡 **Note:** This analysis is AI-generated based on materials science knowledge.
    All recommendations must be validated through experimental testing before production use.
    """)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Analyze Another Material", use_container_width=True):
            st.session_state['show_result'] = False
            st.session_state['api_error'] = None
            reset_auto_category_state()  # Reset auto-category state
            st.rerun()
    with col2:
        if st.button("📋 Clear All", use_container_width=True):
            reset_auto_category_state()  # Reset auto-category state
            # Reset suggested category state
            st.session_state.show_suggestions_panel = False
            st.session_state.suggestions_list = None
            st.session_state.suggestion_action = None
            st.session_state.suggested_category_selected = None
            st.session_state.category_approved_for_export = False
            st.session_state.clear()
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 12px;">
        <p>Materials Science AI with Intelligent Category Presets | Powered by Claude (Anthropic) | 2026</p>
    </div>
    """,
    unsafe_allow_html=True
)


if __name__ == "__main__":
    pass
