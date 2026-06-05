"""Test export blocking when processing method is incomplete"""
import sys
sys.path.insert(0, 'D:\\material_studio_1')

print("=" * 80)
print("TEST: Export Blocking for Incomplete Processing Methods")
print("=" * 80)
print()

# Validation function (same as in app.py)
def check_export_allowed(result, verification_status):
    """Determine if export is allowed"""
    processing_method = result.get("processing_method", [])
    processing_method_incomplete = False
    
    if len(processing_method) > 0:
        content_lines = [str(step).strip() for step in processing_method if str(step).strip()]
        if len(content_lines) < 8:
            processing_method_incomplete = True
        else:
            header_count = sum(1 for line in content_lines if any(line.startswith(f"{j}.") for j in range(1, 9)))
            if header_count == len(content_lines):
                processing_method_incomplete = True
    
    can_export = verification_status != "fail" and not processing_method_incomplete
    return can_export, processing_method_incomplete

# Test case 1: Empty processing method (should be allowed)
print("Test 1: No processing method (optional feature)")
result1 = {"material_category": "other_material", "processing_method": []}
can_export1, incomplete1 = check_export_allowed(result1, "pass")
print(f"  Processing method entries: 0")
print(f"  Result: {'✅ ALLOWED' if can_export1 else '❌ BLOCKED'} (incomplete={incomplete1})")
print()

# Test case 2: Headers only (should be blocked)
print("Test 2: Headers only - no descriptions")
result2 = {
    "material_category": "test",
    "processing_method": [
        "1. Step One:",
        "2. Step Two:",
        "3. Step Three:",
        "4. Step Four:",
        "5. Step Five:",
        "6. Step Six:",
        "7. Step Seven:",
        "8. Step Eight:"
    ]
}
can_export2, incomplete2 = check_export_allowed(result2, "pass")
content2 = len([s for s in result2["processing_method"] if str(s).strip()])
print(f"  Processing method entries: {content2}")
print(f"  Result: {'✅ ALLOWED' if can_export2 else '❌ BLOCKED'} (incomplete={incomplete2})")
if incomplete2:
    print(f"  Error message: 'Processing method incomplete. Please apply processing preset before export.'")
print()

# Test case 3: Verification failed (should be blocked)
print("Test 3: Verification failed (regardless of processing method)")
result3 = {"material_category": "test", "processing_method": []}
can_export3, incomplete3 = check_export_allowed(result3, "fail")
print(f"  Verification status: FAIL")
print(f"  Result: {'✅ ALLOWED' if can_export3 else '❌ BLOCKED'}")
if not can_export3 and not incomplete3:
    print(f"  Error message: 'Cannot export: Verification failed...'")
print()

# Test case 4: Complete processing method (should be allowed)
print("Test 4: Complete processing method with descriptions")
result4 = {
    "material_category": "test",
    "processing_method": [
        "1. Surface Preparation:",
        "   - Clean the surface",
        "   - Repair cracks",
        "",
        "2. Powder Pre-Mix:",
        "   - Blend fillers",
        "",
        "3. Liquid Binder Preparation:",
        "   - Prepare binder",
        "",
        "4. Composite Mixing:",
        "   - Mix uniformly",
        "",
        "5. Application:",
        "   - Apply coats",
        "",
        "6. Drying and Curing:",
        "   - Dry thoroughly",
        "",
        "7. Quality Control:",
        "   - Check continuity",
        "",
        "8. Evidence Boundary:",
        "   - Planning level",
        ""
    ]
}
can_export4, incomplete4 = check_export_allowed(result4, "pass")
content4 = len([s for s in result4["processing_method"] if str(s).strip()])
print(f"  Processing method entries: {len(result4['processing_method'])}")
print(f"  Non-empty lines: {content4}")
print(f"  Result: {'✅ ALLOWED' if can_export4 else '❌ BLOCKED'} (incomplete={incomplete4})")
print()

# Summary
print("=" * 80)
results = [
    (1, can_export1, True),   # Should be ALLOWED (no PM - optional)
    (2, can_export2, False),  # Should be BLOCKED (headers only)
    (3, can_export3, False),  # Should be BLOCKED (verification failed)
    (4, can_export4, True),   # Should be ALLOWED (complete PM)
]

passed = all(
    (can_export == expected) for _, can_export, expected in results
)

if passed:
    print("✅ ALL EXPORT BLOCKING TESTS PASSED")
    print()
    print("Test Results Summary:")
    print("  1. No processing method → ALLOWED ✅")
    print("  2. Headers only → BLOCKED ✅")
    print("  3. Verification failed → BLOCKED ✅")
    print("  4. Complete processing method → ALLOWED ✅")
else:
    print("❌ SOME TESTS FAILED")
    for test_num, can_export, expected in results:
        status = "✅" if (can_export == expected) else "❌"
        print(f"  Test {test_num}: {status} (allowed={can_export}, expected={expected})")

print("=" * 80)
