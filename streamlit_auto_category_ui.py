"""
STREAMLIT UI INTEGRATION FOR AUTO-CATEGORY WORKFLOW
====================================================

This module provides Streamlit UI components and integration logic
for the auto-category creation workflow.
"""

import streamlit as st
from auto_category_creation import (
    detect_category_gap,
    propose_new_category,
    check_duplicate_category,
    add_category_to_registry,
    apply_new_category_and_verify
)


def show_category_gap_detection_ui(classification_result: dict, user_request: str, category_registry: dict) -> dict:
    """
    Main UI workflow for auto-category detection and proposal.
    
    Handles:
    1. Detect if new category is needed
    2. Show proposal to user (if needed)
    3. Handle user approval/edit/reject
    4. Apply or cancel the new category
    
    Args:
        classification_result: Result from classify_material_hierarchically()
        user_request: Original user prompt
        category_registry: CATEGORY_REGISTRY from category_registry.py
        
    Returns:
        {
            "action_taken": "none" | "new_category_applied" | "existing_used" | "cancelled",
            "final_category": str,
            "material_data": dict (if applied),
            "message": str
        }
    """
    
    # Step 1: Detect category gap
    gap_detection = detect_category_gap(user_request, classification_result)
    
    if not gap_detection.get("proposal_needed"):
        # No proposal needed - use existing classification
        return {
            "action_taken": "none",
            "final_category": classification_result.get("specific_preset", "other_material"),
            "material_data": None,
            "message": f"Strong match with existing category: {classification_result.get('specific_preset', 'unknown')}"
        }
    
    # Step 2: Show proposal UI
    st.info("🔍 **Category Detection** - No strong match found for this material request.")
    
    st.markdown("### Proposed New Category")
    
    # Generate proposal
    proposal = propose_new_category(user_request, classification_result)
    proposed_cat = proposal.get("proposed_category", {})
    
    # Check for duplicates
    duplicate_check = check_duplicate_category(proposed_cat, category_registry)
    
    # Show proposal details in expandable sections
    with st.expander("📋 View Proposed Category Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Basic Info")
            st.write(f"**Display Name:** {proposed_cat.get('display_name', 'N/A')}")
            st.write(f"**Material Family:** {proposed_cat.get('material_family', 'N/A')}")
            st.write(f"**Functional Class:** {proposed_cat.get('functional_class', 'N/A')}")
            st.write(f"**Application Domain:** {proposed_cat.get('application_domain', 'N/A')}")
            st.write(f"**Confidence:** {proposal.get('confidence', 0)}%")
        
        with col2:
            st.subheader("Aliases")
            aliases = proposed_cat.get("aliases", [])
            if aliases:
                st.write(", ".join(aliases))
            else:
                st.write("None")
        
        st.subheader("Default Composition")
        if proposed_cat.get("composition"):
            for comp in proposed_cat["composition"]:
                st.write(f"- {comp.get('component', 'Unknown')}: {comp.get('ratio', 0)*100:.1f}%")
        
        st.subheader("Key Parameters")
        params = proposed_cat.get("category_specific_parameters", {})
        if params:
            for param_name, param_spec in list(params.items())[:5]:
                st.write(f"- **{param_name}:** {param_spec}")
        
        st.subheader("Safety Tests")
        safety = proposed_cat.get("safety_tests", [])
        if safety:
            for test in safety[:5]:
                st.write(f"- {test}")
    
    # Show duplicate check results
    if duplicate_check.get("duplicate_found"):
        st.warning("⚠️ **Similar Categories Found**")
        st.write(duplicate_check.get("recommendation", ""))
        
        for similar in duplicate_check.get("similar_categories", [])[:3]:
            st.write(f"- {similar.get('display_name')} ({similar.get('similarity_score'):.0f}% match)")
                     
        # Option to use existing
        if st.button("👉 Use Existing Category Instead"):
            recommended = duplicate_check.get("similar_categories", [{}])[0]
            return {
                "action_taken": "existing_used",
                "final_category": recommended.get("category_key", "other_material"),
                "material_data": None,
                "message": f"Using existing category: {recommended.get('display_name', 'Unknown')}"
            }
    
    # Show safety warnings
    if proposal.get("safety_warnings"):
        st.error("⚠️ **Safety Warnings Detected**")
        for warning in proposal.get("safety_warnings", []):
            st.write(warning)
    
    # Step 3: User action buttons
    st.markdown("---")
    st.subheader("What would you like to do?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Approve & Add", key="approve_category"):
            # Add category to registry
            add_result = add_category_to_registry(proposed_cat)
            
            # Apply to material data
            material_data = {
                "material_category": proposed_cat.get("normalized_category_name", ""),
                "material_category_display": proposed_cat.get("display_name", ""),
            }
            
            apply_result = apply_new_category_and_verify(material_data, proposed_cat)
            
            st.success(f"✅ Category Added: {proposed_cat.get('display_name')}")
            st.session_state["action"] = "new_category_applied"
            st.session_state["final_category"] = proposed_cat.get("normalized_category_name")
            st.session_state["material_data"] = apply_result.get("material_data")
            st.rerun()
    
    with col2:
        if st.button("✏️ Edit Before Adding", key="edit_category"):
            st.session_state["edit_mode"] = True
            st.session_state["category_to_edit"] = proposed_cat
            st.info("📝 Edit mode activated. Modify the category details below.")
            st.rerun()
    
    with col3:
        if st.button("❌ Reject & Use 'Other'", key="reject_category"):
            st.session_state["action"] = "cancelled"
            st.session_state["final_category"] = "other_material"
            st.info("Falling back to 'Other (Custom Material)' category.")
            st.rerun()
    
    with col4:
        if st.button("❔ Learn More", key="learn_more"):
            st.session_state["show_help"] = not st.session_state.get("show_help", False)
            st.rerun()
    
    # Handle edit mode
    if st.session_state.get("edit_mode"):
        show_category_editing_ui(proposed_cat)
    
    # Return default (waiting for user action)
    return {
        "action_taken": "waiting_for_user",
        "final_category": None,
        "material_data": None,
        "message": "Waiting for user action on proposed category..."
    }


