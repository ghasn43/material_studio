#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the new Oil & Gas Produced-Water Pre-Treatment Media category"""

from category_registry import (
    classify_material_hierarchically,
    apply_category_preset,
    detect_category_conflicts,
    normalize_category_name,
    CATEGORY_REGISTRY,
)

print("=" * 80)
print("OIL & GAS PRODUCED-WATER PRE-TREATMENT MEDIA CATEGORY TEST")
print("=" * 80)

# Test 1: Verify category exists in registry
print("\n" + "=" * 80)
print("TEST 1: Verify category exists in registry")
print("=" * 80)

category_key = "oil_gas_produced_water_pretreatment_media"
if category_key in CATEGORY_REGISTRY:
    category = CATEGORY_REGISTRY[category_key]
    print(f"✅ Category found: {category['display_name']}")
    print(f"   Display name: {category['display_name']}")
    print(f"   Composition items: {len(category['default_composition'])}")
    print(f"   Parameters: {len(category['category_specific_parameters'])}")
else:
    print(f"❌ Category NOT found in registry!")

# Test 2: Test normalization
print("\n" + "=" * 80)
print("TEST 2: Test category name normalization")
print("=" * 80)

test_names = [
    "oil_gas_produced_water_pretreatment_media",
    "Oil & Gas Produced-Water Pre-Treatment Media",
    "produced water pre-treatment",
    "oilfield water pre-treatment",
    "ADNOC pre-treatment",
]

for test_name in test_names:
    normalized = normalize_category_name(test_name)
    status = "✅" if normalized == category_key else "❌"
    print(f"{status} {test_name} → {normalized}")

# Test 3: Classification with oil/gas keywords
print("\n" + "=" * 80)
print("TEST 3: Classification with oil/gas keywords")
print("=" * 80)

test_requests = [
    ("Produced water pre-treatment media for ADNOC oil/gas operations", "oil_gas_produced_water_pretreatment_media"),
    ("High-salinity produced water treatment for reinjection and reuse", "oil_gas_produced_water_pretreatment_media"),
    ("Oil and grease removal from oilfield produced water", "oil_gas_produced_water_pretreatment_media"),
    ("Hydrocarbon and TOC reduction in Gulf produced water", "oil_gas_produced_water_pretreatment_media"),
    ("Sulfide-resistant media for hot Gulf conditions", "oil_gas_produced_water_pretreatment_media"),
]

for request, expected_category in test_requests:
    result = classify_material_hierarchically(request)
    actual_category = result['specific_preset']
    confidence = result['confidence_score']
    status = "✅" if actual_category == expected_category else "❌"
    print(f"{status} {request[:50]}...")
    print(f"   Expected: {expected_category}, Got: {actual_category}, Confidence: {confidence:.0%}")

# Test 4: Preset application
print("\n" + "=" * 80)
print("TEST 4: Preset application and composition validation")
print("=" * 80)

test_data = {"material_name": "Produced water pre-treatment"}
result = apply_category_preset(test_data, category_key)

print(f"Category applied: {result.get('material_category')}")
print(f"Composition items: {len(result.get('composition', []))}")
print(f"Composition is valid: {result.get('composition_validation', {}).get('is_valid', 'unknown')}")
print(f"Parameters set: {len(result.get('category_specific_parameters', {}))}")

print("\nComposition:")
for item in result.get('composition', []):
    print(f"  - {item['component']}: {item['ratio']*100:.0f}%")

# Test 5: Conflict detection
print("\n" + "=" * 80)
print("TEST 5: Conflict detection")
print("=" * 80)

# Test 5a: Produced water detected with desalination category selected
test_request_5a = "High-salinity produced water treatment for ADNOC oil and gas operations"
conflict_5a = detect_category_conflicts(test_request_5a, "desalination_pretreatment_media")
print(f"\nTest 5a: Produced water with desalination category selected")
print(f"Request: {test_request_5a}")
print(f"Selected category: desalination_pretreatment_media")
print(f"Conflict detected: {conflict_5a['conflict_detected']}")
if conflict_5a['conflict_detected']:
    print(f"Reason: {conflict_5a['conflict_reason']}")
    print(f"Recommended: {conflict_5a.get('recommended_category')}")
    print(f"Blocked export: {conflict_5a['blocked_export']}")
else:
    print("No conflict")

# Test 5b: Produced water with correct category (should have no conflict)
conflict_5b = detect_category_conflicts(test_request_5a, "oil_gas_produced_water_pretreatment_media")
print(f"\nTest 5b: Produced water with correct category selected")
print(f"Selected category: oil_gas_produced_water_pretreatment_media")
print(f"Conflict detected: {conflict_5b['conflict_detected']}")

# Test 6: Verify it overrides desalination pre-treatment
print("\n" + "=" * 80)
print("TEST 6: Priority override (produced water > desalination pre-treatment)")
print("=" * 80)

priority_test = "Desalination pre-treatment media for produced water in UAE oil and gas operations"
result_priority = classify_material_hierarchically(priority_test)
selected = result_priority['specific_preset']
confidence = result_priority['confidence_score']
status = "✅" if selected == "oil_gas_produced_water_pretreatment_media" else "❌"
print(f"{status} Priority test:")
print(f"   Request: {priority_test}")
print(f"   Selected: {selected} (Confidence: {confidence:.0%})")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED")
print("=" * 80)
