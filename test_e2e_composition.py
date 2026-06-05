#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive test of composition validation in the complete workflow"""

from category_registry import (
    classify_material_hierarchically,
    apply_category_preset,
    validate_composition_components,
    clean_composition_components,
    run_three_stage_verification,
)

print("=" * 80)
print("END-TO-END COMPOSITION VALIDATION TEST")
print("=" * 80)

# Test Case 1: Photocatalytic coating request
print("\n" + "=" * 80)
print("TEST 1: Photocatalytic Coating Classification & Composition Validation")
print("=" * 80)

user_request_1 = "Photocatalytic TiO2 coating for water purification using UV light"
print(f"\nUser Request: {user_request_1}")

# Step 1: Classify
result_1 = classify_material_hierarchically(user_request_1)
print(f"\nClassification Result:")
print(f"  Category: {result_1['specific_preset']}")
print(f"  Confidence: {result_1['confidence_score']:.1%}")

# Step 2: Apply preset
result_1 = apply_category_preset(result_1, result_1['specific_preset'])
print(f"\nAfter Preset Application:")
print(f"  Composition items: {len(result_1.get('composition', []))}")
print(f"  Composition validation: {result_1.get('composition_validation', {}).get('is_valid', 'unknown')}")

# Step 3: Verify composition
validation_1 = validate_composition_components(result_1)
print(f"\nComposition Validation:")
print(f"  Valid: {validation_1['is_valid']}")
print(f"  Invalid items: {len(validation_1['invalid_items'])}")
print(f"  Message: {validation_1['message']}")

if validation_1['is_valid']:
    print("\n✅ PASS: Composition is valid - no substrate/environment items found!")
else:
    print("\n❌ FAIL: Invalid items detected!")

# Display composition
print(f"\nComposition Details:")
for item in result_1.get('composition', []):
    print(f"  - {item.get('component', 'unknown')}: {item.get('ratio', 0)*100:.1f}%")

# Test Case 2: Roof waterproofing request
print("\n" + "=" * 80)
print("TEST 2: Roof Waterproofing Coating Classification & Composition Validation")
print("=" * 80)

user_request_2 = "Roof waterproofing and thermal insulation composite coating for concrete"
print(f"\nUser Request: {user_request_2}")

result_2 = classify_material_hierarchically(user_request_2)
print(f"\nClassification Result:")
print(f"  Category: {result_2['specific_preset']}")
print(f"  Confidence: {result_2['confidence_score']:.1%}")

result_2 = apply_category_preset(result_2, result_2['specific_preset'])
print(f"\nAfter Preset Application:")
print(f"  Composition items: {len(result_2.get('composition', []))}")
print(f"  Composition validation: {result_2.get('composition_validation', {}).get('is_valid', 'unknown')}")

validation_2 = validate_composition_components(result_2)
print(f"\nComposition Validation:")
print(f"  Valid: {validation_2['is_valid']}")
print(f"  Invalid items: {len(validation_2['invalid_items'])}")
print(f"  Message: {validation_2['message']}")

if validation_2['is_valid']:
    print("\n✅ PASS: Composition is valid - no substrate/environment items found!")
else:
    print("\n❌ FAIL: Invalid items detected!")

# Test Case 3: Atmospheric water harvesting
print("\n" + "=" * 80)
print("TEST 3: Atmospheric Water Harvesting Material")
print("=" * 80)

user_request_3 = "Porous material for atmospheric water harvesting using activated carbon"
print(f"\nUser Request: {user_request_3}")

result_3 = classify_material_hierarchically(user_request_3)
print(f"\nClassification Result:")
print(f"  Category: {result_3['specific_preset']}")
print(f"  Confidence: {result_3['confidence_score']:.1%}")

result_3 = apply_category_preset(result_3, result_3['specific_preset'])
print(f"\nAfter Preset Application:")
print(f"  Composition items: {len(result_3.get('composition', []))}")
print(f"  Composition validation: {result_3.get('composition_validation', {}).get('is_valid', 'unknown')}")

validation_3 = validate_composition_components(result_3)
print(f"\nComposition Validation:")
print(f"  Valid: {validation_3['is_valid']}")
print(f"  Invalid items: {len(validation_3['invalid_items'])}")

if validation_3['is_valid']:
    print("\n✅ PASS: Composition is valid!")
else:
    print("\n❌ FAIL: Invalid items detected!")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

test_results = [
    ("Photocatalytic Coating", validation_1['is_valid']),
    ("Roof Waterproofing", validation_2['is_valid']),
    ("Water Harvesting", validation_3['is_valid']),
]

passed = sum(1 for _, valid in test_results if valid)
total = len(test_results)

for test_name, is_valid in test_results:
    status = "✅ PASS" if is_valid else "❌ FAIL"
    print(f"  {status}: {test_name}")

print(f"\nTotal: {passed}/{total} tests passed")
if passed == total:
    print("\n✅ ALL TESTS PASSED - Global composition validation working!")
else:
    print(f"\n❌ {total - passed} TEST(S) FAILED")

print("=" * 80)
