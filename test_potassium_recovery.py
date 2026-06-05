"""
Test script to verify potassium brine separation material category preset works correctly.
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
print("TEST: Potassium Brine Separation Material Category Preset")
print("=" * 80)

# Test 1: Keyword detection
print("\n[1] Testing keyword detection for potassium brine separation...\n")

test_prompts = [
    "Design a potassium salt recovery material from mineral-rich brine",
    "I need a K+ selective adsorbent for potash brine with crown ether functional groups",
    "Create a material for selective potassium capture from Dead Sea brine competing with sodium and magnesium",
    "Potassium recovery system for brine using functionalized porous silica",
    "Design an ion-exchange material for potassium recovery with magnesium competition",
]

for prompt in test_prompts:
    category_key, display_name = detect_material_category(prompt)
    print(f"  Prompt: {prompt}")
    print(f"  → Category: {category_key} ({display_name})")
    print()

# Test 2: Verify preset exists and contains all required fields
print("[2] Verifying preset structure...\n")

preset = MATERIAL_PRESETS.get("potassium_brine_separation_material", {})
if preset:
    print(f"  ✓ Preset found: {preset['display_name']}")
    print(f"  ✓ Keywords: {len(preset['keywords'])} keywords")
    print(f"  ✓ Parameters: {len(preset['parameters'])} category-specific parameters")
    print(f"  ✓ Validation plan: {len(preset['validation_plan'])} validation items")
    print(f"  ✓ Category disclaimer: {len(preset['category_disclaimer'])} characters")
    
    # Check for key parameters
    key_params = [
        "target_ion",
        "competing_ions",
        "brine_matrix",
        "initial_potassium_concentration",
        "selectivity_coefficients",
        "fouling_scaling_test"
    ]
    
    print("\n  Key parameters check:")
    for param in key_params:
        if param in preset['parameters']:
            print(f"    ✓ {param}: {preset['parameters'][param][:50]}...")
        else:
            print(f"    ✗ {param}: MISSING")
else:
    print("  ✗ Preset NOT found")

# Test 3: Fallback composition
print("\n[3] Testing fallback composition...\n")

comp = generate_fallback_composition("potassium_brine_separation_material")
if comp:
    print(f"  ✓ Generated {len(comp)} components:")
    total_ratio = 0
    for item in comp:
        ratio = float(item['ratio'])
        percent = ratio * 100
        total_ratio += ratio
        print(f"    • {item['component']}: {ratio:.2f} ({percent:.1f}%)")
    print(f"  ✓ Total ratio: {total_ratio:.2f} (should be 1.0)")
    
    # Check for specific required components
    components_text = " ".join([item['component'] for item in comp])
    required = ["Functionalized", "ion-exchange", "Zeolite", "polymer binder", "Graphene"]
    print("\n  Required components check:")
    for req in required:
        if req in components_text:
            print(f"    ✓ {req}")
        else:
            print(f"    ✗ {req}: MISSING")
else:
    print("  ✗ No composition generated")

# Test 4: Full fallback result
print("\n[4] Testing full fallback result generation...\n")

user_prompt = "Design a potassium recovery material from mineral-rich brine with selective K+/Na+ separation using functionalized silica and crown ether groups"
result = generate_fallback_result(user_prompt)

print(f"  Material Category: {result['material_category']}")
print(f"  Display Name: {result['material_category_display']}")
print(f"  Is Fallback: {result['is_fallback']}")
print(f"  Composition items: {len(result['composition'])}")
print(f"  Preset parameters: {len(result['preset_parameters'])} items")
print(f"  Preset validation: {len(result['preset_validation_plan'])} items")

# Verify disclaimer mentions potassium-specific language
disclaimer = result.get('category_disclaimer', '')
print("\n  Disclaimer check:")
if "potassium recovery" in disclaimer:
    print("    ✓ Mentions 'potassium recovery'")
else:
    print("    ✗ Missing 'potassium recovery'")
    
if "water harvesting" in disclaimer or "water-harvesting" in disclaimer or "phosphate" in disclaimer:
    print("    ✗ Contains other category language (should not)")
else:
    print("    ✓ No water harvesting or phosphate language")

if "ion selectivity" in disclaimer or "brine compatibility" in disclaimer:
    print("    ✓ Mentions selectivity/brine-specific language")
else:
    print("    ✗ Missing selectivity/brine-specific language")

if "mineral-processing experts" in disclaimer or "water-treatment specialists" in disclaimer:
    print("    ✓ Mentions appropriate specialists")
else:
    print("    ✗ Missing specialist consultation language")

# Test 5: PDF generation
print("\n[5] Testing PDF generation...\n")

try:
    pdf_bytes = generate_pdf(user_prompt, result)
    print(f"  ✓ PDF generated: {len(pdf_bytes)} bytes")
    
    # Extract text to verify disclaimer made it to PDF
    from PyPDF2 import PdfReader
    from io import BytesIO
    
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    if len(pdf_reader.pages) > 0:
        page_text = pdf_reader.pages[0].extract_text()
        
        print("\n  PDF content verification:")
        if "potassium" in page_text:
            print("    ✓ Contains 'potassium' reference")
        else:
            print("    ✗ Missing potassium reference")
            
        if "ion selectivity" in page_text or "brine" in page_text:
            print("    ✓ Contains selectivity/brine reference")
        else:
            print("    ✗ Missing selectivity/brine reference")
            
        if "water harvesting" in page_text or "water-harvesting" in page_text or "phosphate" in page_text:
            print("    ✗ Contains other category language (should not)")
        else:
            print("    ✓ No other category language in PDF")
            
        # Print first 200 characters of disclaimer section to verify
        if "DISCLAIMER" in page_text:
            start = page_text.find("DISCLAIMER")
            end = min(start + 200, len(page_text))
            print(f"\n  First 200 chars of disclaimer in PDF:")
            print(f"    {page_text[start:end]}...")
    else:
        print("  ✗ PDF has no pages")
        
except Exception as e:
    print(f"  ✗ PDF generation error: {e}")

# Test 6: Verify all validation items are present
print("\n[6] Verifying validation plan completeness...\n")

val_plan = preset.get('validation_plan', {})
print(f"  Validation items in plan:")
for i, (key, value) in enumerate(val_plan.items(), 1):
    desc = str(value)[:50] if isinstance(value, str) else str(value)[:50]
    print(f"    {i}. {key}: {desc}...")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
