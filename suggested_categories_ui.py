"""
STREAMLIT UI FOR SUGGESTED CATEGORIES
======================================

Provides Streamlit components for displaying and managing suggested material categories.

Functions:
- show_suggested_categories_panel: Display suggestions with selection interface
- show_category_preview: Show detailed category information
- category_selector_ui: Let user choose among suggestions
"""

import streamlit as st
from suggested_category_workflow import generate_suggested_category_preset


def show_suggested_categories_panel(suggestions: list, user_request: str, material_data: dict = None) -> dict:
    """
    Display suggested categories panel and handle user selection.
    
    Args:
        suggestions: List of suggested categories from propose_candidate_categories()
        user_request: Original user request
        material_data: Current material analysis result (optional)
        
    Returns:
        {
            "action": "use_existing" | "use_suggested" | "edit_suggested" | "cancel",
            "selected_category": dict,  # Selected suggested category
            "final_category": str,  # Normalized category name to use
            "should_regenerate": bool,
            "reason": str
        }
    """
    
    st.markdown("---")
    st.markdown("### 🎯 Suggested Material Categories")
    st.info(
        "The top classification may not fully match your request. "
        "Review these suggestions to find the best category or create a new one."
    )
    
    if not suggestions:
        st.warning("No suggestions available. Please try describing your material differently.")
        return {
            "action": "cancel",
            "selected_category": None,
            "final_category": None,
            "should_regenerate": False,
            "reason": "No suggestions generated"
        }
    
    # Initialize session state for suggestion tracking
    if "suggested_category_selected" not in st.session_state:
        st.session_state.suggested_category_selected = None
    if "suggestion_action" not in st.session_state:
        st.session_state.suggestion_action = None
    
    # Display suggestions as tabs
    suggestion_tabs = st.tabs([f"Suggestion {i+1}" for i in range(len(suggestions))])
    
    for idx, (tab, suggestion) in enumerate(zip(suggestion_tabs, suggestions)):
        with tab:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Display name and key info
                st.subheader(suggestion["display_name"])
                
                # Confidence badge
                confidence = suggestion["confidence"]
                if confidence >= 80:
                    confidence_emoji = "🟢"
                elif confidence >= 60:
                    confidence_emoji = "🟡"
                else:
                    confidence_emoji = "🔴"
                
                st.write(f"{confidence_emoji} **Confidence:** {confidence}%")
                
                # Category info in columns
                info_col1, info_col2, info_col3, info_col4 = st.columns(4)
                with info_col1:
                    st.write(f"**Family:** `{suggestion['material_family']}`")
                with info_col2:
                    st.write(f"**Class:** `{suggestion['functional_class']}`")
                with info_col3:
                    st.write(f"**Domain:** `{suggestion['application_domain']}`")
                with info_col4:
                    status = "✅ Exists" if suggestion["exists_in_registry"] else "✨ New"
                    st.write(f"**Status:** {status}")
                
                st.markdown(f"**Normalized Name:** `{suggestion['normalized_category_name']}`")
                
                # Matched keywords
                if suggestion["matched_keywords"]:
                    st.write(f"**Matched Keywords:** {', '.join(suggestion['matched_keywords'][:8])}")
                
                # Reason
                st.write(f"**Why:** {suggestion['reason']}")
            
            with col2:
                st.write("")  # Spacing
                if st.button(
                    f"✅ Select",
                    key=f"btn_select_suggestion_{idx}",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.suggested_category_selected = idx
                    st.session_state.suggestion_action = "selected"
                    st.rerun()
    
    # Action section below tabs
    st.markdown("---")
    st.markdown("### 🎬 What would you like to do?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Use Recommended", use_container_width=True, key="btn_use_recommended"):
            recommended = suggestions[0]
            st.session_state.suggestion_action = "use_recommended"
            st.session_state.suggested_category_selected = 0
            st.rerun()
    
    with col2:
        if st.button("✨ Add New Category", use_container_width=True, key="btn_add_new"):
            if st.session_state.suggested_category_selected is not None:
                st.session_state.suggestion_action = "add_new"
                st.rerun()
            else:
                st.warning("Please select a suggestion first")
    
    with col3:
        if st.button("✏️ Edit & Add", use_container_width=True, key="btn_edit_add"):
            if st.session_state.suggested_category_selected is not None:
                st.session_state.suggestion_action = "edit_add"
                st.rerun()
            else:
                st.warning("Please select a suggestion first")
    
    with col4:
        if st.button("❌ Cancel", use_container_width=True, key="btn_cancel_suggestions"):
            st.session_state.suggestion_action = "cancel"
            st.rerun()
    
    # Process user action
    if st.session_state.suggestion_action == "selected":
        idx = st.session_state.suggested_category_selected
        selected = suggestions[idx]
        st.success(f"✅ Selected: {selected['display_name']}")
        
        return {
            "action": "use_suggested",
            "selected_category": selected,
            "final_category": selected["normalized_category_name"],
            "should_regenerate": True,
            "reason": f"User selected suggested category: {selected['display_name']}"
        }
    
    elif st.session_state.suggestion_action == "use_recommended":
        recommended = suggestions[0]
        return {
            "action": "use_suggested",
            "selected_category": recommended,
            "final_category": recommended["normalized_category_name"],
            "should_regenerate": True,
            "reason": f"User accepted recommended category: {recommended['display_name']}"
        }
    
    elif st.session_state.suggestion_action == "add_new":
        idx = st.session_state.suggested_category_selected
        selected = suggestions[idx]
        
        if not selected["exists_in_registry"]:
            st.info(f"Adding '{selected['display_name']}' to registry...")
            st.markdown("---")
            st.markdown("### 📋 Category Preview")
            
            # Show what will be added
            with st.expander("View Complete Category Preset", expanded=False):
                preset = generate_suggested_category_preset(selected, user_request)
                st.json({
                    "display_name": preset["display_name"],
                    "material_family": preset["material_family"],
                    "functional_class": preset["functional_class"],
                    "application_domain": preset["application_domain"],
                    "num_keywords": len(preset.get("priority_keywords", [])),
                    "num_composition_items": len(preset.get("default_composition", [])),
                    "has_processing_method": len(preset.get("processing_method", [])) > 0
                })
            
            if st.button("✅ Confirm & Add to Registry", key="btn_confirm_add"):
                return {
                    "action": "use_suggested",
                    "selected_category": selected,
                    "final_category": selected["normalized_category_name"],
                    "should_regenerate": True,
                    "should_add_to_registry": True,
                    "reason": f"User confirmed adding new category: {selected['display_name']}"
                }
    
    elif st.session_state.suggestion_action == "edit_add":
        idx = st.session_state.suggested_category_selected
        selected = suggestions[idx]
        
        st.markdown("---")
        st.markdown("### ✏️ Edit Category Before Adding")
        
        # Editable fields
        col1, col2 = st.columns(2)
        with col1:
            edited_display = st.text_input(
                "Display Name",
                value=selected["display_name"],
                key="edit_display_name"
            )
        with col2:
            edited_normalized = st.text_input(
                "Normalized Name (snake_case)",
                value=selected["normalized_category_name"],
                key="edit_normalized_name"
            )
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            edited_family = st.text_input(
                "Material Family",
                value=selected["material_family"],
                key="edit_family"
            )
        with col2:
            edited_class = st.text_input(
                "Functional Class",
                value=selected["functional_class"],
                key="edit_class"
            )
        with col3:
            edited_domain = st.text_input(
                "Application Domain",
                value=selected["application_domain"],
                key="edit_domain"
            )
        with col4:
            st.write("")  # Spacing
        
        # Save edited category
        if st.button("💾 Save & Add", key="btn_save_edited"):
            edited_category = dict(selected)
            edited_category["display_name"] = edited_display
            edited_category["normalized_category_name"] = edited_normalized
            edited_category["material_family"] = edited_family
            edited_category["functional_class"] = edited_class
            edited_category["application_domain"] = edited_domain
            
            return {
                "action": "use_suggested",
                "selected_category": edited_category,
                "final_category": edited_normalized,
                "should_regenerate": True,
                "should_add_to_registry": True,
                "reason": f"User edited and confirmed adding: {edited_display}"
            }
    
    elif st.session_state.suggestion_action == "cancel":
        return {
            "action": "cancel",
            "selected_category": None,
            "final_category": None,
            "should_regenerate": False,
            "reason": "User cancelled suggestion panel"
        }
    
    # Still waiting for user action
    return {
        "action": "waiting",
        "selected_category": None,
        "final_category": None,
        "should_regenerate": False,
        "reason": "Waiting for user action"
    }


def show_category_comparison(current_category: str, suggestions: list, user_request: str):
    """
    Show comparison between current (wrong) category and suggestions.
    
    Args:
        current_category: Current selected category key
        suggestions: List of suggested categories
        user_request: Original user request
    """
    from category_registry import CATEGORY_REGISTRY
    
    st.markdown("### 🔄 Why Suggestions Are Better")
    
    current_cat = CATEGORY_REGISTRY.get(current_category, {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**❌ Current Selection**")
        st.write(f"**{current_cat.get('display_name', current_category)}**")
        st.write(f"Family: `{current_cat.get('material_family', 'unknown')}`")
        st.write(f"Class: `{current_cat.get('functional_class', 'unknown')}`")
        st.write(f"Domain: `{current_cat.get('application_domain', 'unknown')}`")
        
        # Check match
        request_lower = user_request.lower()
        keywords = current_cat.get("priority_keywords", [])
        matched = sum(1 for kw in keywords if kw.lower() in request_lower)
        match_pct = (matched / len(keywords) * 100) if keywords else 0
        
        st.metric("Keyword Match", f"{match_pct:.0f}%")
    
    with col2:
        if suggestions:
            st.markdown("**✅ Recommended**")
            rec = suggestions[0]
            st.write(f"**{rec['display_name']}**")
            st.write(f"Family: `{rec['material_family']}`")
            st.write(f"Class: `{rec['functional_class']}`")
            st.write(f"Domain: `{rec['application_domain']}`")
            st.metric("Confidence", f"{rec['confidence']}%")


def category_selector_ui(current_category: str, existing_suggestions: list = None):
    """
    Simple category selector UI (for fallback/manual selection).
    
    Args:
        current_category: Current selected category
        existing_suggestions: Pre-computed suggestions (optional)
        
    Returns:
        Selected category key or None
    """
    from category_registry import CATEGORY_REGISTRY
    
    st.markdown("### 📚 Or Choose Existing Category")
    
    categories = [
        (key, data.get("display_name", key))
        for key, data in CATEGORY_REGISTRY.items()
        if key != "other_material"
    ]
    categories.sort(key=lambda x: x[1])
    
    selected_idx = st.selectbox(
        "Available categories:",
        range(len(categories)),
        format_func=lambda i: categories[i][1],
        key="manual_category_select"
    )
    
    chosen_key, chosen_display = categories[selected_idx]
    
    if st.button(f"Use {chosen_display}", use_container_width=True, key="btn_manual_category"):
        return chosen_key
    
    return None
