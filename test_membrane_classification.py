"""
Test Suite for Membrane Water Treatment Category Preset
========================================================
Tests keyword detection, classification priority, and preset loading.
"""

import sys
import json
sys.path.insert(0, 'd:\\material_studio_1')

from app import detect_material_category, MATERIAL_PRESETS, generate_fallback_composition

# User's original request (the one that was mis-classified as Heavy Metal Adsorbent)
user_request = """Design an anti-fouling membrane for water treatment using a polymer membrane matrix, 
hydrophilic additives, silica nanoparticles, activated carbon, and optional antimicrobial stabilizers. 
The membrane should reduce organic fouling, improve water flux, and maintain contaminant rejection under 
repeated filtration cycles. The design must be tested for permeability, rejection efficiency, fouling 
resistance, cleaning recovery, nanoparticle leaching, and mechanical durability."""

print("=" * 80)
print("MEMBRANE WATER TREATMENT CLASSIFICATION TEST SUITE")
print("=" * 80)
print()

# Test 1: Classification of user's original request
print("[TEST 1] User Request Classification")
print("-" * 80)
print(f"Request: {user_request[:100]}...")
preset_key, display_name = detect_material_category(user_request)
print(f"Detected Category: {preset_key}")
print(f"Display Name: {display_name}")
expected = "membrane_water_treatment"
result_1 = preset_key == expected
print(f"PASS" if result_1 else f"FAIL - Expected {expected}, got {preset_key}")
print()

# Test 2: Verify not classified as Heavy Metal Adsorbent
print("[TEST 2] Verify NOT classified as Heavy Metal Adsorbent")
print("-" * 80)
result_2 = preset_key != "adsorbent_heavy_metals"
print(f"Classification is NOT adsorbent_heavy_metals: {result_2}")
print(f"PASS" if result_2 else f"FAIL - Request was incorrectly classified as adsorbent_heavy_metals")
print()

# Test 3: Keyword detection with various membrane keywords
print("[TEST 3] Keyword Detection - Multiple Prompts")
print("-" * 80)
test_prompts = [
    "Design an anti-fouling membrane for water treatment",
    "Create a PVDF polymer membrane with hydrophilic additives",
    "Develop a PES ultrafiltration membrane with improved water flux",
    "Design a nanofiltration membrane with mixed-matrix structure for contaminant rejection",
    "Create an anti-fouling polymer membrane matrix with silica nanoparticles",
]
keyword_tests = []
for i, prompt in enumerate(test_prompts, 1):
    key, name = detect_material_category(prompt)
    is_correct = key == "membrane_water_treatment"
    keyword_tests.append(is_correct)
    status = "PASS" if is_correct else "FAIL"
    print(f"{status} Test {i}: {prompt[:60]}... -> {key}")

result_3 = all(keyword_tests)
print(f"\nOverall: {sum(keyword_tests)}/{len(keyword_tests)} tests passed")
print(f"PASS" if result_3 else f"FAIL - Some prompts not classified as membrane_water_treatment")
print()

# Test 4: Preset structure verification
print("[TEST 4] Membrane Preset Structure Verification")
print("-" * 80)
membrane_preset = MATERIAL_PRESETS.get("membrane_water_treatment", {})
required_fields = ["display_name", "keywords", "parameters", "validation_plan", "category_disclaimer"]
structure_checks = []
for field in required_fields:
    has_field = field in membrane_preset
    structure_checks.append(has_field)
    status = "OK" if has_field else "MISSING"
    print(f"{status} Field '{field}': {'Present' if has_field else 'Missing'}")

if "keywords" in membrane_preset:
    keyword_count = len(membrane_preset["keywords"])
    print(f"  Keywords count: {keyword_count}")

if "parameters" in membrane_preset:
    param_count = len(membrane_preset["parameters"])
    print(f"  Parameters count: {param_count}")
    print(f"  Parameters: {list(membrane_preset['parameters'].keys())}")

if "validation_plan" in membrane_preset:
    validation_count = len(membrane_preset["validation_plan"])
    print(f"  Validation plan items: {validation_count}")

result_4 = all(structure_checks)
print(f"PASS" if result_4 else f"FAIL - Missing required fields")
print()

# Test 5: Fallback composition verification
print("[TEST 5] Fallback Composition Verification")
print("-" * 80)
composition = generate_fallback_composition("membrane_water_treatment")
component_count = len(composition)
print(f"Component count: {component_count}")
if component_count > 0:
    print("Components:")
    total_ratio = 0
    for comp in composition:
        print(f"  • {comp['component']}: {comp['ratio']:.2f} ({comp['ratio']*100:.1f}%)")
        total_ratio += comp['ratio']
    
    ratio_sum_correct = abs(total_ratio - 1.0) < 0.001
    print(f"\nTotal ratio: {total_ratio:.4f}")
    result_5 = component_count == 6 and ratio_sum_correct
    print(f"PASS - 6 components, sum to 1.0" if result_5 else f"FAIL - Expected 6 components summing to 1.0")
