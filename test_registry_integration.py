"""
Test Registry Integration
Tests that the central CATEGORY_REGISTRY is properly integrated into app.py
and that all material categories work correctly.
"""

import sys
import os
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the registry functions
from category_registry import (
    classify_material_category,
    get_category_preset,
    apply_category_preset,
    validate_required_fields,
    format_scientific_label,
    get_category_info,
    CATEGORY_REGISTRY,
    SCIENTIFIC_LABEL_MAPPINGS,
)

# Import app functions
from app import detect_material_category, generate_fallback_result, enrich_with_preset


def test_classification_priority():
    """Test that classification respects priority order."""
    print("\n" + "="*70)
    print("TEST 1: Classification Priority")
    print("="*70)
    
    test_cases = [
        ("anti-fouling membrane design", "membrane_water_treatment"),
        ("potassium recovery from brine", "potassium_brine_separation_material"),
        ("phosphate recovery from wastewater", "phosphate_recovery_material"),
        ("TiO2 photocatalytic coating", "photocatalytic_coating"),
        ("water harvesting from air", "atmospheric_water_harvesting_material"),
        ("heavy metal adsorbent", "adsorbent_heavy_metals"),
        ("custom material", "other_material"),
    ]
    
    passed = 0
    for user_input, expected_category in test_cases:
        classified_key, display_name, confidence = classify_material_category(user_input)
        status = "✓ PASS" if classified_key == expected_category else "✗ FAIL"
        print(f"{status}: '{user_input}'")
        print(f"   Expected: {expected_category}, Got: {classified_key} (confidence: {confidence}%)")
        if classified_key == expected_category:
            passed += 1
    
    print(f"\nResult: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_preset_application():
    """Test that presets are correctly applied to materials."""
    print("\n" + "="*70)
    print("TEST 2: Preset Application")
    print("="*70)
    
    categories_to_test = [
        "membrane_water_treatment",
        "atmospheric_water_harvesting_material",
        "photocatalytic_coating",
        "phosphate_recovery_material",
        "potassium_brine_separation_material",
        "adsorbent_heavy_metals",
    ]
    
    passed = 0
    for category_key in categories_to_test:
        preset = get_category_preset(category_key)
        
        # Check required fields
        has_name = "normalized_category_name" in preset
        has_params = "category_specific_parameters" in preset
        has_validation = "validation_plan" in preset
        has_composition = "default_composition" in preset
        has_disclaimer = "category_specific_disclaimer" in preset
        
        all_present = has_name and has_params and has_validation and has_composition and has_disclaimer
        status = "✓ PASS" if all_present else "✗ FAIL"
        
        print(f"{status}: {category_key}")
        if not all_present:
            print(f"   Missing: ", end="")
            missing = []
            if not has_name: missing.append("name")
            if not has_params: missing.append("parameters")
            if not has_validation: missing.append("validation")
            if not has_composition: missing.append("composition")
            if not has_disclaimer: missing.append("disclaimer")
            print(", ".join(missing))
        else:
            info = get_category_info(category_key)
            print(f"   {info['parameter_count']} parameters, {info['validation_item_count']} validation items")
            passed += 1
    
    print(f"\nResult: {passed}/{len(categories_to_test)} tests passed")
    return passed == len(categories_to_test)


def test_scientific_label_formatting():
    """Test that scientific labels are correctly formatted."""
    print("\n" + "="*70)
    print("TEST 3: Scientific Label Formatting")
    print("="*70)
    
    test_cases = [
        ("K+ ions", "K⁺ ions"),
        ("SO4^2- sulfate", "SO₄²⁻ sulfate"),
        ("pH 7", "pH 7"),
        ("TiO2 particles", "TiO₂ particles"),
        ("Measure K+ and Pb2+ with ICP-OES at pH 5-7", "Measure K⁺ and Pb²⁺ with ICP-OES at pH 5-7"),
        ("Mg2+ and Ca2+", "Mg²⁺ and Ca²⁺"),
        ("HCO3^- bicarbonate", "HCO₃⁻ bicarbonate"),
    ]
    
    passed = 0
    for input_text, expected_output in test_cases:
        result = format_scientific_label(input_text)
        status = "✓ PASS" if result == expected_output else "✗ FAIL"
        print(f"{status}: '{input_text}'")
        if result != expected_output:
            print(f"   Expected: '{expected_output}'")
            print(f"   Got:      '{result}'")
        else:
            passed += 1
    
    print(f"\nResult: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_fallback_generation():
    """Test that fallback results are correctly generated from presets."""
    print("\n" + "="*70)
    print("TEST 4: Fallback Generation")
    print("="*70)
    
    user_requests = [
        "Design an anti-fouling membrane for water treatment",
        "Extract potassium from agricultural brine",
        "Recover phosphate from wastewater",
    ]
    
    passed = 0
    for request in user_requests:
        result = generate_fallback_result(request)
        
        # Check required fields
        has_category = "material_category" in result
        has_composition = "composition" in result and len(result["composition"]) > 0
        has_parameters = "preset_parameters" in result
        has_validation = "preset_validation_plan" in result
        has_disclaimer = "category_disclaimer" in result
        has_fallback_flag = "is_fallback" in result and result["is_fallback"] is True
        
        all_present = has_category and has_composition and has_parameters and has_validation and has_disclaimer and has_fallback_flag
        
        status = "✓ PASS" if all_present else "✗ FAIL"
        print(f"{status}: {request[:50]}...")
        
        if not all_present:
            print(f"   Missing: ", end="")
            missing = []
            if not has_category: missing.append("category")
            if not has_composition: missing.append("composition")
            if not has_parameters: missing.append("parameters")
            if not has_validation: missing.append("validation")
            if not has_disclaimer: missing.append("disclaimer")
            if not has_fallback_flag: missing.append("fallback_flag")
            print(", ".join(missing))
        else:
            category = result.get("material_category")
            comp_count = len(result.get("composition", []))
            param_count = len(result.get("preset_parameters", {}))
            validation_count = len(result.get("preset_validation_plan", {}))
            print(f"   Category: {category}")
            print(f"   Composition: {comp_count} components, Parameters: {param_count}, Validation: {validation_count}")
            passed += 1
    
    print(f"\nResult: {passed}/{len(user_requests)} tests passed")
    return passed == len(user_requests)


def test_enrich_with_preset_integration():
    """Test that enrich_with_preset properly applies registry presets."""
    print("\n" + "="*70)
    print("TEST 5: Enrich with Preset Integration")
    print("="*70)
    
    ai_results = [
        {
            "target_application": "Membrane design for water treatment",
            "composition": [{"component": "PVDF polymer", "ratio": 0.5}],
            "user_defined_parameters": {},
            "user_defined_validation": {},
        },
        {
            "target_application": "Heavy metal removal",
            "composition": [{"component": "Activated carbon", "ratio": 0.3}],
            "user_defined_parameters": {},
            "user_defined_validation": {},
        },
    ]
    
    user_requests = [
        "Design an anti-fouling membrane",
        "Remove lead and cadmium from water",
    ]
    
    expected_categories = [
        "membrane_water_treatment",
        "adsorbent_heavy_metals",
    ]
    
    passed = 0
    for i, (request, ai_result, expected_cat) in enumerate(zip(user_requests, ai_results, expected_categories)):
        enriched = enrich_with_preset(request, ai_result)
        
        has_category = enriched.get("material_category") == expected_cat
        has_preset_params = len(enriched.get("preset_parameters", {})) > 0
        has_preset_validation = len(enriched.get("preset_validation_plan", {})) > 0
        has_disclaimer = "category_disclaimer" in enriched
        
        all_correct = has_category and has_preset_params and has_preset_validation and has_disclaimer
        
        status = "✓ PASS" if all_correct else "✗ FAIL"
        print(f"{status}: {request[:50]}...")
        
        if not all_correct:
            print(f"   Category match: {has_category} (expected {expected_cat}, got {enriched.get('material_category')})")
            print(f"   Has preset parameters: {has_preset_params}")
            print(f"   Has preset validation: {has_preset_validation}")
            print(f"   Has disclaimer: {has_disclaimer}")
        else:
            passed += 1
    
    print(f"\nResult: {passed}/{len(user_requests)} tests passed")
    return passed == len(user_requests)


def test_detect_material_category_wrapper():
    """Test that the app.py wrapper function works correctly."""
    print("\n" + "="*70)
    print("TEST 6: detect_material_category Wrapper Function")
    print("="*70)
    
    test_cases = [
        ("anti-fouling PVDF membrane", "membrane_water_treatment"),
        ("moisture capture material", "atmospheric_water_harvesting_material"),
        ("photocatalytic TiO2 coating", "photocatalytic_coating"),
        ("phosphate recovery from agricultural runoff", "phosphate_recovery_material"),
        ("potassium selective sorbent", "potassium_brine_separation_material"),
        ("lead and cadmium adsorbent", "adsorbent_heavy_metals"),
    ]
    
    passed = 0
    for user_input, expected_category in test_cases:
        category_key, display_name = detect_material_category(user_input)
        status = "✓ PASS" if category_key == expected_category else "✗ FAIL"
        print(f"{status}: {user_input[:50]}...")
        if category_key == expected_category:
            passed += 1
            print(f"   Correctly classified as: {display_name}")
        else:
            print(f"   Expected: {expected_category}, Got: {category_key}")
    
    print(f"\nResult: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def main():
    """Run all integration tests."""
    print("\n" + "#"*70)
    print("# REGISTRY INTEGRATION TEST SUITE")
    print("#"*70)
    
    test_results = {
        "Classification Priority": test_classification_priority(),
        "Preset Application": test_preset_application(),
        "Scientific Label Formatting": test_scientific_label_formatting(),
        "Fallback Generation": test_fallback_generation(),
        "Enrich with Preset": test_enrich_with_preset_integration(),
        "detect_material_category Wrapper": test_detect_material_category_wrapper(),
    }
    
    print("\n" + "#"*70)
    print("# SUMMARY")
    print("#"*70)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for v in test_results.values() if v)
    
    for test_name, passed in test_results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} test groups passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Registry integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test group(s) failed. Review output above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
