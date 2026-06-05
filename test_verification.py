#!/usr/bin/env python3
"""
Test pre-export verification layer for MaterialGenesis
"""
from category_registry import (
    detect_category_conflicts,
    validate_preset_consistency,
    verify_material_decision,
    CATEGORY_REGISTRY
)

# Test Case 1: CO2 Capture misclassified as Photocatalytic Coating
print("\n" + "="*70)
print("TEST 1: CO2 Capture → Photocatalytic Coating (Should Block)")
print("="*70)

user_request_1 = "I need an amine-functionalized silica material for CO2 capture with water vapor selectivity"
conflict_1 = detect_category_conflicts(user_request_1, "photocatalytic_coating")
print(f"Conflict Detected: {conflict_1['conflict_detected']}")
print(f"Blocked: {conflict_1['blocked_export']}")
print(f"Reason: {conflict_1['conflict_reason']}")
print(f"Recommended: {conflict_1['recommended_category']}")

# Test Case 2: Membrane misclassified as Heavy Metal Adsorbent (without heavy metals)
print("\n" + "="*70)
print("TEST 2: Membrane → Adsorbent (no heavy metals) (Should Block)")
print("="*70)

user_request_2 = "Design a membrane with high water flux and anti-fouling properties for desalination"
conflict_2 = detect_category_conflicts(user_request_2, "adsorbent_heavy_metals")
print(f"Conflict Detected: {conflict_2['conflict_detected']}")
print(f"Blocked: {conflict_2['blocked_export']}")
print(f"Reason: {conflict_2['conflict_reason']}")
print(f"Recommended: {conflict_2['recommended_category']}")

# Test Case 3: Membrane → Adsorbent (WITH heavy metals - should NOT block)
print("\n" + "="*70)
print("TEST 3: Membrane + Heavy Metals → Adsorbent (Should NOT Block)")
print("="*70)

user_request_3 = "Design a membrane with high water flux and anti-fouling to remove lead and cadmium"
conflict_3 = detect_category_conflicts(user_request_3, "adsorbent_heavy_metals")
print(f"Conflict Detected: {conflict_3['conflict_detected']}")
print(f"Blocked: {conflict_3['blocked_export']}")

# Test Case 4: AWH misclassified as generic
print("\n" + "="*70)
print("TEST 4: AWH → Generic (Should Block)")
print("="*70)

user_request_4 = "I need a desiccant composite for atmospheric water harvesting with hygroscopic salt"
conflict_4 = detect_category_conflicts(user_request_4, "other_material")
print(f"Conflict Detected: {conflict_4['conflict_detected']}")
print(f"Blocked: {conflict_4['blocked_export']}")
print(f"Reason: {conflict_4['conflict_reason']}")
print(f"Recommended: {conflict_4['recommended_category']}")

# Test Case 5: Potassium recovery conflict
print("\n" + "="*70)
print("TEST 5: K+ Recovery → Generic (Should Block)")
print("="*70)

user_request_5 = "Selective K+ recovery from mineral-rich potash brine with sodium competition"
conflict_5 = detect_category_conflicts(user_request_5, "other_material")
print(f"Conflict Detected: {conflict_5['conflict_detected']}")
print(f"Blocked: {conflict_5['blocked_export']}")
print(f"Reason: {conflict_5['conflict_reason']}")
print(f"Recommended: {conflict_5['recommended_category']}")

# Test Case 6: Valid potassium classification
print("\n" + "="*70)
print("TEST 6: K+ Recovery → Potassium Brine (Correct - Should NOT Block)")
print("="*70)

user_request_6 = "Selective K+ recovery from mineral-rich potash brine"
conflict_6 = detect_category_conflicts(user_request_6, "potassium_brine_separation_material")
print(f"Conflict Detected: {conflict_6['conflict_detected']}")
print(f"Blocked: {conflict_6['blocked_export']}")

# Test Case 7: Full verification workflow
print("\n" + "="*70)
print("TEST 7: Full Verification - CO2 + Wrong Category")
print("="*70)

material_data = {
    "preset_parameters": {"light_source": "UV", "target_pollutant": "acetaldehyde"},
    "validation_plan": {}
}

verification = verify_material_decision(user_request_1, "photocatalytic_coating", material_data)
print(f"Verification Status: {verification['verification_status']}")
print(f"Blocked Export: {verification['blocked_export']}")
print(f"User Confirmation Required: {verification['user_confirmation_required']}")
print(f"Details: {verification['details']}")

print("\n" + "="*70)
print("✅ ALL VERIFICATION TESTS COMPLETE")
print("="*70)
