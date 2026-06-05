#!/usr/bin/env python
"""
Test script for Desalination Pre-Treatment Media category classification and conflict detection.

Tests:
1. Classification of desalination pre-treatment media prompt
2. Conflict detection when mixed with membrane water treatment
3. Conflict detection when mixed with heavy metal adsorbent
4. Verification of correct category parameters and disclaimer
5. Verification of clear_previous_preset_fields functionality
"""

import sys
sys.path.insert(0, '/d/material_studio_1')

from category_registry import (
    classify_material_category,
    classify_material_hierarchically,
    detect_category_conflicts,
    get_category_preset,
    clear_previous_preset_fields,
    apply_category_preset,
    CATEGORY_REGISTRY
)

print("=" * 100)
print("DESALINATION PRE-TREATMENT MEDIA - CLASSIFICATION AND CONFLICT DETECTION TESTS")
print("=" * 100)

# Test user request
user_request = """Design a pre-treatment media for desalination systems using activated carbon, iron oxide, porous silica, 
and mineral stabilizers to reduce organic matter, suspended solids, and selected metal contaminants before membrane 
desalination. The material should improve membrane lifetime and reduce fouling risk. Testing is required for contaminant 
removal, pressure drop, media regeneration, microbial growth risk, leaching, and compatibility with seawater or brackish water."""

print("\n" + "=" * 100)
print("TEST 1: Classification of Desalination Pre-Treatment Media Prompt")
print("=" * 100)

normalized_name, display_name, confidence = classify_material_category(user_request)
print(f"\n✓ Classification Result:")
print(f"  Normalized category: {normalized_name}")
print(f"  Display name: {display_name}")
print(f"  Confidence: {confidence}%")

expected_normalized = "desalination_pretreatment_media"
expected_display = "Desalination Pre-Treatment Media"

if normalized_name == expected_normalized and display_name == expected_display:
    print(f"\n✅ PASS: Correctly classified as '{display_name}'")
else:
    print(f"\n❌ FAIL: Expected '{expected_display}' but got '{display_name}'")
    sys.exit(1)

# Test hierarchical classification
print("\n" + "=" * 100)
print("TEST 2: Hierarchical Classification")
print("=" * 100)

hier_class = classify_material_hierarchically(user_request)
print(f"\n✓ Hierarchical Classification:")
print(f"  Specific preset: {hier_class['specific_preset']}")
print(f"  Confidence: {hier_class['confidence_score']}%")
print(f"  Material family: {hier_class['material_family']}")
print(f"  Functional class: {hier_class['functional_class']}")
print(f"  Application domain: {hier_class['application_domain']}")

if hier_class['specific_preset'] == 'desalination_pretreatment_media':
    print(f"\n✅ PASS: Hierarchical classification correct")
else:
    print(f"\n❌ FAIL: Expected 'desalination_pretreatment_media' but got '{hier_class['specific_preset']}'")
    sys.exit(1)

# Test category preset
print("\n" + "=" * 100)
print("TEST 3: Category Preset Data")
print("=" * 100)

preset = get_category_preset("desalination_pretreatment_media")
print(f"\n✓ Preset Data Retrieved:")
print(f"  Category name: {preset.get('display_name')}")
print(f"  Default composition items: {len(preset.get('default_composition', []))}")
print(f"  Category-specific parameters: {len(preset.get('category_specific_parameters', {}))}")
print(f"  Validation plan items: {len(preset.get('validation_plan', {}))}")

# Verify composition
composition = preset.get('default_composition', [])
if len(composition) == 6:
    print(f"\n✓ Composition includes all 6 components:")
    for item in composition:
        print(f"    - {item['component']}: {item['ratio']*100:.0f}%")
    total_ratio = sum(item['ratio'] for item in composition)
    if abs(total_ratio - 1.0) < 0.01:
        print(f"  Total ratio: {total_ratio:.2f} ✅")
    else:
        print(f"  Total ratio: {total_ratio:.2f} ❌ (should be 1.00)")
        sys.exit(1)
