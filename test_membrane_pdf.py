"""
Test Membrane PDF Generation
=============================
Verifies that the user's anti-fouling membrane request generates
the correct PDF with membrane-specific parameters and disclaimer.
"""

import sys
import json
sys.path.insert(0, 'd:\\material_studio_1')

from app import detect_material_category, generate_fallback_result, generate_pdf, MATERIAL_PRESETS
from PyPDF2 import PdfReader
from io import BytesIO

# User's original request
user_request = """Design an anti-fouling membrane for water treatment using a polymer membrane matrix, 
hydrophilic additives, silica nanoparticles, activated carbon, and optional antimicrobial stabilizers. 
The membrane should reduce organic fouling, improve water flux, and maintain contaminant rejection under 
repeated filtration cycles. The design must be tested for permeability, rejection efficiency, fouling 
resistance, cleaning recovery, nanoparticle leaching, and mechanical durability."""

print("=" * 80)
print("MEMBRANE PDF GENERATION TEST")
print("=" * 80)
print()

# Test 1: Verify fallback result is for membrane
print("[TEST 1] Generate Fallback Result")
print("-" * 80)
result = generate_fallback_result(user_request)
is_membrane = result.get("material_category") == "membrane_water_treatment"
display_name = result.get("material_category_display", "")
print(f"Material Category: {result.get('material_category')}")
print(f"Display Name: {display_name}")
print(f"Is Membrane: {is_membrane}")
result_1 = is_membrane and "Membrane" in display_name
print(f"PASS" if result_1 else f"FAIL")
print()

# Test 2: Verify composition is correct (6 components)
print("[TEST 2] Verify Fallback Composition")
print("-" * 80)
composition = result.get("composition", [])
print(f"Component count: {len(composition)}")
if len(composition) > 0:
    total_ratio = sum(c.get("ratio", 0) for c in composition)
    print(f"Total ratio: {total_ratio:.4f}")
    for comp in composition:
        print(f"  - {comp['component']}: {comp['ratio']:.2f}")
    result_2 = len(composition) == 6 and abs(total_ratio - 1.0) < 0.001
    print(f"PASS - 6 components, ratios sum to 1.0" if result_2 else f"FAIL")
else:
    result_2 = False
    print("FAIL - No composition")
print()

# Test 3: Verify preset parameters are loaded (not heavy metal)
print("[TEST 3] Verify Preset Parameters")
print("-" * 80)
preset_params = result.get("preset_parameters", {})
print(f"Preset parameters count: {len(preset_params)}")
has_membrane_params = "membrane_type" in preset_params and "water_flux_target" in preset_params
has_no_metal_params = "target_ions" not in preset_params and "adsorbent_dosage" not in preset_params
print(f"Has membrane-specific parameters (membrane_type, water_flux_target): {has_membrane_params}")
print(f"Does NOT have heavy-metal parameters: {has_no_metal_params}")
if has_membrane_params:
    print(f"Sample params: membrane_type={preset_params.get('membrane_type')}")
    print(f"              water_flux_target={preset_params.get('water_flux_target')}")
result_3 = has_membrane_params and has_no_metal_params
print(f"PASS" if result_3 else f"FAIL")
print()

# Test 4: Verify preset validation plan is loaded (not heavy metal)
print("[TEST 4] Verify Validation Plan")
print("-" * 80)
preset_validation = result.get("preset_validation_plan", {})
print(f"Validation plan items: {len(preset_validation)}")
has_membrane_validation = "pure_water_permeability" in preset_validation and "fouling_resistance_test" in preset_validation
has_no_metal_validation = "heavy_metal_uptake_capacity" not in preset_validation
print(f"Has membrane-specific validation (permeability, fouling): {has_membrane_validation}")
print(f"Does NOT have heavy-metal validation: {has_no_metal_validation}")
result_4 = has_membrane_validation and has_no_metal_validation
print(f"PASS" if result_4 else f"FAIL")
print()

# Test 5: Verify category disclaimer is membrane-specific
print("[TEST 5] Verify Category Disclaimer")
print("-" * 80)
disclaimer = result.get("category_disclaimer", "")
membrane_terms = ["membrane", "permeability", "contaminant rejection", "anti-fouling", "cleaning recovery"]
heavy_metal_terms = ["heavy metal", "Pb", "Cd", "As", "Cr", "ion removal", "leaching safety"]

