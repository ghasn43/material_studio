"""
INTEGRATION GUIDE FOR AUTO-CATEGORY CREATION INTO APP.PY
=========================================================

This file documents the exact integration points and code changes needed.
"""

# ==============================================================================
# INTEGRATION POINT 1: ADD IMPORTS AT TOP OF APP.PY
# ==============================================================================

# Add these imports after existing imports (around line 20):

"""
# Import auto-category creation system
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
"""

# ==============================================================================
# INTEGRATION POINT 2: ADD SIDEBAR TOGGLE FOR AUTO-CATEGORY
# ==============================================================================

# Add this to sidebar (around line 1220):

"""
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🤖 AI Features")
    enable_auto_category = st.toggle(
        "🤖 Auto-Category Creation",
        value=False,
        help="When a material request doesn't match existing categories, "
             "automatically propose a new category for approval. "
             "RECOMMENDED: Enable this for novel materials."
    )
"""

# ==============================================================================
# INTEGRATION POINT 3: ADD AUTO-CATEGORY LOGIC AFTER CLASSIFICATION
# ==============================================================================

# Add this code after hier_classification is obtained (around line 1350):

"""
# STEP 1: Check for category gap if auto-category is enabled
if enable_auto_category and hier_classification:
    gap_detection = detect_category_gap(user_prompt, hier_classification)
    
    if gap_detection.get("proposal_needed"):
        st.markdown("---")
        st.markdown("### 🤖 Auto-Category Creation")
        
        # Show gap detection reason
        st.info(gap_detection.get("reason", "No suitable category found"))
        
        # Call the UI workflow
        gap_result = show_category_gap_detection_ui(
            hier_classification,
            user_prompt,
            CATEGORY_REGISTRY
        )
        
        # Handle result
        if gap_result.get("action_taken") == "new_category_applied":
            st.success(f"✅ New category '{gap_result['final_category']}' applied!")
            
            # Update material_data with new category
            new_category = st.session_state.get("new_category")
            if new_category:
                result = apply_new_category_and_verify(result, new_category)
                st.session_state['result'] = result
                st.rerun()
        
        elif gap_result.get("action_taken") == "existing_used":
            st.info(f"Using existing category: {gap_result['final_category']}")
            # Continue with existing category workflow
        
        elif gap_result.get("action_taken") == "cancelled":
            st.warning("Falling back to 'Other (Custom Material)' category")
            # Continue with fallback
        
        elif gap_result.get("action_taken") == "waiting_for_user":
            # Stop rendering - wait for user action
            st.stop()
"""

# ==============================================================================
# INTEGRATION POINT 4: SESSION STATE INITIALIZATION
# ==============================================================================

# Add this in the main section before the form (around line 1190):

"""
# Initialize session state variables for auto-category
if "enable_auto_category" not in st.session_state:
    st.session_state.enable_auto_category = False
if "new_category" not in st.session_state:
    st.session_state.new_category = None
if "show_auto_category_ui" not in st.session_state:
    st.session_state.show_auto_category_ui = False
"""

# ==============================================================================
# INTEGRATION POINT 5: ADD VERIFICATION CALL
# ==============================================================================

# Update existing run_three_stage_verification call (around line 1750):

"""
# Run three-stage verification WITH confidence score
verification_result = run_three_stage_verification(
    user_prompt,
    material_category,
    result,
    stored_confidence=hier_classification.get("confidence_score")  # Pass confidence
)
"""

# ==============================================================================
# TESTING CHECKLIST
# ==============================================================================

INTEGRATION_TEST_CASES = [
    {
        "name": "Test 1: Low Confidence Classification",
        "input": "A porous material with activated carbon and hygroscopic salt for moisture capture",
        "expected": "Should detect low confidence and propose new category",
        "enable_auto_category": True
    },
    {
        "name": "Test 2: Novel Material Request",
        "input": "Novel biocomposite for self-healing building coatings with strain monitoring",
        "expected": "Should detect 'novel material' keyword and propose new category",
        "enable_auto_category": True
    },
    {
        "name": "Test 3: Other Category Fallback",
        "input": "A complex nanostructured material for quantum computing applications",
        "expected": "Should classify as 'other_material' and propose new category if enabled",
        "enable_auto_category": True
    },
    {
        "name": "Test 4: Strong Match (No Proposal)",
        "input": "Atmospheric water harvesting material using activated carbon and hygroscopic salts",
        "expected": "Should have high confidence and NOT propose new category",
        "enable_auto_category": True
    },
    {
        "name": "Test 5: Duplicate Detection",
        "input": "Atmospheric moisture capture composite for water extraction",
        "expected": "Should detect similarity to AWH material and warn about duplicates",
        "enable_auto_category": True
    },
    {
        "name": "Test 6: Auto-Category Disabled",
        "input": "Novel custom material with unique properties",
        "expected": "Should NOT show auto-category UI even for low confidence",
        "enable_auto_category": False
    },
    {
        "name": "Test 7: Cleaning/Fabric Material",
        "input": "Fabric stain removal composite with enzyme activators and bleach-resistant additives",
        "expected": "Should propose new category and show safety warnings for bleach",
        "enable_auto_category": True
    },
    {
        "name": "Test 8: User Approve Workflow",
        "input": "Low-confidence custom material",
        "expected": "User clicks 'Approve' → category added → report regenerated",
        "enable_auto_category": True,
        "user_action": "approve"
    },
    {
        "name": "Test 9: User Edit Workflow",
        "input": "Low-confidence custom material",
        "expected": "User clicks 'Edit' → editing UI shown → can modify fields",
        "enable_auto_category": True,
        "user_action": "edit"
    },
    {
        "name": "Test 10: User Reject Workflow",
        "input": "Low-confidence custom material",
        "expected": "User clicks 'Reject' → falls back to 'Other' category",
        "enable_auto_category": True,
        "user_action": "reject"
    }
]