def show_category_editing_ui(category: dict) -> dict:
    """
    UI for editing proposed category before approval.
    
    Allows user to modify:
    - Display name
    - Aliases
    - Key parameters
    - Disclaimer
    """
    
    st.markdown("### Edit Proposed Category")
    
    # Edit display name
    display_name = st.text_input(
        "Display Name",
        value=category.get("display_name", ""),
        help="User-friendly name for this category"
    )
    category["display_name"] = display_name
    
    # Edit aliases
    aliases_str = st.text_area(
        "Aliases (comma-separated)",
        value=", ".join(category.get("aliases", [])),
        height=80,
        help="Alternative names for this category"
    )
    category["aliases"] = [a.strip() for a in aliases_str.split(",") if a.strip()]
    
    # Edit key parameters
    st.subheader("Category-Specific Parameters")
    params = category.get("category_specific_parameters", {})
    
    for i, (param_name, param_spec) in enumerate(list(params.items())[:5]):
        new_spec = st.text_input(
            f"Parameter: {param_name}",
            value=param_spec,
            key=f"param_{i}"
        )
        params[param_name] = new_spec
    
    category["category_specific_parameters"] = params
    
    # Edit disclaimer
    disclaimer = st.text_area(
        "Category Disclaimer",
        value=category.get("category_specific_disclaimer", ""),
        height=150,
        help="Important disclaimers and limitations for this category"
    )
    category["category_specific_disclaimer"] = disclaimer
    
    # Save edits
    if st.button("💾 Save Edits", key="save_edits"):
        st.session_state["category_to_edit"] = category
        st.session_state["edit_mode"] = False
        st.success("✅ Edits saved. Ready to approve and add.")
        st.rerun()
    
    return category


def show_category_approval_panel(material_data: dict, category: dict) -> dict:
    """
    Final review panel before applying new category.
    
    Shows:
    - Category name and why it's needed
    - Matched keywords from user request
    - Proposed composition
    - Proposed parameters
    - Proposed validation plan
    - Proposed disclaimer
    - Approve/edit/reject buttons
    """
    
    st.markdown("---")
    st.markdown("## Category Review Panel")
    
    # Tab 1: Category Overview
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Composition", "Parameters", "Validation"])
    
    with tab1:
        st.write(f"**Category Name:** {category.get('display_name', 'N/A')}")
        st.write(f"**Reason:** {category.get('created_from_request', 'N/A')}")
        st.write(f"**Material Family:** {category.get('material_family', 'N/A')}")
        st.write(f"**Functional Class:** {category.get('functional_class', 'N/A')}")
        st.write(f"**Application Domain:** {category.get('application_domain', 'N/A')}")
        
        st.subheader("Matched Keywords")
        keywords = category.get("priority_keywords", [])
        if keywords:
            st.write(", ".join(keywords[:10]))
    
    with tab2:
        st.subheader("Proposed Composition")
        composition = category.get("default_composition", [])
        if composition:
            for comp in composition:
                st.write(f"- {comp.get('component', 'Unknown')}: {comp.get('ratio', 0)*100:.1f}%")
        else:
            st.write("No composition specified")
    
    with tab3:
        st.subheader("Proposed Parameters")
        params = category.get("category_specific_parameters", {})
        if params:
            for param_name, param_spec in list(params.items())[:8]:
                st.write(f"**{param_name}:** {param_spec}")
        else:
            st.write("No parameters specified")
    
    with tab4:
        st.subheader("Proposed Validation Plan")
        validation = category.get("validation_plan", {})
        if validation:
            for val_name, val_spec in list(validation.items())[:8]:
                st.write(f"- {val_spec}")
        else:
            st.write("No validation plan specified")
    
    # Disclaimer preview
    st.subheader("Disclaimer")
    disclaimer = category.get("category_specific_disclaimer", "")
    if disclaimer:
        st.info(disclaimer[:500] + ("..." if len(disclaimer) > 500 else ""))
    
    return category
