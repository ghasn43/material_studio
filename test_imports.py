#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test all imports from category_registry"""

try:
    from category_registry import (
        CATEGORY_REGISTRY,
        CATEGORY_PRIORITY_ORDER,
        HIERARCHICAL_PRESETS,
        MATERIAL_FAMILIES,
        FUNCTIONAL_CLASSES,
        APPLICATION_DOMAINS,
        classify_material_category,
        classify_material_hierarchically,
        get_category_preset,
        apply_category_preset,
        validate_required_fields,
        format_scientific_label,
        export_report,
        get_category_display_name,
        validate_category_exists,
        clear_previous_preset_fields,
        run_three_stage_verification,
        normalize_category_name,
    )
    print("✓ All imports successful!")
    print(f"  - CATEGORY_REGISTRY keys: {len(CATEGORY_REGISTRY)}")
    print(f"  - normalize_category_name callable: {callable(normalize_category_name)}")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
