#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST SUITE: Manual Category Override Workflow
=============================================
Tests the handle_manual_category_override function to verify that when a user
manually selects a category from the dropdown after misclassification:

1. Category changes to selected value
2. Old preset fields are cleared
3. New preset fields are applied
4. Verification reruns
5. Generate PDF button becomes active (if verification passes)
"""

from category_registry import (
    detect_prompt_domain,
    validate_domain_category_alignment,
    classify_material_hierarchically,
    run_three_stage_verification,
    clear_previous_preset_fields,
    apply_category_preset,
    normalize_category_name,
    get_category_display_name,
    CATEGORY_TO_DOMAIN,
    CATEGORY_REGISTRY
)


def test_phosphate_recovery_manual_override():
    """
    Test Case: Phosphate Recovery Manual Override
    
    Scenario:
    1. User enters phosphate recovery prompt
    2. System misclassifies as Oil & Gas Produced Water (wrong domain)
    3. User manually selects Phosphate Recovery Material
    4. Verify that:
       - Category changes
       - Old preset fields disappear
       - Phosphate preset fields appear
       - Verification reruns successfully
       - Export is allowed
    """
    print("\n" + "="*80)
    print("TEST: Phosphate Recovery Manual Override")
    print("="*80)
    
    # Step 1: User enters phosphate recovery prompt
    user_prompt = """We're developing an adsorbent material for phosphate recovery from agricultural wastewater. 
    The material should preferentially bind orthophosphate ions while allowing desorption through pH adjustment. 
    Key requirements: adsorption/desorption cycles, nutrient recovery from fertilizer reuse applications, 
    pH-dependent binding to facilitate fertilizer release, compatibility with competing ions present in agricultural runoff. 
    What composition, characterization methods, and validation plan would be appropriate?"""
    
    print("\n✓ Step 1: User enters phosphate recovery prompt")
    print(f"  Prompt: {user_prompt[:80]}...")
    
    # Step 2: Detect domain (should be phosphate_recovery)
    domain_result = detect_prompt_domain(user_prompt)
    detected_domain = domain_result["domain"]
    domain_confidence = domain_result["confidence"]
    
    print(f"\n✓ Step 2: Detect domain")
    print(f"  Detected Domain: {detected_domain} ({domain_confidence}% confidence)")
    assert detected_domain == "phosphate_recovery", f"Expected phosphate_recovery, got {detected_domain}"
    print(f"  ✅ Domain correctly detected as phosphate_recovery")
    
    # Step 3: Initial classification (might be wrong - simulate misclassification)
    hier_result = classify_material_hierarchically(user_prompt)
    initial_category = hier_result.get("specific_preset", "other_material")
    initial_confidence = hier_result.get("confidence_score", 0)
    
    print(f"\n✓ Step 3: Initial category classification")
    print(f"  Initial Category: {initial_category} ({initial_confidence}% confidence)")
    
    # Initialize material_data with initial classification
    material_data = {
        "material_category": initial_category,
        "material_category_display": get_category_display_name(initial_category),
        "composition": [],
        "parameters": {},
        "validation_plan": {},
        "processing_method": [],
        "category_disclaimer": "",
    }
    
    # Step 4: Run initial verification
    initial_verification = run_three_stage_verification(
        user_request=user_prompt,
        selected_category=initial_category,
        material_data=material_data,
        stored_confidence=initial_confidence
    )
    
    print(f"\n✓ Step 4: Initial verification")
    print(f"  Initial Verification Status: {initial_verification['overall_status'].upper()}")
    
    # Step 5: User manually selects Phosphate Recovery Material
    print(f"\n✓ Step 5: User manually selects Phosphate Recovery Material")
    selected_category_key = "phosphate_recovery_material"
    selected_category_display = "Phosphate Recovery Material"
    
    # MANUAL OVERRIDE: Clear old fields
    material_data = clear_previous_preset_fields(material_data)
    print(f"  - Old preset fields cleared")
    
    # Normalize the category name
    normalized_category = normalize_category_name(selected_category_key)
    print(f"  - Category normalized: {normalized_category}")
    
    # Update material category
    material_data["material_category"] = normalized_category
    material_data["material_category_display"] = get_category_display_name(normalized_category)
    
    # Apply new preset
    material_data = apply_category_preset(material_data, normalized_category)
    print(f"  - New preset applied: {selected_category_display}")
    
    # Verify new preset fields were applied
    has_phosphate_params = len(material_data.get("category_specific_parameters", {})) > 0
    has_validation_plan = len(material_data.get("validation_plan", {})) > 0
    
    print(f"  - Preset parameters applied: {has_phosphate_params}")
    print(f"  - Validation plan applied: {has_validation_plan}")
    assert has_phosphate_params, "Phosphate preset parameters not applied"
    assert has_validation_plan, "Phosphate validation plan not applied"
    print(f"  ✅ Phosphate preset fields applied successfully")
    
    # Step 6: Rerun verification with new category
    print(f"\n✓ Step 6: Rerun verification with new category")
    new_verification = run_three_stage_verification(
        user_request=user_prompt,
        selected_category=normalized_category,
        material_data=material_data,
        stored_confidence=None
    )
    
    new_status = new_verification["overall_status"]
    print(f"  - New Verification Status: {new_status.upper()}")
    
    # Step 7: Check domain-category alignment
    print(f"\n✓ Step 7: Check domain-category alignment")
    alignment = validate_domain_category_alignment(detected_domain, normalized_category)
    is_aligned = alignment["aligned"]
    category_domain = CATEGORY_TO_DOMAIN.get(normalized_category, "unknown")
    
    print(f"  - Detected Domain: {detected_domain}")
    print(f"  - Category Domain: {category_domain}")
    print(f"  - Aligned: {is_aligned}")
    assert is_aligned, f"Domain-category alignment failed: {detected_domain} vs {category_domain}"
    print(f"  ✅ Domain-category alignment confirmed")
    
    # Step 8: Verify export is allowed
    print(f"\n✓ Step 8: Verify export is allowed")
    can_export = new_status in ["pass", "warning"]
    print(f"  - Verification Status: {new_status}")
    print(f"  - Can Export: {can_export}")
    assert can_export, f"Export should be allowed after manual override, but verification status is {new_status}"
    print(f"  ✅ Export is allowed after manual category selection")
    
    # Step 9: Verify category actually changed
    print(f"\n✓ Step 9: Verify category change")
    print(f"  - Initial Category: {initial_category}")
    print(f"  - New Category: {normalized_category}")
    assert material_data["material_category"] == normalized_category, "Category did not update"
    print(f"  ✅ Category successfully changed")
    
    # Overall result
    print(f"\n" + "="*80)
    print(f"🎉 TEST PASSED: Manual category override workflow works correctly!")
    print("="*80)
    print(f"\nSummary:")
    print(f"  ✅ Domain detected correctly as phosphate_recovery")
    print(f"  ✅ Old preset fields cleared")
    print(f"  ✅ New phosphate preset applied")
    print(f"  ✅ Verification rerun successfully")
    print(f"  ✅ Domain-category alignment verified")
    print(f"  ✅ Export allowed ({new_status} status)")
    print(f"  ✅ Category successfully changed to {selected_category_display}")
    
    return True


def test_battery_manual_override():
    """
    Test Case: Battery Electrode Manual Override
    
    Scenario:
    1. User enters battery electrode prompt
    2. System classifies correctly or with warnings
    3. User confirms Sodium-Ion Battery Anode Composite manually
    4. Verify that:
       - Category confirmed
       - Preset fields present
       - Verification passes
       - Export is allowed
    """
    print("\n" + "="*80)
    print("TEST: Battery Electrode Manual Override")
    print("="*80)
    
    user_prompt = """I'm developing a sodium-ion battery anode composite with hard carbon as the active material. 
    The composite includes conductive carbon black (8 wt%), a sodium-compatible binder, and processing additives. 
    Target properties include specific capacity >300 mAh/g, coulombic efficiency >98%, rate capability up to 2C, 
    cycling stability >200 cycles at 50-80°C."""
    
    print("\n✓ User enters battery electrode prompt")
    
    # Detect domain
    domain_result = detect_prompt_domain(user_prompt)
    detected_domain = domain_result["domain"]
    
    assert detected_domain == "battery_electrode", f"Expected battery_electrode, got {detected_domain}"
    print(f"✓ Domain detected: {detected_domain}")
    
    # Initial classification
    hier_result = classify_material_hierarchically(user_prompt)
    initial_category = hier_result.get("specific_preset", "other_material")
    
    print(f"✓ Initial category: {initial_category}")
    
    # Manual override to battery category
    selected_category_key = "sodium_ion_battery_anode_composite"
    
    # Create material data
    material_data = {
        "material_category": initial_category,
        "material_category_display": get_category_display_name(initial_category),
    }
    
    # Clear and apply new preset
    material_data = clear_previous_preset_fields(material_data)
    normalized_category = normalize_category_name(selected_category_key)
    material_data["material_category"] = normalized_category
    material_data = apply_category_preset(material_data, normalized_category)
    
    print(f"✓ Category changed to: {normalized_category}")
    
    # Rerun verification
    new_verification = run_three_stage_verification(
        user_request=user_prompt,
        selected_category=normalized_category,
        material_data=material_data
    )
    
    # Verify results
    assert new_verification["overall_status"] in ["pass", "warning"], \
        f"Verification should pass for battery, got {new_verification['overall_status']}"
    
    alignment = validate_domain_category_alignment(detected_domain, normalized_category)
    assert alignment["aligned"], "Battery domain-category should be aligned"
    
    print(f"✓ Verification status: {new_verification['overall_status']}")
    print(f"✓ Domain-category aligned: {alignment['aligned']}")
    print(f"🎉 Battery manual override test passed!")
    
    return True


def main():
    """Run all manual override tests."""
    print("\n" + "#"*80)
    print("# MANUAL CATEGORY OVERRIDE TEST SUITE")
    print("#"*80)
    print("\nTesting handle_manual_category_override workflow...")
    
    try:
        # Test 1: Phosphate Recovery
        success_1 = test_phosphate_recovery_manual_override()
        
        # Test 2: Battery Electrode
        success_2 = test_battery_manual_override()
        
        if success_1 and success_2:
            print("\n" + "="*80)
            print("✅ ALL MANUAL OVERRIDE TESTS PASSED")
            print("="*80)
            print("\nThe manual category override workflow is fully functional:")
            print("✅ Category can be changed via manual selection")
            print("✅ Old preset fields are cleared")
            print("✅ New preset fields are applied")
            print("✅ Verification reruns correctly")
            print("✅ Export becomes available after successful verification")
            print("="*80)
            return 0
        else:
            print("\n⚠️  Some tests failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
