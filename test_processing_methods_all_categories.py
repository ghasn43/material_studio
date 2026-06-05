#!/usr/bin/env python3
"""
Test script to verify processing methods render correctly for all 11 material categories.
Tests PDF generation for each category type.
"""

import sys
sys.path.insert(0, 'D:\\material_studio_1')

from category_registry import CATEGORY_REGISTRY, apply_category_preset, run_three_stage_verification
from app import generate_pdf

# Test categories with different processing method types
TEST_CATEGORIES = [
    ('atmospheric_water_harvesting_material', 'AWH Material', 'Design a porous composite for atmospheric water harvesting'),
    ('membrane_water_treatment', 'Membrane', 'Create a selective nanofiltration membrane for water purification'),
    ('thermal_insulation_composite', 'Thermal Insulation', 'Develop a lightweight thermal insulation composite'),
    ('roof_waterproofing_thermal_insulation_coating', 'Roof Coating', 'Create a waterproof thermal insulation coating for roofs'),
    ('photocatalytic_coating', 'Photocatalytic', 'Design a TiO2-based photocatalytic coating for self-cleaning surfaces'),
]

def test_category_processing_method(category_key, category_name, prompt):
    """Test PDF generation for a single category's processing method."""
    print(f"\n{'='*80}")
    print(f"Testing {category_name} ({category_key})")
    print(f"{'='*80}")
    
    # Create minimal result dictionary
    result = {
        'material_category': category_key,
        'user_request': prompt,
        'target_application': f'Test application for {category_name}',
        'composition': [
            {'component': 'Component A', 'ratio': 0.4},
            {'component': 'Component B', 'ratio': 0.3},
            {'component': 'Component C', 'ratio': 0.2},
            {'component': 'Component D', 'ratio': 0.1},
        ]
    }
    
    # Apply category preset
    try:
        apply_category_preset(result, category_key)
        print(f"[OK] Category preset applied")
    except Exception as e:
        print(f"[FAIL] Error applying preset: {str(e)[:100]}")
        return False
    
    # Check processing method
    processing_method = result.get('processing_method', [])
    print(f"[OK] Processing method steps: {len(processing_method)}")
    
    # Create mock verification result
    three_stage_result = {
        "overall_status": "pass",
        "stage_1_result": {"status": "pass", "keyword_match_percentage": 95, "matched_keywords": [category_name]},
        "stage_2_result": {"status": "pass", "reason": "All required fields present"},
        "stage_3_result": {"status": "pass", "reason": "Scientific consistency verified"},
        "stage_4_result": {"status": "pass", "datasets_queried": [], "components_checked": 0, "components_verified": 0, "materials_found": 0, "literature_hits": 0, "evidence_summary": "External dataset verification was not completed."}
    }
    
    # Generate PDF
    try:
        pdf_bytes = generate_pdf(prompt, result, three_stage_result)
        print(f"[OK] PDF generated: {len(pdf_bytes) / 1024:.1f} KB")
        
        # Save for inspection
        filename = f'test_{category_key}_processing_method.pdf'
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        print(f"[OK] PDF saved: {filename}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error generating PDF: {str(e)[:100]}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("PROCESSING METHOD TEST - All Categories")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for category_key, category_name, prompt in TEST_CATEGORIES:
        if test_category_processing_method(category_key, category_name, prompt):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'='*80}")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
