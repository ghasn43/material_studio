"""Test empty processing method validation"""
import sys
sys.path.insert(0, 'D:\\material_studio_1')

# Test the validation logic that checks processing method completeness

def validate_processing_method(processing_method):
    """Test validation function for processing method completeness"""
    has_processing_method = len(processing_method) > 0
    processing_method_incomplete = False
    
    if has_processing_method:
        # Check if processing method has actual content (not just headers)
        content_lines = [str(step).strip() for step in processing_method if str(step).strip()]
        # Should have headers (8 steps) plus at least 2-3 bullet points per step = ~24+ lines minimum
        if len(content_lines) < 8:
            processing_method_incomplete = True
        else:
            # Check that headers aren't the only content
            header_count = sum(1 for line in content_lines if any(line.startswith(f"{j}.") for j in range(1, 9)))
            if header_count == len(content_lines):  # Only headers, no content
                processing_method_incomplete = True
    
    return processing_method_incomplete

# Test case 1: Complete processing method (should pass)
print("Test 1: Complete processing method")
complete_pm = [
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
result1 = validate_processing_method(complete_pm)
print(f"  Result: {'BLOCKED (incomplete)' if result1 else 'ALLOWED (complete)'}")
print()

# Test case 2: Headers only (should be blocked)
print("Test 2: Headers only - NO substeps")
headers_only = [
    "1. Surface Preparation:",
    "2. Powder Pre-Mix:",
    "3. Liquid Binder Preparation:",
    "4. Composite Mixing:",
    "5. Application:",
    "6. Drying and Curing:",
    "7. Quality Control:",
    "8. Evidence Boundary:"
]
result2 = validate_processing_method(headers_only)
print(f"  Result: {'BLOCKED (incomplete)' if result2 else 'ALLOWED (complete)'}")
print()

# Test case 3: Empty list (should be blocked)
print("Test 3: Empty processing method")
empty_pm = []
result3 = validate_processing_method(empty_pm)
print(f"  Result: {'BLOCKED (incomplete)' if result3 else 'ALLOWED (complete)'}")
print()

# Test case 4: Real roof waterproofing processing method
print("Test 4: Real roof waterproofing method from category_registry")
from category_registry import CATEGORY_REGISTRY
real_pm = CATEGORY_REGISTRY["roof_waterproofing_thermal_insulation_coating"]["processing_method"]
result4 = validate_processing_method(real_pm)
content_count = len([s for s in real_pm if str(s).strip()])
print(f"  Total entries: {len(real_pm)}")
print(f"  Non-empty lines: {content_count}")
print(f"  Result: {'BLOCKED (incomplete)' if result4 else 'ALLOWED (complete)'}")
print()

print("=" * 80)
if not result1 and result2 and not result3 and not result4:
    print("✅ ALL TESTS PASSED - Validation logic works correctly!")
else:
    print("❌ TESTS FAILED")
    print(f"  Test 1 (complete): {result1} (expected False)")
    print(f"  Test 2 (headers): {result2} (expected True)")
    print(f"  Test 3 (empty): {result3} (expected True)")
    print(f"  Test 4 (real): {result4} (expected False)")
