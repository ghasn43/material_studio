"""
Test script to verify heavy metal adsorbent category preset works correctly.
"""

import sys
sys.path.insert(0, 'd:\\material_studio_1')

from app import (
    detect_material_category,
    generate_fallback_composition,
    generate_fallback_result,
    generate_pdf,
    MATERIAL_PRESETS,
    get_generic_disclaimer
)

print("=" * 80)
print("TEST: Heavy Metal Adsorbent Category Preset")
print("=" * 80)

# Test 1: Keyword detection
print("\n[1] Testing keyword detection for heavy metal adsorbents...\n")

test_prompts = [
    "Design a biochar-based adsorbent for lead and cadmium removal from wastewater",
    "Create a heavy metal adsorbent using modified biochar, porous silica, and iron oxide nanoparticles",
    "I need an adsorbent material for arsenic and chromium removal from contaminated water",
    "Heavy metal removal material for Pb, Cd, As wastewater treatment",
    "Design an iron oxide nanoparticle adsorbent for toxic metal ion removal from mine wastewater",
]

for prompt in test_prompts:
    category_key, display_name = detect_material_category(prompt)
    print(f"  Prompt: {prompt}")
    print(f"  -> Category: {category_key} ({display_name})")
    print()

# Test 2: Verify preset exists and contains all required fields
print("[2] Verifying preset structure...\n")

preset = MATERIAL_PRESETS.get("adsorbent_heavy_metals", {})
if preset:
    print(f"  [OK] Preset found: {preset['display_name']}")
    print(f"  [OK] Keywords: {len(preset['keywords'])} keywords")
    print(f"  [OK] Parameters: {len(preset['parameters'])} category-specific parameters")
    print(f"  [OK] Validation plan: {len(preset['validation_plan'])} validation items")
    print(f"  [OK] Category disclaimer: {len(preset['category_disclaimer'])} characters")
    
    # Check for key parameters
    key_params = [
        "target_ions",
        "initial_metal_concentration",
        "ph_working_range",
        "competing_ions",
        "removal_efficiency_target",
        "leaching_safety_test"
    ]
    
    print("\n  Key parameters check:")
    for param in key_params:
        if param in preset['parameters']:
            print(f"    [OK] {param}: {preset['parameters'][param][:40]}...")
        else:
            print(f"    [FAIL] {param}: MISSING")
else:
    print("  [FAIL] Preset NOT found")

# Test 3: Fallback composition
print("\n[3] Testing fallback composition...\n")

comp = generate_fallback_composition("adsorbent_heavy_metals")
if comp:
    print(f"  [OK] Generated {len(comp)} components:")
    total_ratio = 0
    for item in comp:
        ratio = float(item['ratio'])
        percent = ratio * 100
        total_ratio += ratio
        print(f"    * {item['component']}: {ratio:.2f} ({percent:.1f}%)")
    print(f"  [OK] Total ratio: {total_ratio:.2f} (should be 1.0)")
    
    # Check for specific required components
    components_text = " ".join([item['component'] for item in comp])
    required = ["Modified biochar", "Porous silica", "Iron oxide", "Bentonite", "Natural polymer"]
    print("\n  Required components check:")
    for req in required:
        if req in components_text:
            print(f"    [OK] {req}")
        else:
            print(f"    [FAIL] {req}: MISSING")
else:
    print("  [FAIL] No composition generated")

# Test 4: Full fallback result
print("\n[4] Testing full fallback result generation...\n")

user_prompt = "Design a heavy metal adsorbent for Pb, Cd, As removal from industrial wastewater using modified biochar and iron oxide nanoparticles"
result = generate_fallback_result(user_prompt)

print(f"  Material Category: {result['material_category']}")
print(f"  Display Name: {result['material_category_display']}")
print(f"  Is Fallback: {result['is_fallback']}")
print(f"  Composition items: {len(result['composition'])}")
print(f"  Preset parameters: {len(result['preset_parameters'])} items")
print(f"  Preset validation: {len(result['preset_validation_plan'])} items")

# Verify disclaimer mentions heavy-metal-specific language
disclaimer = result.get('category_disclaimer', '')
print("\n  Disclaimer check:")
if "heavy-metal" in disclaimer or "heavy metal" in disclaimer:
    print("    [OK] Mentions 'heavy metal'")
else:
    print("    [FAIL] Missing 'heavy metal'")
    
if "water harvesting" in disclaimer or "phosphate" in disclaimer or "potassium" in disclaimer:
    print("    [FAIL] Contains other category language (should not)")
else:
    print("    [OK] No other category language")

if "regeneration" in disclaimer and "leaching" in disclaimer:
    print("    [OK] Mentions regeneration and leaching")
else:
    print("    [FAIL] Missing regeneration or leaching language")

if "environmental" in disclaimer or "regulatory" in disclaimer:
    print("    [OK] Mentions environmental and regulatory concerns")
else:
    print("    [FAIL] Missing environmental/regulatory language")

# Test 5: PDF generation
print("\n[5] Testing PDF generation...\n")

try:
    pdf_bytes = generate_pdf(user_prompt, result)
    print(f"  [OK] PDF generated: {len(pdf_bytes)} bytes")
    
    # Extract text to verify disclaimer made it to PDF
    from PyPDF2 import PdfReader
    from io import BytesIO
    
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    if len(pdf_reader.pages) > 0:
        page_text = pdf_reader.pages[0].extract_text()
        
        print("\n  PDF content verification:")
        if "heavy metal" in page_text or "Pb" in page_text or "Cd" in page_text:
            print("    [OK] Contains metal references")
        else:
            print("    [FAIL] Missing metal references")
            
        if "wastewater" in page_text or "adsorption" in page_text:
            print("    [OK] Contains wastewater/adsorption references")
        else:
            print("    [FAIL] Missing wastewater/adsorption references")
            
        if "water harvesting" in page_text or "phosphate" in page_text or "potassium" in page_text:
            print("    [FAIL] Contains other category language (should not)")
        else:
            print("    [OK] No other category language in PDF")
            
        # Print first 150 characters of disclaimer section to verify
        if "DISCLAIMER" in page_text:
            start = page_text.find("DISCLAIMER")
            end = min(start + 150, len(page_text))
            print(f"\n  First 150 chars of disclaimer in PDF:")
            print(f"    {page_text[start:end]}...")
    else:
        print("  [FAIL] PDF has no pages")
        
except Exception as e:
    print(f"  [FAIL] PDF generation error: {e}")

# Test 6: Verify all validation items are present
print("\n[6] Verifying validation plan completeness...\n")

val_plan = preset.get('validation_plan', {})
print(f"  Validation items in plan:")
for i, (key, value) in enumerate(val_plan.items(), 1):
    desc = str(value)[:45] if isinstance(value, str) else str(value)[:45]
    print(f"    {i}. {key}: {desc}...")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
