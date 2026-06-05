#!/usr/bin/env python3
"""Test battery electrode domain guardrail fix."""

from category_registry import classify_material_hierarchically, detect_category_conflicts

# Original failing prompt
battery_prompt = """Design a low-cost sodium-ion battery anode composite using hard carbon, conductive carbon black, 
inorganic stabilizers, sodium-compatible binder, and porosity modifiers. The electrode should improve sodium 
storage capacity, cycling stability, rate capability, and mechanical integrity while minimizing irreversible 
capacity loss. Validation is required for specific capacity, coulombic efficiency, cycling durability, rate 
performance, electrode swelling, impedance, and safety before any battery-performance claim is made."""

print("=" * 80)
print("TESTING BATTERY ELECTRODE DOMAIN GUARDRAIL FIX")
print("=" * 80)
print()

# Test 1: Classification
print("TEST 1: Material Classification")
print("-" * 80)
result = classify_material_hierarchically(battery_prompt)
print(f"Selected Category: {result.get('specific_preset', 'N/A')}")
print(f"Display Name: {result.get('display_name', 'N/A')}")
print(f"Confidence: {result.get('confidence_score', 0)}%")
print(f"Matched Keywords: {result.get('matched_keywords', [])[:5]}...")
print()

# Test 2: Conflict Detection
print("TEST 2: Conflict Detection")
print("-" * 80)
selected_cat = result.get('specific_preset', 'other_material')
conflict = detect_category_conflicts(battery_prompt, selected_cat)
print(f"Conflict Detected: {conflict.get('conflict_detected', False)}")
print(f"Blocked Export: {conflict.get('blocked_export', False)}")
if conflict.get('conflict_reason'):
    print(f"Reason: {conflict['conflict_reason']}")
print()

# Test 3: Expected behavior
print("TEST 3: Verification")
print("-" * 80)
if selected_cat == "sodium_ion_battery_anode_composite":
    print("✅ PASS: Correctly classified as Sodium-Ion Battery Anode Composite")
else:
    print(f"❌ FAIL: Classified as {selected_cat} instead of sodium_ion_battery_anode_composite")

if not conflict.get('conflict_detected'):
    print("✅ PASS: No conflicts detected for correct category")
else:
    print(f"⚠️  WARNING: Conflict detected even with correct category: {conflict.get('conflict_reason')}")

print()
print("=" * 80)
