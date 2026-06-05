#!/usr/bin/env python3
"""
Comprehensive test: Verify all 11 material categories have functioning processing methods.
Tests preset data structure, PDF rendering, and content validation.
"""

import sys
sys.path.insert(0, 'D:\\material_studio_1')

from category_registry import CATEGORY_REGISTRY, get_category_preset, apply_category_preset
from app import generate_pdf

def test_category_preset(category_key):
    """Test that a category's preset has proper processing method data."""
    preset = get_category_preset(category_key)
    
    # Check processing_method exists
    processing_method = preset.get('processing_method', [])
    if not processing_method:
        return f"ERROR: No processing_method in preset"
    
    # Check it's a list
    if not isinstance(processing_method, list):
        return f"ERROR: processing_method is not a list (got {type(processing_method)})"
    
    # Check each item is a string
    for i, item in enumerate(processing_method):
        if not isinstance(item, str):
            return f"ERROR: Step {i} is not a string (got {type(item)})"
    
    # Check minimum length (at least 6 steps, but real data has 6-8)
    if len(processing_method) < 6:
        return f"WARNING: Only {len(processing_method)} steps (minimum expected 6)"
    
    return f"OK: {len(processing_method)} steps"

def test_category_pdf(category_key):
    """Test that a category can generate PDF with processing method."""
    result = {
        'material_category': category_key,
        'user_request': f'Test for {category_key}',
        'target_application': f'Application for {category_key}',
        'composition': [
            {'component': 'Base Material', 'ratio': 0.6},
            {'component': 'Additive', 'ratio': 0.4},
        ]
    }
    
    # Apply preset
    apply_category_preset(result, category_key)
    
    # Create mock verification result
    three_stage_result = {
        "overall_status": "pass",
        "stage_1_result": {"status": "pass", "keyword_match_percentage": 90, "matched_keywords": []},
        "stage_2_result": {"status": "pass", "reason": "OK"},
        "stage_3_result": {"status": "pass", "reason": "OK"},
        "stage_4_result": {"status": "pass", "datasets_queried": [], "components_checked": 0, 
                          "components_verified": 0, "materials_found": 0, "literature_hits": 0, 
                          "evidence_summary": "OK"}
    }
    
    try:
        pdf_bytes = generate_pdf(f'Test {category_key}', result, three_stage_result)
        return f"OK: {len(pdf_bytes) / 1024:.1f} KB"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

def main():
    print("="*90)
    print("COMPREHENSIVE TEST: All 11 Material Categories - Processing Method Validation")
    print("="*90)
    
    categories_to_test = list(CATEGORY_REGISTRY.keys())
    
    print(f"\nTesting {len(categories_to_test)} categories...\n")
    print(f"{'Category':<45} {'Preset Data':<25} {'PDF Render':<20}")
    print("-" * 90)
    
    preset_pass = 0
    preset_fail = 0
    pdf_pass = 0
    pdf_fail = 0
    
    for category_key in sorted(categories_to_test):
        # Test preset
        preset_result = test_category_preset(category_key)
        if preset_result.startswith("OK"):
            preset_pass += 1
            preset_status = f"[OK] {preset_result}"
        else:
            preset_fail += 1
            preset_status = f"[FAIL] {preset_result}"
        
        # Test PDF
        pdf_result = test_category_pdf(category_key)
        if pdf_result.startswith("OK"):
            pdf_pass += 1
            pdf_status = f"[OK] {pdf_result}"
        else:
            pdf_fail += 1
            pdf_status = f"[FAIL] {pdf_result}"
        
        print(f"{category_key:<45} {preset_status:<30} {pdf_status:<20}")
    
    # Summary
    print("\n" + "="*90)
    print(f"SUMMARY:")
    print(f"  Preset Data:    {preset_pass} passed, {preset_fail} failed (Total: {preset_pass + preset_fail})")
    print(f"  PDF Rendering:  {pdf_pass} passed, {pdf_fail} failed (Total: {pdf_pass + pdf_fail})")
    
    if preset_fail == 0 and pdf_fail == 0:
        print(f"\n[SUCCESS] All {len(categories_to_test)} categories have working processing methods!")
        return 0
    else:
        print(f"\n[FAILURE] {preset_fail + pdf_fail} tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
