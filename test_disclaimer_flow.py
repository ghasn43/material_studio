#!/usr/bin/env python3
"""Corrected test for category-specific disclaimers in PDF."""

import sys
sys.path.insert(0, r'd:\material_studio_1')

from app import (
    enrich_with_preset,
    detect_material_category,
    generate_pdf,
    generate_fallback_result,
    MATERIAL_PRESETS
)

# Test: Photocatalytic Coating Analysis Flow
print("=" * 80)
print("TEST: Photocatalytic Coating Analysis (Full Flow)")
print("=" * 80)

photocatalytic_prompt = "Photocatalytic TiO2 coating for water purification using UV light"

# Simulate the app flow
print(f"\nStep 1: Detect category from prompt")
preset_key, display_name = detect_material_category(photocatalytic_prompt)
print(f"  Detected: {preset_key} ({display_name})")

print(f"\nStep 2: Generate fallback result")
fallback_result = generate_fallback_result(photocatalytic_prompt)
print(f"  Category in fallback: {fallback_result.get('material_category')}")
print(f"  Disclaimer in fallback: {fallback_result.get('category_disclaimer')[:100]}...")

print(f"\nStep 3: Enrich with preset")
enriched = enrich_with_preset(photocatalytic_prompt, fallback_result)
print(f"  Category in enriched: {enriched.get('material_category')}")
print(f"  Disclaimer in enriched: {enriched.get('category_disclaimer')[:100]}...")

print(f"\nStep 4: Check disclaimer is photocatalytic")
disclaimer = enriched.get('category_disclaimer', '')
if 'photocatalytic degradation efficiency' in disclaimer.lower():
    print("  ✅ Disclaimer mentions 'photocatalytic degradation efficiency'")
else:
    print("  ❌ WRONG: Disclaimer does NOT mention 'photocatalytic degradation efficiency'")
    print(f"     Disclaimer text: {disclaimer[:200]}...")

if 'water harvesting' in disclaimer.lower() or 'water-harvesting' in disclaimer.lower():
    print("  ❌ WRONG: Disclaimer mentions 'water harvesting' (should not)")
    print(f"     Disclaimer text: {disclaimer[:200]}...")
else:
    print("  ✅ Disclaimer does NOT mention 'water harvesting'")

print(f"\nStep 5: Generate PDF")
pdf_bytes = generate_pdf(photocatalytic_prompt, enriched)

# Extract PDF text
try:
    from PyPDF2 import PdfReader
    from io import BytesIO
    
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    
    print(f"  PDF size: {len(pdf_bytes)} bytes")
    print(f"  PDF contains {len(pdf_reader.pages)} page(s)")
    
    # Look for disclaimer in PDF
    if 'DISCLAIMER' in pdf_text:
        # Extract disclaimer section
        disclaimer_start = pdf_text.find('DISCLAIMER')
        disclaimer_end = pdf_text.find('.', disclaimer_start + 200) + 1
        pdf_disclaimer = pdf_text[disclaimer_start:disclaimer_end]
        print(f"\n  PDF Disclaimer:\n  {pdf_disclaimer}")
        
        if 'photocatalytic degradation efficiency' in pdf_disclaimer.lower():
            print("\n  ✅ PDF contains 'photocatalytic degradation efficiency'")
        else:
            print("\n  ❌ PDF does NOT contain 'photocatalytic degradation efficiency'")
            
        if 'water harvesting' in pdf_disclaimer.lower():
            print("  ❌ PDF contains 'water harvesting' (should not)")
        else:
            print("  ✅ PDF does NOT contain 'water harvesting'")
    else:
        print("  ❌ DISCLAIMER section not found in PDF!")
        
except Exception as e:
    print(f"  Error extracting PDF: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
