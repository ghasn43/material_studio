# -*- coding: utf-8 -*-
"""
CENTRAL CATEGORY REGISTRY
==========================
Single source of truth for all material categories.
Provides consistent classification, preset data, and validation.

This registry ensures:
- Consistent category naming and prioritization
- No conflicting classifications
- Proper preset loading and merging
- Scientific label protection
- Unified disclaimer application
"""

# Import scientific dataset verification module
try:
    from scientific_data_connectors import verify_with_free_datasets, format_verification_for_pdf
    SCIENTIFIC_VERIFICATION_AVAILABLE = True
except ImportError:
    SCIENTIFIC_VERIFICATION_AVAILABLE = False

# ============================================================================
# DOMAIN DETECTION SYSTEM (Domain-First Classification)
# ============================================================================
# This system detects the actual domain of the user request BEFORE category classification.
# It prevents misclassification by filtering out generic keywords that could match multiple domains.

DOMAIN_KEYWORDS = {
    "battery_electrode": {
        "keywords": [
            "sodium-ion battery", "na-ion", "battery anode", "anode composite", "hard carbon",
            "conductive carbon black", "sodium-compatible binder", "sodium storage",
            "specific capacity", "coulombic efficiency", "rate capability", "cycling stability",
            "cycling durability", "electrode swelling", "impedance", "electrochemical impedance",
            "sei", "half-cell", "full-cell", "current collector", "electrode",
            "sodium battery", "na+ storage", "anode material", "galvanostatic",
            "na metal", "sodium metal", "battery electrode", "half cell", "li-ion",
            "lithium-ion", "battery performance", "battery testing"
        ],
        "min_keywords": 2
    },
    "phosphate_recovery": {
        "keywords": [
            "phosphate recovery", "orthophosphate", "phosphate uptake", "fertilizer reuse",
            "nutrient recovery", "nutrient release", "adsorption/desorption", "agricultural wastewater",
            "pH dependence", "competing ions", "phosphorus recovery", "phosphate removal",
            "nutrient removal", "wastewater phosphate", "phosphate binding", "phosphate release",
            "phosphate adsorbent", "nutrient cycling", "agricultural runoff"
        ],
        "min_keywords": 2
    },
    "carbon_capture": {
        "keywords": [
            "CO2 capture", "carbon dioxide capture", "flue gas", "CO2/N2 selectivity",
            "amine-functionalized", "regeneration energy", "amine loss", "carbon capture",
            "carbon dioxide", "direct air capture", "dac", "CO2 separation", "CO2 adsorption",
            "greenhouse gas", "emissions reduction", "carbon sequestration"
        ],
        "min_keywords": 1
    },
    "oil_gas_produced_water": {
        "keywords": [
            "produced water", "oil and gas", "oilfield", "oil and grease", "oil/grease",
            "hydrocarbons", "hydrocarbon", "TOC", "COD", "sulfide", "reinjection",
            "reuse", "ADNOC", "UAE oil", "gulf conditions", "hot gulf", "backwash",
            "downstream membrane fouling", "produced-water", "oil production", "gas field",
            "reservoir", "petroleum", "crude oil", "wellhead", "offshore"
        ],
        "min_keywords": 2
    },
    "desalination_pretreatment": {
        "keywords": [
            "desalination pre-treatment", "desalination pretreatment", "pre-treatment media",
            "seawater treatment", "desal pre-treatment", "pretreatment media", "desalination",
            "salt removal", "brine", "brackish water", "reverse osmosis", "RO pretreatment"
        ],
        "min_keywords": 1
    },
    "fabric_cleaning": {
        "keywords": [
            "fabric", "cotton", "clothing", "laundry", "garment", "textile", "cloth",
            "oil stain", "grease stain", "washing", "pre-treat", "pre-wash",
            "stain removal from fabric", "fabric stain", "fabric-safe", "colorfastness"
        ],
        "min_keywords": 2
    },
    "roof_waterproofing": {
        "keywords": [
            "roof", "rooftop", "roof-applied", "concrete roof", "waterproofing",
            "rainwater leakage", "water leakage", "roof coating", "building roof",
            "roof membrane", "roof protection", "roof sealant"
        ],
        "min_keywords": 2
    },
    "atmospheric_water_harvesting": {
        "keywords": [
            "atmospheric water", "water harvesting", "fog harvesting", "air humidity",
            "moisture capture", "desiccant", "hygroscopic", "water from air"
        ],
        "min_keywords": 2
    },
    "photocatalytic_water_treatment": {
        "keywords": [
            "photocatalytic", "photocatalysis", "TiO2", "water treatment",
            "dye degradation", "pollutant degradation", "UV-activated", "light-driven"
        ],
        "min_keywords": 2
    },
    "self_cleaning_building": {
        "keywords": [
            "self-cleaning", "self cleaning", "exterior coating", "building coating",
            "facade coating", "photocatalytic nanoparticles", "facade", "exterior",
            "self-cleaning surface", "dirt repellent", "dust repellent"
        ],
        "min_keywords": 2
    },
    "heavy_metal_adsorption": {
        "keywords": [
            "heavy metal", "lead removal", "cadmium removal", "arsenic removal",
            "chromium removal", "toxic metal", "metal ion", "Pb", "Cd", "As", "Cr",
            "metal contamination", "metal adsorbent", "metal binding"
        ],
        "min_keywords": 2
    },
    "potassium_brine": {
        "keywords": [
            "potassium", "potassium brine", "K+ recovery", "brine separation",
            "KCl recovery", "potassium chloride", "salt recovery"
        ],
        "min_keywords": 2
    },
    "membrane_treatment": {
        "keywords": [
            "membrane", "anti-fouling", "polymer membrane", "pvdf", "pes", "filtration",
            "microfiltration", "ultrafiltration", "nanofiltration", "mixed-matrix",
            "water flux", "permeability", "rejection efficiency", "fouling resistance"
        ],
        "min_keywords": 2
    },
    "thermal_insulation": {
        "keywords": [
            "thermal", "insulation", "thermal insulation", "thermal resistance",
            "heat resistance", "temperature stability", "thermal conductivity",
            "insulating", "insulator", "thermal barrier"
        ],
        "min_keywords": 2
    }
}

# Map categories to domains
CATEGORY_TO_DOMAIN = {
    "sodium_ion_battery_anode_composite": "battery_electrode",
    "phosphate_recovery_material": "phosphate_recovery",
    "co2_capture_material": "carbon_capture",
    "oil_gas_produced_water_pretreatment_media": "oil_gas_produced_water",
    "desalination_pretreatment_media": "desalination_pretreatment",
    "fabric_oil_stain_removal_composite": "fabric_cleaning",
    "roof_waterproofing_thermal_insulation_coating": "roof_waterproofing",
    "atmospheric_water_harvesting_material": "atmospheric_water_harvesting",
    "photocatalytic_coating": "photocatalytic_water_treatment",
    "self_cleaning_building_coating": "self_cleaning_building",
    "adsorbent_heavy_metals": "heavy_metal_adsorption",
    "potassium_brine_separation_material": "potassium_brine",
    "membrane_water_treatment": "membrane_treatment",
    "thermal_insulation_composite": "thermal_insulation",
    "other_material": "unknown"
}

# ============================================================================
# DOMAIN-FIRST ARCHITECTURE: Domain Definitions and Category Restrictions
# ============================================================================
# This enforces domain-specific category restrictions to prevent cross-domain contamination

DOMAIN_DEFINITIONS = {
    "water_wastewater": {
        "display_name": "Water & Wastewater Materials",
        "description": "Materials for water treatment, wastewater purification, and water reuse",
        "allowed_categories": [
            "membrane_water_treatment",
            "photocatalytic_coating",
            "adsorbent_heavy_metals",
            "desalination_pretreatment_media",
        ],
        "forbidden_keywords": ["battery", "electrode", "anode", "cathode", "phosphate recovery", "oil and gas", "roof", "fabric", "stain"],
    },
    
    "oil_gas_water": {
        "display_name": "Oil & Gas Produced-Water Materials",
        "description": "Materials for oil and gas wastewater treatment, produced water purification",
        "allowed_categories": [
            "oil_gas_produced_water_pretreatment_media",
        ],
        "forbidden_keywords": ["battery", "phosphate", "roof", "fabric", "stain", "capture", "desalination"],
    },
    
    "carbon_capture_materials": {
        "display_name": "Carbon Capture Materials",
        "description": "Materials for CO₂ capture and carbon sequestration",
        "allowed_categories": [
            "co2_capture_material",
        ],
        "forbidden_keywords": ["battery", "phosphate", "produced water", "roof", "fabric", "textile", "thermal insulation", "electrode"],
    },
    
    "battery_electrochemical": {
        "display_name": "Battery & Electrochemical Materials",
        "description": "Materials for battery electrodes, supercapacitors, and electrochemical energy storage",
        "allowed_categories": [
            "sodium_ion_battery_anode_composite",
        ],
        "forbidden_keywords": ["water treatment", "phosphate", "roof", "fabric", "stain", "thermal insulation", "membrane"],
    },
    
    "agriculture_nutrient": {
        "display_name": "Agriculture & Nutrient Recovery Materials",
        "description": "Materials for phosphate recovery, nutrient cycling, and agricultural applications",
        "allowed_categories": [
            "phosphate_recovery_material",
        ],
        "forbidden_keywords": ["battery", "electrode", "oil and gas", "produced water", "roof", "fabric", "water treatment", "membrane"],
    },
    
    "coatings_construction": {
        "display_name": "Coatings & Construction Materials",
        "description": "Materials for roof coatings, building protection, weatherproofing",
        "allowed_categories": [
            "roof_waterproofing_thermal_insulation_coating",
            "thermal_insulation_composite",
            "self_cleaning_building_coating",
        ],
        "forbidden_keywords": ["battery", "phosphate", "produced water", "water treatment", "fabric", "stain"],
    },
    
    "atmospheric_water": {
        "display_name": "Atmospheric Water Harvesting Materials",
        "description": "Materials for moisture capture and atmospheric water harvesting",
        "allowed_categories": [
            "atmospheric_water_harvesting_material",
        ],
        "forbidden_keywords": ["battery", "phosphate", "produced water", "roof", "fabric", "electrode"],
    },
    
    "textile_cleaning": {
        "display_name": "Textile & Consumer Cleaning Materials",
        "description": "Materials for fabric stain removal, textile cleaning, laundry applications",
        "allowed_categories": [
            "fabric_oil_stain_removal_composite",
        ],
        "forbidden_keywords": ["battery", "phosphate", "produced water", "water treatment", "roof", "electrode"],
    },
    
    "membrane_materials": {
        "display_name": "Membrane Materials",
        "description": "Advanced membrane materials for separation, filtration, and purification",
        "allowed_categories": [
            "membrane_water_treatment",
        ],
        "forbidden_keywords": ["battery", "phosphate", "roof", "fabric", "stain"],
    },
    
    "general_explorer": {
        "display_name": "General Explorer Mode",
        "description": "For materials that don't fit specialized domains or experimental materials",
        "allowed_categories": [
            "other_material",
        ],
        "forbidden_keywords": [],
    },
}

# Reverse mapping: category -> domain
CATEGORY_TO_DOMAIN_SPECIFIC = {}
for domain_key, domain_info in DOMAIN_DEFINITIONS.items():
    for category in domain_info["allowed_categories"]:
        CATEGORY_TO_DOMAIN_SPECIFIC[category] = domain_key

# ============================================================================
# NEGATIVE KEYWORD RULES: Prevent Cross-Domain Contamination
# ============================================================================

NEGATIVE_KEYWORD_RULES = {
    "membrane_water_treatment": {
        "must_include_keywords": ["membrane", "filtration", "water flux", "rejection"],
        "weak_generic_keywords": ["porous", "water", "filter", "separation"],
        "forbidden_cross_domain_keywords": ["anode", "cathode", "electrode", "phosphate recovery", "roof", "fabric", "thermal"],
    },
    
    "photocatalytic_coating": {
        "must_include_keywords": ["photocatalytic", "TiO2", "light-driven", "water treatment"],
        "weak_generic_keywords": ["coating", "nanoparticles", "degradation"],
        "forbidden_cross_domain_keywords": ["battery", "electrode", "phosphate", "roof", "fabric", "thermal"],
    },
    
    "adsorbent_heavy_metals": {
        "must_include_keywords": ["heavy metal", "adsorption", "lead", "cadmium", "arsenic"],
        "weak_generic_keywords": ["adsorbent", "removal", "contamination"],
        "forbidden_cross_domain_keywords": ["battery", "electrode", "phosphate", "roof", "fabric", "produced water"],
    },
    
    "desalination_pretreatment_media": {
        "must_include_keywords": ["desalination", "pretreatment", "seawater"],
        "weak_generic_keywords": ["water", "treatment", "salt"],
        "forbidden_cross_domain_keywords": ["battery", "phosphate", "roof", "fabric", "electrode"],
    },
    
    "oil_gas_produced_water_pretreatment_media": {
        "must_include_keywords": ["produced water", "oil and gas", "hydrocarbon", "ADNOC"],
        "weak_generic_keywords": ["water", "treatment", "removal"],
        "forbidden_cross_domain_keywords": ["battery", "phosphate", "roof", "fabric", "thermal", "electrode"],
    },
    
    "sodium_ion_battery_anode_composite": {
        "must_include_keywords": ["battery", "sodium-ion", "anode", "electrode", "Na+"],
        "weak_generic_keywords": ["carbon", "binder", "composite"],
        "forbidden_cross_domain_keywords": ["phosphate", "roof", "fabric", "water treatment", "produced water", "thermal"],
    },
    
    "phosphate_recovery_material": {
        "must_include_keywords": ["phosphate", "nutrient recovery", "phosphorus", "agricultural"],
        "weak_generic_keywords": ["recovery", "adsorption", "removal"],
        "forbidden_cross_domain_keywords": ["battery", "roof", "fabric", "water treatment", "electrode"],
    },
    
    "roof_waterproofing_thermal_insulation_coating": {
        "must_include_keywords": ["roof", "waterproofing", "coating", "building"],
        "weak_generic_keywords": ["coating", "water", "thermal"],
        "forbidden_cross_domain_keywords": ["battery", "phosphate", "water treatment", "fabric", "electrode"],
    },
    
    "thermal_insulation_composite": {
        "must_include_keywords": ["thermal insulation", "thermal conductivity", "heat resistance"],
        "weak_generic_keywords": ["insulation", "thermal", "temperature"],
        "forbidden_cross_domain_keywords": ["battery", "phosphate", "water treatment", "fabric", "electrode"],
    },
    
    "self_cleaning_building_coating": {
        "must_include_keywords": ["self-cleaning", "facade", "photocatalytic", "building"],
        "weak_generic_keywords": ["coating", "surface", "nanoparticles"],
        "forbidden_cross_domain_keywords": ["battery", "phosphate", "water treatment", "fabric", "electrode"],
    },
    
    "atmospheric_water_harvesting_material": {
        "must_include_keywords": ["atmospheric water", "harvesting", "desiccant", "hygroscopic"],
        "weak_generic_keywords": ["water", "moisture", "capture"],
        "forbidden_cross_domain_keywords": ["battery", "phosphate", "roof", "fabric", "electrode"],
    },
    
    "fabric_oil_stain_removal_composite": {
        "must_include_keywords": ["fabric", "textile", "stain removal", "laundry"],
        "weak_generic_keywords": ["stain", "cleaning", "removal"],
        "forbidden_cross_domain_keywords": ["battery", "phosphate", "water treatment", "roof", "electrode"],
    },
    
    "co2_capture_material": {
        "must_include_keywords": ["CO2 capture", "carbon capture", "amine", "regeneration"],
        "weak_generic_keywords": ["capture", "carbon", "absorption"],
        "forbidden_cross_domain_keywords": ["battery", "phosphate", "roof", "fabric", "water treatment"],
    },
    
    "potassium_brine_separation_material": {
        "must_include_keywords": ["potassium", "brine", "separation", "KCl"],
        "weak_generic_keywords": ["recovery", "separation", "salt"],
        "forbidden_cross_domain_keywords": ["battery", "phosphate", "roof", "fabric", "water treatment"],
    },
}

# ============================================================================
# CENTRAL CATEGORY REGISTRY (Single Source of Truth)
# ============================================================================