membrane_count = sum(1 for term in membrane_terms if term in disclaimer)
metal_count = sum(1 for term in heavy_metal_terms if term in disclaimer)

print(f"Disclaimer length: {len(disclaimer)} chars")
print(f"Contains membrane language: {membrane_count}/{len(membrane_terms)}")
print(f"Contains heavy-metal language: {metal_count}/{len(heavy_metal_terms)}")
print(f"  Membrane terms found: {[t for t in membrane_terms if t in disclaimer]}")
print(f"  Metal terms found: {[t for t in heavy_metal_terms if t in disclaimer]}")

result_5 = membrane_count >= 4 and metal_count == 0
print(f"PASS" if result_5 else f"FAIL")
print()

# Test 6: Generate PDF and verify content
print("[TEST 6] Generate PDF and Extract Content")
print("-" * 80)
extracted_text = ""
result_6 = False
try:
    pdf_output = generate_pdf(user_request, result)
    # pdf_output is a BytesIO object
    if isinstance(pdf_output, BytesIO):
        pdf_bytes = pdf_output.getvalue()
    else:
        pdf_bytes = pdf_output
    
    print(f"PDF generated: {len(pdf_bytes)} bytes")
    
    # Extract text from PDF
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()
    
    print(f"Extracted text length: {len(extracted_text)} chars")
    
    # Check for key membrane terms
    has_membrane_text = "anti-fouling" in extracted_text.lower() or "membrane" in extracted_text.lower()
    has_water_treatment = "water treatment" in extracted_text.lower() or "water" in extracted_text.lower()
    has_disclaimer = "DISCLAIMER" in extracted_text
    
    print(f"Contains 'membrane' or 'anti-fouling': {has_membrane_text}")
    print(f"Contains 'water treatment': {has_water_treatment}")
    print(f"Contains 'DISCLAIMER': {has_disclaimer}")
    
    # Check that heavy metal terms are NOT in PDF
    no_heavy_metals = "Pb2+" not in extracted_text and "Cd2+" not in extracted_text
    no_target_ions = "target ions" not in extracted_text.lower() or "Pb2+" not in extracted_text
    
    print(f"Does NOT contain 'Pb2+' or 'Cd2+': {no_heavy_metals}")
    print(f"Does NOT show heavy-metal target ions: {no_target_ions}")
    
    result_6 = has_membrane_text and has_disclaimer and no_heavy_metals and len(pdf_bytes) > 2000
    print(f"PASS - PDF generated with membrane content, no heavy metal references" if result_6 else f"FAIL")
except Exception as e:
    print(f"FAIL - PDF generation error: {e}")
    import traceback
    traceback.print_exc()
    result_6 = False

print()

# Test 7: Verify parameters in PDF
print("[TEST 7] Verify Parameters Appear in PDF")
print("-" * 80)
try:
    param_strings = ["water flux", "rejection", "fouling", "cleaning recovery", "permeability"]
    found_params = []
    for param in param_strings:
        if param in extracted_text.lower():
            found_params.append(param)
    
    print(f"Found {len(found_params)}/{len(param_strings)} expected parameters:")
    for p in found_params:
        print(f"  - {p}: YES")
    for p in param_strings:
        if p not in found_params:
            print(f"  - {p}: NO")
    
    result_7 = len(found_params) >= 3
    print(f"PASS" if result_7 else f"FAIL - Missing key parameters")
except Exception as e:
    print(f"FAIL - {e}")
    result_7 = False

print()
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
results = [result_1, result_2, result_3, result_4, result_5, result_6, result_7]
test_names = [
    "Fallback result is for membrane",
    "Composition (6 components, sum to 1.0)",
    "Preset parameters (membrane, not heavy metal)",
    "Validation plan (membrane, not heavy metal)",
    "Category disclaimer (membrane-specific)",
    "PDF generation with membrane content",
    "Parameters appear in PDF"
]

for i, (name, result) in enumerate(zip(test_names, results), 1):
    status = "PASS" if result else "FAIL"
    print(f"[{i}] {name}: {status}")

total_passed = sum(results)
total_tests = len(results)
print(f"\nTotal: {total_passed}/{total_tests} tests passed")
if total_passed == total_tests:
    print("\n=== ALL TESTS PASSED ===")
else:
    print(f"\n=== {total_tests - total_passed} TEST(S) FAILED ===")
    sys.exit(1)
