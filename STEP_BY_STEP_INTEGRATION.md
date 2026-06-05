"""
STEP-BY-STEP INTEGRATION GUIDE FOR APP.PY
==========================================

This document provides exact code snippets and line numbers for integrating
the auto-category creation system into app.py.

Follow each step in order.
"""

# ==============================================================================
# STEP 1: ADD IMPORTS (After line 20, with other imports)
# ==============================================================================

# Add these lines after existing imports:
"""
# Import auto-category creation and helper
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
from app_integration_helper import (
    init_auto_category_session,
    add_auto_category_sidebar_toggle,
    handle_auto_category_workflow,
    apply_auto_category_to_material,
    reset_auto_category_state
)
"""

# ==============================================================================
# STEP 2: INITIALIZE SESSION STATE (Around line 1180, in main section)
# ==============================================================================

# Find this section:
"""
# Existing code...
if "show_result" not in st.session_state:
    st.session_state.show_result = False
"""

# Add after it:
"""
# Initialize auto-category session state
init_auto_category_session()
"""

# ==============================================================================
# STEP 3: ADD SIDEBAR TOGGLE (In sidebar section, around line 1220)
# ==============================================================================

# Find this section:
"""
with st.sidebar:
    st.markdown("### 📋 Instructions")
    # ... instructions ...
    
    st.markdown("### 💡 Example Prompts")
    # ... example prompts ...
"""

# Add before the closing of with st.sidebar block:
"""
    # Add auto-category toggle
    enable_auto_category = add_auto_category_sidebar_toggle()
"""

# ==============================================================================
# STEP 4: CALL AUTO-CATEGORY WORKFLOW (After classification, around line 1350)
# ==============================================================================

# Find this section (after hier_classification is obtained):
"""
if "show_result" in st.session_state and st.session_state.get("show_result"):
    result = st.session_state['result']
    user_prompt = st.session_state['user_prompt']
    
    st.markdown("---")
"""

# Add this code after the above section and before "Show notice if this was generated from fallback":
"""
    # ===== AUTO-CATEGORY WORKFLOW (NEW) =====
    if enable_auto_category and hier_classification:
        # Run auto-category workflow
        auto_cat_result = handle_auto_category_workflow(
            user_prompt,
            hier_classification,
            CATEGORY_REGISTRY
        )
        
        # Handle workflow result
        if auto_cat_result["should_stop_rendering"]:
            # Stop and wait for user action
            st.stop()
        
        # Apply new category if approved
        if auto_cat_result.get("action") == "approve" and auto_cat_result.get("new_category"):
            new_cat = auto_cat_result["new_category"]
            st.info(f"✅ Applying new category: {new_cat.get('display_name')}")
            
            # Apply to material data
            result = apply_auto_category_to_material(result, new_cat, user_prompt)
            st.session_state['result'] = result
            
            # Update material category for rest of workflow
            material_category = new_cat.get("normalized_category_name", "other_material")
            
            st.success("New category applied! Regenerating report with new preset...")
            st.rerun()
        
        # Use fallback if rejected
        elif auto_cat_result.get("action") == "reject":
            material_category = "other_material"
            result["material_category"] = material_category
            st.session_state['result'] = result
    else:
        material_category = result.get("material_category", "other_material")
    # ===== END AUTO-CATEGORY WORKFLOW =====
"""

# ==============================================================================
# STEP 5: UPDATE VERIFICATION CALL (Around line 1750)
# ==============================================================================

# Find this section:
"""
# Run three-stage verification
verification_result = run_three_stage_verification(
    user_prompt,
    material_category,
    result
)
"""

# Replace with:
"""
# Run three-stage verification with confidence score
verification_result = run_three_stage_verification(
    user_prompt,
    material_category,
    result,
    stored_confidence=hier_classification.get("confidence_score") if hier_classification else None
)
"""

# ==============================================================================
# STEP 6: ADD RESET ON NEW ANALYSIS (Around line 1830)
# ==============================================================================

# Find this section:
"""
if st.button("🔄 Analyze Another Material", use_container_width=True):
    st.session_state['show_result'] = False
    st.session_state['result'] = None
    st.rerun()
"""

# Replace with:
"""
if st.button("🔄 Analyze Another Material", use_container_width=True):
    st.session_state['show_result'] = False
    st.session_state['result'] = None
    reset_auto_category_state()  # Reset auto-category state
    st.rerun()
"""