CATEGORY_REGISTRY = {
    "membrane_water_treatment": {
        "normalized_category_name": "membrane_water_treatment",
        "display_name": "Membrane Water Treatment Material",
        "priority": 10,  # Checked first to prevent misclassification as adsorbent
        "aliases": ["membrane", "membrane filtration", "membrane separation", "membrane-based"],
        
        "priority_keywords": [
            "membrane", "anti-fouling", "polymer membrane matrix", "PVDF", "PES", "PSf",
            "water flux", "permeability", "rejection efficiency", "filtration cycles",
            "cleaning recovery", "pore size", "molecular weight cut-off", "MWCO",
            "microfiltration", "ultrafiltration", "nanofiltration", "mixed-matrix membrane"
        ],
        
        "default_composition": [
            {"component": "Polymer membrane matrix (PVDF, PES, PSf, or cellulose acetate)", "ratio": 0.50},
            {"component": "Hydrophilic additive (PEG, PVP, or zwitterionic polymer)", "ratio": 0.15},
            {"component": "Silica nanoparticles or hydrophilic inorganic filler", "ratio": 0.15},
            {"component": "Activated carbon, biochar, or MOF additive", "ratio": 0.10},
            {"component": "Antimicrobial or stabilizing additive (ZnO, TiO2, Ag, clay, or alumina)", "ratio": 0.05},
            {"component": "Crosslinker or casting modifier", "ratio": 0.05},
        ],
        
        "category_specific_parameters": {
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
        
        "characterization_methods": ["SEM/EDS", "XRD", "FTIR", "BET", "Mercury porosimetry", "Contact angle", "Tensile testing", "ICP-OES", "ICP-MS"],
        
        "safety_tests": [
            "Nanoparticle leaching (ICP-OES/ICP-MS)",
            "Mechanical durability under operating pressure",
            "Treated water quality analysis",
            "Microbial safety if antimicrobial additives present"
        ],
        
        "processing_method": [
            "1. Dope Solution Preparation:",
            "   - Dissolve polymer (PVDF, PES, PSf, or cellulose acetate) in solvent (DMAc, NMP, or DMF).",
            "   - Add hydrophilic additives (PEG, PVP) and nanoparticles under controlled mixing.",
            "   - Degas solution to remove air bubbles.",
            "   - Allow degassed solution to rest before casting.",
            "",
            "2. Membrane Casting:",
            "   - Cast dope solution onto glass plate or support material.",
            "   - Use controlled blade height to achieve uniform thickness (typical 100-300 um).",
            "   - Allow brief air-exposure time (2-10 seconds) for partial solvent evaporation.",
            "",
            "3. Phase Inversion:",
            "   - Immerse cast membrane into non-solvent bath (deionized water or water/alcohol mixture).",
            "   - Maintain bath temperature (typically ambient or 25-30 C).",
            "   - Precipitation occurs as solvent diffuses out and non-solvent diffuses in.",
            "   - Duration: typically 10-30 minutes for full precipitation.",
            "",
            "4. Washing and Rinsing:",
            "   - Remove membrane from coagulation bath.",
            "   - Rinse multiple times in fresh deionized water (3-5 rinses minimum).",
            "   - Each rinse: 10-30 minutes to remove residual solvent and water-soluble additives.",
            "",
            "5. Drying:",
            "   - Air-dry membrane at ambient temperature for 1-2 hours.",
            "   - Optional gentle heating (30-40 C) to complete drying, but avoid high temperatures (risk of pore collapse).",
            "   - Store dried membrane in dry conditions until testing.",
            "",
            "6. Leaching Pre-Wash (if water-soluble additives used):",
            "   - Soak membrane in deionized water for 24-48 hours before use.",
            "   - Change water 2-3 times to remove trapped additives.",
            "   - This reduces initial flux decline and improves fouling resistance.",
            "",
            "7. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact casting parameters (blade height, evaporation time), coagulation conditions, and drying time must be optimized experimentally.",
            "   - No commercial performance claim should be made before rigorous validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven membrane permeability, contaminant rejection, anti-fouling performance, cleaning recovery, treated-water safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, long-term filtration testing, leaching analysis, mechanical durability testing, treated-water quality analysis, and consultation with qualified materials engineers, membrane specialists, and water-treatment experts. This report is for research and development guidance only."
    },
    
    "fabric_oil_stain_removal_composite": {
        "normalized_category_name": "fabric_oil_stain_removal_composite",
        "display_name": "Fabric Oil-Stain Removal Composite",
        "priority": 1,  # HIGHEST PRIORITY: fabric stains must override heavy metals and adsorbents
        "aliases": ["fabric stain remover", "oil stain removal", "laundry pre-treatment", "fabric safe"],
        
        "priority_keywords": [
            "fabric", "cotton clothing", "cotton fabric", "oil-stain removal", "oil stain",
            "grease stain", "cooking oil", "laundry", "pre-treatment", "pre-wash",
            "colorfastness", "rinsability", "skin-contact safety", "washing-machine",
            "garment", "textile", "cloth", "stain removal from fabric", "fabric stain",
            "fabric safe", "laundry stain", "clothing stain", "fabric-safe", "wash-safe"
        ],
        
        "default_composition": [
            {"component": "Biodegradable nonionic/anionic surfactant blend", "ratio": 0.30},
            {"component": "Mild alkaline builder (sodium carbonate or sodium bicarbonate)", "ratio": 0.20},
            {"component": "Oil-absorbing porous filler (silica/clay/biochar)", "ratio": 0.15},
            {"component": "Lipase-compatible enzyme or enzyme-support additive", "ratio": 0.10},
            {"component": "Water-dispersible cellulose binder/carrier", "ratio": 0.10},
            {"component": "Citrate or water-softening chelating agent", "ratio": 0.05},
            {"component": "Anti-caking/stabilizer/preservative system", "ratio": 0.05},
            {"component": "Optional oxygen-based booster (low-level sodium percarbonate)", "ratio": 0.05},
        ],
        
        "category_specific_parameters": {
            "fabric_type": "Cotton, cotton-blend, or cellulose-based textile",
            "stain_type": "Cooking oil, olive oil, grease, oily food residue, sebum model",
            "application_form": "Powder pre-treat, paste, or spray formulation",
            "contact_time": "5–30 minutes for effective stain lifting before washing",
            "wash_conditions": "Standard machine wash, warm or hot water (30–60°C)",
            "pH_range": "6–9 (neutral to mildly alkaline for fabric safety)",
            "surfactant_system": "Type and concentration for oil emulsification without fabric damage",
            "enzyme_compatibility": "Lipase or ester-bond degradation activity (if enzyme-active)",
            "rinsability": "Target: residue-free after one or two rinses in washing machine",
            "colorfastness": "No dye bleeding or color change on treated fabric",
            "fabric_damage_risk": "No visible fibrillation, pilling, or tensile strength loss",
            "skin_contact_safety": "Non-irritating formulation; safe for hand application",
            "environmental_safety": "Biodegradable ingredients; low aquatic toxicity"
        },
        
        "validation_plan": {
            "oil_stain_removal_efficiency": "% stain removal on standardized cotton swatches with cooking oil, olive oil, grease, or sebum stains",
            "stain_testing_protocol": "Before/after image analysis or colorimetric stain scoring (ASTM D6888 or equivalent)",
            "comparison_baseline": "Performance vs. commercial laundry pre-treatment products and untreated controls",
            "cotton_fiber_compatibility": "Tensile strength, elongation, or fabric hand after treatment",
            "colorfastness_verification": "No color change or dye bleeding on dyed cotton samples (AATCC 106 or equivalent)",
            "rinsability_test": "Visible residue assessment after standard machine rinse cycles",
            "pH_measurement": "Neutral pH confirmation in formulation",
            "skin_irritation_risk": "Non-irritant classification or dermatological safety screening",
            "biodegradability_assessment": "OECD 301 or equivalent biodegradation test for surfactants",
            "aquatic_toxicity": "Acute toxicity screening for aquatic organisms (OECD 202, 203, or equivalent)",
            "washing_machine_compatibility": "Safe for standard front-load and top-load machines; no mechanical damage"
        },
        
        "characterization_methods": ["FTIR (surfactant verification)", "pH measurement", "Enzyme activity assay (if applicable)", "Fiber tensile testing", "Colorimetry", "Contact angle (hydrophobicity testing)"],
        
        "safety_tests": [
            "Stain removal efficiency on standardized swatches",
            "Colorfastness and dye stability",
            "Fabric tensile strength and durability",
            "Skin irritation screening",
            "Biodegradability assessment",
            "Aquatic toxicity testing",
            "Rinsability and residue evaluation"
        ],
        
        "processing_method": [
            "1. Surfactant and Builder Mixing:",
            "   - Blend biodegradable surfactant (nonionic and anionic types) with mild alkaline builder (sodium carbonate or bicarbonate).",
            "   - Ensure uniform distribution to avoid clumping.",
            "   - Target final surfactant concentration 20–30 wt% in formulation.",
            "",
            "2. Enzyme or Support Component Addition:",
            "   - If using lipase enzyme: add enzyme powder or enzyme-coated support material.",
            "   - Mix gently to avoid enzyme deactivation or powder segregation.",
            "   - Alternatively, add enzyme-support pre-complex if pre-made.",
            "",
            "3. Filler and Binder Addition:",
            "   - Add oil-absorbing porous filler (silica gel, clay, or biochar) to enhance oil-stain lifting.",
            "   - Incorporate cellulose binder or carrier to create cohesive pre-treat powder.",
            "   - Mix under moderate agitation to avoid degradation of sensitive components.",
            "",
            "4. Chelating Agent and Preservative:",
            "   - Add citrate or similar chelating agent for water softening and improved cleaning.",
            "   - Add anti-caking agent (if powder formulation) or preservative (if paste/spray formulation).",
            "   - Mix thoroughly until uniformly distributed.",
            "",
            "5. Optional Oxygen Booster:",
            "   - Add low-level sodium percarbonate (oxygen-based booster) for enhanced stain lifting if desired.",
            "   - Keep level low (<5%) to maintain fabric safety and avoid bleaching of colored textiles.",
            "",
            "6. Granulation and Drying (for powder pre-treat):",
            "   - If formulation is damp: granulate into uniform particles (0.5–2 mm) using controlled wet granulation.",
            "   - Air-dry at ambient temperature or gentle heat (30–40°C) for 6–12 hours.",
            "   - Target residual moisture <3% for storage stability.",
            "",
            "7. Packaging and Stability Testing:",
            "   - Package in moisture-proof containers for long-term stability.",
            "   - Store at cool, dry conditions (15–25°C, <50% RH).",
            "   - Verify stain-removal activity retention after 6 months storage.",
            "",
            "8. Evidence Boundary:",
            "   - This is a planning-level formulation route for research guidance.",
            "   - Exact surfactant blend, enzyme loading, filler type, and processing conditions must be optimized experimentally.",
            "   - No commercial laundry pre-treatment or fabric-safety claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven oil-stain removal performance, fabric safety, colorfastness, skin-contact safety, biodegradability, washing-machine compatibility, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation with standardized cotton swatches, fiber tensile testing, colorfastness verification, skin irritation screening, biodegradability testing, aquatic toxicity assessment, machine-washing compatibility verification, and consultation with qualified materials engineers, textile specialists, detergent formulation experts, and consumer-safety professionals. This report is for research and development guidance only."
    },
    
    "desalination_pretreatment_media": {
        "normalized_category_name": "desalination_pretreatment_media",
        "display_name": "Desalination Pre-Treatment Media",
        "priority": 15,
        "aliases": ["pre-treatment media", "desalination pretreatment", "RO pretreatment", "NF pretreatment"],
        
        "priority_keywords": [
            "desalination pre-treatment", "pre-treatment media", "pretreatment media",
            "before membrane desalination", "improve membrane lifetime", "reduce fouling risk",
            "pressure drop", "media regeneration", "microbial growth risk",
            "seawater compatibility", "brackish water compatibility",
            "suspended solids", "organic matter removal", "desalination pretreatment",
            "pre-treatment desalination", "RO pretreatment", "NF pretreatment",
            "membrane fouling reduction", "activated carbon", "iron oxide",
            "porous silica", "mineral stabilizers"
        ],
        
        "default_composition": [
            {"component": "Activated carbon", "ratio": 0.35},
            {"component": "Iron oxide or iron hydroxide", "ratio": 0.25},
            {"component": "Porous silica", "ratio": 0.20},
            {"component": "Bentonite clay, alumina, zeolite, or mineral stabilizer", "ratio": 0.10},
            {"component": "Calcium carbonate, magnesium oxide, or pH/scaling buffer", "ratio": 0.05},
            {"component": "Polymer or biopolymer binder", "ratio": 0.05},
        ],
        
        "category_specific_parameters": {
            "feed_water_type": "Seawater, brackish water, or RO/NF pre-treatment stream",
            "target_contaminants": "Organic matter, turbidity/TSS, selected metals, biofouling precursors",
            "media_form": "Granules, beads, pellets, cartridge media, or packed-bed media",
            "bed_depth_media_loading": "User-defined based on reactor design",
            "flow_rate_empty_bed_contact_time": "Defined test condition",
            "pressure_drop_target": "Measured across the media bed (kPa or bar)",
            "organic_matter_removal": "TOC, COD, or UV254 reduction (%)",
            "turbidity_suspended_solids_removal": "NTU or TSS reduction (%)",
            "metal_removal": "Fe, Mn, Pb, As, Cu, or selected metals removal efficiency",
            "regeneration_method": "Backwash, chemical wash, thermal regeneration, or media replacement",
            "microbial_growth_risk": "Bacterial count, biofilm growth, and biostability testing",
            "leaching_test": "Fe, silica, binder residues, stabilizer, pH buffer, and trace contaminants",
            "saltwater_compatibility": "Seawater/brackish water exposure, scaling risk, and performance retention"
        },
        
        "validation_plan": {
            "contaminant_removal_efficiency": "TOC, COD, UV254 reduction (%) for organic matter",
            "toc_cod_uv254_reduction": "Organic matter reduction under defined conditions",
            "turbidity_suspended_solids_reduction": "NTU and TSS reduction (%) vs. feed water specification",
            "selected_metal_removal_testing": "Fe, Mn, Pb, As, Cu, or site-specific metals (ICP-OES)",
            "pressure_drop_vs_flow_rate": "Measured pressure drop across media bed at varying flow rates",
            "breakthrough_curve_testing": "Dynamic column breakthrough curves for target contaminants",
            "regeneration_efficiency": "Media recovery after backwash, chemical wash, or thermal regeneration (%)",
            "cycling_durability": "Pressure drop and contaminant removal after 5-10 cycles",
            "microbial_growth_biofilm_risk_testing": "Bacterial count, biofilm growth, and biostability assessment",
            "leaching_safety_analysis": "Fe, silica, binder, stabilizer, pH buffer, and trace metals leaching (ICP-OES)",
            "seawater_brackish_water_compatibility": "Performance retention in high-salinity feed water",
            "scaling_fouling_tendency": "CaCO3, silica, and biological scaling assessment",
            "downstream_membrane_fouling_reduction_test": "RO/NF membrane flux decline with and without pre-treatment",
            "treated_water_safety_ecotoxicity_review": "Residual contaminant levels, pH, conductivity, microbial safety"
        },
        
        "characterization_methods": [
            "SEM/EDS",
            "XRD",
            "FTIR",
            "BET",
            "Mercury porosimetry",
            "ICP-OES",
            "Ion chromatography",
            "Pressure drop measurement",
            "Particle size distribution"
        ],
        
        "safety_tests": [
            "Contaminant removal verification",
            "Leaching analysis (Fe, silica, binder)",
            "Microbial growth and biofilm risk assessment",
            "Seawater/brackish water compatibility",
            "Pressure drop and media integrity"
        ],
        
        "processing_method": [
            "1. Powder Pre-Mix:",
            "   - Mix activated carbon, iron oxide/hydroxide, and porous silica in dry state.",
            "   - Add bentonite clay, alumina, or zeolite as stabilizer.",
            "   - Blend thoroughly to ensure uniform distribution.",
            "",
            "2. Binder and pH Buffer Addition:",
            "   - Add polymer or biopolymer binder (wet mixing).",
            "   - Include calcium carbonate or magnesium oxide as pH/scaling buffer.",
            "   - Mix until cohesive paste is formed.",
            "",
            "3. Pelletizing or Granulation:",
            "   - Extrude or granulate the mixture into uniform particles (typical 2-6 mm diameter).",
            "   - Use controlled pressure and temperature if thermal bonding is employed.",
            "   - Ensure consistent particle size to minimize pressure drop variation.",
            "",
            "4. Drying:",
            "   - Air-dry at ambient temperature or gentle heat (40-60 C) for 12-24 hours.",
            "   - Ensure moisture content <5% to prevent microbe growth and compaction.",
            "",
            "5. Activation (optional if required):",
            "   - Light steam activation (if activated carbon component needs refreshing).",
            "   - Controlled thermal treatment at 100-150 C for 1-2 hours.",
            "",
            "6. Leaching Pre-Wash:",
            "   - Backwash media with deionized or low-TDS water for 30-60 minutes.",
            "   - Change wash water 2-3 times to remove fines and loosely bound binder residues.",
            "   - This reduces initial turbidity and improves filtration performance.",
            "",
            "7. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact particle size, binder ratio, drying temperature, and pre-wash protocol must be optimized experimentally.",
            "   - No commercial performance or regulatory claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven desalination pre-treatment performance, contaminant removal efficiency, membrane-fouling reduction, seawater compatibility, regeneration performance, treated-water safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, pressure-drop testing, contaminant-removal testing, leaching analysis, microbial-growth assessment, seawater/brackish-water compatibility testing, downstream membrane-fouling studies, and consultation with qualified materials engineers, desalination specialists, water-treatment experts, and environmental/regulatory professionals. This report is for research and development guidance only."
    },
    
    "oil_gas_produced_water_pretreatment_media": {
        "normalized_category_name": "oil_gas_produced_water_pretreatment_media",
        "display_name": "Oil & Gas Produced-Water Pre-Treatment Media",
        "priority": 14,  # High priority: more specific than desalination pre-treatment
        "aliases": ["produced water pre-treatment", "oilfield water pre-treatment", "produced-water media", "oil and gas pre-treatment", "ADNOC pre-treatment", "Gulf produced water", "oilfield produced water"],
        
        "priority_keywords": [
            "produced water", "oil and gas operations", "ADNOC", "UAE oil/gas", "Gulf operating conditions",
            "hot Gulf conditions", "oil and grease", "hydrocarbons", "TOC", "COD",
            "sulfide-related contaminants", "sulfide", "reinjection", "reuse", "high-salinity produced water",
            "backwashability", "downstream membrane fouling", "oilfield water", "oil production",
            "gas field", "reservoir", "formation water", "produced-water treatment"
        ],
        
        "default_composition": [
            {"component": "Activated carbon / organoclay blend", "ratio": 0.30},
            {"component": "Iron oxide or iron hydroxide", "ratio": 0.20},
            {"component": "Porous silica", "ratio": 0.15},
            {"component": "Zeolite / bentonite / alumina stabilizer", "ratio": 0.15},
            {"component": "Anti-scaling mineral buffer (magnesium oxide or calcium carbonate)", "ratio": 0.10},
            {"component": "Water-stable polymer or ceramic binder", "ratio": 0.10},
        ],
        
        "category_specific_parameters": {
            "feed_water_type": "Produced water, seawater, brackish water, or mixed oilfield water",
            "oil_grease_removal": "mg/L reduction under defined test conditions",
            "hydrocarbon_removal": "TPH, BTEX, or oil/grease reduction (%)",
            "toc_cod_reduction": "Organic load reduction (%)",
            "turbidity_tss_removal": "NTU and suspended solids reduction (%)",
            "selected_metal_removal": "Fe, Mn, Pb, As, Cu, Ni, Cr, or site-specific metals removal efficiency",
            "sulfide_compatibility": "Sulfide exposure, odor/corrosion risk, and performance retention",
            "high_salinity_compatibility": "Seawater/brine/produced-water exposure tolerance",
            "pressure_drop_target": "Measured across packed bed or cartridge (kPa or bar)",
            "breakthrough_behavior": "Dynamic column breakthrough curves",
            "regeneration_backwashability": "Backwash or chemical cleaning recovery (%)",
            "microbial_growth_risk": "Biofilm and biostability assessment",
            "scaling_fouling_tendency": "CaCO3, sulfate, silica, and biological scaling risk",
            "leaching_safety": "Fe, binder, organoclay, mineral stabilizer, and trace contaminants",
            "downstream_membrane_fouling_reduction": "RO/NF flux decline comparison with/without pre-treatment",
            "reinjection_reuse_compatibility": "Treated-water quality against intended use"
        },
        
        "validation_plan": {
            "oil_grease_removal_efficiency": "mg/L reduction of oil and grease (O&G) under defined test conditions",
            "hydrocarbon_removal_testing": "TPH, BTEX, or individual hydrocarbon analysis",
            "toc_cod_uv254_reduction": "Organic load reduction under high-salinity/produced-water conditions",
            "turbidity_tss_removal": "NTU and suspended solids reduction from produced water",
            "selected_metal_removal": "Fe, Mn, Pb, As, Cu, Ni, Cr by ICP-OES or ICP-MS",
            "sulfide_compatibility_screening": "Sulfide exposure, H2S production risk, and odor/corrosion-related testing",
            "pressure_drop_vs_flow_rate": "Pressure drop across packed bed at varying flow rates",
            "breakthrough_curve_testing": "Dynamic column breakthrough curves for target contaminants",
            "regeneration_backwash_efficiency": "Media recovery after backwash or chemical cleaning",
            "cycling_durability": "Pressure drop and contaminant removal after 5-10 cycles",
            "high_salinity_produced_water_compatibility": "Performance retention in produced-water/seawater/brine environment",
            "scaling_fouling_tendency": "CaCO3, sulfate, silica, and biological scaling assessment",
            "microbial_growth_biofilm_risk": "Bacterial count, biofilm growth, and biostability in produced water",
            "leaching_safety_analysis": "Fe, binder, organoclay, mineral stabilizer, and trace metals leaching",
            "downstream_membrane_fouling_reduction_test": "RO/NF membrane flux decline with and without pre-treatment",
            "treated_water_quality_review": "Residual contaminants, pH, conductivity, and suitability for reinjection/reuse"
        },
        
        "characterization_methods": [
            "SEM/EDS",
            "XRD",
            "FTIR",
            "BET",
            "Mercury porosimetry",
            "ICP-OES",
            "ICP-MS",
            "Ion chromatography",
            "Pressure drop measurement",
            "Particle size distribution",
            "Oil and grease analysis (O&G)"
        ],
        
        "safety_tests": [
            "Oil and grease removal verification",
            "Hydrocarbon removal analysis",
            "TOC/COD reduction testing",
            "Sulfide compatibility and H2S generation risk",
            "Leaching analysis (Fe, binder, organoclay, stabilizer)",
            "Microbial growth and biofilm risk assessment",
            "High-salinity and produced-water compatibility",
            "Pressure drop and media integrity",
            "Treated-water quality for reinjection/reuse"
        ],
        
        "processing_method": [
            "1. Powder Pre-Mix (Desalination Base + Oilfield Modifications):",
            "   - Mix activated carbon, organoclay, iron oxide/hydroxide, and porous silica in dry state.",
            "   - Add zeolite, bentonite, or alumina as stabilizer.",
            "   - Blend thoroughly to ensure uniform distribution.",
            "   - This blend targets both organic matter and hydrocarbon removal.",
            "",
            "2. Anti-Scaling and High-Salinity Conditioning:",
            "   - Add anti-scaling mineral buffer (magnesium oxide or calcium carbonate).",
            "   - Include additives to enhance high-salinity/produced-water tolerance.",
            "   - Optimize formulation for sulfide compatibility if sulfide-bearing water is expected.",
            "",
            "3. Binder Addition (Oilfield-Specific):",
            "   - Add water-stable polymer or ceramic binder for produced-water conditions.",
            "   - Ensure binder stability under high-salinity and thermal stress.",
            "   - Mix until cohesive paste is formed.",
            "",
            "4. Pelletizing or Granulation:",
            "   - Extrude or granulate the mixture into uniform particles (typical 2-6 mm diameter).",
            "   - Use controlled pressure and temperature if thermal bonding is employed.",
            "   - Ensure consistent particle size to minimize pressure drop variation.",
            "",
            "5. Drying:",
            "   - Air-dry at ambient temperature or gentle heat (40-60°C) for 12-24 hours.",
            "   - Ensure moisture content <5% to prevent microbe growth and compaction.",
            "",
            "6. High-Salinity Preconditioning (Oilfield-Specific):",
            "   - Backwash media with high-salinity synthetic produced water or seawater for 30-60 minutes.",
            "   - This step conditions the media to high-salinity environments and reduces initial fines.",
            "   - Change wash water 2-3 times to remove loosely bound materials.",
            "",
            "7. Oil/Grease Breakthrough Testing (Optional Before Deployment):",
            "   - Conduct mini breakthrough test with actual or synthetic produced water.",
            "   - Verify oil/grease removal efficiency and pressure-drop profile.",
            "   - This validates performance before field deployment.",
            "",
            "8. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact particle size, binder ratio, drying temperature, and preconditioning protocol must be optimized experimentally for produced-water conditions.",
            "   - No commercial performance or regulatory claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: These parameters do not demonstrate proven produced-water treatment performance, oil/grease removal, hydrocarbon removal, sulfide compatibility, membrane-fouling reduction, reinjection suitability, environmental safety, regulatory compliance, or commercial readiness. All recommendations are conditional upon produced-water testing, high-salinity compatibility testing, oil/grease and hydrocarbon analysis, pressure-drop testing, breakthrough analysis, leaching assessment, microbial-growth evaluation, downstream membrane-fouling studies, sulfide-compatibility screening, and expert review by oilfield-water-treatment, desalination, environmental, and regulatory specialists. This report is for research and development guidance only."
    },
    
    "atmospheric_water_harvesting_material": {
        "normalized_category_name": "atmospheric_water_harvesting_material",
        "display_name": "Atmospheric Water Harvesting Material",
        "priority": 20,
        "aliases": ["AWH material", "moisture harvesting", "atmospheric water"],
        
        "priority_keywords": [
            "atmospheric water harvesting", "AWH", "moisture capture", "hygroscopic salt",
            "water uptake", "desorption temperature", "wet/dry cycling", "salt leaching",
            "water from air", "collected water quality", "cycling durability",
            "regeneration energy", "thermal regeneration", "water harvesting",
            "harvest water from air", "absorb moisture", "desiccant",
            "moisture harvesting", "atmospheric water"
        ],
        
        "default_composition": [
            {"component": "Activated carbon or porous carbon", "ratio": 0.30},
            {"component": "Porous silica or silica gel", "ratio": 0.25},
            {"component": "Aluminum oxide, inorganic stabilizer, or clay", "ratio": 0.15},
            {"component": "Calcium chloride or controlled hygroscopic salt", "ratio": 0.15},
            {"component": "Cellulose, polymer binder, or structural polymer", "ratio": 0.10},
            {"component": "Titanium dioxide, biochar, or carbon black (photothermal additive)", "ratio": 0.05},
        ],
        
        "category_specific_parameters": {
            "relative_humidity_range": "40–90% RH (optimal moisture capture window)",
            "water_uptake_target": "0.3–0.8 g water per g dry material",
            "adsorption_time": "4–12 hours under ambient conditions",
            "desorption_temperature": "50–80 °C (thermal or solar regeneration)",
            "regeneration_method": "Sunlight-assisted heating or low-grade thermal (waste heat compatible)",
            "cycling_target": "50–100 wet/dry cycles minimum (durability benchmark)",
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
            "collected_water_quality": "pH, TDS, conductivity, chloride (mg/L), trace metals, and microbial count per applicable standard"
        },
        
        "characterization_methods": ["Gravimetric analysis", "ICP-OES", "Thermal analysis (TGA/DSC)", "BET", "Microscopy"],
        
        "safety_tests": [
            "Salt leaching analysis",
            "Collected water quality (pH, TDS, conductivity, microbial)",
            "Trace metal analysis (ICP)",
            "Cycling durability"
        ],
        
        "processing_method": [
            "1. Powder Mixing and Homogenization:",
            "   - Blend dry activated carbon, porous silica, and aluminum oxide/clay uniformly.",
            "   - Add hygroscopic salt (calcium chloride) gradually while mixing to avoid clumping.",
            "   - Incorporate photothermal additives (TiO2, biochar) if included.",
            "   - Target: uniform powder with no agglomerates.",
            "",
            "2. Binder Preparation:",
            "   - Dissolve polymer binder (cellulose, polyurethane, or silicone) in compatible solvent or water.",
            "   - Add stabilizers and anti-caking agents if needed.",
            "   - Ensure smooth, bubble-free binder solution.",
            "",
            "3. Paste Formation:",
            "   - Slowly add dry powder to binder under controlled mechanical mixing.",
            "   - Mix until uniform, cohesive paste forms.",
            "   - Avoid excessive aeration.",
            "",
            "4. Shaping and Molding:",
            "   - Shape paste into pellets, disks, or monoliths (1-10 cm diameter depending on application).",
            "   - Use extrusion, compression molding, or hand-forming techniques.",
            "   - Ensure consistent shape and density.",
            "",
            "5. Drying:",
            "   - Air-dry at room temperature for 12-24 hours or gentle heat (40-50 C) for 6-8 hours.",
            "   - Ensure complete moisture removal to prevent salt deliquescence.",
            "   - Target moisture content <5%.",
            "",
            "6. Activation Cycling (optional):",
            "   - Perform 5-10 test wet/dry cycles at target humidity and desorption temperature to stabilize material.",
            "   - Document water uptake and release performance over cycles.",
            "",
            "7. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact mixing speed, drying temperature, and shaping parameters must be optimized experimentally.",
            "   - No commercial water-harvesting or potability claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven water-harvesting performance, potable-water safety, commercial readiness, or suitability for any specific application. All recommendations are CONDITIONAL upon rigorous laboratory validation, field testing, compliance with applicable water-quality standards, and consultation with qualified materials engineers and water-quality specialists. This report is for research and development guidance only."
    },
    
    "photocatalytic_coating": {
        "normalized_category_name": "photocatalytic_coating",
        "display_name": "Photocatalytic Coating",
        "priority": 30,
        "aliases": ["photocatalyst", "photodegradation coating", "self-cleaning coating"],
        
        "priority_keywords": [
            "photocatalytic", "photocatalytic coating", "photodegradation", "TiO2",
            "UV light", "visible light", "pollutant degradation", "coating surface",
            "glass surface", "ceramic surface", "polymer surface", "binder system",
            "solar light", "photocatalytic degradation", "self-cleaning"
        ],
        
        "default_composition": [
            {"component": "Titanium dioxide (TiO2) or photocatalyst", "ratio": 0.40},
            {"component": "Biochar or activated carbon", "ratio": 0.20},
            {"component": "Silica support or silica sol", "ratio": 0.20},
            {"component": "Inorganic stabilizer (alumina, clay, or zirconia)", "ratio": 0.10},
            {"component": "Durable binder system", "ratio": 0.10},
        ],
        
        "category_specific_parameters": {
            "substrate_type": "Glass, ceramic, or polymer",
            "coating_thickness": "0.5–5 micrometers",
            "curing_temperature": "Room temperature or 60–150 °C",
            "light_source": "UV-A, UV-B, or visible light (wavelength specification)",
            "target_pollutant": "Dyes, volatile organic compounds, or bacterial spores",
            "pollutant_concentration": "ppm or mg/L range",
            "catalyst_loading": "mg/cm² or wt%"
        },
        
        "validation_plan": {
            "pollutant_degradation_efficiency": ">80% degradation at 90 min under specified light",
            "reaction_kinetics": "First-order rate constant (k) in min⁻¹",
            "catalyst_stability": "Activity retention after 10 cycles",
            "leaching_test": "ICP-MS or atomic absorption spectroscopy for metal ion release",
            "characterization_methods": ["SEM", "XRD", "FTIR", "UV-Vis DRS", "BET"],
            "toxicity_safety_review": "Leachate non-toxic; no hazardous byproducts"
        },
        
        "characterization_methods": ["SEM/EDS", "XRD", "FTIR", "UV-Vis DRS", "BET", "ICP-MS"],
        
        "safety_tests": [
            "Metal ion leaching (ICP-MS)",
            "Pollutant degradation byproduct analysis",
            "Toxicity assessment",
            "Coating adhesion and durability"
        ],
        
        "processing_method": [
            "1. Substrate Surface Preparation:",
            "   - Clean substrate (glass, ceramic, or polymer) thoroughly with solvent or detergent.",
            "   - Remove dust, grease, and loose particles.",
            "   - Dry completely before coating.",
            "   - Optional: light plasma or UV-ozone treatment to enhance adhesion.",
            "",
            "2. Photocatalyst Powder Preparation:",
            "   - Disperse TiO2 or alternative photocatalyst in solvent or liquid binder.",
            "   - Use ultrasonication to break agglomerates and achieve uniform dispersion.",
            "   - Maintain target catalyst loading (mg/cm²) throughout preparation.",
            "",
            "3. Coating Mixture Formulation:",
            "   - Combine photocatalyst dispersion with binder (silica sol or polymer).",
            "   - Add adhesion promoters and flow agents if needed.",
            "   - Mix thoroughly to ensure homogeneous coating solution.",
            "",
            "4. Coating Application:",
            "   - Apply coating by dip-coating, spin-coating, spray, or brush depending on substrate and viscosity.",
            "   - Control coating thickness (0.5-5 micrometers) via application method and speed.",
            "   - Ensure even, bubble-free coverage.",
            "",
            "5. Drying:",
            "   - Air-dry at room temperature or gentle heat (30-50 C) for 30 minutes to 2 hours.",
            "   - Allow volatile solvents to evaporate completely.",
            "",
            "6. Thermal Curing (if applicable):",
            "   - Heat at 60-150 C depending on binder type and substrate tolerance.",
            "   - Duration: 1-4 hours for full crosslinking and densification.",
            "   - Ramp heating rate slowly (2-5 C/min) to avoid substrate stress.",
            "",
            "7. Adhesion and Quality Verification:",
            "   - Test adhesion (ASTM D3359 cross-hatch or tape test).",
            "   - Verify coating continuity and absence of cracks or delamination.",
            "   - Confirm photocatalytic activity by pollutant degradation testing.",
            "",
            "8. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact catalyst loading, application method, curing temperature, and coating thickness must be optimized experimentally.",
            "   - No commercial photocatalytic or self-cleaning performance claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven photocatalytic degradation efficiency, coating durability, treated-water safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, leaching analysis, toxicity testing, durability testing, field testing where appropriate, and consultation with qualified materials engineers and water-quality specialists. This report is for research and development guidance only."
    },
    
    "phosphate_recovery_material": {
        "normalized_category_name": "phosphate_recovery_material",
        "display_name": "Phosphate Recovery Material",
        "priority": 40,
        "aliases": ["phosphorus recovery", "nutrient recovery", "phosphate adsorbent"],
        
        "priority_keywords": [
            "phosphate recovery", "phosphate ions", "phosphorus recovery", "nutrient recovery",
            "fertilizer reuse", "agricultural wastewater", "industrial wastewater phosphate",
            "calcium-based minerals", "iron oxide phosphate adsorption", "PO₄-P", "orthophosphate"
        ],
        
        "default_composition": [
            {"component": "Calcium hydroxide or calcium-based mineral", "ratio": 0.35},
            {"component": "Iron oxide or iron hydroxide", "ratio": 0.25},
            {"component": "Porous activated carbon or biochar", "ratio": 0.20},
            {"component": "Bentonite clay or inorganic stabilizer", "ratio": 0.10},
            {"component": "Polymer or biopolymer binder", "ratio": 0.10},
        ],
        
        "category_specific_parameters": {
            "target_phosphate_species": "Orthophosphate / PO₄-P",
            "initial_phosphate_concentration": "1–100 mg/L PO₄-P for screening",
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
            "phosphate_uptake_capacity": "mg PO₄-P / g adsorbent (Langmuir saturation)",
            "removal_efficiency": "preliminary target >60–80% under screening conditions",
            "regeneration_efficiency": ">50–80% phosphate recovery after desorption",
            "cycling_stability": "5–10 adsorption/desorption cycles minimum",
            "competing_ion_tolerance": "performance measured in synthetic and real wastewater",
            "fertilizer_reuse_potential": "nutrient release tested before circular-economy claim",
            "characterization_methods": ["SEM/EDS", "XRD", "FTIR", "ICP-OES", "BET"],
            "leaching_and_safety": "Fe, Ca, binder leaching; pH and conductivity of treated solution"
        },
        
        "characterization_methods": ["SEM/EDS", "XRD", "FTIR", "ICP-OES", "BET", "Ion chromatography"],
        
        "safety_tests": [
            "Leaching analysis (Fe, Ca, binder)",
            "Nutrient release testing",
            "Treated water quality (pH, conductivity)",
            "Cycling durability"
        ],
        
        "processing_method": [
            "1. Dry Powder Mixing:",
            "   - Blend calcium hydroxide or calcium mineral with iron oxide/hydroxide.",
            "   - Add porous activated carbon or biochar.",
            "   - Incorporate bentonite clay as inorganic stabilizer.",
            "   - Ensure uniform distribution of all components.",
            "",
            "2. Binder and Pellet Formation:",
            "   - Add polymer or biopolymer binder (wet mixing) to dry blend.",
            "   - Mix until cohesive paste is formed.",
            "   - Extrude or granulate mixture into uniform pellets (1-5 mm diameter).",
            "",
            "3. Drying:",
            "   - Air-dry at ambient temperature or gentle heat (40-60 C) for 12-24 hours.",
            "   - Target moisture content <5%.",
            "   - Ensure pellets are hard and friable, not soft or sticky.",
            "",
            "4. Activation (optional):",
            "   - Light thermal activation at 100-120 C for 2-4 hours if biochar component needs refreshing.",
            "   - Optional: brief pH buffering soak to establish optimal pH microenvironment.",
            "",
            "5. Leaching Pre-Wash:",
            "   - Wash pellets with deionized water 2-3 times to remove fines and loose binder residues.",
            "   - Each wash: 30-60 minutes.",
            "   - Discard initial wash waters; save final wash for baseline ion analysis.",
            "",
            "6. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact binder ratio, drying temperature, pellet size, and activation conditions must be optimized experimentally.",
            "   - No commercial nutrient-recovery or fertilizer-reuse claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven phosphate recovery performance, regeneration efficiency, nutrient reuse safety, environmental safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, real-wastewater testing, phosphate-ion analysis, leaching studies, regeneration testing, nutrient-release evaluation, and consultation with qualified materials engineers, water-treatment specialists, and agronomic/environmental experts. This report is for research and development guidance only."
    },
    
    "potassium_brine_separation_material": {
        "normalized_category_name": "potassium_brine_separation_material",
        "display_name": "Potassium Brine Separation Material",
        "priority": 50,
        "aliases": ["potassium recovery", "K⁺ selective", "potash material"],
        
        "priority_keywords": [
            "potassium salts", "potassium recovery", "potash brine", "K⁺ recovery",
            "mineral-rich brine", "selective separation from brine", "sodium and magnesium competition",
            "brine selectivity", "ion-exchange groups for potassium", "K⁺/Na⁺ selectivity",
            "potassium selective", "potassium sorbent", "potassium ion", "potassium extraction",
            "potassium separation", "agricultural brine", "potassium-selective"
        ],
        
        "default_composition": [
            {"component": "Functionalized porous silica", "ratio": 0.40},
            {"component": "Potassium-selective ion-exchange resin or crown ether groups", "ratio": 0.25},
            {"component": "Zeolite or alumina stabilizer", "ratio": 0.15},
            {"component": "Water-stable polymer binder (PVA, PVDF, or cellulose)", "ratio": 0.10},
            {"component": "Graphene oxide, biochar, or anti-fouling additive", "ratio": 0.05},
            {"component": "Optional inert porosity modifier", "ratio": 0.05},
        ],
        
        "category_specific_parameters": {
            "target_ion": "K⁺ with competing Na⁺, Mg²⁺, Ca²⁺ present",
            "brine_composition": "Synthetic or natural mineral-rich brine with salinity and ionic strength specified",
            "initial_potassium_concentration": "User-defined based on brine source; screening range 100–10,000 mg/L K+",
            "ph_working_range": "6–9",
            "contact_time": "30–120 minutes",
            "adsorbent_dosage": "1–10 g/L",
            "selectivity_targets": "K⁺/Na⁺ selectivity coefficient >10–100 depending on application",
            "regeneration_method": "acid, base, or salt-based desorption depending on functional groups and material stability",
            "regeneration_efficiency": ">50–80% K⁺ recovery or capacity restored",
            "cycling_target": "10–50 adsorption/desorption cycles minimum",
            "product_quality_test": "recovered potassium purity and contamination by Na, Mg, Ca"
        },
        
        "validation_plan": {
            "potassium_uptake_capacity": "mg K⁺ / g material at saturation",
            "adsorption_kinetics": "time-dependent K⁺ uptake profile and equilibration time",
            "adsorption_isotherm": "Langmuir, Freundlich, or Dubinin-Radushkevich model fitting",
            "k_na_selectivity": "K⁺/Na⁺ selectivity coefficient and uptake comparison",
            "k_mg_selectivity": "K⁺/Mg²⁺ selectivity coefficient and uptake comparison",
            "k_ca_selectivity": "K⁺/Ca²⁺ selectivity coefficient and uptake comparison",
            "regeneration_efficiency": ">50–80% K⁺ recovery target after desorption",
            "cycling_durability": ">80% capacity retention after 10 cycles for early screening",
            "scaling_fouling_resistance": "stable capacity under repeated high-salinity brine exposure",
            "real_brine_testing": "performance in authentic mineral, seawater, or potash brine samples",
            "product_purity_analysis": "recovered potassium salt composition by ICP-OES or ion chromatography",
            "leaching_safety_and_mechanical_stability": "binder, silica, resin, and additive leaching plus wet cycling durability"
        },
        
        "characterization_methods": ["SEM/EDS", "XRD", "FTIR", "ICP-OES", "BET", "Ion chromatography", "Zeta potential"],
        
        "safety_tests": [
            "Leaching analysis (silica, binder, ion-exchange resin)",
            "Real brine compatibility testing",
            "Product purity analysis (ICP-OES/Ion chromatography)",
            "Cycling durability and scaling resistance"
        ],
        
        "processing_method": [
            "1. Powder Preparation:",
            "   - If ion-exchange resin base: activate resin according to manufacturer protocol.",
            "   - If silica-based: blend porous silica with functional group precursors (amine groups, phosphate groups, etc.).",
            "   - If other mineral base: grind and sieve to uniform particle size (0.5-2 mm).",
            "",
            "2. Functionalization (if required):",
            "   - Add selective functional groups (crown ethers, imprinted polymers, or ion-exchange sites) for K+ preference.",
            "   - Perform wet impregnation or surface modification if using silica or carbon base.",
            "   - Aim for high K+/Na+ and K+/Mg2+, K+/Ca2+ selectivity.",
            "",
            "3. Binder and Pelletization:",
            "   - Add polymer or biopolymer binder to facilitate cohesion and mechanical strength.",
            "   - Form uniform pellets or beads (2-6 mm diameter) suitable for packed-bed operation.",
            "   - Use extrusion or controlled granulation for size uniformity.",
            "",
            "4. Drying:",
            "   - Dry at 40-60 C for 12-24 hours or at higher temperature if thermally stable.",
            "   - Ensure moisture <5% to prevent swelling and irreversible pore collapse.",
            "",
            "5. Conditioning:",
            "   - Soak pellets in concentrated brine solution matching target source (seawater, mineral brine, potash brine).",
            "   - Allow 24-48 hours for saturation equilibration.",
            "   - Drain and store in dry conditions until use.",
            "",
            "6. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact functionalization method, selectivity achievement, binder ratio, and conditioning parameters must be optimized experimentally.",
            "   - No commercial K+ recovery or product purity claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven potassium recovery performance, ion selectivity, brine compatibility, regeneration efficiency, product purity, environmental safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, real-brine testing, ion-selectivity analysis, regeneration studies, scaling/fouling assessment, leaching analysis, and consultation with qualified materials engineers, water-treatment specialists, and mineral-processing experts. This report is for research and development guidance only."
    },
    
    "adsorbent_heavy_metals": {
        "normalized_category_name": "adsorbent_heavy_metals",
        "display_name": "Heavy Metal Adsorbent",
        "priority": 60,
        "aliases": ["metal adsorbent", "toxic metal removal", "heavy-metal sorbent"],
        
        "priority_keywords": [
            "heavy metals", "heavy metal", "lead", "cadmium", "arsenic", "chromium",
            "Pb", "Cd", "As", "Cr", "toxic metal removal",
            "metal ion adsorption", "wastewater adsorption", "modified biochar",
            "iron oxide nanoparticles", "metal ion removal", "leaching safety",
            "adsorbent heavy metals", "metal adsorbent", "metal sorbent"
        ],
        
        "default_composition": [
            {"component": "Modified biochar or activated carbon", "ratio": 0.35},
            {"component": "Porous silica or silica gel", "ratio": 0.25},
            {"component": "Iron oxide nanoparticles or iron hydroxide", "ratio": 0.20},
            {"component": "Bentonite clay or alumina stabilizer", "ratio": 0.10},
            {"component": "Natural polymer or biopolymer binder", "ratio": 0.10},
        ],
        
        "category_specific_parameters": {
            "target_ions": "Pb²⁺, Cd²⁺, As³⁺/As⁵⁺, Cr³⁺/Cr⁶⁺",
            "initial_metal_concentration": "1–100 mg/L for screening",
            "ph_working_range": "3–9",
            "contact_time": "30–240 minutes",
            "adsorbent_dosage": "0.5–5 g/L",
            "competing_ions": "Ca²⁺, Mg²⁺, Na⁺, Cl⁻, SO₄²⁻, nitrate",
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
            "competing_ion_selectivity": "metal removal in presence of Ca²⁺, Mg²⁺, Na⁺ interference",
            "multi_metal_performance": "simultaneous Pb, Cd, As, Cr removal efficiency",
            "regeneration_efficiency": "% metal recovered after acid, base, or chelating-agent desorption",
            "cycling_durability": "capacity retention after 5–10 adsorption/desorption cycles",
            "leaching_safety": "Fe, silica, binder, and additive leaching by ICP-OES; pH and conductivity of eluates",
            "treated_water_quality": "residual Pb, Cd, As, Cr by ICP-OES; comparison to drinking-water standards",
            "real_wastewater_testing": "performance in synthetic and authentic industrial or mine wastewater",
            "ecotoxicity_assessment": "toxicity of treated water and spent adsorbent disposal pathway"
        },
        
        "characterization_methods": ["SEM/EDS", "XRD", "FTIR", "BET", "ICP-OES", "ICP-MS", "Zeta potential"],
        
        "safety_tests": [
            "Multi-metal removal efficiency (ICP-OES)",
            "Leaching analysis (Fe, silica, binder)",
            "Treated water quality (ICP-OES for residual metals)",
            "Ecotoxicity assessment",
            "Cycling durability and regeneration"
        ],
        
        "processing_method": [
            "1. Powder Mixing:",
            "   - Blend adsorbent base (activated carbon, biochar, iron oxide, or zeolite) with inorganic additives.",
            "   - Incorporate functional group precursors if enhanced binding is needed (thiol groups, phosphate groups, etc.).",
            "   - Mix thoroughly to ensure homogeneous composition.",
            "",
            "2. Binder Addition and Pelletization:",
            "   - Add polymer or silica binder (wet mixing) to create cohesive paste.",
            "   - Extrude or granulate into uniform pellets (1-8 mm diameter depending on application).",
            "   - Ensure pellets are hard enough to withstand operational shear forces.",
            "",
            "3. Drying:",
            "   - Air-dry at ambient temperature or gentle heat (40-60 C) for 12-24 hours.",
            "   - Target moisture content <5% to prevent microbe growth and pore collapse.",
            "",
            "4. Activation:",
            "   - Perform light thermal activation at 100-150 C for 2-4 hours to open pores and remove moisture.",
            "   - Optional: acidic or basic pre-wash to establish optimal functional group ionization.",
            "",
            "5. Leaching Pre-Wash:",
            "   - Wash adsorbent pellets with deionized water or dilute acid/base (depending on material) 2-3 times.",
            "   - Each wash: 30-60 minutes.",
            "   - Remove loosely bound fines and binder residues.",
            "   - Save final wash water for baseline metal concentration analysis.",
            "",
            "6. pH and Ionic Strength Conditioning:",
            "   - If targeted for acidic wastewater: brief soak in acidified water.",
            "   - If targeted for neutral/alkaline wastewater: condition with neutral/alkaline solution.",
            "   - This pre-equilibrates the adsorbent to the target operating pH.",
            "",
            "7. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact binder ratio, drying/activation temperature, pellet size, and pH conditioning must be optimized experimentally.",
            "   - No commercial metal-removal performance or treated-water safety claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven heavy-metal removal performance, adsorption selectivity, regeneration efficiency, treated-water safety, environmental safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, real-wastewater testing, metal-ion analysis, leaching studies, regeneration testing, toxicity/ecotoxicity assessment, safe-disposal evaluation, and consultation with qualified materials engineers, water-treatment specialists, and environmental/regulatory experts. This report is for research and development guidance only."
    },
    
    "co2_capture_material": {
        "normalized_category_name": "co2_capture_material",
        "display_name": "Carbon Dioxide Capture Material",
        "priority": 5,
        "aliases": ["CO2 capture", "carbon capture", "carbon dioxide capture", "CO2 adsorbent"],
        
        "priority_keywords": [
            "CO2 capture", "carbon capture", "carbon dioxide capture", "CO2", "CO₂",
            "amine-functionalized", "amine-functionalized silica", "adsorbent CO2",
            "flue gas", "direct air capture", "DAC", "CO2 uptake", "CO2/N2 selectivity",
            "regeneration energy", "amine loss", "cyclic performance",
            "amine stability", "humidity tolerance", "water vapor selectivity"
        ],
        
        "default_composition": [
            {"component": "Activated carbon", "ratio": 0.35},
            {"component": "Amine-functionalized silica", "ratio": 0.30},
            {"component": "Porous mineral filler (zeolite, clay, or alumina)", "ratio": 0.20},
            {"component": "Polymer binder", "ratio": 0.10},
            {"component": "Moisture-control or stabilizing additive", "ratio": 0.05},
        ],
        
        "category_specific_parameters": {
            "capture_source": "Direct air capture (DAC), indoor air, or flue gas",
            "co2_concentration": "400 ppm for air; 5–15% for flue gas screening",
            "co2_uptake_capacity": "mmol CO₂/g adsorbent or mg CO₂/g material",
            "operating_temperature": "25–60°C for adsorption screening",
            "operating_pressure": "1 bar unless pressure-swing testing is specified",
            "relative_humidity_range": "Dry gas and humid gas testing conditions",
            "selectivity_target": "CO₂/N₂ and CO₂/H₂O selectivity ratios",
            "regeneration_temperature": "60–120°C, preferably low-grade heat",
            "regeneration_method": "Temperature swing, vacuum swing, or combined TVSA",
            "regeneration_energy": "kWh/kg CO₂ recovered",
            "amine_loss_test": "Amine degradation, volatilization, or leaching after cycling",
            "cycling_target": "50–100 adsorption/desorption cycles",
            "breakthrough_test": "Dynamic column breakthrough curve under defined gas flow"
        },
        
        "validation_plan": {
            "co2_uptake_capacity": "Gravimetric, volumetric, or breakthrough testing",
            "co2_n2_selectivity": "Breakthrough curves or isotherm-based selectivity calculation",
            "humidity_tolerance": "Water-vapor competition and humidity effects on CO₂ uptake",
            "adsorption_desorption_kinetics": "Time to saturation and release profiles",
            "regeneration_energy_measurement": "Thermal input quantification per cycle",
            "amine_loss_or_degradation": "FTIR, TGA-MS, or leachate analysis post-cycling",
            "cycling_durability": "CO₂ uptake retention over 50–100 cycles",
            "thermal_stability": "TGA/DSC analysis of decomposition temperature and stability",
            "bet_surface_area_pore_size": "N₂ or CO₂ adsorption isotherms",
            "ftir_xps_confirmation": "FTIR or XPS to confirm amine functionalization",
            "sem_morphology": "SEM imaging of structural integrity and surface changes",
            "flue_gas_or_air_testing": "Simulated or real gas-mixture breakthrough testing",
            "safety_review": "Amine emissions, dust generation, and spent sorbent handling"
        },
        
        "characterization_methods": [
            "Thermogravimetric Analysis (TGA)",
            "Differential Scanning Calorimetry (DSC)",
            "Fourier Transform Infrared Spectroscopy (FTIR)",
            "X-ray Photoelectron Spectroscopy (XPS)",
            "Scanning Electron Microscopy (SEM)",
            "Energy Dispersive X-ray (EDX)",
            "Brunauer–Emmett–Teller (BET)",
            "Barrett–Joyner–Halenda (BJH) Pore Analysis",
            "Gas Chromatography (GC)",
            "ICP-OES (for amine residues)"
        ],
        
        "safety_tests": [
            "Amine volatilization and degradation",
            "Dust generation and inhalation risk",
            "Thermal stability and decomposition products",
            "Spent sorbent disposal and environmental impact",
            "Leachate analysis for amine residues"
        ],
        
        "processing_method": [
            "1. Base Sorbent Preparation:",
            "   - If silica-based: prepare mesoporous silica with high surface area (typically >500 m2/g).",
            "   - If resin-based: use high-quality polymer resin with good thermal and chemical stability.",
            "   - Ensure particles are uniform (1-3 mm diameter pellets or beads).",
            "",
            "2. Amine Impregnation or Functionalization:",
            "   - Impregnate sorbent with primary amine (MEA, AMP) or blend of amines.",
            "   - Load target: 3-8 mmol amine per gram sorbent.",
            "   - Use wet incipient impregnation method for even distribution.",
            "   - Allow impregnation solution to soak for 2-4 hours under mild stirring.",
            "",
            "3. Drying:",
            "   - Remove excess liquid by filtration.",
            "   - Air-dry at ambient temperature for 12 hours or gentle heat (40-60 C) for 6-8 hours.",
            "   - Target residual moisture <5%.",
            "   - Alternatively, use rotary evaporation or vacuum drying for faster moisture removal.",
            "",
            "4. Thermal Activation (if applicable):",
            "   - Low-temperature thermal treatment at 80-120 C for 1-2 hours to remove residual volatiles.",
            "   - Do NOT over-heat; excessive temperature can degrade amine and reduce capacity.",
            "   - Cool to room temperature before cycling preconditioning.",
            "",
            "5. Cycling Preconditioning:",
            "   - Perform 3-5 simulated adsorption/desorption cycles at lab scale (small fixed bed or batch).",
            "   - Adsorption: expose to simulated flue gas or CO2/N2 mixture at target conditions.",
            "   - Desorption: regenerate with heat (60-100 C) or vacuum, or chemical desorption as designed.",
            "   - Document CO2 capacity and regeneration efficiency to establish baseline.",
            "",
            "6. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact amine loading, impregnation method, drying temperature, and cycling protocol must be optimized experimentally.",
            "   - No commercial CO2 capture performance or amine stability claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven CO₂ capture capacity, CO₂/N₂ selectivity, humidity tolerance, regeneration efficiency, amine stability, environmental safety, regulatory compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, gas-mixture testing, breakthrough analysis, regeneration-energy measurement, amine-loss assessment, cycling durability testing, and consultation with qualified materials engineers, carbon-capture specialists, and environmental/regulatory experts. This report is for research and development guidance only."
    },
    
    "thermal_insulation_composite": {
        "normalized_category_name": "thermal_insulation_composite",
        "display_name": "Thermal Insulation Composite",
        "priority": 6,
        "aliases": ["insulation material", "thermal insulation", "building insulation", "fire-safe insulation"],
        
        "priority_keywords": [
            "thermal insulation", "thermal insulation composite", "insulation composite",
            "heat transfer", "thermal conductivity", "reduce heat transfer",
            "compressive strength", "flexural strength", "mechanical strength",
            "flame response", "fire-safe", "fire safety", "fire-resistant",
            "indoor air safety", "indoor air quality", "formaldehyde-free",
            "aging stability", "moisture resistance", "water absorption",
            "building insulation", "lightweight insulation", "low-density",
            "thermal stability", "temperature resistance", "fire rating",
            "smoke generation", "flame spread", "building material"
        ],
        
        "default_composition": [
            {"component": "Lightweight porous fiber (fiberglass, mineral wool, or cellulose)", "ratio": 0.50},
            {"component": "Foam matrix (phenolic, polyurethane, or aerogel)", "ratio": 0.30},
            {"component": "Inorganic stabilizer or clay", "ratio": 0.10},
            {"component": "Moisture barrier or hydrophobic agent", "ratio": 0.05},
            {"component": "Flame-retardant additive (mineral-based)", "ratio": 0.05},
        ],
        
        "category_specific_parameters": {
            "thermal_conductivity_target": "W/(m·K) at 25°C and 40°C mean temperature",
            "density": "kg/m³ for lightweight classification",
            "compressive_strength": "kPa at 10% and 25% deformation",
            "flexural_strength": "kPa for structural integrity assessment",
            "water_absorption": "% by mass after 24-hour immersion",
            "water_vapor_permeability": "g/(m²·day·Pa) for vapor-control assessment",
            "flame_response": "Flame spread index, smoke development, heat release rate",
            "fire_rating": "Class A, B, C, or performance-based rating (e.g., ASTM E84)",
            "operating_temperature_range": "°C for service conditions",
            "aging_stability": "Thermal conductivity retention after 500-hour heat aging at elevated temperature",
            "formaldehyde_emission": "ppm or ppb for indoor air safety",
            "odor_volatile_compounds": "Volatile organic compound (VOC) profile",
            "installation_safety": "Fiber release during installation and handling protocols"
        },
        
        "validation_plan": {
            "thermal_conductivity_measurement": "ASTM C518 (steady-state) or ASTM C1114 (dynamic) at defined mean temperatures",
            "density_and_porosity": "Weight per unit volume and pore structure characterization",
            "compressive_strength": "ASTM D1621 at specified deformation rates",
            "flexural_strength": "ASTM C203 or equivalent for composite rigidity",
            "water_absorption_and_retention": "ASTM C1104 or C272 immersion testing",
            "water_vapor_transmission": "ASTM E96 cup method for vapor-control rating",
            "flame_and_smoke_performance": "ASTM E84 (Tunnel test) or ISO 5660-1 (cone calorimetry)",
            "fire_rating_certification": "Third-party fire-rating testing per building code requirements",
            "thermal_aging_stability": "Thermal conductivity before and after 500-hour aging protocol",
            "formaldehyde_emission_testing": "ASTM D6007 or equivalent chamber testing for VOC profile",
            "fibrous_material_release": "Fiber length distribution, airborne fiber count, and migration assessment",
            "mechanical_durability": "Compression and flexural strength retention after thermal cycling",
            "freeze_thaw_durability": "Performance retention after freeze-thaw cycles if cold-service application",
            "characterization_methods": ["SEM", "TGA", "DSC", "FTIR", "Mechanical testing"]
        },
        
        "characterization_methods": [
            "Scanning Electron Microscopy (SEM)",
            "Thermogravimetric Analysis (TGA)",
            "Differential Scanning Calorimetry (DSC)",
            "Fourier Transform Infrared Spectroscopy (FTIR)",
            "Mechanical Testing (ASTM D1621, C203)",
            "Thermal Conductivity Analysis (ASTM C518, C1114)",
            "Cone Calorimetry (ISO 5660-1)",
            "Gas Chromatography-Mass Spectrometry (GC-MS) for VOC"
        ],
        
        "safety_tests": [
            "Flame spread and smoke development (ASTM E84)",
            "Heat release rate (cone calorimetry ISO 5660-1)",
            "Formaldehyde and VOC emissions (chamber testing)",
            "Fiber release and inhalation risk assessment",
            "Thermal stability and decomposition analysis",
            "Water resistance and moisture management"
        ],
        
        "processing_method": [
            "1. Dry Blending:",
            "   - Mix insulation fibers or powder (glass wool, stone wool, or cellulose) with binder precursor in dry state.",
            "   - Add fire-retardant additives if required.",
            "   - Incorporate density-control agents (lightweight fillers, perlite, or expanded clay) for thermal efficiency.",
            "   - Ensure uniform distribution.",
            "",
            "2. Binder Impregnation:",
            "   - Add phenol-formaldehyde, polyurethane, or bio-based binder in controlled amount (typically 5-15 wt%).",
            "   - Wet-mix until fibers or particles are uniformly coated and cohesive.",
            "   - Maintain fiber structure; avoid excessive compaction.",
            "",
            "3. Forming and Molding:",
            "   - Pour or spread binder-impregnated mixture onto mold or conveyor.",
            "   - Compress lightly to achieve target density (30-150 kg/m3 depending on application).",
            "   - Form into boards, mats, or blocks of desired thickness (25-100 mm).",
            "   - Use mechanical pressing for controlled density; avoid over-pressing (reduces insulation).",
            "",
            "4. Pressing and Consolidation:",
            "   - Apply controlled pressure to achieve target density and thickness uniformity.",
            "   - Duration: 5-30 minutes depending on binder and product size.",
            "   - Release pressure carefully to avoid damage.",
            "",
            "5. Curing:",
            "   - Thermal cure at 80-180 C depending on binder type (phenolic, polyurethane, or natural resin).",
            "   - Duration: 1-8 hours for full crosslinking.",
            "   - Ramp heating rate slowly (1-3 C/min) to avoid rapid volatile release and cracking.",
            "   - Monitor exhaust for safety (formaldehyde or isocyanate fumes if applicable).",
            "",
            "6. Conditioning and Stabilization:",
            "   - Allow finished product to cool to room temperature in a well-ventilated area.",
            "   - Store in dry conditions for 24-48 hours before testing or use.",
            "   - Optional: mild post-cure at elevated temperature to drive off residual volatiles.",
            "",
            "7. Quality Control:",
            "   - Check thermal conductivity and density uniformity.",
            "   - Verify dimensional stability (shrinkage <5%).",
            "   - Test compressive strength and mechanical durability.",
            "   - Confirm fire performance and off-gassing profile.",
            "",
            "8. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance.",
            "   - Exact fiber/particle type, binder percentage, pressing pressure, curing temperature, and duration must be optimized experimentally.",
            "   - No commercial thermal insulation, fire-safety, or mechanical property claim should be made before validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven thermal insulation performance, fire safety, indoor air safety, mechanical durability, thermal stability, flame-spread rating, smoke-generation characteristics, formaldehyde/VOC emissions, fiber-release risk, long-term aging behavior, code compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, thermal-conductivity testing, mechanical-strength testing, flame and smoke testing per ASTM/ISO standards, formaldehyde/VOC emission analysis, fiber-release assessment, third-party fire-rating certification where required by building code, thermal-aging studies, and consultation with qualified materials engineers, building scientists, fire-safety specialists, and indoor-air-quality experts. This report is for research and development guidance only."
    },
    
    "self_cleaning_building_coating": {
        "normalized_category_name": "self_cleaning_building_coating",
        "display_name": "Self-Cleaning Building Coating",
        "priority": 7,
        "aliases": ["self-cleaning exterior coating", "photocatalytic building coating", "dirt-degrading coating", "exterior self-cleaning coating"],
        
        "priority_keywords": [
            "self-cleaning", "self cleaning", "self-cleaning coating", "exterior coating",
            "building coating", "facade coating", "photocatalytic nanoparticles",
            "photocatalytic dirt degradation", "surface organic dirt", "sunlight degradation",
            "dust accumulation", "UV aging", "adhesion", "abrasion resistance",
            "color stability", "weather resistance", "algae resistance", "biofilm resistance",
            "hydrophobic coating", "water repellent", "outdoor durability", "weathering",
            "building material coating", "dirt-resistant", "outdoor facade"
        ],
        
        "default_composition": [
            {"component": "TiO2 or other photocatalyst (for dirt degradation)", "ratio": 0.12},
            {"component": "Hydrophobic polymer or silane binder", "ratio": 0.25},
            {"component": "Silica nanoparticles (for hydrophobicity and durability)", "ratio": 0.15},
            {"component": "UV absorber or stabilizer (for color and weathering resistance)", "ratio": 0.08},
            {"component": "Adhesion promoter and hardener", "ratio": 0.20},
            {"component": "Pigments and extenders", "ratio": 0.20},
        ],
        
        "category_specific_parameters": {
            "substrate_type": "Concrete, ceramic tile, stucco, painted drywall, or composite building materials",
            "coating_thickness": "50–200 micrometers for exterior application",
            "dry_time": "Hours to days depending on temperature and humidity",
            "water_contact_angle": ">110° for hydrophobic (self-cleaning) behavior",
            "adhesion_to_substrate": "ASTM D3359 cross-hatch adhesion rating (4B or 5B preferred)",
            "uv_resistance_target": "Color change <5 ΔE units after 500 hours UV exposure (ASTM G154)",
            "dirt_self_cleaning_efficiency": "% area cleaned by rainfall and UV exposure over 6 months",
            "weathering_durability": "Gloss retention and color stability after outdoor exposure",
            "abrasion_resistance": "Mass loss <10 mg after 1000 cycles (ASTM D6290)",
            "algae_biofilm_resistance": "Growth inhibition or clean appearance after exposure to outdoor spores"
        },
        
        "validation_plan": {
            "substrate_adhesion_testing": "ASTM D3359 cross-hatch adhesion rating on concrete, ceramic, and painted substrates",
            "water_contact_angle_measurement": "Static and dynamic contact angles; target >110° for hydrophobic self-cleaning",
            "photocatalytic_dirt_degradation": "Organic dirt (e.g., oleic acid staining) degradation under UV or solar light exposure",
            "uv_weathering_resistance": "ASTM G154 or outdoor weathering (500–1000 hours) with gloss and color stability monitoring",
            "water_resistance_and_hydrolytic_stability": "No blistering, peeling, or weakening after 500–1000 hours salt-fog or humidity chamber exposure (ASTM B117, ASTM D2247)",
            "abrasion_resistance": "ASTM D6290 dry abrasion testing with mass loss measurement",
            "dirt_accumulation_and_rainfall_cleaning": "Long-term outdoor exposure (6–12 months) to assess self-cleaning performance in real weather",
            "algae_and_biofilm_resistance": "Growth inhibition or resistance rating under spore exposure and outdoor conditions",
            "coating_durability_after_cleaning": "Adhesion and appearance retained after pressure washing or chemical cleaning",
            "mechanical_durability": "No cracking, peeling, or deterioration after thermal cycling (ASTM C1294) and freeze-thaw (ASTM C1194) testing"
        },
        
        "characterization_methods": [
            "Scanning Electron Microscopy (SEM)",
            "Contact Angle Measurement (goniometer)",
            "UV-Vis Spectroscopy (for photocatalytic activity)",
            "Fourier Transform Infrared Spectroscopy (FTIR)",
            "X-ray Diffraction (XRD)",
            "Accelerated Weathering Testing (ASTM G154)",
            "Salt-Fog Testing (ASTM B117)",
            "Thermal Cycling and Freeze-Thaw Testing",
            "Optical Microscopy (for dirt and biofilm observation)"
        ],
        
        "safety_tests": [
            "VOC emissions and off-gassing",
            "Leaching of coating components into rainwater",
            "Skin and eye irritation (safety data sheet compliance)",
            "Environmental impact of photocatalytic activity and nanoparticle release",
            "Weathering byproduct assessment"
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven self-cleaning performance, dirt-degradation efficiency, weathering durability, adhesion reliability, algae/biofilm resistance, UV stability, abrasion resistance, long-term outdoor performance, code compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, adhesion testing per ASTM D3359, accelerated weathering testing per ASTM G154, water-contact-angle measurement, photocatalytic-dirt-degradation studies, long-term outdoor exposure testing (6–12 months minimum), pressure-wash and chemical-cleaning durability assessment, algae/biofilm-resistance testing, salt-fog and humidity-chamber testing, environmental and health-safety evaluation of nanoparticles and byproducts, and consultation with qualified coatings engineers, building material specialists, and environmental/regulatory experts. This report is for research and development guidance only.",
        
        "processing_method": [
            "1. Surface Preparation:",
            "   - Clean all surfaces (glass, ceramic, or polymer substrate) from dust, contaminants, and loose particles.",
            "   - Remove old or weak coatings.",
            "   - Dry substrate thoroughly before application.",
            "",
            "2. Powder Pre-Mix (if powder-based formulation):",
            "   - Pre-mix photocatalytic powder (TiO2 or alternative) with filler.",
            "   - Add UV stabilizers and antioxidants.",
            "   - Sieve to remove agglomerates.",
            "",
            "3. Binder and Adhesive Preparation:",
            "   - Prepare compatible binder system (silica-based or polymer).",
            "   - Add adhesion promoters if needed.",
            "   - Add flow control and leveling agents.",
            "",
            "4. Composite Mixing:",
            "   - Slowly incorporate powder into liquid binder under mechanical stirring.",
            "   - Mix until uniform and bubble-free.",
            "   - Adjust viscosity with compatible solvent if required.",
            "",
            "5. Application:",
            "   - Apply by brush, roller, spray, or immersion depending on substrate and viscosity.",
            "   - Ensure even coverage to target thickness.",
            "   - Apply single or multiple coats as design specifies.",
            "",
            "6. Curing and Drying:",
            "   - Allow each coat to dry fully before applying additional coats.",
            "   - Ambient cure: 24-72 hours depending on environmental conditions.",
            "   - Optional thermal curing at low temperature (if binder is heat-curable).",
            "   - Avoid moisture and direct water exposure during early curing.",
            "",
            "7. Quality Control and Testing:",
            "   - Check adhesion to substrate (ASTM D3359 cross-hatch or pull-off test).",
            "   - Verify coating continuity and absence of pinholes.",
            "   - Measure contact angle (hydrophilicity/oleophobicity).",
            "   - Confirm photocatalytic activity and self-cleaning performance.",
            "   - Test weathering durability (salt fog, UV exposure).",
            "",
            "8. Evidence Boundary:",
            "   - This is a planning-level fabrication route for research guidance only.",
            "   - Exact mixing parameters, curing time, and application thickness must be optimized experimentally.",
            "   - No commercial performance claim should be made before rigorous testing and validation."
        ]
    },
    
    "roof_waterproofing_thermal_insulation_coating": {
        "normalized_category_name": "roof_waterproofing_thermal_insulation_coating",
        "display_name": "Roof Waterproofing & Thermal Insulation Coating",
        "priority": 8,
        "aliases": ["roof coating", "waterproofing coating", "thermal reflective coating", "cool roof"],
        
        "priority_keywords": [
            # Roof-specific keywords
            "roof coating", "roof waterproofing", "roof-applied", "rooftop", "concrete roof", "concrete rooftop",
            "roof application", "applied to roof",
            
            # Waterproofing keywords  
            "waterproofing", "water leakage", "rainwater leakage", "water resistance",
            "water-resistant", "water-resistant coating",
            
            # Thermal performance keywords
            "thermal insulation", "thermal insulation coating", "thermal reflectivity",
            "solar reflectance", "solar heat gain", "thermal reflective coating", "cool roof",
            "temperature reduction",
            
            # Material property keywords
            "UV resistance", "UV aging", "weather resistance", "crack bridging",
            "adhesion", "adhesion to concrete",
            
            # Functional keywords
            "cool roof coating", "weather-resistant binder", "thermal reflective"
        ],
        
        "default_composition": [
            {"component": "Titanium dioxide or calcium carbonate reflective filler", "ratio": 0.30},
            {"component": "Hydrophobic porous silica or treated perlite", "ratio": 0.25},
            {"component": "Hollow microspheres or lightweight aggregate", "ratio": 0.15},
            {"component": "Weather-resistant acrylic or styrene-acrylic binder", "ratio": 0.20},
            {"component": "SBR or EVA elastomeric waterproofing additive", "ratio": 0.05},
            {"component": "Silicone/silane water-repellent additive or UV stabilizer", "ratio": 0.05},
        ],
        
        "category_specific_parameters": {
            "coating_form": "Liquid emulsion or water-based polymer dispersion",
            "coverage_rate": "0.5–1.5 mm per coat; typically 2 coats minimum",
            "solar_reflectance_target": "0.65–0.85 (cool roof standard requirement)",
            "thermal_emittance": "0.75–0.95",
            "water_resistance": "No water ponding or beading failure after 168-hour immersion",
            "crack_bridging_capability": "Bridge hairline cracks up to 2–3 mm",
            "adhesion_to_concrete": "Minimum adhesion per ASTM D3359 (no delamination)",
            "tensile_strength_after_curing": "Minimum elongation >200% for flexibility",
            "uv_resistance_durability": "Retain color and gloss after 1000+ hours accelerated UV exposure",
            "salt_fog_resistance": "Withstand salt-fog chamber testing (ASTM B117) for 1000+ hours",
            "temperature_reduction": "Measured roof surface temperature reduction vs. bare concrete"
        },
        
        "validation_plan": {
            "solar_reflectance_measurement": "ASTM C1549 or equivalent; target ≥0.65–0.85",
            "thermal_emittance_measurement": "ASTM C1371 or equivalent; target ≥0.75",
            "adhesion_testing": "ASTM D3359 (cross-hatch method) or ASTM D4541 (pull-off adhesion)",
            "water_resistance_and_ponding": "168-hour immersion; no water beading or film failure",
            "crack_bridging_capability": "Bridge pre-cut hairline cracks (2–3 mm) without re-cracking",
            "coating_thickness_uniformity": "Wet and dry film thickness measurement; confirm 0.5–1.5 mm per coat",
            "tensile_strength_and_elongation": "ASTM D412 or equivalent; minimum elongation >200%",
            "uv_and_weathering_durability": "ASTM G154 accelerated UV chamber (1000 hours) and salt-fog testing (ASTM B117, 1000 hours)",
            "water_absorption": "ASTM D2247 or equivalent; minimal water uptake",
            "thermal_performance_field_test": "Infrared thermography; measure roof surface temperature reduction vs. bare concrete",
            "pollutant_resistance_and_dirt_shedding": "Dirt repellency and cleaning recovery after soiling and rinsing",
            "flexibility_and_elongation": "Cyclic bend test to verify no cracking or adhesion loss"
        },
        
        "characterization_methods": ["SEM/EDS", "XRD (if ceramic fillers)", "FTIR", "Thermography", "Contact angle", "Adhesion pull-off", "Thickness gauge"],
        
        "safety_tests": [
            "Water resistance and ponding durability",
            "Adhesion to concrete substrate",
            "Crack bridging and flexibility",
            "UV and salt-fog weathering durability",
            "Solar reflectance and thermal performance"
        ],
        
        "processing_method": [
            "1. Surface Preparation:",
            "   - Clean the concrete roof surface from dust, oil, loose particles, old weak coating, and standing moisture.",
            "   - Repair visible cracks and damaged areas before coating.",
            "   - Apply only to a dry, stable substrate unless the selected binder allows damp-surface application.",
            "",
            "2. Powder Pre-Mix:",
            "   - Dry blend titanium dioxide or aluminum oxide reflective filler with porous silica, treated expanded perlite, or lightweight insulating filler.",
            "   - Add UV stabilizer powder and fiber reinforcement slowly to avoid clumping.",
            "   - Use hydrophobic or surface-treated insulating fillers where possible to reduce water absorption.",
            "",
            "3. Liquid Binder Preparation:",
            "   - Prepare the acrylic or styrene-acrylic binder phase.",
            "   - Add elastomeric waterproofing additive such as SBR, acrylic elastomer, EVA, silicone, or polyurethane dispersion according to compatibility.",
            "   - Add defoamer, dispersant, and adhesion promoter if available.",
            "",
            "4. Composite Mixing:",
            "   - Slowly add the powder blend into the liquid binder under mechanical mixing until a uniform spreadable coating is obtained.",
            "   - Avoid excessive air bubbles.",
            "   - Adjust viscosity only with compatible water or solvent recommended by the binder supplier.",
            "",
            "5. Application:",
            "   - Apply by roller, brush, trowel, or spray depending on viscosity.",
            "   - Use at least two coats.",
            "   - Apply the first coat as a sealing/adhesion layer and the second coat as the waterproof reflective insulation layer.",
            "   - Apply the second coat after the first coat has dried sufficiently.",
            "",
            "6. Drying and Curing:",
            "   - Allow each coat to dry fully before applying the next layer.",
            "   - Suggested ambient curing is 24–72 hours depending on temperature, humidity, coating thickness, and binder supplier guidance.",
            "   - Avoid application during rain, wet surfaces, or extreme midday heat that may cause rapid drying and cracking.",
            "",
            "7. Quality Control:",
            "   - Check coating continuity, pinholes, adhesion to concrete, crack coverage, dry film thickness, surface defects, and water ponding resistance.",
            "   - Measure roof surface temperature reduction compared with uncoated concrete.",
            "",
            "8. Evidence Boundary:",
            "   - This is a planning-level processing route.",
            "   - Exact mixing speed, viscosity, coat thickness, curing time, and additive levels must be optimized experimentally.",
            "   - No waterproofing, insulation, or commercial claim should be made before laboratory and rooftop validation."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven waterproofing performance, thermal reflectivity, weather resistance, adhesion reliability, durability, code compliance, or commercial readiness. All recommendations are CONDITIONAL upon rigorous laboratory validation, solar-reflectance measurement, thermal-performance testing, adhesion testing per ASTM D3359, crack-bridging verification, accelerated weathering testing per ASTM G154, salt-fog testing per ASTM B117, field thermal-performance measurement, and consultation with qualified coatings engineers, roofing specialists, and building material experts. This report is for research and development guidance only."
    },
    
    "sodium_ion_battery_anode_composite": {
        "normalized_category_name": "sodium_ion_battery_anode_composite",
        "display_name": "Sodium-Ion Battery Anode Composite",
        "priority": 9,  # Higher specificity than thermal insulation
        "aliases": ["sodium-ion battery anode", "Na-ion anode", "sodium-ion anode", "battery anode material", "sodium battery electrode"],
        
        "priority_keywords": [
            "sodium-ion battery", "Na-ion", "battery anode", "anode composite", "hard carbon",
            "conductive carbon black", "sodium-compatible binder", "sodium storage capacity",
            "specific capacity", "coulombic efficiency", "cycling stability", "rate capability",
            "mechanical integrity", "irreversible capacity loss", "electrode swelling",
            "impedance", "electrode", "SEI", "half-cell", "full-cell",
            "sodium battery", "Na+ storage", "anode material"
        ],
        
        "default_composition": [
            {"component": "Hard carbon active material", "ratio": 0.80},
            {"component": "Conductive carbon black", "ratio": 0.08},
            {"component": "Sodium-compatible binder (CMC/SBR, PVDF, sodium alginate, or PAA)", "ratio": 0.07},
            {"component": "Inorganic stabilizer (alumina, titania, phosphate additive, or ceramic nanoparticle)", "ratio": 0.03},
            {"component": "Porosity modifier / pore-forming additive", "ratio": 0.02},
        ],
        
        "category_specific_parameters": {
            "electrode_type": "Sodium-ion battery anode",
            "active_material": "Hard carbon",
            "conductive_additive": "Carbon black, graphene, CNT, or conductive carbon",
            "binder_type": "CMC/SBR, PVDF, sodium alginate, PAA, or compatible binder",
            "active_material_loading": "mg/cm²",
            "electrode_thickness": "µm",
            "porosity": "%",
            "electrolyte_compatibility": "Carbonate or ether-based sodium-ion electrolyte",
            "specific_capacity_target": "mAh/g at defined current density",
            "initial_coulombic_efficiency": "%",
            "cycling_stability": "Capacity retention (%) after defined cycles",
            "rate_capability": "Capacity retention at different C-rates",
            "impedance": "EIS resistance before/after cycling",
            "electrode_swelling": "Thickness or volume change after cycling",
            "safety_thermal_stability": "DSC/TGA or abuse-risk screening"
        },
        
        "validation_plan": {
            "half_cell_testing": "Half-cell testing vs. Na/Na+ reference electrode",
            "galvanostatic_charging_discharging": "GCPL cycling per standardized protocol",
            "specific_capacity_measurement": "Specific capacity in mAh/g at defined current density",
            "initial_coulombic_efficiency": "First-cycle efficiency assessment",
            "cycling_durability": "Capacity retention over 100–500 cycles",
            "rate_performance": "Multiple C-rates (0.1C, 0.5C, 1C, 2C, 5C, 10C)",
            "electrochemical_impedance_spectroscopy": "EIS before and after cycling (Nyquist plots)",
            "cyclic_voltammetry": "CV analysis for reversibility assessment",
            "electrode_swelling_measurement": "Volumetric change via dilatometry or microscopy",
            "mechanical_durability_sem": "SEM morphology before/after cycling (particle integrity)",
            "xrd_raman_characterization": "XRD/Raman spectroscopy for hard carbon structure",
            "bet_surface_area": "BET surface area and pore-size distribution",
            "sei_layer_analysis": "XPS or Raman spectroscopy for SEI composition and evolution",
            "compositional_analysis_icp": "Elemental composition by ICP-OES if binder degradation suspected",
            "thermal_stability_tga": "Thermal decomposition profile (TGA) of anode composite",
            "electrolyte_compatibility": "Compatibility with sodium-ion carbonate and ether electrolytes",
            "half_cell_vs_full_cell_performance": "Full-cell testing with suitable sodium cathode for practical performance"
        },
        
        "characterization_methods": [
            "Galvanostatic Charge/Discharge (GCPL)",
            "Electrochemical Impedance Spectroscopy (EIS)",
            "Cyclic Voltammetry (CV)",
            "Scanning Electron Microscopy (SEM)",
            "X-ray Photoelectron Spectroscopy (XPS)",
            "X-ray Diffraction (XRD)",
            "Raman Spectroscopy",
            "Thermogravimetric Analysis (TGA)",
            "Brunauer–Emmett–Teller (BET)",
            "ICP-OES (elemental composition)"
        ],
        
        "safety_tests": [
            "Specific capacity and coulombic efficiency",
            "Cycling durability and capacity retention",
            "Mechanical integrity after cycling",
            "SEI layer formation and stability",
            "Thermal stability (TGA decomposition)",
            "Electrode swelling and volumetric stability"
        ],
        
        "processing_method": [
            "1. Dry hard carbon and conductive carbon black to remove moisture.",
            "   - Obtain or synthesize hard carbon (from precarbonization of polymers or biomass).",
            "   - Grind to uniform particle size (<10 µm) if not purchased as powder.",
            "   - Dry both hard carbon and carbon black in oven at 80–120°C for 2–4 hours.",
            "",
            "2. Prepare binder solution or dispersion using sodium-ion-compatible binder.",
            "   - Dissolve CMC, SBR, PVDF, sodium alginate, or PAA in compatible solvent.",
            "   - For CMC: DI water; for PVDF: NMP; for SBR: water-based dispersion.",
            "   - Target binder loading: 7–10 wt% of final electrode.",
            "   - Degas to remove air bubbles.",
            "",
            "3. Mix hard carbon, conductive carbon black, inorganic stabilizer, and porosity modifier into slurry.",
            "   - Dry-blend hard carbon (80%), carbon black (8%), stabilizer (3%), modifier (2%).",
            "   - Add dry-blended mixture to binder solution in multiple portions under gentle stirring.",
            "   - Mix thoroughly (planetary mill or high-shear mixer) without over-mixing that damages carbon.",
            "   - Target slurry viscosity: 50–500 cP for casting or coating.",
            "",
            "4. Coat slurry onto suitable current collector.",
            "   - Use copper or aluminum current collector.",
            "   - Apply via doctor blade, slot-die, spray coating, or dip-coating.",
            "   - Target electrode thickness: 50–200 µm (wet).",
            "",
            "5. Dry electrode under controlled temperature or vacuum.",
            "   - Air-dry at room temperature for 30 minutes to 2 hours.",
            "   - Optional: gentle heat at 50–80°C if solvent permits (avoid >80°C).",
            "   - Vacuum dry at 60–80°C for 4–12 hours to remove residual solvent and moisture.",
            "   - Target active material loading: 1–5 mg/cm² after drying.",
            "",
            "6. Calendar to target thickness and porosity.",
            "   - Apply light mechanical pressing if required by design.",
            "   - Avoid over-pressing that reduces porosity or damages structure.",
            "",
            "7. Assemble half-cells in dry-room or glovebox conditions.",
            "   - Avoid air and moisture exposure (Na+ reactivity with H₂O).",
            "   - Use Na metal reference electrode and sodium-ion electrolyte (carbonate or ether).",
            "",
            "8. Perform formation cycling before rate and cycling tests.",
            "   - Formation: 2–5 slow cycles at C/20 to C/10 rate.",
            "   - Allows SEI stabilization and electrode pre-wetting.",
            "",
            "9. Conduct electrochemical characterization per validation plan.",
            "   - Galvanostatic charge/discharge, EIS, CV, and rate-performance testing.",
            "   - Document specific capacity, coulombic efficiency, cycle life, and impedance evolution."
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: All material parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science and electrochemistry knowledge. These parameters DO NOT demonstrate proven specific capacity, coulombic efficiency, cycling stability, rate capability, mechanical durability, thermal stability, safety, regulatory compliance, or commercial readiness for sodium-ion batteries. All recommendations are CONDITIONAL upon rigorous laboratory validation, electrochemical characterization per half-cell and full-cell testing, cycling durability assessment, SEM/XPS analysis of electrode morphology and SEI evolution, thermal-stability analysis, full-cell integration testing, and consultation with qualified materials engineers, battery scientists, electrochemists, and battery-system specialists. This report is for research and development guidance only."
    },
    
    "other_material": {
        "normalized_category_name": "other_material",
        "display_name": "Other (Custom Material)",
        "priority": 999,  # Lowest priority - fallback only
        "aliases": ["custom", "unknown", "generic"],
        
        "priority_keywords": [],  # Matches nothing - fallback only
        
        "default_composition": [],  # No default composition
        
        "category_specific_parameters": {},
        
        "validation_plan": {},
        
        "characterization_methods": [],
        
        "safety_tests": [],
        
        "processing_method": [
            "1. Material Synthesis / Procurement:",
            "   - Obtain or synthesize base materials according to specifications.",
            "   - Verify purity and quality of raw materials if procured externally.",
            "   - Document source, batch number, and certification data.",
            "",
            "2. Preliminary Processing:",
            "   - Apply any necessary pretreatment (drying, grinding, sieving, etc.).",
            "   - Conduct quality control tests on raw materials.",
            "   - Document material properties before processing.",
            "",
            "3. Main Processing / Fabrication Route:",
            "   - Follow the specified synthesis or fabrication method.",
            "   - Monitor critical parameters (temperature, pressure, time, mixing conditions).",
            "   - Record all processing conditions and observations.",
            "",
            "4. Product Formation / Assembly:",
            "   - Consolidate, shape, or assemble components as needed.",
            "   - Apply any post-processing (finishing, coating, annealing, etc.).",
            "   - Ensure product meets dimensional and visual specifications.",
            "",
            "5. Post-Processing and Conditioning:",
            "   - Apply thermal treatment, curing, or aging if required.",
            "   - Perform any necessary washing, solvent exchange, or drying.",
            "   - Condition product under specified environmental conditions.",
            "",
            "6. Quality Assurance and Testing:",
            "   - Conduct characterization tests per category-specific validation plan.",
            "   - Document all test results and compare against targets.",
            "   - Perform safety and regulatory compliance testing.",
            "",
            "7. Final Documentation:",
            "   - Complete processing log with all parameters and observations.",
            "   - Archive samples for future reference and regulatory files.",
            "   - Prepare technical specifications sheet for product.",
            "",
            "NOTE: This is a generic processing template. Actual procedures must be customized based on the specific material type and intended application. Consult qualified materials engineers and follow all relevant safety regulations.",
        ],
        
        "category_specific_disclaimer": "DISCLAIMER: This material does not match a predefined category. All parameters, compositions, and performance targets in this report are AI-generated planning defaults based on materials science knowledge. These parameters DO NOT demonstrate proven performance, commercial readiness, or regulatory compliance. All recommendations are CONDITIONAL upon rigorous laboratory validation and consultation with qualified materials engineers. This report is for research and development guidance only."
    }
}

# Ordered list of categories by priority (for classification)
CATEGORY_PRIORITY_ORDER = [
    "fabric_oil_stain_removal_composite",  # HIGHEST PRIORITY: fabric/laundry stain removal (NEW)
    "roof_waterproofing_thermal_insulation_coating",  # HIGHEST: specific roof coating
    "sodium_ion_battery_anode_composite",  # HIGH: Battery electrode domain guardrail (catches battery anodes before thermal insulation)
    "phosphate_recovery_material",  # HIGH: Check phosphate-specific recovery BEFORE oil/gas (phosphate keywords are more distinctive)
    "oil_gas_produced_water_pretreatment_media",  # HIGH: More specific than desalination pre-treatment for oilfield water
    "desalination_pretreatment_media",  # Check desalination pre-treatment FIRST (before membrane_water_treatment)
    "membrane_water_treatment",
    "co2_capture_material",
    "self_cleaning_building_coating",  # Before thermal insulation (more specific)
    "thermal_insulation_composite",
    "atmospheric_water_harvesting_material",
    "photocatalytic_coating",
    "potassium_brine_separation_material",
    "adsorbent_heavy_metals",  # Lower priority to prevent misclassification
    "other_material",
]

# ============================================================================
# CATEGORY NAME NORMALIZATION FUNCTION
# ============================================================================

def normalize_category_name(category_input: str) -> str:
    """
    Normalize category names and display names to internal normalized names.
    Maps display names, aliases, and variants to internal category keys.
    
    Args:
        category_input: Display name, alias, or normalized name
        
    Returns:
        Normalized internal category name (e.g., "fabric_oil_stain_removal_composite")
    """
    if not category_input:
        return "other_material"
    
    # Create mapping of display names and aliases to normalized names
    name_mapping = {
        # Exact matches
        "fabric_oil_stain_removal_composite": "fabric_oil_stain_removal_composite",
        "Fabric Oil-Stain Removal Composite": "fabric_oil_stain_removal_composite",
        "fabric oil stain removal": "fabric_oil_stain_removal_composite",
        "oil stain removal": "fabric_oil_stain_removal_composite",
        
        "roof_waterproofing_thermal_insulation_coating": "roof_waterproofing_thermal_insulation_coating",
        "Roof Waterproofing & Thermal Insulation Coating": "roof_waterproofing_thermal_insulation_coating",
        "roof waterproofing thermal insulation coating": "roof_waterproofing_thermal_insulation_coating",
        
        "sodium_ion_battery_anode_composite": "sodium_ion_battery_anode_composite",
        "Sodium-Ion Battery Anode Composite": "sodium_ion_battery_anode_composite",
        "sodium ion battery anode": "sodium_ion_battery_anode_composite",
        "sodium-ion anode": "sodium_ion_battery_anode_composite",
        "battery anode composite": "sodium_ion_battery_anode_composite",
        "na-ion anode": "sodium_ion_battery_anode_composite",
        
        "desalination_pretreatment_media": "desalination_pretreatment_media",
        "Desalination Pre-Treatment Media": "desalination_pretreatment_media",
        "desalination pre-treatment": "desalination_pretreatment_media",
        
        "oil_gas_produced_water_pretreatment_media": "oil_gas_produced_water_pretreatment_media",
        "Oil & Gas Produced-Water Pre-Treatment Media": "oil_gas_produced_water_pretreatment_media",
        "oil gas produced water pretreatment": "oil_gas_produced_water_pretreatment_media",
        "produced water pre-treatment": "oil_gas_produced_water_pretreatment_media",
        "oilfield water pre-treatment": "oil_gas_produced_water_pretreatment_media",
        "produced water treatment": "oil_gas_produced_water_pretreatment_media",
        "ADNOC pre-treatment": "oil_gas_produced_water_pretreatment_media",
        
        "self_cleaning_building_coating": "self_cleaning_building_coating",
        "Self-Cleaning Building Coating": "self_cleaning_building_coating",
        "Self-Cleaning Photocatalytic Building Coating": "self_cleaning_building_coating",
        "self-cleaning exterior coating": "self_cleaning_building_coating",
        
        "co2_capture_material": "co2_capture_material",
        "Carbon Dioxide Capture Material": "co2_capture_material",
        "CO2 Capture Material": "co2_capture_material",
        "CO₂ Capture Material": "co2_capture_material",
        "carbon dioxide capture": "co2_capture_material",
        "CO2 capture": "co2_capture_material",
        "co2 capture": "co2_capture_material",
        
        "thermal_insulation_composite": "thermal_insulation_composite",
        "Thermal Insulation Composite": "thermal_insulation_composite",
        "thermal insulation": "thermal_insulation_composite",
        
        "atmospheric_water_harvesting_material": "atmospheric_water_harvesting_material",
        "Atmospheric Water Harvesting Material": "atmospheric_water_harvesting_material",
        "atmospheric water harvesting": "atmospheric_water_harvesting_material",
        "AWH material": "atmospheric_water_harvesting_material",
        
        "membrane_water_treatment": "membrane_water_treatment",
        "Membrane Water Treatment Material": "membrane_water_treatment",
        "membrane water treatment": "membrane_water_treatment",
        "membrane filtration": "membrane_water_treatment",
        
        "adsorbent_heavy_metals": "adsorbent_heavy_metals",
        "Heavy Metal Adsorbent": "adsorbent_heavy_metals",
        "heavy metal adsorbent": "adsorbent_heavy_metals",
        "metal adsorbent": "adsorbent_heavy_metals",
        
        "phosphate_recovery_material": "phosphate_recovery_material",
        "Phosphate Recovery Material": "phosphate_recovery_material",
        "phosphate recovery": "phosphate_recovery_material",
        
        "potassium_brine_separation_material": "potassium_brine_separation_material",
        "Potassium Brine Separation Material": "potassium_brine_separation_material",
        "potassium recovery": "potassium_brine_separation_material",
        "potassium brine separation": "potassium_brine_separation_material",
        
        "photocatalytic_coating": "photocatalytic_coating",
        "Photocatalytic Coating": "photocatalytic_coating",
        "photocatalytic coating": "photocatalytic_coating",
        
        "other_material": "other_material",
        "Other Material": "other_material",
    }
    
    # Try exact match first
    if category_input in name_mapping:
        return name_mapping[category_input]
    
    # Try case-insensitive match
    input_lower = category_input.lower()
    for key, value in name_mapping.items():
        if key.lower() == input_lower:
            return value
    
    # If no match found, check if it's already a valid category key
    if category_input in CATEGORY_REGISTRY:
        return category_input
    
    # Default fallback
    return "other_material"


# ============================================================================
# DOMAIN DETECTION FUNCTIONS (Domain-First Classification)
# ============================================================================

def detect_prompt_domain(user_request: str) -> dict:
    """
    Detect the actual domain of the user request using keyword matching.
    Returns the most likely domain with confidence score and matched keywords.
    
    This runs BEFORE category classification to filter out generic keywords.
    
    Args:
        user_request: The user's material request
        
    Returns:
        {
            "domain": "battery_electrode" | "phosphate_recovery" | ... | "unknown",
            "confidence": 0-100,
            "matched_keywords": ["keyword1", "keyword2", ...],
            "reason": "Explanation of domain detection"
        }
    """
    request_lower = user_request.lower()
    domain_scores = {}
    domain_keywords_matched = {}
    
    # Score each domain based on keyword matches
    for domain, domain_data in DOMAIN_KEYWORDS.items():
        keywords = domain_data["keywords"]
        min_keywords_required = domain_data["min_keywords"]
        
        matched = []
        for keyword in keywords:
            if keyword.lower() in request_lower:
                matched.append(keyword)
        
        if len(matched) >= min_keywords_required:
            # Score based on number of matched keywords
            score = min(100, len(matched) * 15)  # Each keyword adds 15 points, cap at 100
            domain_scores[domain] = score
            domain_keywords_matched[domain] = matched
    
    # Find best match
    if not domain_scores:
        return {
            "domain": "unknown",
            "confidence": 0,
            "matched_keywords": [],
            "reason": "No domain keywords detected"
        }
    
    best_domain = max(domain_scores, key=domain_scores.get)
    best_score = domain_scores[best_domain]
    best_keywords = domain_keywords_matched[best_domain]
    
    return {
        "domain": best_domain,
        "confidence": best_score,
        "matched_keywords": best_keywords,
        "reason": f"Detected {best_domain} domain with {len(best_keywords)} matching keywords"
    }


def validate_domain_category_alignment(prompt_domain: str, selected_category: str) -> dict:
    """
    Validate that the selected category matches the detected domain.
    
    Args:
        prompt_domain: Domain detected from user request (e.g., "battery_electrode")
        selected_category: Category selected by classification (e.g., "sodium_ion_battery_anode_composite")
        
    Returns:
        {
            "aligned": True/False,
            "prompt_domain": "battery_electrode",
            "category_domain": "battery_electrode",
            "reason": "...",
            "blocking_export": False or "Reason why export is blocked"
        }
    """
    # If domain is unknown, allow it (no blocking)
    if prompt_domain == "unknown":
        return {
            "aligned": True,
            "prompt_domain": prompt_domain,
            "category_domain": CATEGORY_TO_DOMAIN.get(selected_category, "unknown"),
            "reason": "Unknown domain - allowing category selection",
            "blocking_export": False
        }
    
    # Get the domain for the selected category
    category_domain = CATEGORY_TO_DOMAIN.get(selected_category, "unknown")
    
    # Check alignment
    aligned = (prompt_domain == category_domain)
    
    if aligned:
        return {
            "aligned": True,
            "prompt_domain": prompt_domain,
            "category_domain": category_domain,
            "reason": f"Domain and category aligned: {prompt_domain}",
            "blocking_export": False
        }
    else:
        return {
            "aligned": False,
            "prompt_domain": prompt_domain,
            "category_domain": category_domain,
            "reason": f"Domain mismatch: prompt is {prompt_domain} but category is {category_domain}",
            "blocking_export": f"Cannot export: request appears to be about {prompt_domain}, but selected category is for {category_domain}"
        }


# ============================================================================
# COMPOSITION VALIDATION SYSTEM (Global Rule)
# ============================================================================
# Substrates, surfaces, and application environments that should NOT be in composition
INVALID_COMPOSITION_ITEMS = {
    # Substrate types
    "substrate", "glass substrate", "ceramic substrate", "polymer substrate",
    "textile substrate", "concrete substrate", "metal substrate",
    # Application surfaces
    "concrete rooftop", "building wall", "roof surface", "exterior wall",
    "textile surface", "fabric surface", "cotton clothing", "apparel",
    # Support objects
    "glass support", "ceramic support", "polymer support",
    "collector tray", "collection vessel", "reactor surface",
    # Water/environment related
    "desalination membrane", "treated water", "feed water", "water matrix",
    "wastewater", "flue gas", "gas stream", "air stream", "exhaust stream",
    # General environment/context
    "treated surface", "application environment", "use environment",
    "operating medium", "contact medium",
}

def validate_composition_components(material_data: dict) -> dict:
    """
    Validate that composition contains only formulation components, not substrates/environments.
    
    Checks for substrate/application object items and returns detailed validation results.
    Does NOT modify the material_data; only reports issues.
    
    Args:
        material_data: Dictionary with 'composition' list
        
    Returns:
        Dictionary with:
        - 'is_valid': bool indicating if composition is valid
        - 'invalid_items': list of invalid component strings found
        - 'message': descriptive message
    """
    if not material_data or "composition" not in material_data:
        return {"is_valid": True, "invalid_items": [], "message": "No composition to validate"}
    
    composition = material_data.get("composition", [])
    invalid_found = []
    
    for item in composition:
        if isinstance(item, dict):
            component = item.get("component", "").lower()
            # Check if component matches any invalid substrate/environment item
            for invalid in INVALID_COMPOSITION_ITEMS:
                if invalid in component:
                    invalid_found.append(item.get("component", "unknown"))
                    break
    
    return {
        "is_valid": len(invalid_found) == 0,
        "invalid_items": invalid_found,
        "message": f"Found {len(invalid_found)} substrate/environment items in composition" if invalid_found else "Composition is valid (no substrates/environments)"
    }

def clean_composition_components(material_data: dict) -> dict:
    """
    Remove substrate/environment items from composition and move them to category-specific parameters.
    
    Args:
        material_data: Dictionary with 'composition' and optionally 'category_specific_parameters'
        
    Returns:
        Modified material_data with cleaned composition
    """
    if not material_data or "composition" not in material_data:
        return material_data
    
    composition = material_data.get("composition", [])
    removed_items = []
    cleaned_composition = []
    
    for item in composition:
        if isinstance(item, dict):
            component = item.get("component", "").lower()
            is_invalid = False
            for invalid in INVALID_COMPOSITION_ITEMS:
                if invalid in component:
                    is_invalid = True
                    removed_items.append(item.get("component", "unknown"))
                    break
            
            if not is_invalid:
                cleaned_composition.append(item)
        else:
            cleaned_composition.append(item)
    
    # Update composition
    material_data["composition"] = cleaned_composition
    
    # Add warning if items were removed
    if removed_items:
        material_data["composition_warning"] = (
            f"Substrate/application objects were removed from composition: {', '.join(removed_items)}. "
            "These items have been categorized in the category-specific parameters section."
        )
    
    return material_data

# ============================================================================
# HIERARCHICAL MATERIAL CLASSIFICATION SYSTEM (4 Levels)
# ============================================================================

# Level 1: Material Families
MATERIAL_FAMILIES = {
    "polymer": {
        "name": "Polymer-based material",
        "keywords": ["polymer", "polyurethane", "PU", "PVDF", "PES", "PSf", "nylon", "polyester", "polyamide", "polysulfone"]
    },
    "ceramic": {
        "name": "Ceramic / oxide material",
        "keywords": ["ceramic", "alumina", "silica", "titania", "TiO2", "SiO2", "Al2O3", "zeolite", "oxide"]
    },
    "carbon": {
        "name": "Carbon-based material",
        "keywords": ["carbon", "activated carbon", "graphene", "carbon nanotubes", "CNT", "biochar", "charcoal"]
    },
    "composite": {
        "name": "Composite material",
        "keywords": ["composite", "hybrid", "mixed-matrix", "MMM", "blend", "nanocomposite"]
    },
    "metal": {
        "name": "Metal / alloy material",
        "keywords": ["metal", "alloy", "copper", "silver", "gold", "aluminum", "steel", "nickel"]
    },
    "bio": {
        "name": "Biomaterial",
        "keywords": ["bio", "biomaterial", "chitosan", "cellulose", "protein", "peptide", "natural"]
    },
    "nano": {
        "name": "Nanomaterial",
        "keywords": ["nano", "nanoparticle", "nanostructure", "quantum dot", "fullerene"]
    },
    "hybrid": {
        "name": "Hybrid organic-inorganic material",
        "keywords": ["hybrid", "organic-inorganic", "MOF", "metal-organic framework", "framework"]
    }
}

# Level 2: Functional Classes
FUNCTIONAL_CLASSES = {
    "adsorbent": {
        "name": "Adsorbent",
        "keywords": ["adsorbent", "adsorbate", "adsorption", "uptake", "sorption", "absorption", "captive"]
    },
    "membrane": {
        "name": "Membrane",
        "keywords": ["membrane", "filtration", "separation", "permeate", "rejection", "flux"]
    },
    "catalyst": {
        "name": "Catalyst",
        "keywords": ["catalyst", "catalysis", "catalytic", "conversion", "reaction rate"]
    },
    "photocatalyst": {
        "name": "Photocatalyst",
        "keywords": ["photocatalyst", "photocatalytic", "photocatalysis", "UV", "visible light"]
    },
    "coating": {
        "name": "Coating",
        "keywords": ["coating", "film", "surface treatment", "layer", "lamination", "deposition"]
    },
    "electrode": {
        "name": "Electrode",
        "keywords": ["electrode", "electrochemical", "anode", "cathode", "electrolyte"]
    },
    "sensor": {
        "name": "Sensor",
        "keywords": ["sensor", "detection", "sensing", "response", "signal"]
    },
    "scaffold": {
        "name": "Scaffold",
        "keywords": ["scaffold", "biomedical", "tissue engineering", "cell support", "porosity"]
    },
    "packaging": {
        "name": "Packaging film",
        "keywords": ["packaging", "film", "barrier", "barrier properties", "food packaging"]
    },
    "structural": {
        "name": "Structural composite",
        "keywords": ["structural", "reinforcement", "strength", "mechanical property", "composite"]
    },
    "insulation": {
        "name": "Thermal insulation material",
        "keywords": ["insulation", "thermal", "heat", "temperature", "conductivity"]
    },
    "ion_exchange": {
        "name": "Ion-exchange material",
        "keywords": ["ion exchange", "ion-exchange", "resin", "selective uptake", "recovery"]
    }
}

# Level 3: Application Domains
APPLICATION_DOMAINS = {
    "water_treatment": {
        "name": "Water treatment",
        "keywords": ["water treatment", "water purification", "wastewater", "drinking water", "potable"]
    },
    "awh": {
        "name": "Atmospheric water harvesting",
        "keywords": ["atmospheric water harvesting", "AWH", "harvest water from air", "moisture capture"]
    },
    "co2_capture": {
        "name": "CO₂ capture",
        "keywords": ["CO2 capture", "carbon capture", "CO2", "carbon dioxide"]
    },
    "nutrient_recovery": {
        "name": "Nutrient recovery",
        "keywords": ["nutrient recovery", "phosphate recovery", "potassium recovery", "nutrient"]
    },
    "brine_separation": {
        "name": "Brine separation",
        "keywords": ["brine", "brine separation", "salt separation", "mineral recovery"]
    },
    "energy": {
        "name": "Energy storage",
        "keywords": ["energy storage", "battery", "supercapacitor", "electrochemical"]
    },
    "hydrogen": {
        "name": "Hydrogen production",
        "keywords": ["hydrogen", "hydrogen production", "water splitting", "H2"]
    },
    "construction": {
        "name": "Construction",
        "keywords": ["construction", "building material", "cement", "concrete"]
    },
    "biomedical": {
        "name": "Biomedical",
        "keywords": ["biomedical", "medical", "drug delivery", "therapy", "implant"]
    },
    "agriculture": {
        "name": "Agriculture",
        "keywords": ["agriculture", "fertilizer", "controlled release", "soil"]
    },
    "remediation": {
        "name": "Environmental remediation",
        "keywords": ["remediation", "cleanup", "contamination", "environmental", "remediate"]
    }
}

# Level 4: Hierarchical Mapping for Each Preset
HIERARCHICAL_PRESETS = {
    "membrane_water_treatment": {
        "material_family": "polymer",
        "functional_class": "membrane",
        "application_domain": "water_treatment",
        "priority": 1,
        "keywords": ["membrane", "filtration", "water", "separation"]
    },
    "desalination_pretreatment_media": {
        "material_family": "composite",
        "functional_class": "adsorbent",
        "application_domain": "water_treatment",
        "priority": 1.5,
        "keywords": ["desalination pretreatment", "pre-treatment media", "pressure drop", "seawater compatibility"]
    },
    "oil_gas_produced_water_pretreatment_media": {
        "material_family": "composite",
        "functional_class": "adsorbent",
        "application_domain": "water_treatment",
        "priority": 1.4,
        "keywords": ["produced water", "oil and gas", "oilfield", "hydrocarbon", "ADNOC", "UAE", "sulfide", "reinjection"]
    },
    "atmospheric_water_harvesting_material": {
        "material_family": "composite",
        "functional_class": "adsorbent",
        "application_domain": "awh",
        "priority": 2,
        "keywords": ["atmospheric", "water harvesting", "AWH", "moisture capture"]
    },
    "self_cleaning_building_coating": {
        "material_family": "ceramic",
        "functional_class": "coating",
        "application_domain": "construction",
        "priority": 4,
        "keywords": ["self-cleaning", "exterior coating", "building coating", "photocatalytic", "dirt degradation"]
    },
    "photocatalytic_coating": {
        "material_family": "ceramic",
        "functional_class": "photocatalyst",
        "application_domain": "water_treatment",
        "priority": 3,
        "keywords": ["photocatalytic", "TiO2", "coating", "UV"]
    },
    "phosphate_recovery_material": {
        "material_family": "composite",
        "functional_class": "adsorbent",
        "application_domain": "nutrient_recovery",
        "priority": 4,
        "keywords": ["phosphate", "recovery", "P", "nutrient"]
    },
    "potassium_brine_separation_material": {
        "material_family": "composite",
        "functional_class": "ion_exchange",
        "application_domain": "brine_separation",
        "priority": 5,
        "keywords": ["potassium", "brine", "K+", "recovery", "ion exchange"]
    },
    "adsorbent_heavy_metals": {
        "material_family": "composite",
        "functional_class": "adsorbent",
        "application_domain": "water_treatment",
        "priority": 6,
        "keywords": ["heavy metal", "adsorption", "Pb", "Cd", "Hg"]
    },
    # Future expandable presets (placeholders)
    "pfas_adsorbent": {
        "material_family": "polymer",
        "functional_class": "adsorbent",
        "application_domain": "water_treatment",
        "priority": 7,
        "keywords": ["PFAS", "PFOA", "PFOS", "per- and polyfluoro"]
    },
    "co2_capture_material": {
        "material_family": "hybrid",
        "functional_class": "adsorbent",
        "application_domain": "co2_capture",
        "priority": 2,
        "keywords": [
            "CO2", "CO2 capture", "carbon capture", "carbon dioxide capture",
            "amine-functionalized", "amine-functionalized silica",
            "flue gas", "direct air capture", "DAC",
            "CO2 uptake", "CO2/N2 selectivity", "water vapor selectivity",
            "regeneration energy", "amine loss", "cyclic performance",
            "amine stability", "humidity tolerance"
        ]
    },
    "thermal_insulation_composite": {
        "material_family": "composite",
        "functional_class": "insulation",
        "application_domain": "construction",
        "priority": 3,
        "keywords": [
            "thermal insulation", "insulation composite", "heat transfer",
            "thermal conductivity", "compressive strength", "flexural strength",
            "flame response", "fire-safe", "fire-resistant",
            "indoor air safety", "aging stability", "building insulation",
            "lightweight insulation", "foam matrix", "fiber-based"
        ]
    },
    "oil_spill_absorbent": {
        "material_family": "carbon",
        "functional_class": "adsorbent",
        "application_domain": "remediation",
        "priority": 9,
        "keywords": ["oil", "spill", "absorbent", "petroleum"]
    },
    "controlled_release_fertilizer": {
        "material_family": "polymer",
        "functional_class": "coating",
        "application_domain": "agriculture",
        "priority": 10,
        "keywords": ["controlled release", "fertilizer", "slow release"]
    },
    "battery_electrode_material": {
        "material_family": "composite",
        "functional_class": "electrode",
        "application_domain": "energy",
        "priority": 11,
        "keywords": ["battery", "electrode", "anode", "cathode"]
    },
    "hydrogen_evolution_electrocatalyst": {
        "material_family": "metal",
        "functional_class": "catalyst",
        "application_domain": "hydrogen",
        "priority": 12,
        "keywords": ["hydrogen evolution", "HER", "electrocatalyst", "water splitting"]
    }
}

# Priority Rules for Conflict Resolution
PRIORITY_RULES = {
    "membrane_over_adsorbent": ["membrane", "filtration", "flux", "permeability", "MWCO"],
    "co2_over_photocatalytic": ["CO2", "carbon capture", "CO2 capture"],
    "awh_over_composite": ["atmospheric water", "AWH", "moisture capture from air"],
    "phosphate_over_adsorbent": ["phosphate", "phosphorus", "nutrient recovery"],
    "potassium_over_ion_exchange": ["potassium brine", "K+ recovery", "brine separation"],
    "coating_over_photocatalyst": ["coating", "film", "substrate", "binder", "surface"]
}

# ============================================================================
# HIERARCHICAL CLASSIFICATION FUNCTION
# ============================================================================

def classify_material_hierarchically(user_request: str) -> dict:
    """
    Classify material hierarchically with confidence scoring using priority-based matching.
    Returns hierarchical structure with all 4 levels + confidence + reasoning.
    """
    # Use existing priority-based classification first
    request_lower = user_request.lower()
    preset_scores = {}
    
    # STRONG PRIORITY RULES: Override generic keyword matching for specific domains
    # These rules prevent misclassification by checking for domain-specific keywords FIRST
    
    # Rule 1: FABRIC/LAUNDRY domain → fabric_oil_stain_removal_composite (NOT heavy metal adsorbent)
    fabric_keywords = ["fabric", "cotton", "clothing", "laundry", "garment", "textile", "cloth",
                       "oil stain", "grease stain", "washing", "pre-treat", "pre-wash", "stain removal from fabric"]
    if any(kw in request_lower for kw in fabric_keywords):
        # Check for heavy metal keywords to avoid confusion
        heavy_metal_keywords = ["lead", "cadmium", "arsenic", "chromium", "toxic metal", "pb", "cd", "as", "cr", "metal ion"]
        if not any(hm in request_lower for hm in heavy_metal_keywords):
            preset_scores["fabric_oil_stain_removal_composite"] = 100  # Highest score to override
    
    # Rule 2: ROOF domain → roof_waterproofing_thermal_insulation_coating (NOT thermal_insulation_composite)
    roof_keywords = ["roof", "rooftop", "roof-applied", "concrete roof", "waterproofing", 
                     "rainwater leakage", "water leakage", "roof coating", "building roof"]
    if any(kw in request_lower for kw in roof_keywords):
        preset_scores["roof_waterproofing_thermal_insulation_coating"] = 100
    
    # Rule 3: CO2/CARBON CAPTURE → co2_capture_material (NOT photocatalytic_coating)
    co2_keywords = ["co2", "co₂", "carbon dioxide", "carbon capture", "carbon capture material",
                    "direct air capture", "dac", "flue gas", "amine-functionalized"]
    if any(kw in request_lower for kw in co2_keywords):
        preset_scores["co2_capture_material"] = 100
    
    # Rule 4: PHOSPHATE RECOVERY → phosphate_recovery_material (BEFORE oil/gas and other water treatment)
    # Must run BEFORE oil/gas to prevent wastewater keywords from triggering oil/gas classification
    phosphate_keywords = ["phosphate recovery", "phosphate ions", "orthophosphate", "phosphorus recovery",
                         "nutrient recovery", "fertilizer reuse", "agricultural wastewater phosphate",
                         "phosphate uptake", "phosphate adsorbent", "phosphate binding", "phosphate release"]
    if any(kw in request_lower for kw in phosphate_keywords):
        preset_scores["phosphate_recovery_material"] = 100
    
    # Rule 5: OIL & GAS PRODUCED WATER → oil_gas_produced_water_pretreatment_media (BEFORE desalination_pretreatment_media)
    oil_gas_keywords = ["produced water", "oil and gas", "oilfield", "oil and grease", "oil/grease",
                        "hydrocarbons", "hydrocarbon", "TOC", "COD", "sulfide", "reinjection",
                        "reuse", "ADNOC", "UAE oil", "gulf conditions", "hot gulf", "backwash",
                        "downstream membrane fouling", "produced-water", "oil production", "gas field", "reservoir"]
    if any(kw in request_lower for kw in oil_gas_keywords):
        # Only set to 100 if phosphate recovery rule didn't already match
        if "phosphate_recovery_material" not in preset_scores or preset_scores.get("phosphate_recovery_material") != 100:
            preset_scores["oil_gas_produced_water_pretreatment_media"] = 100
    
    # Rule 6: DESALINATION PRE-TREATMENT → desalination_pretreatment_media (BEFORE membrane)
    desal_keywords = ["desalination pre-treatment", "desalination pretreatment", "pre-treatment media",
                      "seawater treatment", "desal pre-treatment", "pretreatment media"]
    if any(kw in request_lower for kw in desal_keywords):
        # Check if this is oil/gas produced water or phosphate recovery (more specific)
        if "produced water" not in request_lower and not any(og in request_lower for og in oil_gas_keywords) and not any(phos in request_lower for phos in phosphate_keywords):
            preset_scores["desalination_pretreatment_media"] = 100
    
    # Rule 7: SELF-CLEANING BUILDING COATING → self_cleaning_building_coating
    self_clean_keywords = ["self-cleaning", "self cleaning", "exterior coating", "building coating",
                          "facade coating", "photocatalytic nanoparticles", "facade", "exterior"]
    if any(kw in request_lower for kw in self_clean_keywords):
        # Check it's not just thermal insulation
        if not ("thermal" in request_lower and "insulation" in request_lower and "roof" not in request_lower):
            preset_scores["self_cleaning_building_coating"] = 100
    
    # Rule 8: MEMBRANE WATER TREATMENT → membrane_water_treatment (unless heavy metals)
    membrane_keywords = ["membrane", "anti-fouling", "polymer membrane", "pvdf", "pes", "filtration",
                        "microfiltration", "ultrafiltration", "nanofiltration", "mixed-matrix"]
    if any(kw in request_lower for kw in membrane_keywords):
        # Check for heavy metal keywords and other specific domains
        heavy_metal_keywords = ["heavy metal", "lead", "cadmium", "arsenic", "chromium"]
        if not any(hm in request_lower for hm in heavy_metal_keywords) and not any(og in request_lower for og in oil_gas_keywords) and not any(phos in request_lower for phos in phosphate_keywords):
            preset_scores["membrane_water_treatment"] = 100
    
    # **CRITICAL RULE 9: BATTERY ELECTRODE DOMAIN GUARDRAIL** ← Must run BEFORE normal classification
    # This prevents misclassification of battery anodes as thermal insulation or other categories
    battery_electrode_keywords = [
        "sodium-ion battery", "na-ion", "battery anode", "anode composite", "hard carbon",
        "conductive carbon black", "sodium-compatible binder", "sodium storage",
        "specific capacity", "coulombic efficiency", "rate capability", "cycling stability",
        "cycling durability", "electrode swelling", "impedance", "electrochemical impedance",
        "sei", "half-cell", "full-cell", "current collector", "electrode",
        "sodium battery", "na+ storage", "anode material", "galvanostatic",
        "na metal", "sodium metal", "battery electrode", "half cell"
    ]
    
    # Check if request contains STRONG battery keywords
    battery_keyword_count = sum(1 for kw in battery_electrode_keywords if kw in request_lower)
    if battery_keyword_count >= 2:  # At least 2 battery keywords for high confidence
        # HARD OVERRIDE: Battery prompts go to sodium_ion_battery_anode_composite
        # This overrides any other classification including thermal insulation
        preset_scores["sodium_ion_battery_anode_composite"] = 100
    
    matched_keywords_map = {}
    priority_rule_scores = preset_scores.copy()  # Save priority rule results
    
    # First pass: check presets in priority order
    for category_key in CATEGORY_PRIORITY_ORDER:
        if category_key == "other_material":
            continue
        
        # IMPORTANT: Don't overwrite priority rule scores (they're always 100 and highest priority)
        if category_key in priority_rule_scores and priority_rule_scores[category_key] == 100:
            continue  # Skip this category, priority rule already set it to 100
        
        category_data = CATEGORY_REGISTRY.get(category_key, {})
        priority_keywords = category_data.get("priority_keywords", [])
        
        # Score based on priority keyword matches
        score = 0
        matched = []
        for keyword in priority_keywords:
            if keyword.lower() in request_lower:
                matched.append(keyword)
                # Multi-word keywords score higher
                score += len(keyword.split()) * 3
        
        if matched:
            preset_scores[category_key] = score
            matched_keywords_map[category_key] = matched
    
    # If no matches from priority keywords, do partial matching
    if not any(score == 100 for score in preset_scores.values()):  # Only do partial if no 100-score priority rule matched
        for category_key in CATEGORY_PRIORITY_ORDER:
            if category_key == "other_material":
                continue
            
            # Skip if already matched by priority rule
            if category_key in priority_rule_scores and priority_rule_scores[category_key] == 100:
                continue
            
            category_data = CATEGORY_REGISTRY.get(category_key, {})
            priority_keywords = category_data.get("priority_keywords", [])
            
            score = 0
            matched = []
            for keyword in priority_keywords:
                # Check for partial matches
                for word in keyword.split():
                    if word.lower() in request_lower:
                        matched.append(keyword)
                        score += 1
                        break
            
            if matched:
                preset_scores[category_key] = score
                matched_keywords_map[category_key] = matched
    
    # Rank presets by score
    ranked_presets = sorted(preset_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Determine top preset
    if ranked_presets:
        top_preset = ranked_presets[0][0]
        top_score = ranked_presets[0][1]
        confidence = min(100, max(60, int((top_score / 10) * 40 + 60)))  # 60-100 range
    else:
        top_preset = "other_material"
        confidence = 0
        ranked_presets = []
    
    # Get hierarchical data for top preset
    top_hier_data = HIERARCHICAL_PRESETS.get(top_preset, {})
    material_family = top_hier_data.get("material_family", "composite")
    functional_class = top_hier_data.get("functional_class", "adsorbent")
    application_domain = top_hier_data.get("application_domain", "water_treatment")
    
    # Build hierarchical names
    family_name = MATERIAL_FAMILIES.get(material_family, {}).get("name", material_family)
    functional_name = FUNCTIONAL_CLASSES.get(functional_class, {}).get("name", functional_class)
    app_name = APPLICATION_DOMAINS.get(application_domain, {}).get("name", application_domain)
    display_name = CATEGORY_REGISTRY.get(top_preset, {}).get("display_name", top_preset)
    
    # Detect close call
    close_call = False
    close_call_alternative = None
    if len(ranked_presets) >= 2:
        score_diff = abs(ranked_presets[0][1] - ranked_presets[1][1])
        if score_diff <= 2:
            close_call = True
            close_call_alternative = ranked_presets[1][0]
    
    # Detect conflicts
    conflict_detected = False
    if close_call and confidence < 80:
        conflict_detected = True
    
    # Build top 3 list
    top_3_list = []
    for i, (preset_name, score) in enumerate(ranked_presets[:3]):
        top_3_list.append({
            "preset": preset_name,
            "display_name": CATEGORY_REGISTRY.get(preset_name, {}).get("display_name", preset_name),
            "score": score
        })
    
    # Build alternatives (first 5)
    alternatives = []
    for i, (preset_name, score) in enumerate(ranked_presets[:5]):
        alternatives.append({
            "preset": preset_name,
            "display_name": CATEGORY_REGISTRY.get(preset_name, {}).get("display_name", preset_name)
        })
    
    # Build reasoning
    reasoning = (
        f"Selected: {display_name} ({confidence}% confidence)\n"
        f"Material Family: {family_name}\n"
        f"Functional Class: {functional_name}\n"
        f"Application Domain: {app_name}\n"
        f"Matched keywords: {', '.join(matched_keywords_map.get(top_preset, [])[:5])}"
    )
    
    requires_confirmation = confidence < 75 or close_call or conflict_detected
    
    return {
        "material_family": material_family,
        "functional_class": functional_class,
        "application_domain": application_domain,
        "specific_preset": top_preset,
        "confidence_score": confidence,
        "matched_keywords": matched_keywords_map.get(top_preset, []),
        "top_3_categories": top_3_list,
        "alternative_categories": alternatives,
        "reasoning_explanation": reasoning,
        "conflict_detected": conflict_detected,
        "requires_user_confirmation": requires_confirmation,
        "close_call": close_call,
        "close_call_alternative": close_call_alternative
    }


def detect_category_conflicts(user_request: str, selected_category: str) -> dict:
    """
    Detect hard category conflicts using explicit conflict rules.
    
    Returns:
        {
            "conflict_detected": bool,
            "conflict_reason": str,
            "recommended_category": str,
            "blocked_export": bool
        }
    """
    request_lower = user_request.lower()
    
    # **IMPORTANT: Check Desalination Pre-Treatment FIRST (before Membrane rule)**
    # This prevents "membrane desalination" from incorrectly triggering the membrane conflict rule
    desalination_pretreatment_keywords = [
        "desalination pre-treatment", "pre-treatment media", "pretreatment media",
        "before membrane desalination", "improve membrane lifetime", "reduce fouling risk",
        "pressure drop", "media regeneration", "microbial growth risk",
        "seawater compatibility", "brackish water compatibility",
        "suspended solids", "organic matter removal", "desalination pretreatment",
        "pre-treatment desalination", "ro pretreatment", "nf pretreatment",
        "membrane fouling reduction", "activated carbon", "iron oxide",
        "porous silica", "mineral stabilizers"
    ]
    
    if any(kw.lower() in request_lower for kw in desalination_pretreatment_keywords):
        if selected_category == "membrane_water_treatment":
            # Check if this is really a pre-treatment media (before membrane), not the membrane itself
            membrane_material_keywords = [
                "anti-fouling polymer", "pvdf", "pes", "psf", "cellulose acetate",
                "hydrophilic additive", "peg", "pvp", "zwitterionic",
                "polymer membrane matrix", "membrane material",
                "polymeric membrane", "pore size", "mwco", "molecular weight cutoff"
            ]
            if not any(kw.lower() in request_lower for kw in membrane_material_keywords):
                return {
                    "conflict_detected": True,
                    "conflict_reason": "Potential Conflict Detected: This request describes desalination pre-treatment media, not the membrane itself.",
                    "recommended_category": "desalination_pretreatment_media",
                    "blocked_export": True
                }
        
        elif selected_category == "adsorbent_heavy_metals":
            # Check if heavy metal removal is the primary focus or just secondary
            heavy_metal_focus_keywords = [
                "lead", "cadmium", "arsenic", "chromium", "mercury",
                "heavy metal removal", "toxic metal", "metal adsorption",
                "pb2+", "cd2+", "as3+", "cr6+"
            ]
            if not any(kw.lower() in request_lower for kw in heavy_metal_focus_keywords):
                return {
                    "conflict_detected": True,
                    "conflict_reason": "Potential Conflict Detected: This request describes desalination pre-treatment media, not a heavy metal adsorbent.",
                    "recommended_category": "desalination_pretreatment_media",
                    "blocked_export": True
                }
    
    # Oil & Gas Produced-Water Pre-Treatment Rule (NEW)
    # Detect when user describes produced water treatment but selects a generic category
    oil_gas_produced_water_keywords = [
        "produced water", "oil and gas operations", "ADNOC", "UAE oil/gas", "gulf operating conditions",
        "hot gulf conditions", "oil and grease", "hydrocarbons", "TOC", "COD",
        "sulfide-related", "reinjection", "reuse", "high-salinity produced water",
        "backwashability", "downstream membrane fouling", "oilfield water"
    ]
    
    if any(kw.lower() in request_lower for kw in oil_gas_produced_water_keywords):
        if selected_category == "desalination_pretreatment_media":
            return {
                "conflict_detected": True,
                "conflict_reason": "A more specific Oil & Gas Produced-Water Pre-Treatment Media category is available.",
                "recommended_category": "oil_gas_produced_water_pretreatment_media",
                "blocked_export": False  # Suggestion only, not a hard block
            }
        elif selected_category == "membrane_water_treatment":
            return {
                "conflict_detected": True,
                "conflict_reason": "Oil & Gas Produced-Water Pre-Treatment Media is a more appropriate category for this application.",
                "recommended_category": "oil_gas_produced_water_pretreatment_media",
                "blocked_export": False
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
    
    # Membrane Conflict Rule (now safe since desalination was checked first)
    membrane_keywords = [
        "membrane", "anti-fouling", "permeability", "water flux",
        "rejection efficiency", "filtration cycles", "cleaning recovery"
    ]
    heavy_metal_keywords = ["lead", "cadmium", "arsenic", "chromium", "mercury", "heavy metal"]
    
    if any(kw.lower() in request_lower for kw in membrane_keywords):
        if selected_category == "adsorbent_heavy_metals":
            # Only block if no heavy metals mentioned
            if not any(kw.lower() in request_lower for kw in heavy_metal_keywords):
                return {
                    "conflict_detected": True,
                    "conflict_reason": "Request mentions membrane/filtration, but selected category is Heavy Metal Adsorbent.",
                    "recommended_category": "membrane_water_treatment",
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
    
    # Thermal Insulation Conflict Rule
    thermal_insulation_keywords = [
        "thermal insulation", "insulation composite", "reduce heat transfer",
        "thermal conductivity", "compressive strength", "flexural strength",
        "flame response", "fire-safe", "fire-resistant", "fire safety",
        "indoor air safety", "aging stability", "building insulation",
        "lightweight insulation", "thermal stability", "temperature resistance",
        "building material", "heat transfer"
    ]
    water_related_categories = [
        "atmospheric_water_harvesting_material",
        "photocatalytic_coating",
        "adsorbent_heavy_metals",
        "membrane_water_treatment",
        "co2_capture_material",
        "phosphate_recovery_material",
        "potassium_brine_separation_material"
    ]
    
    if any(kw.lower() in request_lower for kw in thermal_insulation_keywords):
        if selected_category in water_related_categories:
            return {
                "conflict_detected": True,
                "conflict_reason": f"Request mentions thermal insulation and building materials, but selected category is {CATEGORY_REGISTRY.get(selected_category, {}).get('display_name', selected_category)}. These are incompatible.",
                "recommended_category": "thermal_insulation_composite",
                "blocked_export": True
            }
    
    # **CRITICAL DOMAIN-MISMATCH RULE: Sodium-Ion Battery Anode Detection**
    # This rule prevents misclassification of battery anodes as thermal insulation
    # Domain mismatch should trigger new-category workflow EVEN WITH HIGH CONFIDENCE
    sodium_ion_battery_keywords = [
        "sodium-ion battery", "na-ion", "battery anode", "anode composite", "hard carbon",
        "conductive carbon black", "sodium-compatible binder", "sodium storage capacity",
        "specific capacity", "coulombic efficiency", "cycling stability", "rate capability",
        "mechanical integrity", "irreversible capacity loss", "electrode swelling",
        "impedance", "electrode", "sei", "half-cell", "full-cell",
        "sodium battery", "na+ storage", "anode material", "sodium battery anode",
        "sodium-ion anode", "na ion", "sodium ion battery", "battery electrode"
    ]
    
    if any(kw.lower() in request_lower for kw in sodium_ion_battery_keywords):
        if selected_category == "thermal_insulation_composite":
            # HARD BLOCK: This is a strong domain mismatch
            # Battery electrodes should NOT be classified as thermal insulation
            return {
                "conflict_detected": True,
                "conflict_reason": "DOMAIN MISMATCH DETECTED: This request clearly describes a sodium-ion battery anode composite (electrochemistry domain), but was classified as Thermal Insulation Composite (building materials domain). These domains are incompatible. The Sodium-Ion Battery Anode Composite category is available.",
                "recommended_category": "sodium_ion_battery_anode_composite",
                "blocked_export": True  # CRITICAL: Block export for domain mismatch
            }
        elif selected_category not in ["sodium_ion_battery_anode_composite", "adsorbent_heavy_metals"]:
            # If battery keywords present but category not set to battery anode, suggest it
            return {
                "conflict_detected": True,
                "conflict_reason": "This request describes sodium-ion battery anode material. The more appropriate category 'Sodium-Ion Battery Anode Composite' is available for electrochemical validation.",
                "recommended_category": "sodium_ion_battery_anode_composite",
                "blocked_export": True
            }
    
    # No conflicts detected
    return {
        "conflict_detected": False,
        "conflict_reason": "",
        "recommended_category": selected_category,
        "blocked_export": False
    }


def validate_preset_consistency(selected_category: str, material_data: dict) -> dict:
    """
    Validate that the loaded preset fields match the selected category.
    
    Returns:
        {
            "status": "pass", "warning", or "fail",
            "missing_fields": [...],
            "unexpected_fields": [...],
            "details": str
        }
    """
    category_data = CATEGORY_REGISTRY.get(selected_category, {})
    required_fields = category_data.get("required_fields", {})
    
    preset_params = material_data.get("preset_parameters", {})
    validation_plan = material_data.get("validation_plan", {})
    
    # Check required parameters are present
    missing_fields = []
    for field_name in required_fields:
        if field_name not in preset_params:
            missing_fields.append(field_name)
    
    # Category-specific validation
    if selected_category == "co2_capture_material":
        expected = ["CO₂ uptake", "CO₂/N₂ selectivity", "humidity tolerance", "regeneration energy", "amine loss", "cycling durability"]
        validation_labels = [format_parameter_label(k) for k in preset_params.keys()]
        missing = [e for e in expected if e not in str(validation_labels)]
        if missing:
            return {
                "status": "warning",
                "missing_fields": missing,
                "unexpected_fields": [],
                "details": f"CO₂ capture preset missing expected fields: {', '.join(missing)}"
            }
    
    elif selected_category == "photocatalytic_coating":
        expected = ["substrate type", "coating thickness", "light source", "target pollutant", "degradation efficiency", "leaching", "adhesion"]
        validation_labels = [format_parameter_label(k) for k in preset_params.keys()]
        missing = [e for e in expected if e not in str(validation_labels)]
        if missing:
            return {
                "status": "warning",
                "missing_fields": missing,
                "unexpected_fields": [],
                "details": f"Photocatalytic coating preset missing expected fields: {', '.join(missing)}"
            }
    
    elif selected_category == "membrane_water_treatment":
        expected = ["water flux", "operating pressure", "rejection target", "fouling resistance", "cleaning recovery", "pore size/MWCO", "leaching", "mechanical durability"]
        validation_labels = [format_parameter_label(k) for k in preset_params.keys()]
        missing = [e for e in expected if e not in str(validation_labels)]
        if missing:
            return {
                "status": "warning",
                "missing_fields": missing,
                "unexpected_fields": [],
                "details": f"Membrane preset missing expected fields: {', '.join(missing)}"
            }
    
    if missing_fields:
        return {
            "status": "fail",
            "missing_fields": missing_fields,
            "unexpected_fields": [],
            "details": f"Missing required fields for {selected_category}: {', '.join(missing_fields)}"
        }
    
    return {
        "status": "pass",
        "missing_fields": [],
        "unexpected_fields": [],
        "details": "All required fields present and consistent"
    }


def verify_material_decision(user_request: str, selected_category: str, material_data: dict) -> dict:
    """
    Verify that the selected category is consistent with the user request and material data.
    
    Returns:
        {
            "verification_status": "pass", "warning", or "fail",
            "conflict_detected": bool,
            "conflict_reason": str,
            "recommended_category": str,
            "blocked_export": bool,
            "user_confirmation_required": bool,
            "details": str
        }
    """
    # Step 1: Check for hard conflicts
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
    
    # Step 2: Check preset consistency
    consistency_result = validate_preset_consistency(selected_category, material_data)
    
    if consistency_result["status"] == "fail":
        return {
            "verification_status": "fail",
            "conflict_detected": False,
            "conflict_reason": "",
            "recommended_category": selected_category,
            "blocked_export": True,
            "user_confirmation_required": False,
            "details": consistency_result["details"]
        }
    
    # Step 3: Determine if user confirmation is needed
    user_confirmation_needed = consistency_result["status"] == "warning"
    
    if conflict_result["conflict_detected"] or user_confirmation_needed:
        return {
            "verification_status": "warning",
            "conflict_detected": conflict_result["conflict_detected"],
            "conflict_reason": conflict_result["conflict_reason"],
            "recommended_category": conflict_result["recommended_category"],
            "blocked_export": False,
            "user_confirmation_required": True,
            "details": consistency_result["details"]
        }
    
    # All checks passed
    return {
        "verification_status": "pass",
        "conflict_detected": False,
        "conflict_reason": "",
        "recommended_category": selected_category,
        "blocked_export": False,
        "user_confirmation_required": False,
        "details": "Verification passed: category is consistent with request and preset"
    }


def run_three_stage_verification(user_request: str, selected_category: str, material_data: dict, stored_confidence: float = None) -> dict:
    """
    Run a comprehensive four-stage verification system before final report export.
    
    Stage 1: Category Keyword Verification
    - Check if selected category's priority keywords match the user request
    - SKIP if stored_confidence >= 85% (trust the initial classification)
    
    Stage 2: Preset-Field Compatibility Verification
    - Check if generated report fields match user's requested tests and parameters
    
    Stage 3: Disclaimer Compatibility Verification
    - Check if disclaimer matches the selected category
    
    Stage 4: Scientific Dataset Verification (Optional)
    - Verify material components against free/open-access datasets
    - Provides evidence layer for material plausibility
    
    Args:
        user_request: Original user prompt
        selected_category: Normalized category key (e.g., thermal_insulation_composite)
        material_data: Generated material data with parameters
        stored_confidence: Initial classification confidence (0-100). If >= 85, skip Stage 1 re-check.
    
    Returns:
        {
            "overall_status": "pass", "warning", or "fail",
            "stage_1_result": {...},
            "stage_2_result": {...},
            "stage_3_result": {...},
            "stage_4_result": {...},
            "blocked_export": bool,
            "verification_message": str,
            "recommended_category": str
        }
    """
    request_lower = user_request.lower()
    
    # ===== STAGE 1: Category Keyword Verification =====
    # If initial classification had high confidence, trust it and skip re-verification
    if stored_confidence is not None and stored_confidence >= 85:
        stage_1_result = {
            "status": "pass",
            "keyword_match_percentage": stored_confidence,
            "matched_keywords": [],
            "unmatched_keywords": [],
            "reason": f"Category was initially classified with {stored_confidence:.0f}% confidence. Verification skipped (high confidence).",
            "recommended_category": selected_category
        }
    else:
        stage_1_result = _stage_1_category_keyword_verification(request_lower, selected_category)
    
    # ===== STAGE 2: Preset-Field Compatibility Verification =====
    stage_2_result = _stage_2_preset_field_compatibility(request_lower, selected_category, material_data)
    
    # ===== STAGE 3: Disclaimer Compatibility Verification =====
    stage_3_result = _stage_3_disclaimer_compatibility(selected_category)
    
    # ===== STAGE 4: Scientific Dataset Verification =====
    stage_4_result = _stage_4_scientific_dataset_verification(selected_category, material_data)
    
    # Determine overall status
    failed_stages = []
    if stage_1_result["status"] == "fail":
        failed_stages.append("Stage 1 (Category Keywords)")
    if stage_2_result["status"] == "fail":
        failed_stages.append("Stage 2 (Preset Fields)")
    if stage_3_result["status"] == "fail":
        failed_stages.append("Stage 3 (Disclaimer)")
    # Stage 4 warnings do not block export (it's evidence layer only)
    
    warning_stages = []
    if stage_1_result["status"] == "warning":
        warning_stages.append("Stage 1")
    if stage_2_result["status"] == "warning":
        warning_stages.append("Stage 2")
    if stage_4_result["status"] == "warning":
        warning_stages.append("Stage 4 (Dataset)")
    
    overall_status = "fail" if failed_stages else ("warning" if warning_stages else "pass")
    blocked_export = overall_status == "fail"
    
    # Build verification message
    if blocked_export:
        message = f"⚠️ **Verification Failed**: {', '.join(failed_stages)} detected incompatibilities. "
        message += f"Category '{CATEGORY_REGISTRY.get(selected_category, {}).get('display_name', selected_category)}' may not match your request. "
        message += "Please review the suggested alternative or adjust your selection."
    elif overall_status == "warning":
        message = f"⚠️ **Verification Warning**: {', '.join(warning_stages)} detected potential issues. Review parameters before export."
    else:
        message = "✅ **Verification Passed**: All checks passed. Report is ready for export."
    
    return {
        "overall_status": overall_status,
        "stage_1_result": stage_1_result,
        "stage_2_result": stage_2_result,
        "stage_3_result": stage_3_result,
        "stage_4_result": stage_4_result,
        "blocked_export": blocked_export,
        "verification_message": message,
        "recommended_category": stage_1_result.get("recommended_category", selected_category)
    }


def _stage_1_category_keyword_verification(request_lower: str, selected_category: str) -> dict:
    """
    Stage 1: Verify category keywords match user request.
    
    Returns:
        {
            "status": "pass", "warning", or "fail",
            "keyword_match_percentage": float (0-100),
            "matched_keywords": [str],
            "unmatched_keywords": [str],
            "reason": str,
            "recommended_category": str
        }
    """
    category_data = CATEGORY_REGISTRY.get(selected_category, {})
    priority_keywords = category_data.get("priority_keywords", [])
    
    if not priority_keywords:
        # "Other" category has no keywords - auto-fail
        return {
            "status": "fail",
            "keyword_match_percentage": 0,
            "matched_keywords": [],
            "unmatched_keywords": [],
            "reason": "Selected category 'Other (Custom Material)' has no specific keywords. Please select a more specific category.",
            "recommended_category": "other_material"
        }
    
    matched = []
    unmatched = []
    
    for keyword in priority_keywords[:10]:  # Check first 10 keywords
        if keyword.lower() in request_lower:
            matched.append(keyword)
        else:
            unmatched.append(keyword)
    
    match_percentage = (len(matched) / len(priority_keywords[:10])) * 100 if priority_keywords else 0
    
    # Determine status
    if match_percentage >= 50:
        status = "pass"
        reason = f"Category keywords match {match_percentage:.0f}% of user request."
    elif match_percentage >= 25:
        status = "warning"
        reason = f"Category keywords match only {match_percentage:.0f}% of user request. Verify the classification is correct."
    else:
        status = "fail"
        reason = f"Category keywords match only {match_percentage:.0f}% of user request. This category may not be appropriate."
    
    return {
        "status": status,
        "keyword_match_percentage": match_percentage,
        "matched_keywords": matched,
        "unmatched_keywords": unmatched,
        "reason": reason,
        "recommended_category": selected_category
    }


def _stage_2_preset_field_compatibility(request_lower: str, selected_category: str, material_data: dict) -> dict:
    """
    Stage 2: Verify generated report fields match user's requested tests and parameters.
    
    Returns:
        {
            "status": "pass", "warning", or "fail",
            "field_compatibility": dict,
            "missing_expected_fields": [str],
            "mismatched_fields": [str],
            "reason": str
        }
    """
    category_data = CATEGORY_REGISTRY.get(selected_category, {})
    expected_params = category_data.get("category_specific_parameters", {})
    expected_validation = category_data.get("validation_plan", {})
    
    generated_params = material_data.get("category_specific_parameters", {})
    generated_validation = material_data.get("validation_plan", {})
    
    # Check parameter field compatibility
    param_compatibility = {}
    missing_params = []
    
    for param_name in list(expected_params.keys())[:8]:  # Check first 8 parameters
        if param_name in generated_params:
            param_compatibility[param_name] = "present"
        else:
            missing_params.append(param_name)
    
    # Check validation field compatibility
    validation_compatibility = {}
    missing_validation = []
    
    for val_name in list(expected_validation.keys())[:8]:  # Check first 8 validation items
        if val_name in generated_validation:
            validation_compatibility[val_name] = "present"
        else:
            missing_validation.append(val_name)
    
    # Determine status
    all_missing = missing_params + missing_validation
    missing_percentage = (len(all_missing) / (8 + 8)) * 100 if (8 + 8) > 0 else 0
    
    if missing_percentage <= 10:
        status = "pass"
        reason = f"All expected fields present. Report is compatible with category."
    elif missing_percentage <= 30:
        status = "warning"
        reason = f"Some expected fields missing ({missing_percentage:.0f}%). Verify completeness before export."
    else:
        status = "fail"
        reason = f"Many expected fields missing ({missing_percentage:.0f}%). Report may not match category requirements."
    
    return {
        "status": status,
        "field_compatibility": {
            "parameter_compatibility": param_compatibility,
            "validation_compatibility": validation_compatibility
        },
        "missing_expected_fields": all_missing,
        "mismatched_fields": [],
        "reason": reason
    }


def _stage_3_disclaimer_compatibility(selected_category: str) -> dict:
    """
    Stage 3: Verify disclaimer matches the selected category.
    
    Returns:
        {
            "status": "pass", "warning", or "fail",
            "disclaimer_present": bool,
            "includes_category_name": bool,
            "includes_disclaimers": [str],
            "reason": str
        }
    """
    category_data = CATEGORY_REGISTRY.get(selected_category, {})
    disclaimer = category_data.get("category_specific_disclaimer", "")
    display_name = category_data.get("display_name", "")
    
    if not disclaimer:
        return {
            "status": "fail",
            "disclaimer_present": False,
            "includes_category_name": False,
            "includes_disclaimers": [],
            "reason": f"No disclaimer found for category '{display_name}'. This is required for export."
        }
    
    # Check for key disclaimer phrases
    key_phrases = [
        "do not demonstrate",
        "conditional upon",
        "rigorous laboratory validation",
        "testing"
    ]
    
    found_phrases = [phrase for phrase in key_phrases if phrase.lower() in disclaimer.lower()]
    includes_category = display_name.lower() in disclaimer.lower()
    
    if found_phrases and includes_category:
        status = "pass"
        reason = f"Disclaimer properly configured for '{display_name}' with required validation warnings."
    elif found_phrases:
        status = "warning"
        reason = f"Disclaimer present but doesn't explicitly reference '{display_name}'."
    else:
        status = "fail"
        reason = f"Disclaimer incomplete or missing required validation warnings."
    
    return {
        "status": status,
        "disclaimer_present": bool(disclaimer),
        "includes_category_name": includes_category,
        "includes_disclaimers": found_phrases,
        "reason": reason
    }


def _stage_4_scientific_dataset_verification(selected_category: str, material_data: dict) -> dict:
    """
    Stage 4: Verify components and material properties against free/open-access scientific datasets.
    
    This stage queries PubChem, Materials Project, NIST, COD, and other databases
    to provide evidence-based verification of material plausibility.
    
    Returns:
        {
            "status": "pass", "warning", or "unavailable",
            "verification_result": {...} or None if unavailable,
            "datasets_queried": [str],
            "components_verified": int,
            "components_checked": int,
            "materials_found": int,
            "literature_hits": int,
            "reason": str,
            "evidence_summary": str
        }
    """
    
    if not SCIENTIFIC_VERIFICATION_AVAILABLE:
        return {
            "status": "unavailable",
            "verification_result": None,
            "reason": "Scientific dataset module not available (operating offline)",
            "evidence_summary": "External dataset verification skipped. App is operating in offline mode."
        }
    
    try:
        # Run scientific dataset verification
        verification_result = verify_with_free_datasets(material_data, selected_category)
        
        components_checked = len(verification_result.get("components_checked", []))
        components_verified = len(verification_result.get("components_verified", []))
        materials_found = len(verification_result.get("materials_found", []))
        datasets_queried = verification_result.get("datasets_queried", [])
        
        # Determine status
        if components_checked == 0:
            status = "unavailable"
            reason = "No components to verify"
        elif components_verified == components_checked:
            status = "pass"
            reason = f"All {components_verified} components verified in external databases"
        elif components_verified >= components_checked * 0.7:
            status = "pass"
            reason = f"{components_verified}/{components_checked} components verified; most matched"
        else:
            status = "warning"
            reason = f"Only {components_verified}/{components_checked} components verified; some may be proprietary"
        
        return {
            "status": status,
            "verification_result": verification_result,
            "datasets_queried": datasets_queried,
            "components_verified": components_verified,
            "components_checked": components_checked,
            "materials_found": materials_found,
            "literature_hits": verification_result.get("literature_hits", 0),
            "reason": reason,
            "evidence_summary": verification_result.get("evidence_summary", "")
        }
        
    except Exception as e:
        return {
            "status": "unavailable",
            "verification_result": None,
            "reason": f"Scientific dataset verification error: {str(e)}",
            "evidence_summary": "Dataset verification could not be completed due to an error. Offline mode active."
        }

# ============================================================================
# PROTECTED LABEL FORMATTING (Preserve Scientific Notation)
# ============================================================================

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
    """
    Format a parameter key into a display label, preserving scientific notation.
    
    Process:
    1. Convert underscores to spaces
    2. Check if label is in PROTECTED_LABEL_MAP
    3. If protected, return the protected version
    4. Otherwise, title-case the label
    
    Args:
        key: Parameter key (usually with underscores like "ph_working_range")
        
    Returns:
        Properly formatted label with scientific notation preserved
    """
    # Replace underscores with spaces
    label = key.replace("_", " ").lower()
    
    # Check protected map first
    if label in PROTECTED_LABEL_MAP:
        return PROTECTED_LABEL_MAP[label]
    
    # For unprotected labels, apply title case
    return key.replace("_", " ").title()



SCIENTIFIC_LABEL_MAPPINGS = {
    # pH and acidity
    "pH": "pH",
    "pKa": "pKa",
    
    # Ions and charged species
    "K+": "K⁺",
    "Na+": "Na⁺",
    "Mg2+": "Mg²⁺",
    "Ca2+": "Ca²⁺",
    "Fe2+": "Fe²⁺",
    "Fe3+": "Fe³⁺",
    "Pb2+": "Pb²⁺",
    "Cd2+": "Cd²⁺",
    "Zn2+": "Zn²⁺",
    "Cu2+": "Cu²⁺",
    "Ni2+": "Ni²⁺",
    "Al3+": "Al³⁺",
    "Cr3+": "Cr³⁺",
    "Cr6+": "Cr⁶⁺",
    
    # Anions - multiple formats for caret notation
    "Cl-": "Cl⁻",
    "F-": "F⁻",
    "Br-": "Br⁻",
    "I-": "I⁻",
    "OH-": "OH⁻",
    "SO4^2-": "SO₄²⁻",  # Caret notation
    "SO4 2-": "SO₄²⁻",  # Space notation
    "SO42-": "SO₄²⁻",   # Direct notation
    "SO4-": "SO₄²⁻",    # Simplified notation
    "NO3-": "NO₃⁻",
    "NO3^-": "NO₃⁻",    # Caret notation
    "PO4^3-": "PO₄³⁻",  # Caret notation
    "PO4 3-": "PO₄³⁻",  # Space notation
    "PO43-": "PO₄³⁻",   # Direct notation
    "PO4-": "PO₄³⁻",    # Simplified notation
    "PO4-P": "PO₄-P",
    "HPO4-": "HPO₄²⁻",
    "H2PO4-": "H₂PO₄⁻",
    "CO3^2-": "CO₃²⁻",  # Caret notation
    "CO3 2-": "CO₃²⁻",  # Space notation
    "CO32-": "CO₃²⁻",   # Direct notation
    "CO3-": "CO₃²⁻",    # Simplified notation
    "HCO3^-": "HCO₃⁻",  # Caret notation
    "HCO3-": "HCO₃⁻",   # Direct notation
    
    # Oxides and molecules
    "TiO2": "TiO₂",
    "SiO2": "SiO₂",
    "Fe2O3": "Fe₂O₃",
    "Fe3O4": "Fe₃O₄",
    "Al2O3": "Al₂O₃",
    "ZnO": "ZnO",
    "MgO": "MgO",
    "CaO": "CaO",
    "CO2": "CO₂",
    "CO": "CO",
    "H2O": "H₂O",
    "H2O2": "H₂O₂",
    
    # Degrees and units
    "degrees C": "°C",
    "degrees F": "°F",
    "um": "µm",
    "micrometers": "µm",
    "nm": "nm",
    "m-1": "m⁻¹",
    "min-1": "min⁻¹",
    "s-1": "s⁻¹",
    "m2": "m²",
    "g/cm2": "g/cm²",
    "mg/cm2": "mg/cm²",
    "L/m2.h": "L/m²·h",
    
    # Analytical methods
    "ICP-OES": "ICP-OES",
    "ICP-MS": "ICP-MS",
    "SEM/EDS": "SEM/EDS",
    "XRD": "XRD",
    "FTIR": "FTIR",
    "BET": "BET",
    "UV-A": "UV-A",
    "UV-B": "UV-B",
    "UV-Vis": "UV-Vis",
    "UV-Vis DRS": "UV-Vis DRS",
    "TGA/DSC": "TGA/DSC",
    "IC": "IC",
}

# ============================================================================
# CORE FUNCTIONS: CLASSIFICATION AND PRESET MANAGEMENT
# ============================================================================

def classify_material_category(user_request: str) -> tuple:
    """
    Classify material category using priority-based keyword matching.
    
    Returns:
        (normalized_category_name, display_name, confidence)
    """
    request_lower = user_request.lower()
    
    # Try each category in priority order
    for category_key in CATEGORY_PRIORITY_ORDER:
        category_data = CATEGORY_REGISTRY.get(category_key, {})
        priority_keywords = category_data.get("priority_keywords", [])
        
        # Skip empty categories
        if not priority_keywords:
            continue
        
        # Check if any priority keyword is in the request
        for keyword in priority_keywords:
            if keyword.lower() in request_lower:
                normalized_name = category_data.get("normalized_category_name", category_key)
                display_name = category_data.get("display_name", category_key)
                return normalized_name, display_name, 100
    
    # Default to Other if no match
    return "other_material", "Other (Custom Material)", 0


def clear_previous_preset_fields(material_data: dict) -> dict:
    """
    Clear all preset-specific fields before applying a new category preset.
    
    This ensures clean transitions when switching categories and prevents
    contamination of new reports with old category parameters.
    
    Args:
        material_data: Material data dictionary with potentially old preset fields
        
    Returns:
        Cleaned material_data dict with preset fields removed
    """
    # List of preset-specific fields to remove
    preset_fields = [
        # Category-specific parameters
        "category_specific_parameters",
        "performance_targets",
        
        # Validation and testing
        "validation_plan",
        "safety_tests",
        "characterization_methods",
        
        # Composition and preset info
        "default_composition",
        "composition",
        
        # Processing method (CRITICAL: prevent cross-contamination)
        "processing_method",
        "recommended_processing_method",
        
        # Disclaimers and notes
        "category_specific_disclaimer",
        "disclaimer",
        "evidence_boundary",
        "category_override_note",
        
        # Other preset-related fields
        "priority_keywords",
        "preset_parameters",
        "preset_validation_plan",
        "category_disclaimer",
    ]
    
    # Remove each preset field if present
    for field in preset_fields:
        if field in material_data:
            del material_data[field]
    
    return material_data


def get_category_preset(category_name: str) -> dict:
    """
    Retrieve the full preset data for a category from the registry.
    
    Args:
        category_name: normalized_category_name
        
    Returns:
        Complete category preset dictionary
    """
    return CATEGORY_REGISTRY.get(category_name, CATEGORY_REGISTRY.get("other_material", {}))


def get_category_display_name(category_name: str) -> str:
    """Get the display name for a category."""
    preset = get_category_preset(category_name)
    return preset.get("display_name", category_name)


def validate_category_exists(category_name: str) -> bool:
    """Check if a category exists in the registry."""
    return category_name in CATEGORY_REGISTRY and category_name != "other_material"


def apply_missing_preset_fields(material_data: dict, category_name: str) -> dict:
    """
    Apply only the missing fields from category preset.
    Used when user accepts suggested category but wants to keep existing data.
    
    Args:
        material_data: The material analysis result
        category_name: The normalized category name
        
    Returns:
        Updated material_data with missing fields filled in
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


def apply_category_preset(material_data: dict, category_name: str) -> dict:
    """
    Apply category preset to material data.
    Merges preset parameters, validation plan, and disclaimer into material_data.
    IMPORTANT: This function first clears all old preset fields to prevent contamination.
    
    Args:
        material_data: The material analysis result from Claude
        category_name: The normalized category name or display name (will be normalized)
        
    Returns:
        Enriched material_data with preset information
    """
    # NORMALIZE the category name FIRST to ensure consistency
    normalized_category = normalize_category_name(category_name)
    
    # CLEAR old preset fields BEFORE applying new ones to prevent contamination
    material_data = clear_previous_preset_fields(material_data)
    
    preset = get_category_preset(normalized_category)
    
    # Set category information using normalized name
    material_data["material_category"] = normalized_category
    material_data["material_category_display"] = preset.get("display_name", normalized_category)
    material_data["category_exists"] = validate_category_exists(normalized_category)
    
    # Apply preset parameters if not already set by user
    if "category_specific_parameters" not in material_data:
        material_data["category_specific_parameters"] = preset.get("category_specific_parameters", {})
    
    # Apply validation plan if not already set
    if "validation_plan" not in material_data:
        material_data["validation_plan"] = preset.get("validation_plan", {})
    
    # Apply category disclaimer
    material_data["category_specific_disclaimer"] = preset.get("category_specific_disclaimer", "")
    material_data["category_disclaimer"] = material_data["category_specific_disclaimer"]  # Alias
    
    # Apply default composition if not provided
    if not material_data.get("composition"):
        material_data["composition"] = preset.get("default_composition", [])
    
    # VALIDATE AND CLEAN composition: remove any substrate/environment objects
    material_data = clean_composition_components(material_data)
    validation = validate_composition_components(material_data)
    material_data["composition_validation"] = validation
    
    # Store characterization methods and safety tests for reference
    material_data["characterization_methods"] = preset.get("characterization_methods", [])
    material_data["safety_tests"] = preset.get("safety_tests", [])
    
    # Store processing method for PDF report (MUST BE CLEAN - from current preset only)
    material_data["processing_method"] = preset.get("processing_method", [])
    
    # Create aliases for backward compatibility with UI and PDF export
    material_data["preset_parameters"] = material_data["category_specific_parameters"]
    material_data["preset_validation_plan"] = material_data["validation_plan"]
    
    return material_data


def validate_required_fields(material_data: dict) -> dict:
    """
    Validate that material_data has all required fields.
    Returns validation report.
    """
    validation_report = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    required_fields = ["material_category", "composition", "material_category_display"]
    for field in required_fields:
        if field not in material_data or not material_data[field]:
            validation_report["is_valid"] = False
            validation_report["errors"].append(f"Missing required field: {field}")
    
    # Warn if using Other category
    if material_data.get("material_category") == "other_material":
        validation_report["warnings"].append("No category-specific preset exists for this material. The report may be incomplete.")
    
    # Warn if composition doesn't sum to 1.0
    if material_data.get("composition"):
        total_ratio = sum(c.get("ratio", 0) for c in material_data["composition"])
        if abs(total_ratio - 1.0) > 0.001:
            validation_report["warnings"].append(f"Composition ratios sum to {total_ratio:.4f} instead of 1.0")
    
    return validation_report


def format_scientific_label(text: str) -> str:
    """
    Protect scientific formatting by converting common notation to Unicode.
    
    Process:
    1. Sort patterns by length (longest first) to match specific patterns before short ones
    2. Use case-insensitive matching for most patterns
    3. Use word boundaries for short patterns like "IC" to avoid matching parts of words
    
    Examples:
        K+ -> K⁺
        SO4^2- -> SO₄²⁻
        pH -> pH
        TiO2 -> TiO₂
    """
    if not text:
        return text
    
    import re
    result = text
    
    # Process patterns - sort by length (longest first) for better matching
    # This ensures "SO4^2-" patterns are matched before shorter patterns
    sorted_patterns = sorted(SCIENTIFIC_LABEL_MAPPINGS.items(), 
                            key=lambda x: len(x[0]), 
                            reverse=True)
    
    for pattern, replacement in sorted_patterns:
        # For short patterns (1-3 chars), use word boundaries to avoid matching
        # parts of words. For longer patterns, just use direct matching.
        if len(pattern) <= 3 and pattern.isalpha():
            # Use word boundaries for short alphabetic patterns
            escaped_pattern = re.escape(pattern)
            result = re.sub(r'\b' + escaped_pattern + r'\b', replacement, result, flags=re.IGNORECASE)
        else:
            # Direct replacement for technical patterns (with numbers, symbols)
            escaped_pattern = re.escape(pattern)
            result = re.sub(escaped_pattern, replacement, result, flags=re.IGNORECASE)
    
    return result


def export_report(material_data: dict, format: str = "dict") -> dict:
    """
    Export material data ensuring all fields are properly formatted.
    
    Args:
        material_data: The enriched material data
        format: "dict" (default) or other formats as needed
        
    Returns:
        Exported report with scientific labels protected
    """
    # Create a copy to avoid modifying original
    report = material_data.copy()
    
    # Protect scientific labels in all text fields
    text_fields = [
        "material_category_display",
        "target_application",
        "category_disclaimer",
    ]
    
    for field in text_fields:
        if field in report and isinstance(report[field], str):
            report[field] = format_scientific_label(report[field])
    
    # Protect parameters descriptions
    if "preset_parameters" in report:
        protected_params = {}
        for key, value in report["preset_parameters"].items():
            if isinstance(value, str):
                protected_params[key] = format_scientific_label(value)
            else:
                protected_params[key] = value
        report["preset_parameters"] = protected_params
    
    # Protect validation plan descriptions
    if "preset_validation_plan" in report:
        protected_validation = {}
        for key, value in report["preset_validation_plan"].items():
            if isinstance(value, str):
                protected_validation[key] = format_scientific_label(value)
            else:
                protected_validation[key] = value
        report["preset_validation_plan"] = protected_validation
    
    return report


def get_category_info(category_name: str) -> dict:
    """
    Get comprehensive information about a category.
    
    Returns:
        Dictionary with display_name, aliases, priority_keywords, etc.
    """
    preset = get_category_preset(category_name)
    return {
        "normalized_name": category_name,
        "display_name": preset.get("display_name"),
        "priority": preset.get("priority"),
        "aliases": preset.get("aliases", []),
        "priority_keywords": preset.get("priority_keywords", []),
        "has_default_composition": len(preset.get("default_composition", [])) > 0,
        "parameter_count": len(preset.get("category_specific_parameters", {})),
        "validation_item_count": len(preset.get("validation_plan", {})),
    }


# ============================================================================
# DOMAIN-FIRST CLASSIFICATION FUNCTIONS
# ============================================================================

def get_available_domains() -> dict:
    """Return all available domains with their metadata."""
    return {
        domain_key: {
            "key": domain_key,
            "display_name": DOMAIN_DEFINITIONS[domain_key]["display_name"],
            "description": DOMAIN_DEFINITIONS[domain_key]["description"],
            "category_count": len(DOMAIN_DEFINITIONS[domain_key]["allowed_categories"]),
        }
        for domain_key in DOMAIN_DEFINITIONS.keys()
    }


def get_categories_for_domain(domain_key: str) -> list:
    """Get all allowed categories for a specific domain."""
    if domain_key not in DOMAIN_DEFINITIONS:
        return []
    
    allowed_cats = DOMAIN_DEFINITIONS[domain_key]["allowed_categories"]
    return [
        {
            "key": cat,
            "display_name": CATEGORY_REGISTRY.get(cat, {}).get("display_name", cat),
            "priority": CATEGORY_REGISTRY.get(cat, {}).get("priority", 999),
        }
        for cat in allowed_cats
        if cat in CATEGORY_REGISTRY
    ]


def classify_within_domain(user_request: str, selected_domain: str) -> dict:
    """
    Classify material category ONLY within the selected domain.
    
    Args:
        user_request: The user's material description
        selected_domain: The selected domain (e.g., 'battery_electrochemical')
        
    Returns:
        Classification result with category, confidence, and reasoning
    """
    if selected_domain not in DOMAIN_DEFINITIONS:
        return {
            "success": False,
            "error": f"Unknown domain: {selected_domain}",
            "category": None,
            "confidence": 0
        }
    
    allowed_categories = DOMAIN_DEFINITIONS[selected_domain]["allowed_categories"]
    
    # Classify using full classifier first
    full_classification = classify_material_category(user_request)
    suggested_category = full_classification[0] if full_classification else "other_material"
    
    # Check if suggested category is in allowed domain
    if suggested_category in allowed_categories:
        return {
            "success": True,
            "category": suggested_category,
            "domain": selected_domain,
            "category_display": CATEGORY_REGISTRY.get(suggested_category, {}).get("display_name", suggested_category),
            "confidence": full_classification[1] if len(full_classification) > 1 else 0.5,
            "restricted_to_domain": True,
            "message": f"Classification confirmed within {DOMAIN_DEFINITIONS[selected_domain]['display_name']}"
        }
    else:
        # Category falls outside domain, default to first allowed category
        default_category = allowed_categories[0] if allowed_categories else "other_material"
        return {
            "success": True,
            "category": default_category,
            "domain": selected_domain,
            "category_display": CATEGORY_REGISTRY.get(default_category, {}).get("display_name", default_category),
            "confidence": 0.3,
            "restricted_to_domain": True,
            "message": f"Classification restricted to domain: {DOMAIN_DEFINITIONS[selected_domain]['display_name']}. Using default category: {CATEGORY_REGISTRY.get(default_category, {}).get('display_name', default_category)}"
        }


def validate_domain_category_match(selected_domain: str, selected_category: str) -> dict:
    """
    Verify that the selected category belongs to the selected domain.
    
    Args:
        selected_domain: The selected domain
        selected_category: The selected category
        
    Returns:
        Validation result with match status and details
    """
    if selected_domain not in DOMAIN_DEFINITIONS:
        return {"is_valid": False, "error": f"Unknown domain: {selected_domain}"}
    
    allowed_categories = DOMAIN_DEFINITIONS[selected_domain]["allowed_categories"]
    
    if selected_category not in allowed_categories:
        return {
            "is_valid": False,
            "error": f"Category '{selected_category}' not allowed in domain '{selected_domain}'",
            "selected_domain": selected_domain,
            "selected_category": selected_category,
            "allowed_categories": allowed_categories,
        }
    
    return {
        "is_valid": True,
        "domain": selected_domain,
        "category": selected_category,
        "message": f"✅ Category matches domain"
    }


def check_forbidden_cross_domain_keywords(user_request: str, selected_domain: str, selected_category: str) -> dict:
    """
    Check if the request contains forbidden keywords from other domains.
    
    Args:
        user_request: The user's material description
        selected_domain: The selected domain
        selected_category: The selected category
        
    Returns:
        Dictionary with warnings about cross-domain keyword contamination
    """
    forbidden_keywords = DOMAIN_DEFINITIONS[selected_domain].get("forbidden_keywords", [])
    request_lower = user_request.lower()
    
    found_forbidden = []
    for keyword in forbidden_keywords:
        if keyword.lower() in request_lower:
            found_forbidden.append(keyword)
    
    if found_forbidden:
        return {
            "has_cross_domain_contamination": True,
            "forbidden_keywords_found": found_forbidden,
            "warning": f"⚠️ Request contains keywords from other domains: {', '.join(found_forbidden)}. Please confirm your domain selection."
        }
    
    return {
        "has_cross_domain_contamination": False,
        "message": "✅ No cross-domain keyword contamination detected"
    }


def validate_negative_keywords(material_data: dict, selected_category: str) -> dict:
    """
    Validate material data against negative keyword rules for the category.
    
    Args:
        material_data: The material analysis result
        selected_category: The selected category
        
    Returns:
        Validation result with issues and recommendations
    """
    if selected_category not in NEGATIVE_KEYWORD_RULES:
        return {"is_valid": True, "message": "No negative keyword rules defined for category"}
    
    rules = NEGATIVE_KEYWORD_RULES[selected_category]
    issues = []
    warnings = []
    
    # Check composition, validation plan, and processing method for contamination
    processing_method_raw = material_data.get("processing_method")
    # Handle both string and list formats for processing_method
    if isinstance(processing_method_raw, list):
        processing_method_str = " ".join(str(item) for item in processing_method_raw if item)
    else:
        processing_method_str = str(processing_method_raw or "")
    
    text_fields = [
        processing_method_str,
        str(material_data.get("composition") or ""),
        str(material_data.get("validation_plan") or ""),
    ]
    combined_text = " ".join(text_fields).lower()
    
    # Check for forbidden cross-domain keywords
    for forbidden in rules.get("forbidden_cross_domain_keywords", []):
        if forbidden.lower() in combined_text:
            issues.append(f"❌ Forbidden cross-domain keyword detected: '{forbidden}' (suggests contamination from another domain)")
    
    # Check for must-include keywords
    must_includes = rules.get("must_include_keywords", [])
    found_must_includes = sum(1 for keyword in must_includes if keyword.lower() in combined_text)
    if found_must_includes < len(must_includes) / 2:
        warnings.append(f"⚠️ Only {found_must_includes}/{len(must_includes)} characteristic keywords found. Category may be misclassified.")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "must_include_found": found_must_includes,
        "must_include_total": len(must_includes),
    }


def perform_report_self_audit(material_data: dict, selected_category: str) -> dict:
    """
    Self-audit the generated report before export to verify domain consistency.
    
    Args:
        material_data: The complete material analysis result
        selected_category: The selected category
        
    Returns:
        Audit result with pass/fail and issues found
    """
    audit_result = {
        "audit_passed": True,
        "issues": [],
        "warnings": [],
        "category": selected_category,
        "items_checked": []
    }
    
    # Get the category preset
    preset = get_category_preset(selected_category)
    if not preset:
        audit_result["audit_passed"] = False
        audit_result["issues"].append(f"Category preset not found: {selected_category}")
        return audit_result
    
    # Check 1: Composition belongs to category
    composition = material_data.get("composition", [])
    expected_components = [c.get("component", "").lower() for c in preset.get("default_composition", [])]
    actual_components = [c.get("component", "").lower() for c in composition]
    
    component_match = sum(1 for exp in expected_components for act in actual_components if exp in act or act in exp)
    if component_match < len(expected_components) * 0.5:
        audit_result["warnings"].append(f"⚠️ Composition doesn't match category preset ({component_match}/{len(expected_components)} components found)")
    audit_result["items_checked"].append("composition_match")
    
    # Check 2: Validation plan belongs to category
    expected_validations = set(preset.get("validation_plan", {}).keys())
    actual_validations = set(material_data.get("validation_plan", {}).keys())
    validation_match = len(expected_validations & actual_validations)
    if validation_match < len(expected_validations) * 0.5:
        audit_result["warnings"].append(f"⚠️ Validation plan doesn't match category ({validation_match}/{len(expected_validations)} items found)")
    audit_result["items_checked"].append("validation_plan_match")
    
    # Check 3: Processing method belongs to category
    processing_method_raw = material_data.get("processing_method")
    # Handle both string and list formats
    if isinstance(processing_method_raw, list):
        processing_method = " ".join(str(item) for item in processing_method_raw if item)
    else:
        processing_method = str(processing_method_raw or "")
    expected_processing_keywords = preset.get("priority_keywords", [])[:5]
    method_keywords_found = sum(1 for keyword in expected_processing_keywords if keyword.lower() in processing_method.lower())
    if method_keywords_found < len(expected_processing_keywords) * 0.3:
        audit_result["warnings"].append(f"⚠️ Processing method has few category-specific keywords ({method_keywords_found}/{len(expected_processing_keywords)})")
    audit_result["items_checked"].append("processing_method_match")
    
    # Check 4: Negative keyword validation
    negative_check = validate_negative_keywords(material_data, selected_category)
    if not negative_check["is_valid"]:
        audit_result["audit_passed"] = False
        audit_result["issues"].extend(negative_check["issues"])
    audit_result["items_checked"].append("negative_keywords")
    
    # Check 5: No forbidden domain terms in disclaimer
    disclaimer = (material_data.get("category_disclaimer") or "").lower()
    category_domain = CATEGORY_TO_DOMAIN_SPECIFIC.get(selected_category, "unknown")
    if category_domain in DOMAIN_DEFINITIONS:
        forbidden_terms = DOMAIN_DEFINITIONS[category_domain].get("forbidden_keywords", [])
        found_forbidden_in_disclaimer = [term for term in forbidden_terms if term.lower() in disclaimer]
        if found_forbidden_in_disclaimer:
            audit_result["warnings"].append(f"⚠️ Disclaimer contains forbidden cross-domain terms: {', '.join(found_forbidden_in_disclaimer)}")
    audit_result["items_checked"].append("disclaimer_cross_domain")
    
    # Summary
    audit_result["summary"] = f"Audit checked {len(audit_result['items_checked'])} items: " + \
                             f"{'✅ PASSED' if audit_result['audit_passed'] else '❌ FAILED'} " + \
                             f"({len(audit_result['warnings'])} warnings, {len(audit_result['issues'])} issues)"
    
    return audit_result