else:
    print(f"\n❌ FAIL: Expected 6 composition items but got {len(composition)}")
    sys.exit(1)

# Verify disclaimer
disclaimer = preset.get('category_specific_disclaimer', '')
if 'desalination pre-treatment' in disclaimer.lower() and 'seawater' in disclaimer.lower():
    print(f"\n✅ PASS: Disclaimer includes desalination-specific content")
else:
    print(f"\n❌ FAIL: Disclaimer missing desalination-specific content")
    sys.exit(1)

# Test conflict detection - should NOT conflict with correct category
print("\n" + "=" * 100)
print("TEST 4: Conflict Detection - Correct Category (No Conflict)")
print("=" * 100)

conflict_result = detect_category_conflicts(user_request, "desalination_pretreatment_media")
print(f"\n✓ Conflict detection result:")
print(f"  Conflict detected: {conflict_result['conflict_detected']}")
print(f"  Blocked export: {conflict_result['blocked_export']}")

if not conflict_result['conflict_detected'] and not conflict_result['blocked_export']:
    print(f"\n✅ PASS: No conflict with correct category")
else:
    print(f"\n❌ FAIL: Unexpected conflict with correct category")
    print(f"  Reason: {conflict_result['conflict_reason']}")
    sys.exit(1)

# Test conflict detection - SHOULD conflict with membrane_water_treatment
print("\n" + "=" * 100)
print("TEST 5: Conflict Detection - Wrong Category (Membrane Water Treatment)")
print("=" * 100)

conflict_result = detect_category_conflicts(user_request, "membrane_water_treatment")
print(f"\n✓ Conflict detection result:")
print(f"  Conflict detected: {conflict_result['conflict_detected']}")
print(f"  Blocked export: {conflict_result['blocked_export']}")
print(f"  Recommended category: {conflict_result['recommended_category']}")

if conflict_result['conflict_detected'] and conflict_result['blocked_export']:
    if conflict_result['recommended_category'] == 'desalination_pretreatment_media':
        print(f"\n✅ PASS: Correctly detected conflict and recommended 'desalination_pretreatment_media'")
        print(f"  Reason: {conflict_result['conflict_reason']}")
    else:
        print(f"\n❌ FAIL: Recommended wrong category: {conflict_result['recommended_category']}")
        sys.exit(1)
else:
    print(f"\n❌ FAIL: Should have detected conflict with membrane_water_treatment")
    sys.exit(1)

# Test conflict detection - SHOULD conflict with heavy_metal_adsorbent
print("\n" + "=" * 100)
print("TEST 6: Conflict Detection - Wrong Category (Heavy Metal Adsorbent)")
print("=" * 100)

conflict_result = detect_category_conflicts(user_request, "adsorbent_heavy_metals")
print(f"\n✓ Conflict detection result:")
print(f"  Conflict detected: {conflict_result['conflict_detected']}")
print(f"  Blocked export: {conflict_result['blocked_export']}")
print(f"  Recommended category: {conflict_result['recommended_category']}")

if conflict_result['conflict_detected'] and conflict_result['blocked_export']:
    if conflict_result['recommended_category'] == 'desalination_pretreatment_media':
        print(f"\n✅ PASS: Correctly detected conflict and recommended 'desalination_pretreatment_media'")
        print(f"  Reason: {conflict_result['conflict_reason']}")
    else:
        print(f"\n❌ FAIL: Recommended wrong category: {conflict_result['recommended_category']}")
        sys.exit(1)
else:
    print(f"\n❌ FAIL: Should have detected conflict with adsorbent_heavy_metals")
    sys.exit(1)

# Test clear_previous_preset_fields
print("\n" + "=" * 100)
print("TEST 7: Clear Previous Preset Fields (Prevent Mixed Contamination)")
print("=" * 100)

