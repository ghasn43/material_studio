#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test composition validation and cleaning functions"""

from category_registry import (
    validate_composition_components,
    clean_composition_components,
    apply_category_preset,
)

# Test 1: Validate incorrect photocatalytic composition (with substrate)
print("=" * 70)
print("TEST 1: Validate composition with substrate (SHOULD FAIL)")
print("=" * 70)

test_data_1 = {
    "composition": [
        {"component": "TiO2 photocatalyst", "ratio": 0.15},
        {"component": "Binder (silica or polymer)", "ratio": 0.20},
        {"component": "Glass substrate", "ratio": 0.65},  # INVALID!
    ]
}

validation_1 = validate_composition_components(test_data_1)
print(f"Valid: {validation_1['is_valid']}")
print(f"Invalid items found: {validation_1['invalid_items']}")
print(f"Message: {validation_1['message']}")
print()

# Test 2: Clean composition with substrate
print("=" * 70)
print("TEST 2: Clean composition with substrate")
print("=" * 70)

test_data_2 = {
    "composition": [
        {"component": "TiO2 photocatalyst", "ratio": 0.15},
        {"component": "Binder (silica or polymer)", "ratio": 0.20},
        {"component": "Ceramic substrate", "ratio": 0.65},  # INVALID!
    ]
}

cleaned_2 = clean_composition_components(test_data_2)
print(f"Original items: {len(test_data_2['composition'])}")
print(f"Cleaned items: {len(cleaned_2['composition'])}")
print(f"Warning: {cleaned_2.get('composition_warning', 'None')}")
print(f"Remaining composition:")
for item in cleaned_2['composition']:
    print(f"  - {item['component']}: {item['ratio']*100}%")
print()

# Test 3: Apply photocatalytic preset (should use correct 40-20-20-10-10)
print("=" * 70)
print("TEST 3: Apply photocatalytic_coating preset (40-20-20-10-10)")
print("=" * 70)

test_data_3 = {"material_name": "Durable photocatalytic coating"}
preset_applied = apply_category_preset(test_data_3, "photocatalytic_coating")

print(f"Category: {preset_applied.get('material_category')}")
print(f"Composition items: {len(preset_applied.get('composition', []))}")
print(f"Composition validation valid: {preset_applied.get('composition_validation', {}).get('is_valid', 'unknown')}")
print(f"Composition:")
for item in preset_applied.get('composition', []):
    print(f"  - {item['component']}: {item['ratio']*100}%")
print(f"Warning: {preset_applied.get('composition_warning', 'None')}")
print()

# Test 4: Valid composition (no substrates)
print("=" * 70)
print("TEST 4: Validate valid composition (NO SUBSTRATES)")
print("=" * 70)

test_data_4 = {
    "composition": [
        {"component": "Titanium dioxide (TiO2)", "ratio": 0.40},
        {"component": "Biochar", "ratio": 0.20},
        {"component": "Silica support", "ratio": 0.20},
        {"component": "Alumina stabilizer", "ratio": 0.10},
        {"component": "Polymer binder", "ratio": 0.10},
    ]
}

validation_4 = validate_composition_components(test_data_4)
print(f"Valid: {validation_4['is_valid']}")
print(f"Invalid items found: {validation_4['invalid_items']}")
print(f"Message: {validation_4['message']}")
print()

# Test 5: Test with various substrate types
print("=" * 70)
print("TEST 5: Test detection of various invalid items")
print("=" * 70)

invalid_test_cases = [
    {"component": "Concrete rooftop", "ratio": 0.5},
    {"component": "Cotton clothing", "ratio": 0.3},
    {"component": "Treated water", "ratio": 0.4},
    {"component": "Flue gas stream", "ratio": 0.25},
    {"component": "Desalination membrane", "ratio": 0.15},
]

for case in invalid_test_cases:
    test_data = {"composition": [case]}
    validation = validate_composition_components(test_data)
    status = "❌ INVALID" if not validation['is_valid'] else "✅ VALID"
    print(f"{status}: {case['component']}")

print()
print("=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)
