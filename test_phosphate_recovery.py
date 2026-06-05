"""
Test script to verify phosphate recovery material category preset works correctly.
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
print("TEST: Phosphate Recovery Material Category Preset")
print("=" * 80)

# Test 1: Keyword detection
print("\n[1] Testing keyword detection for phosphate recovery...\n")

test_prompts = [
    "Design a phosphate recovery material for agricultural wastewater",
    "I need a nutrient recovery adsorbent for phosphate ions from wastewater",
    "Create a material for phosphorus recovery using iron oxide and calcium minerals",
    "Phosphate recovery system for industrial wastewater treatment",
    "Design an adsorbent for agricultural phosphate recovery",
]

for prompt in test_prompts:
    category_key, display_name = detect_material_category(prompt)
    print(f"  Prompt: {prompt}")
    print(f"  → Category: {category_key} ({display_name})")
    print()

# Test 2: Verify preset exists and contains all required fields
print("[2] Verifying preset structure...\n")

preset = MATERIAL_PRESETS.get("phosphate_recovery_material", {})
if preset:
    print(f"  ✓ Preset found: {preset['display_name']}")
    print(f"  ✓ Keywords: {len(preset['keywords'])} keywords")
    print(f"  ✓ Parameters: {len(preset['parameters'])} category-specific parameters")
    print(f"  ✓ Validation plan: {len(preset['validation_plan'])} validation items")
    print(f"  ✓ Category disclaimer: {len(preset['category_disclaimer'])} characters")
    
    # Check for key parameters
    key_params = [
        "target_phosphate_species",
        "ph_working_range",
        "contact_time",
        "competing_ions",
        "regeneration_method",
        "leaching_safety_test"
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

comp = generate_fallback_composition("phosphate_recovery_material")
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
    required = ["Calcium", "Iron oxide", "Activated carbon", "Bentonite", "Polymer"]
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

user_prompt = "Design a phosphate recovery adsorbent for agricultural wastewater using iron oxides and calcium minerals"
result = generate_fallback_result(user_prompt)

print(f"  Material Category: {result['material_category']}")
print(f"  Display Name: {result['material_category_display']}")
print(f"  Is Fallback: {result['is_fallback']}")
print(f"  Composition items: {len(result['composition'])}")
print(f"  Preset parameters: {len(result['preset_parameters'])} items")
print(f"  Preset validation: {len(result['preset_validation_plan'])} items")

# Verify disclaimer mentions phosphate-specific language
disclaimer = result.get('category_disclaimer', '')
print("\n  Disclaimer check:")
if "phosphate recovery" in disclaimer:
    print("    ✓ Mentions 'phosphate recovery'")
else:
    print("    ✗ Missing 'phosphate recovery'")
    
if "water harvesting" in disclaimer or "water-harvesting" in disclaimer:
    print("    ✗ Contains water harvesting language (should not)")
else:
    print("    ✓ No water harvesting language")

if "fertilizer" in disclaimer:
    print("    ✓ Mentions 'fertilizer'")
else:
    print("    ✗ Missing 'fertilizer'")

if "leaching analysis" in disclaimer:
    print("    ✓ Mentions 'leaching analysis'")
else:
    print("    ✗ Missing 'leaching analysis'")

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
        if "phosphate recovery" in page_text or "phosphate" in page_text:
            print("    ✓ Contains 'phosphate' reference")
        else:
            print("    ✗ Missing phosphate reference")
            
        if "fertilizer" in page_text:
            print("    ✓ Contains 'fertilizer' reference")
        else:
            print("    ✗ Missing fertilizer reference")
            
        if "water harvesting" in page_text or "water-harvesting" in page_text:
            print("    ✗ Contains water harvesting language (should not)")
        else:
            print("    ✓ No water harvesting language in PDF")
            
        # Print first 200 characters of disclaimer section to verify
        if "DISCLAIMER" in page_text:
            start = page_text.find("DISCLAIMER")
            end = start + 150
            print(f"\n  First 150 chars of disclaimer in PDF:")
            print(f"    {page_text[start:end]}...")
    else:
        print("  ✗ PDF has no pages")
        
except Exception as e:
    print(f"  ✗ PDF generation error: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
