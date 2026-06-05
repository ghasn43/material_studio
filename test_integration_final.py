#!/usr/bin/env python3
"""
Final Integration Test - Verify all systems work together
"""

import sys
sys.path.insert(0, 'd:\\material_studio_1')

from app import detect_category_conflicts
from category_registry import (
    classify_material_hierarchically,
    normalize_category_name,
    apply_category_preset,
)

print("=" * 80)
print("FINAL INTEGRATION TEST - ALL SYSTEMS")
print("=" * 80)
print()

# Test Case 1: Fabric stain with proper classification and conflict detection
print("Test Case 1: Fabric Stain Removal")
print("-" * 80)
prompt1 = "I need a fabric-safe oil stain remover for cotton clothing"
print(f"Prompt: {prompt1}")

# Step 1: Classification
result1 = classify_material_hierarchically(prompt1)
classified_category = result1['specific_preset']
confidence = result1['confidence_score']
print(f"Classification Result: {classified_category} ({confidence}% confidence)")

# Step 2: Verify it's the right category
expected = "fabric_oil_stain_removal_composite"
if normalized_category_name := normalize_category_name(classified_category):
    is_correct = normalized_category_name == normalize_category_name(expected)
    print(f"Expected: {expected}")
    print(f"Got: {classified_category}")
    print(f"Status: {'✅ CORRECT' if is_correct else '❌ WRONG'}")
else:
    print("❌ Normalization failed")

# Step 3: Test conflict detection (if someone tries to use heavy metal category)
print("\nConflict Detection Test:")
conflict_result = detect_category_conflicts(prompt1, "adsorbent_heavy_metals")
print(f"  If category selected: adsorbent_heavy_metals")
print(f"  Conflict Detected: {conflict_result['conflict_detected']}")
print(f"  Blocked Export: {conflict_result['blocked_export']}")
print(f"  Recommendation: {conflict_result['recommended_category']}")
print(f"  Status: {'✅ BLOCKED' if conflict_result['blocked_export'] else '❌ NOT BLOCKED'}")

print()

# Test Case 2: Roof waterproofing
print("Test Case 2: Roof Waterproofing Coating")
print("-" * 80)
prompt2 = "Roof waterproofing thermal insulation coating for concrete rooftop to prevent rainwater leakage"
print(f"Prompt: {prompt2}")

result2 = classify_material_hierarchically(prompt2)
classified_category2 = result2['specific_preset']
confidence2 = result2['confidence_score']
print(f"Classification Result: {classified_category2} ({confidence2}% confidence)")

expected2 = "roof_waterproofing_thermal_insulation_coating"
is_correct2 = normalize_category_name(classified_category2) == normalize_category_name(expected2)
print(f"Expected: {expected2}")
print(f"Status: {'✅ CORRECT' if is_correct2 else '❌ WRONG'}")

print()

# Test Case 3: CO2 capture (not photocatalytic)
print("Test Case 3: CO2 Capture (vs Photocatalytic)")
print("-" * 80)
prompt3 = "CO2 capture material with amine-functionalized silica for direct air capture"
print(f"Prompt: {prompt3}")

result3 = classify_material_hierarchically(prompt3)
classified_category3 = result3['specific_preset']
confidence3 = result3['confidence_score']
print(f"Classification Result: {classified_category3} ({confidence3}% confidence)")

expected3 = "co2_capture_material"
is_correct3 = normalize_category_name(classified_category3) == normalize_category_name(expected3)
print(f"Expected: {expected3}")

# Check conflict detection for wrong photocatalytic choice
conflict_result3 = detect_category_conflicts(prompt3, "photocatalytic_coating")
print(f"If wrongly selected: photocatalytic_coating")
print(f"  Conflict Detected: {conflict_result3['conflict_detected']}")
print(f"  Status: {'✅ DETECTED' if conflict_result3['conflict_detected'] else '❌ MISSED'}")

print()

# Test Case 4: Preset application and cleanup
print("Test Case 4: Preset Application & Cleanup")
print("-" * 80)
old_data = {
    "material_category": "adsorbent_heavy_metals",
    "category_specific_parameters": {"old_param": "value"},
    "processing_method": ["old_step_1", "old_step_2"],
    "validation_plan": {"old_validation": "plan"},
}
print("Before apply_category_preset:")
print(f"  material_category: {old_data['material_category']}")
print(f"  processing_method: {old_data.get('processing_method')}")

new_data = apply_category_preset(old_data, "fabric_oil_stain_removal_composite")
print("\nAfter apply_category_preset:")
print(f"  material_category: {new_data['material_category']}")
print(f"  processing_method: {len(new_data.get('processing_method', []))} steps")
print(f"  category_specific_parameters: {len(new_data.get('category_specific_parameters', {}))} params")

# Check if old values are gone
old_values_exist = (
    "old_param" in str(new_data.get('category_specific_parameters', {})) or
    "old_step_1" in str(new_data.get('processing_method', []))
)
print(f"  Old values contamination: {'❌ FOUND' if old_values_exist else '✅ CLEAN'}")
print(f"  Status: {'✅ CLEAN TRANSITION' if not old_values_exist else '❌ CONTAMINATION'}")

print()
print("=" * 80)
print("INTEGRATION TEST COMPLETE")
print("=" * 80)