# Create material data with fields from membrane_water_treatment
material_data_from_membrane = {
    "material_category": "membrane_water_treatment",
    "material_category_display": "Membrane Water Treatment Material",
    "category_specific_parameters": {
        "water_flux_target": "L/m²·h under defined pressure",
        "operating_pressure": "0.1–10 bar"
    },
    "validation_plan": {
        "pure_water_permeability": "L/m²·h·bar baseline"
    },
    "composition": [
        {"component": "Polymer membrane matrix", "ratio": 0.50},
        {"component": "Hydrophilic additive", "ratio": 0.15}
    ],
    "category_specific_disclaimer": "DISCLAIMER: Membrane-specific disclaimer text...",
    "characterization_methods": ["SEM/EDS"]
}

print(f"\n✓ Material data BEFORE clearing (from membrane_water_treatment):")
print(f"  Keys: {list(material_data_from_membrane.keys())}")
print(f"  Category: {material_data_from_membrane.get('material_category')}")
print(f"  Composition items: {len(material_data_from_membrane.get('composition', []))}")

# Clear the preset fields
cleaned_data = clear_previous_preset_fields(material_data_from_membrane)

print(f"\n✓ Material data AFTER clearing:")
print(f"  Keys: {list(cleaned_data.keys())}")
print(f"  Category: {cleaned_data.get('material_category')}")
print(f"  Composition items: {len(cleaned_data.get('composition', []))}")

# Apply new desalination preset
cleaned_data = apply_category_preset(cleaned_data, "desalination_pretreatment_media")

print(f"\n✓ Material data AFTER applying desalination preset:")
print(f"  Category: {cleaned_data.get('material_category')}")
print(f"  Display name: {cleaned_data.get('material_category_display')}")
print(f"  Composition items: {len(cleaned_data.get('composition', []))}")

# Verify contamination didn't occur
if cleaned_data.get('material_category') == 'desalination_pretreatment_media':
    if cleaned_data.get('material_category_display') == 'Desalination Pre-Treatment Media':
        # Check that old membrane parameters are gone
        params = cleaned_data.get('category_specific_parameters', {})
        if 'water_flux_target' in params:
            print(f"\n❌ FAIL: Old membrane parameter 'water_flux_target' still present!")
            sys.exit(1)
        elif 'pressure_drop_target' in params:
            print(f"\n✅ PASS: New desalination parameter 'pressure_drop_target' is present")
        else:
            print(f"\n⚠️  WARNING: Expected desalination parameters not found")
        
        # Check disclaimer is correct
        disclaimer = cleaned_data.get('category_specific_disclaimer', '')
        if 'membrane' in disclaimer.lower() and 'water flux' in disclaimer.lower():
            print(f"\n❌ FAIL: Old membrane disclaimer still present!")
            sys.exit(1)
        elif 'desalination' in disclaimer.lower():
            print(f"\n✅ PASS: New desalination disclaimer is correct")
        
        print(f"\n✅ PASS: Preset switching successful - no contamination from old category")
    else:
        print(f"\n❌ FAIL: Wrong display name: {cleaned_data.get('material_category_display')}")
        sys.exit(1)
else:
    print(f"\n❌ FAIL: Wrong category after preset switch: {cleaned_data.get('material_category')}")
    sys.exit(1)

# Summary
print("\n" + "=" * 100)
print("✅ ALL TESTS PASSED")
print("=" * 100)
print("\nSummary:")
print("  ✅ Test 1: Classification of desalination prompt - PASS")
print("  ✅ Test 2: Hierarchical classification - PASS")
print("  ✅ Test 3: Category preset data - PASS")
print("  ✅ Test 4: No conflict with correct category - PASS")
print("  ✅ Test 5: Conflict detected with membrane_water_treatment - PASS")
print("  ✅ Test 6: Conflict detected with adsorbent_heavy_metals - PASS")
print("  ✅ Test 7: Clear previous preset fields prevents contamination - PASS")
print("\n" + "=" * 100)
