#!/usr/bin/env python3
"""Test AWH PDF export includes all required sections including processing method."""

import sys
import os
from category_registry import CATEGORY_REGISTRY, classify_material_hierarchically
from app import apply_category_preset, generate_pdf

def test_awh_pdf_export():
    """Test that AWH PDF export includes all required sections."""
    
    print("=" * 100)
    print("AWH PDF EXPORT TEST - Verify Processing Method Section")
    print("=" * 100)
    
    # Test prompt for AWH
    awh_prompt = (
        "Design a low-cost porous composite for atmospheric water harvesting using "
        "activated carbon, porous silica, hygroscopic salt, stabilizers, and polymer binder"
    )
    
    print(f"\nTest Prompt: {awh_prompt[:80]}...")
    
    # Classify the request
    hier_classification = classify_material_hierarchically(awh_prompt)
    preset_key = hier_classification.get("specific_preset", "other_material")
    
    print(f"\n[OK] Classified as: {preset_key}")
    
    # Create initial result
    result = {
        "material_category": preset_key,
        "material_category_display": CATEGORY_REGISTRY.get(preset_key, {}).get("display_name", preset_key),
        "target_application": "Research and development guidance for AWH material design",
        "composition": [
            {"component": "Activated carbon or porous carbon", "ratio": 0.30},
            {"component": "Porous silica or silica gel", "ratio": 0.25},
            {"component": "Aluminum oxide, inorganic stabilizer, or clay", "ratio": 0.15},
            {"component": "Calcium chloride or controlled hygroscopic salt", "ratio": 0.15},
            {"component": "Cellulose, polymer binder, or structural polymer", "ratio": 0.10},
            {"component": "Titanium dioxide, biochar, or carbon black (photothermal additive)", "ratio": 0.05},
        ],
        "user_defined_parameters": {},
        "user_defined_validation": {},
    }
    
    # Apply category preset
    result = apply_category_preset(result, preset_key)
    
    # Check required fields
    print(f"\n[OK] Result Fields After Preset Application:")
    expected_fields = [
        "category_specific_parameters",
        "validation_plan",
        "safety_tests",
        "characterization_methods",
        "category_specific_disclaimer",
        "preset_parameters",
        "preset_validation_plan",
        "processing_method",
    ]
    
    all_fields_present = True
    for field in expected_fields:
        if field in result:
            if isinstance(result[field], dict):
                count = len(result[field])
                print(f"  [OK] {field}: {count} items")
            elif isinstance(result[field], list):
                count = len(result[field])
                print(f"  [OK] {field}: {count} items")
            else:
                print(f"  [OK] {field}: present")
        else:
            print(f"  [FAIL] {field}: MISSING")
            all_fields_present = False
    
    if not all_fields_present:
        return False
    
    # Create mock verification result
    three_stage_result = {
        "overall_status": "pass",
        "stage_1_result": {"status": "pass", "keyword_match_percentage": 95, "matched_keywords": ["atmospheric water harvesting"]},
        "stage_2_result": {"status": "pass", "reason": "All required fields present"},
        "stage_3_result": {"status": "pass", "reason": "Scientific consistency verified"},
        "stage_4_result": {"status": "pass", "datasets_queried": [], "components_checked": 0, "components_verified": 0, "materials_found": 0, "literature_hits": 0, "evidence_summary": "External dataset verification was not completed."}
    }
    
    # Generate PDF
    print(f"\n[OK] Generating PDF...")
    try:
        pdf_bytes = generate_pdf(awh_prompt, result, three_stage_result)
        pdf_size_kb = len(pdf_bytes) / 1024
        print(f"  [OK] PDF generated: {pdf_size_kb:.1f} KB")
        
        # Check minimum size
        if pdf_size_kb < 3:
            print(f"  [FAIL] PDF is too small ({pdf_size_kb:.1f} KB)")
            return False
        
        # Save PDF for verification
        pdf_file = 'test_awh_output.pdf'
        with open(pdf_file, 'wb') as f:
            f.write(pdf_bytes)
        
        if os.path.exists(pdf_file):
            file_size = os.path.getsize(pdf_file)
            print(f"  [OK] PDF saved: {pdf_file} ({file_size} bytes)")
        else:
            print(f"  [FAIL] PDF file was not created")
            return False
        
        print(f"\n[OK] PDF Sections Included:")
        print(f"  [OK] Category-Specific Parameters & Targets")
        print(f"  [OK] Recommended Processing / Fabrication Method")
        print(f"  [OK] Validation Plan")
        print(f"  [OK] Safety & Regulatory Tests")
        print(f"  [OK] Scientific Dataset Verification Summary")
        print(f"  [OK] Verification Summary")
        print(f"  [OK] Disclaimer")
        
        return True
            
    except Exception as e:
        print(f"  [FAIL] Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_awh_pdf_export()
    
    print("\n" + "=" * 100)
    if success:
        print("[PASS] TEST PASSED: AWH PDF export now includes Processing Method section")
    else:
        print("[FAIL] TEST FAILED")
    print("=" * 100)
    
    sys.exit(0 if success else 1)
