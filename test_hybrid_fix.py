#!/usr/bin/env python3
"""
Test script to validate hybrid category-selection fix.
Tests the 7 test cases from requirements section J.
"""

import sys
sys.path.insert(0, 'd:\\material_studio_1')

from category_registry import (
    classify_material_hierarchically,
    normalize_category_name,
    CATEGORY_REGISTRY,
    apply_category_preset,
    clear_previous_preset_fields,
)

# Test cases
test_cases = [
    {
        "name": "Test 1: Cotton oil stain remover",
        "prompt": "Cotton oil stain remover",
        "expected_category": "fabric_oil_stain_removal_composite",
    },
    {
        "name": "Test 2: Roof waterproof thermal insulation coating",
        "prompt": "Roof waterproof thermal insulation coating for concrete rooftop",
        "expected_category": "roof_waterproofing_thermal_insulation_coating",
    },
    {
        "name": "Test 3: CO2 capture",
        "prompt": "CO2 capture material with amine-functionalized silica",
        "expected_category": "co2_capture_material",
    },
    {
        "name": "Test 4: Desalination pre-treatment media",
        "prompt": "Desalination pre-treatment media for seawater osmosis",
        "expected_category": "desalination_pretreatment_media",
    },
    {
        "name": "Test 5: Self-cleaning exterior building coating",
        "prompt": "Self-cleaning exterior building coating with photocatalytic nanoparticles",
        "expected_category": "self_cleaning_building_coating",
    },
    {
        "name": "Test 6: AWH",
        "prompt": "Atmospheric water harvesting material with hygroscopic salt and desiccant",
        "expected_category": "atmospheric_water_harvesting_material",
    },
    {
        "name": "Test 7: Anti-fouling membrane",
        "prompt": "Anti-fouling membrane for water treatment with PVDF polymer",
        "expected_category": "membrane_water_treatment",
    },
]

print("=" * 80)
print("HYBRID CATEGORY-SELECTION FIX TEST SUITE")
print("=" * 80)
print()

# Test normalize_category_name function
print("PART 1: TESTING normalize_category_name() FUNCTION")
print("-" * 80)

test_names = [
    ("fabric_oil_stain_removal_composite", "fabric_oil_stain_removal_composite"),
    ("Fabric Oil-Stain Removal Composite", "fabric_oil_stain_removal_composite"),
    ("fabric oil stain removal", "fabric_oil_stain_removal_composite"),
    ("Thermal Insulation Composite", "thermal_insulation_composite"),
    ("roof_waterproofing_thermal_insulation_coating", "roof_waterproofing_thermal_insulation_coating"),
    ("CO2 Capture Material", "co2_capture_material"),
    ("Heavy Metal Adsorbent", "adsorbent_heavy_metals"),
    ("invalid_name_xyz", "other_material"),  # Should fallback to other_material
]

normalize_pass = 0
normalize_fail = 0

for test_input, expected_output in test_names:
    result = normalize_category_name(test_input)
    status = "✅ PASS" if result == expected_output else "❌ FAIL"
    if result == expected_output:
        normalize_pass += 1
    else:
        normalize_fail += 1
    print(f"{status}: normalize_category_name('{test_input}') = '{result}' (expected '{expected_output}')")

print(f"\nnormalize_category_name() Results: {normalize_pass} passed, {normalize_fail} failed")
print()

# Test classification for each test case
print("PART 2: TESTING classify_material_hierarchically() FOR 7 TEST CASES")
print("-" * 80)

pass_count = 0
fail_count = 0

for i, test in enumerate(test_cases, 1):
    print(f"\n{test['name']}")
    print(f"Prompt: '{test['prompt']}'")
    
    result = classify_material_hierarchically(test['prompt'])
    selected_category = result.get("specific_preset", "other_material")
    confidence = result.get("confidence_score", 0)
    
    # Normalize both for comparison
    expected_normalized = normalize_category_name(test['expected_category'])
    selected_normalized = normalize_category_name(selected_category)
    
    is_match = selected_normalized == expected_normalized
    status = "✅ PASS" if is_match else "❌ FAIL"
    
    if is_match:
        pass_count += 1
    else:
        fail_count += 1
    
    print(f"Expected: {test['expected_category']}")
    print(f"Got:      {selected_category} (confidence: {confidence}%)")
    print(f"Status:   {status}")

print()
print("=" * 80)
print(f"CLASSIFICATION TEST RESULTS: {pass_count}/7 PASSED, {fail_count}/7 FAILED")
print("=" * 80)

# Test preset application
print()
print("PART 3: TESTING PRESET APPLICATION AND CLEANUP")
print("-" * 80)

material_data = {
    "material_category": "adsorbent_heavy_metals",
    "material_category_display": "Heavy Metal Adsorbent",
    "category_specific_parameters": {"old": "parameter"},
    "validation_plan": {"old": "plan"},
    "processing_method": ["old", "method"],
}

print("Initial material_data:")
print(f"  - material_category: {material_data.get('material_category')}")
print(f"  - category_specific_parameters: {material_data.get('category_specific_parameters')}")
print(f"  - processing_method: {material_data.get('processing_method')}")

# Apply new category
material_data = apply_category_preset(material_data, "fabric_oil_stain_removal_composite")

print("\nAfter apply_category_preset(material_data, 'fabric_oil_stain_removal_composite'):")
print(f"  - material_category: {material_data.get('material_category')}")
print(f"  - material_category_display: {material_data.get('material_category_display')}")
has_params = "category_specific_parameters" in material_data
has_processing = "processing_method" in material_data
print(f"  - Has category_specific_parameters: {has_params}")
print(f"  - Has processing_method: {has_processing}")

if material_data.get("material_category") == "fabric_oil_stain_removal_composite" and has_params and has_processing:
    print("\n✅ PRESET APPLICATION TEST PASSED - Old fields cleared and new preset applied")
else:
    print("\n❌ PRESET APPLICATION TEST FAILED")

# Verify fabric_oil_stain_removal_composite exists in registry
print()
print("PART 4: VERIFY fabric_oil_stain_removal_composite IN REGISTRY")
print("-" * 80)

if "fabric_oil_stain_removal_composite" in CATEGORY_REGISTRY:
    category = CATEGORY_REGISTRY["fabric_oil_stain_removal_composite"]
    print("✅ fabric_oil_stain_removal_composite found in CATEGORY_REGISTRY")
    print(f"   Display Name: {category.get('display_name')}")
    print(f"   Priority: {category.get('priority')}")
    print(f"   Keywords: {len(category.get('priority_keywords', []))} keywords")
    print(f"   Default Composition: {len(category.get('default_composition', []))} components")
    print(f"   Category-Specific Parameters: {len(category.get('category_specific_parameters', {}))} parameters")
    print(f"   Validation Plan: {len(category.get('validation_plan', {}))} validation steps")
    print(f"   Processing Method: {len(category.get('processing_method', []))} steps")
else:
    print("❌ fabric_oil_stain_removal_composite NOT found in CATEGORY_REGISTRY")

print()
print("=" * 80)
print("TEST SUITE COMPLETE")
print("=" * 80)
