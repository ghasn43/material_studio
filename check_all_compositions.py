#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check all 12 category default_composition for invalid substrate/environment items"""

from category_registry import (
    CATEGORY_REGISTRY,
    validate_composition_components,
)

INVALID_COMPOSITION_ITEMS = {
    # Substrate types
    "substrate", "glass substrate", "ceramic substrate", "polymer substrate",
    "textile substrate", "concrete substrate", "metal substrate",
    # Application surfaces
    "concrete rooftop", "building wall", "roof surface", "exterior wall",
    "textile surface", "fabric surface", "cotton clothing", "apparel",
    # Support objects
    "glass support", "ceramic support", "polymer support",
    "collector tray", "collection vessel", "reactor surface",
    # Water/environment related
    "desalination membrane", "treated water", "feed water", "water matrix",
    "wastewater", "flue gas", "gas stream", "air stream", "exhaust stream",
    # General environment/context
    "treated surface", "application environment", "use environment",
    "operating medium", "contact medium",
}

print("=" * 80)
print("CHECKING ALL 12 CATEGORIES FOR INVALID COMPOSITION ITEMS")
print("=" * 80)

issues_found = {}

for category_name, preset in CATEGORY_REGISTRY.items():
    if category_name == "other_material":
        continue
    
    composition = preset.get("default_composition", [])
    if not composition:
        print(f"\n✅ {category_name}: NO composition (empty)")
        continue
    
    # Create test data with this category's composition
    test_data = {
        "material_name": category_name,
        "composition": composition
    }
    
    # Validate
    validation = validate_composition_components(test_data)
    
    if validation["is_valid"]:
        print(f"✅ {category_name}: VALID ({len(composition)} components)")
    else:
        print(f"❌ {category_name}: INVALID - Found {len(validation['invalid_items'])} substrate/environment items:")
        for invalid_item in validation["invalid_items"]:
            print(f"   - {invalid_item}")
        issues_found[category_name] = validation["invalid_items"]

print("\n" + "=" * 80)
if issues_found:
    print(f"SUMMARY: {len(issues_found)} categories need fixing:")
    for category, items in issues_found.items():
        print(f"\n  {category}:")
        for item in items:
            print(f"    - {item}")
else:
    print("✅ ALL CATEGORIES PASSED - No substrate/environment items found!")
print("=" * 80)
