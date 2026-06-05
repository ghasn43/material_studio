#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST SUITE: Domain-First Classification System
==============================================
Tests the new domain detection and domain-category alignment validation.

Tests all 6 required test cases to verify the domain-first architecture works correctly.
"""

from category_registry import (
    detect_prompt_domain,
    validate_domain_category_alignment,
    classify_material_hierarchically,
    CATEGORY_TO_DOMAIN
)

def test_case(name, user_prompt, expected_domain, expected_category):
    """Run a single test case and report results."""
    print("\n" + "="*80)
    print(f"TEST: {name}")
    print("="*80)
    print(f"\nPrompt: {user_prompt[:100]}...")
    
    # Step 1: Detect domain
    domain_result = detect_prompt_domain(user_prompt)
    detected_domain = domain_result["domain"]
    domain_confidence = domain_result["confidence"]
    
    print(f"\n✓ Domain Detection:")
    print(f"  - Detected: {detected_domain} ({domain_confidence}% confidence)")
    print(f"  - Expected: {expected_domain}")
    print(f"  - Keywords Matched: {len(domain_result['matched_keywords'])} - {', '.join(domain_result['matched_keywords'][:5])}")
    
    domain_pass = detected_domain == expected_domain
    print(f"  - Result: {'✅ PASS' if domain_pass else '❌ FAIL'}")
    
    # Step 2: Classify category
    hier_result = classify_material_hierarchically(user_prompt)
    selected_category = hier_result.get("specific_preset", "other_material")
    category_confidence = hier_result.get("confidence_score", 0)
    
    print(f"\n✓ Category Classification:")
    print(f"  - Selected: {selected_category} ({category_confidence}% confidence)")
    print(f"  - Expected: {expected_category}")
    
    category_pass = selected_category == expected_category
    print(f"  - Result: {'✅ PASS' if category_pass else '❌ FAIL'}")
    
    # Step 3: Validate alignment
    alignment = validate_domain_category_alignment(detected_domain, selected_category)
    aligned = alignment["aligned"]
    category_domain = CATEGORY_TO_DOMAIN.get(selected_category, "unknown")
    
    print(f"\n✓ Domain-Category Alignment:")
    print(f"  - Prompt Domain: {detected_domain}")
    print(f"  - Category Domain: {category_domain}")
    print(f"  - Aligned: {aligned}")
    print(f"  - Result: {'✅ PASS' if aligned else '❌ FAIL'}")
    
    if not aligned:
        print(f"  - Blocking Reason: {alignment.get('blocking_export', 'N/A')}")
    
    # Overall result
    overall_pass = domain_pass and category_pass and aligned
    print(f"\n{'🎉 OVERALL: PASS' if overall_pass else '⚠️  OVERALL: FAIL'}")
    
    return {
        "name": name,
        "domain_pass": domain_pass,
        "category_pass": category_pass,
        "alignment_pass": aligned,
        "overall_pass": overall_pass,
        "detected_domain": detected_domain,
        "selected_category": selected_category,
        "alignment": alignment
    }


def main():
    """Run all test cases."""
    print("\n" + "#"*80)
    print("# DOMAIN-FIRST CLASSIFICATION TEST SUITE")
    print("#"*80)
    print("\nTesting domain detection and category alignment validation...")
    
    results = []
    
    # Test A: Sodium-ion battery anode prompt
    print("\n\n" + "="*80)
    print("= TEST A: Sodium-Ion Battery Anode")
    print("="*80)
    result_a = test_case(
        "A: Sodium-Ion Battery Anode",
        """I'm developing a sodium-ion battery anode composite with hard carbon as the active material. 
        The composite includes conductive carbon black (8 wt%), a sodium-compatible binder, and processing additives. 
        Target properties include specific capacity >300 mAh/g, coulombic efficiency >98%, rate capability up to 2C, 
        cycling stability >200 cycles at 50-80°C. Please provide composition, characterization methods, 
        and validation parameters for this battery electrode.""",
        "battery_electrode",
        "sodium_ion_battery_anode_composite"
    )
    results.append(result_a)
    
    # Test B: Phosphate recovery prompt
    print("\n\n" + "="*80)
    print("= TEST B: Phosphate Recovery")
    print("="*80)
    result_b = test_case(
        "B: Phosphate Recovery Material",
        """We're developing an adsorbent material for phosphate recovery from agricultural wastewater. 
        The material should preferentially bind orthophosphate ions while allowing desorption through pH adjustment. 
        Key requirements: adsorption/desorption cycles, nutrient recovery from fertilizer reuse applications, 
        pH-dependent binding to facilitate fertilizer release, compatibility with competing ions present in agricultural runoff. 
        What composition, characterization methods, and validation plan would be appropriate?""",
        "phosphate_recovery",
        "phosphate_recovery_material"
    )
    results.append(result_b)
    
    # Test C: CO2 capture prompt
    print("\n\n" + "="*80)
    print("= TEST C: CO2 Capture")
    print("="*80)
    result_c = test_case(
        "C: Carbon Dioxide Capture Material",
        """Developing an amine-functionalized CO2 capture material for direct air capture (DAC). 
        The material must achieve high CO2/N2 selectivity from flue gas or ambient air. 
        Critical parameters: regeneration energy per kg CO2, amine loss during cycling, adsorption kinetics, 
        and cycling stability over 50-100 regeneration cycles. Please provide preset parameters for characterization 
        and validation testing.""",
        "carbon_capture",
        "co2_capture_material"
    )
    results.append(result_c)
    
    # Test D: Produced-water oil/gas prompt
    print("\n\n" + "="*80)
    print("= TEST D: Oil & Gas Produced Water")
    print("="*80)
    result_d = test_case(
        "D: Oil & Gas Produced-Water Pre-Treatment",
        """For ADNOC oilfield operations, we need a produced-water pre-treatment media to remove oil/grease, 
        hydrocarbons, and high-salinity solids before membrane treatment or reinjection. 
        The material must handle hot Gulf conditions (50-80°C) and high-salinity produced water. 
        Key parameters: oil/grease removal efficiency, TOC and COD reduction, sulfide handling, compatibility 
        with downstream membrane equipment, and backwash characteristics. What preset parameters apply?""",
        "oil_gas_produced_water",
        "oil_gas_produced_water_pretreatment_media"
    )
    results.append(result_d)
    
    # Test E: Fabric oil stain prompt
    print("\n\n" + "="*80)
    print("= TEST E: Fabric Oil Stain Removal")
    print("="*80)
    result_e = test_case(
        "E: Fabric Oil-Stain Removal",
        """Designing a pre-treatment composite for removing oil stains and grease from cotton fabric before laundering. 
        The composite should be fabric-safe (no color bleeding, no tensile strength loss), work with standard washing machines, 
        and be non-irritating for hand application. Must demonstrate colorfastness and rinsability after washing. 
        Please provide composition guidelines, characterization methods, and validation tests.""",
        "fabric_cleaning",
        "fabric_oil_stain_removal_composite"
    )
    results.append(result_e)
    
    # Test F: Roof waterproof coating prompt
    print("\n\n" + "="*80)
    print("= TEST F: Roof Waterproofing & Thermal Insulation")
    print("="*80)
    result_f = test_case(
        "F: Roof Waterproofing Coating",
        """Developing a waterproofing and thermal insulation coating for concrete rooftops to prevent rainwater leakage 
        and reduce heat absorption in hot climates. The roof-applied coating must provide water leakage prevention, 
        thermal resistance for building roof cooling, UV stability for exterior durability, and mechanical properties 
        suitable for roof membrane protection. What characterization methods and validation parameters should guide development?""",
        "roof_waterproofing",
        "roof_waterproofing_thermal_insulation_coating"
    )
    results.append(result_f)
    
    # Summary Report
    print("\n\n" + "#"*80)
    print("# TEST SUMMARY")
    print("#"*80)
    
    total = len(results)
    passed = sum(1 for r in results if r["overall_pass"])
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed/total)*100:.0f}%")
    
    # Detailed results
    print("\n" + "-"*80)
    print("Detailed Results:")
    print("-"*80)
    
    for r in results:
        status = "✅" if r["overall_pass"] else "❌"
        print(f"\n{status} {r['name']}")
        print(f"   Domain: {r['detected_domain']:<25} {'✅' if r['domain_pass'] else '❌'}")
        print(f"   Category: {r['selected_category']:<25} {'✅' if r['category_pass'] else '❌'}")
        print(f"   Alignment: {str(r['alignment_pass']):<25} {'✅' if r['alignment_pass'] else '❌'}")
    
    # Expected vs Actual
    print("\n" + "-"*80)
    print("Expected vs Actual:")
    print("-"*80)
    
    test_specs = [
        ("A", "battery_electrode", "sodium_ion_battery_anode_composite"),
        ("B", "phosphate_recovery", "phosphate_recovery_material"),
        ("C", "carbon_capture", "co2_capture_material"),
        ("D", "oil_gas_produced_water", "oil_gas_produced_water_pretreatment_media"),
        ("E", "fabric_cleaning", "fabric_oil_stain_removal_composite"),
        ("F", "roof_waterproofing", "roof_waterproofing_thermal_insulation_coating"),
    ]
    
    for i, (label, exp_domain, exp_category) in enumerate(test_specs):
        r = results[i]
        print(f"\nTest {label}:")
        print(f"  Expected Domain:   {exp_domain}")
        print(f"  Actual Domain:     {r['detected_domain']:<25} {'✅' if r['detected_domain'] == exp_domain else '❌'}")
        print(f"  Expected Category: {exp_category}")
        print(f"  Actual Category:   {r['selected_category']:<25} {'✅' if r['selected_category'] == exp_category else '❌'}")
    
    # Final verdict
    print("\n" + "="*80)
    if passed == total:
        print("🎉 ALL TESTS PASSED - Domain-first system working correctly!")
        print("="*80)
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed - Review results above")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit(main())

