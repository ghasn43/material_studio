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
    )
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import Error: {e}')
except Exception as e:
    print(f'❌ Error: {type(e).__name__}: {e}')