else:
    result_5 = False
    print("FAIL - No composition found")
print()

# Test 6: Verify membrane-specific parameters (not heavy-metal parameters)
print("[TEST 6] Verify Membrane-Specific Parameters (NOT Heavy Metal)")
print("-" * 80)
membrane_params = membrane_preset.get("parameters", {})
expected_membrane_params = [
    "membrane_type", "water_flux_target", "operating_pressure", "rejection_target",
    "fouling_resistance", "cleaning_recovery_target", "pore_size_or_mwco", 
    "contact_angle", "nanoparticle_leaching_test"
]
non_allowed_heavy_metal_params = ["target_ions", "initial_metal_concentration", "adsorbent_dosage"]

param_check = all(param in membrane_params for param in expected_membrane_params[:5])
no_metal_params = not any(param in membrane_params for param in non_allowed_heavy_metal_params)

print(f"Has membrane-specific parameters: {param_check}")
print(f"Does NOT contain heavy-metal parameters: {no_metal_params}")

if param_check:
    print(f"  Present membrane params: {list(membrane_params.keys())}")

result_6 = param_check and no_metal_params
print(f"PASS" if result_6 else f"FAIL - Parameters structure incorrect")
print()

# Test 7: Verify disclaimer content
print("[TEST 7] Verify Category-Specific Disclaimer")
print("-" * 80)
disclaimer = membrane_preset.get("category_disclaimer", "")
membrane_specific_terms = ["membrane", "permeability", "contaminant rejection", "anti-fouling", "cleaning recovery"]
heavy_metal_terms = ["heavy metal", "Pb", "Cd", "As", "Cr", "ion removal", "leaching safety"]

membrane_terms_present = [term in disclaimer for term in membrane_specific_terms]
heavy_metal_terms_absent = [term not in disclaimer for term in heavy_metal_terms]

print(f"Disclaimer length: {len(disclaimer)} characters")
print(f"Contains membrane-specific language: {sum(membrane_terms_present)}/{len(membrane_specific_terms)}")
print(f"  - 'membrane': {'YES' if 'membrane' in disclaimer else 'NO'}")
print(f"  - 'permeability': {'YES' if 'permeability' in disclaimer else 'NO'}")
print(f"  - 'contaminant rejection': {'YES' if 'contaminant rejection' in disclaimer else 'NO'}")
print(f"  - 'anti-fouling': {'YES' if 'anti-fouling' in disclaimer else 'NO'}")

print(f"Does NOT contain heavy-metal language: {sum(heavy_metal_terms_absent)}/{len(heavy_metal_terms)}")

result_7 = all(membrane_terms_present) and all(heavy_metal_terms_absent)
print(f"PASS" if result_7 else f"FAIL - Disclaimer content incorrect")
print()

# Test 8: Priority check - membrane keywords should take precedence
print("[TEST 8] Classification Priority - Membrane vs Heavy Metal Keywords")
print("-" * 80)
hybrid_request = """Design an anti-fouling membrane for water treatment with a polymer matrix, 
silica nanoparticles, and activated carbon. The water may contain heavy metals from industrial discharge, 
but the primary objective is to reduce organic fouling and improve filtration efficiency."""

key, name = detect_material_category(hybrid_request)
print(f"Hybrid request (membrane + heavy metal words): {key}")
print(f"Classification is membrane_water_treatment: {key == 'membrane_water_treatment'}")
result_8 = key == "membrane_water_treatment"
print(f"PASS - Membrane keywords took priority" if result_8 else f"FAIL - Should be membrane_water_treatment")
print()

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
results = [result_1, result_2, result_3, result_4, result_5, result_6, result_7, result_8]
test_names = [
    "User request classification",
    "NOT classified as Heavy Metal Adsorbent",
    "Keyword detection (5 test prompts)",
    "Preset structure verification",
    "Fallback composition (6 components, sum to 1.0)",
    "Membrane-specific parameters (NOT heavy metal)",
    "Category-specific disclaimer",
    "Classification priority (membrane vs heavy metal)"
]
for i, (name, result) in enumerate(zip(test_names, results), 1):
    status = "PASS" if result else "FAIL"
    print(f"[{i}] {name}: {status}")

total_passed = sum(results)
total_tests = len(results)
print(f"\nTotal: {total_passed}/{total_tests} tests passed")
if total_passed == total_tests:
    print("\n=== ALL TESTS PASSED ===")
else:
    print(f"\n=== {total_tests - total_passed} TEST(S) FAILED ===")
    sys.exit(1)
