# -*- coding: utf-8 -*-
"""Minimal app to test imports"""
import streamlit as st

# Minimal test
st.title("Import Test")

try:
    from category_registry import CATEGORY_REGISTRY
    st.success(f"Imports work! Found {len(CATEGORY_REGISTRY)} categories")
except ImportError as e:
    st.error(f"ImportError: {e}")
except Exception as e:
    st.error(f"Other error: {type(e).__name__}: {e}")