# ==============================================================================
# STEP 7: ADD RESET ON CLEAR ALL (Around line 1835)
# ==============================================================================

# Find this section:
"""
if st.button("📋 Clear All", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
"""

# Replace with:
"""
if st.button("📋 Clear All", use_container_width=True):
    reset_auto_category_state()  # Reset auto-category state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
"""

# ==============================================================================
# TESTING CHECKLIST
# ==============================================================================

TESTING_CHECKLIST = """
After integration, test the following scenarios:

□ Test 1: Toggle auto-category on/off in sidebar
  - Verify toggle appears and works
  - Verify feature disabled when toggle is OFF

□ Test 2: Strong category match
  - Request: "Atmospheric water harvesting material"
  - Expected: High confidence, NO auto-category UI

□ Test 3: Low confidence classification
  - Request: "A porous composite for moisture capture"
  - Expected: Auto-category UI shown, proposal generated

□ Test 4: Novel material
  - Request: "Novel custom material never tested before"
  - Expected: Auto-category UI shown with safety warnings

□ Test 5: Cleaning material with hazards
  - Request: "Fabric cleaning composite with caustic alkali and bleach"
  - Expected: Safety warnings shown in proposal

□ Test 6: Approve workflow
  - In auto-category UI: Click "Approve & Add"
  - Expected: Category applied, report regenerated

□ Test 7: Edit workflow
  - In auto-category UI: Click "Edit Before Adding"
  - Expected: Editing form shown, can edit fields

□ Test 8: Reject workflow
  - In auto-category UI: Click "Reject & Use Other"
  - Expected: Falls back to "Other (Custom Material)"

□ Test 9: Duplicate detection
  - Request: "Atmospheric water harvesting material"
  - If low confidence: Should show duplicate warnings

□ Test 10: Session state persistence
  - Generate proposal, toggle auto-category off/on
  - Expected: Session state preserved correctly

□ Test 11: Clear All button
  - Generate proposal, click "Clear All"
  - Expected: All state reset, form cleared

□ Test 12: Multiple analyses
  - Analyze different materials in sequence
  - Expected: Each analysis starts fresh
"""

# ==============================================================================
# DEBUGGING TIPS
# ==============================================================================

DEBUGGING_TIPS = """
If integration has issues:

1. Import errors:
   - Verify all files exist in same directory:
     - auto_category_creation.py
     - streamlit_auto_category_ui.py
     - app_integration_helper.py
     - category_registry.py
     - app.py

2. Session state issues:
   - Check that init_auto_category_session() is called before using state
   - Use st.session_state to inspect values:
     st.write(st.session_state.auto_category_proposal)

3. Workflow stops unexpectedly:
   - Check for st.stop() calls in auto-category workflow
   - Verify should_stop_rendering flag is checked

4. Categories not applied:
   - Check that apply_auto_category_to_material() is called
   - Verify result object is updated and saved to session_state

5. Safety warnings not showing:
   - Check _detect_safety_warnings() function
   - Add debug output to see warnings being generated

6. Testing help:
   - Use st.write() to debug session state
   - Use print() for debugging helper functions
   - Check browser console for JavaScript errors
"""

# ==============================================================================
# EXAMPLE COMPLETE WORKFLOW
# ==============================================================================

EXAMPLE_WORKFLOW = """
Complete workflow example after integration:

User Flow:
1. User enters: "Novel fabric cleaning material with biodegradable surfactants"
2. Clicks "Analyze"
3. App classifies material with low confidence (45%)
4. Auto-category workflow triggers:
   - Shows gap detection reason
   - Generates proposal for "Biodegradable Fabric Cleaner"
   - Checks for duplicates (none found)
   - Shows safety warnings for cleaning chemicals
   - Displays proposal details in expandable section

5. User sees four action buttons and chooses "Approve & Add"
6. Category is applied to material_data
7. Report regenerates with new category preset
8. User can then export PDF with the new category

Code Flow:
app.py:analyze_button → call_claude() → hier_classification
  ↓
handle_auto_category_workflow()
  ├→ detect_category_gap()
  ├→ propose_new_category()
  ├→ check_duplicate_category()
  └→ show_category_gap_detection_ui() [Streamlit UI shows]
    ↓
    User clicks button → apply_auto_category_to_material()
    ↓
    Report regenerated with new preset
"""

print(__doc__)
