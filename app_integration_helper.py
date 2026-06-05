"""
APP.PY INTEGRATION HELPER MODULE
=================================

This module provides ready-to-use functions for integrating auto-category
creation into app.py. It handles all the necessary imports and session
state management.

Usage in app.py:
    from app_integration_helper import init_auto_category_session, handle_auto_category_workflow
    
    # Initialize session (in main section)
    init_auto_category_session()
    
    # Use in material analysis workflow
    auto_cat_result = handle_auto_category_workflow(user_prompt, classification_result, CATEGORY_REGISTRY)
"""

import streamlit as st
from auto_category_creation import (
    detect_category_gap,
    propose_new_category,
    check_duplicate_category,
    add_category_to_registry,
    apply_new_category_and_verify
)
from streamlit_auto_category_ui import (
    show_category_gap_detection_ui,
    show_category_editing_ui,
    show_category_approval_panel
)
from category_registry import CATEGORY_REGISTRY, get_category_preset, apply_category_preset


def init_auto_category_session():
    """
    Initialize all session state variables needed for auto-category workflow.
    Call this once at the start of app.py main section.
    """
    # Feature toggle
    if "enable_auto_category" not in st.session_state:
        st.session_state.enable_auto_category = False
    
    # Auto-category workflow state
    if "auto_category_gap_detected" not in st.session_state:
        st.session_state.auto_category_gap_detected = False
    
    if "auto_category_proposal" not in st.session_state:
        st.session_state.auto_category_proposal = None
    
    if "auto_category_new_category" not in st.session_state:
        st.session_state.auto_category_new_category = None
    
    if "auto_category_action" not in st.session_state:
        st.session_state.auto_category_action = None  # "approve", "edit", "reject", "waiting"
    
    if "auto_category_editing" not in st.session_state:
        st.session_state.auto_category_editing = False
    
    if "show_auto_category_review" not in st.session_state:
        st.session_state.show_auto_category_review = False


def add_auto_category_sidebar_toggle():
    """
    Add the auto-category toggle to sidebar.
    Call this in the sidebar section of app.py.
    
    Returns:
        bool - Current state of enable_auto_category toggle
    """
    st.markdown("---")
    st.markdown("### 🤖 AI Features")
    
    enable = st.toggle(
        "🤖 Auto-Category Creation",
        value=st.session_state.get("enable_auto_category", False),
        help="When a material request doesn't match existing categories, "
             "automatically propose a new category for approval. "
             "RECOMMENDED: Enable this for novel materials."
    )
    
    st.session_state.enable_auto_category = enable
    
    return enable


