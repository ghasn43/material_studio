# -*- coding: utf-8 -*-
"""Minimal Streamlit test to debug import issues"""
import streamlit as st

st.write("Loading imports...")

try:
    from category_registry import normalize_category_name
    st.success("✓ normalize_category_name imported")
except Exception as e:
    st.error(f"✗ normalize_category_name: {e}")

try:
    from category_registry import CATEGORY_REGISTRY
    st.success(f"✓ CATEGORY_REGISTRY imported ({len(CATEGORY_REGISTRY)} categories)")
except Exception as e:
    st.error(f"✗ CATEGORY_REGISTRY: {e}")

try:
    from category_registry import (
        CATEGORY_PRIORITY_ORDER,
        classify_material_hierarchically,
        apply_category_preset,
        clear_previous_preset_fields,
        run_three_stage_verification,
    )
    st.success("✓ All major functions imported")
except Exception as e:
    st.error(f"✗ Major functions: {e}")

st.write("All import tests completed!")