def handle_auto_category_workflow(user_prompt: str, classification_result: dict, category_registry: dict) -> dict:
    """
    Main workflow handler for auto-category creation.
    
    Call this after material classification and before showing results.
    
    Args:
        user_prompt: Original user request
        classification_result: Result from classify_material_hierarchically()
        category_registry: CATEGORY_REGISTRY from category_registry.py
    
    Returns:
        {
            "workflow_active": bool,  # True if auto-category UI is shown
            "workflow_complete": bool,  # True if user has made a decision
            "action": str,  # "approve", "edit", "reject", "waiting", None
            "final_category": str,  # Key of final category to use
            "new_category": dict,  # New category preset (if approved)
            "should_stop_rendering": bool,  # True if app should stop rendering and wait
            "message": str  # Status message to show user
        }
    """
    
    if not st.session_state.get("enable_auto_category"):
        # Auto-category disabled, skip workflow
        return {
            "workflow_active": False,
            "workflow_complete": True,
            "action": None,
            "final_category": classification_result.get("specific_preset", "other_material"),
            "new_category": None,
            "should_stop_rendering": False,
            "message": "Auto-category creation disabled"
        }
    
    # Step 1: Check for category gap
    gap_detection = detect_category_gap(user_prompt, classification_result)
    
    if not gap_detection.get("proposal_needed"):
        # No gap detected, use existing category
        return {
            "workflow_active": False,
            "workflow_complete": True,
            "action": "strong_match",
            "final_category": classification_result.get("specific_preset", "other_material"),
            "new_category": None,
            "should_stop_rendering": False,
            "message": f"Strong match with existing category ({classification_result.get('confidence_score', 0):.0f}% confidence)"
        }
    
    # Gap detected - show UI
    st.markdown("---")
    st.markdown("### 🤖 Auto-Category Creation")
    st.info(gap_detection.get("reason", "Proposing new category for this material"))
    
    # Step 2: Generate proposal if not already done
    if st.session_state.auto_category_proposal is None:
        with st.spinner("🤖 Generating category proposal..."):
            proposal = propose_new_category(user_prompt, classification_result)
            st.session_state.auto_category_proposal = proposal
    else:
        proposal = st.session_state.auto_category_proposal
    
    proposed_cat = proposal.get("proposed_category", {})
    
    # Step 3: Show proposal details
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
                st.write(", ".join(aliases[:5]))
            else:
                st.write("None")
        
        st.subheader("Composition")
        composition = proposed_cat.get("default_composition", [])
        if composition:
            for comp in composition:
                st.write(f"- {comp.get('component', 'Unknown')}: {comp.get('ratio', 0)*100:.1f}%")
    
    # Step 4: Check for duplicates
    duplicate_check = check_duplicate_category(proposed_cat, category_registry)
    
    if duplicate_check.get("duplicate_found"):
        st.warning("⚠️ **Similar Categories Found**")
        st.write(duplicate_check.get("recommendation", ""))
        
        for similar in duplicate_check.get("similar_categories", [])[:3]:
            st.write(f"- {similar.get('display_name')} ({similar.get('similarity_score'):.0f}% match)")
    
    # Step 5: Show safety warnings
    if proposal.get("safety_warnings"):
        st.error("⚠️ **Safety Warnings Detected**")
        for warning in proposal.get("safety_warnings", []):
            st.write(warning)
    
    # Step 6: User action buttons
    st.markdown("---")
    st.subheader("What would you like to do?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Approve & Add", key="btn_approve_auto_cat"):
            st.session_state.auto_category_action = "approve"
            st.session_state.auto_category_new_category = proposed_cat
            st.rerun()
    
    with col2:
        if st.button("✏️ Edit Before Adding", key="btn_edit_auto_cat"):
            st.session_state.auto_category_action = "edit"
            st.session_state.auto_category_editing = True
            st.rerun()
    
    with col3:
        if st.button("❌ Reject & Use 'Other'", key="btn_reject_auto_cat"):
            st.session_state.auto_category_action = "reject"
            st.session_state.auto_category_editing = False
            st.rerun()
    
    with col4:
        if st.button("❔ Learn More", key="btn_help_auto_cat"):
            show_auto_category_help()
    
    # Step 7: Handle editing if needed
    if st.session_state.auto_category_editing:
        st.markdown("---")
        st.markdown("### ✏️ Edit Proposed Category")
        
        edited_cat = dict(proposed_cat)  # Copy for editing
        
        # Edit display name
        edited_cat["display_name"] = st.text_input(
            "Display Name",
            value=edited_cat.get("display_name", ""),
            key="edit_display_name"
        )
        
        # Edit aliases
        aliases_str = st.text_area(
            "Aliases (comma-separated)",
            value=", ".join(edited_cat.get("aliases", [])),
            height=80,
            key="edit_aliases"
        )
        edited_cat["aliases"] = [a.strip() for a in aliases_str.split(",") if a.strip()]
        
        # Save edits button
        if st.button("💾 Save Edits", key="btn_save_edits_auto_cat"):
            st.session_state.auto_category_new_category = edited_cat
            st.session_state.auto_category_editing = False
            st.session_state.auto_category_action = "approve"
            st.rerun()
    
    # Step 8: Process user action
    if st.session_state.auto_category_action == "approve":
        # User approved category
        new_cat = st.session_state.auto_category_new_category
        
        st.success(f"✅ New category '{new_cat.get('display_name')}' will be added")
        
        return {
            "workflow_active": True,
            "workflow_complete": True,
            "action": "approve",
            "final_category": new_cat.get("normalized_category_name", ""),
            "new_category": new_cat,
            "should_stop_rendering": False,
            "message": f"New category '{new_cat.get('display_name')}' approved and will be applied"
        }
    
    elif st.session_state.auto_category_action == "reject":
        st.warning("Falling back to 'Other (Custom Material)' category")
        
        return {
            "workflow_active": True,
            "workflow_complete": True,
            "action": "reject",
            "final_category": "other_material",
            "new_category": None,
            "should_stop_rendering": False,
            "message": "Category proposal rejected, using 'Other' fallback"
        }
    
    elif st.session_state.auto_category_action == "edit":
        # Editing in progress, show stop rendering
        return {
            "workflow_active": True,
            "workflow_complete": False,
            "action": "waiting",
            "final_category": None,
            "new_category": None,
            "should_stop_rendering": True,
            "message": "Waiting for user to complete editing..."
        }
    
    # Still waiting for user action
    return {
        "workflow_active": True,
        "workflow_complete": False,
        "action": "waiting",
        "final_category": None,
        "new_category": None,
        "should_stop_rendering": True,
        "message": "Waiting for user action on proposed category..."
    }


def show_auto_category_help():
    """Display help information about auto-category feature."""
    with st.expander("❔ About Auto-Category Creation", expanded=True):
        st.markdown("""
        ### What is Auto-Category Creation?
        
        When you describe a novel material that doesn't match existing categories,
        this feature automatically proposes a new category tailored to your material.
        
        ### How does it work?
        
        1. **Gap Detection:** Analyzes your request and detects if it matches existing categories
        2. **Proposal Generation:** Creates a complete category preset with:
           - Display name and normalized key
           - Material family, functional class, application domain
           - Default composition
           - Category-specific parameters
           - Validation plan and safety tests
           - Processing method
           - Liability disclaimer
        
        3. **Duplicate Check:** Scans existing categories for similar materials
        4. **User Approval:** Shows you the proposal and lets you:
           - ✅ Approve and add to registry
           - ✏️ Edit fields before approval
           - ❌ Reject and use generic "Other" category
        
        ### When to use it?
        
        - ✅ Novel materials not in existing categories
        - ✅ Experimental or proof-of-concept materials
        - ✅ Hybrid materials combining multiple functions
        - ✅ Cleaning and fabric treatment materials
        
        ### When NOT to use it?
        
        - ❌ Well-established materials (AWH, photocatalytic, etc.)
        - ❌ When you want quick results without approval workflow
        - ❌ For testing or demo purposes
        """)


def apply_auto_category_to_material(result: dict, new_category: dict, user_prompt: str) -> dict:
    """
    Apply approved new category to material data.
    
    Args:
        result: Material analysis result from Claude
        new_category: Approved new category preset
        user_prompt: Original user request
    
    Returns:
        Updated material_data with new category applied
    """
    category_key = new_category.get("normalized_category_name", "unknown")
    
    # Apply new category
    result["material_category"] = category_key
    result["material_category_display"] = new_category.get("display_name", "")
    result["category_exists"] = False  # New category, not in permanent registry yet
    result["auto_created_category"] = True
    
    # Apply preset fields
    result["category_specific_parameters"] = new_category.get("category_specific_parameters", {})
    result["validation_plan"] = new_category.get("validation_plan", {})
    result["category_specific_disclaimer"] = new_category.get("category_specific_disclaimer", "")
    result["characterization_methods"] = new_category.get("characterization_methods", [])
    result["safety_tests"] = new_category.get("safety_tests", [])
    result["processing_method"] = new_category.get("processing_method", [])
    
    # Store new category for later reference
    result["new_category_metadata"] = {
        "created_from_request": user_prompt[:200],
        "created_at": str(__import__('datetime').datetime.now()),
        "full_category": new_category
    }
    
    # Create aliases for PDF export
    result["preset_parameters"] = result["category_specific_parameters"]
    result["preset_validation_plan"] = result["validation_plan"]
    
    return result


def get_auto_category_enabled() -> bool:
    """Get current state of auto-category feature toggle."""
    return st.session_state.get("enable_auto_category", False)


def reset_auto_category_state():
    """Reset all auto-category session state variables."""
    st.session_state.auto_category_gap_detected = False
    st.session_state.auto_category_proposal = None
    st.session_state.auto_category_new_category = None
    st.session_state.auto_category_action = None
    st.session_state.auto_category_editing = False
    st.session_state.show_auto_category_review = False
