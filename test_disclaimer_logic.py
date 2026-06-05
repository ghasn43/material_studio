#!/usr/bin/env python3
"""Test script to verify category-specific disclaimers in PDF."""

import sys
sys.path.insert(0, r'd:\material_studio_1')

from app import (
    enrich_with_preset,
    detect_material_category,
    generate_pdf,
    generate_fallback_result
)
from fpdf import FPDF
from io import BytesIO

# Test 1: Photocatalytic Coating
print("=" * 80)
print("TEST 1: Photocatalytic Coating Disclaimer")
print("=" * 80)

photocatalytic_prompt = "Photocatalytic TiO2 coating for water purification using UV light"
preset_key, display_name = detect_material_category(photocatalytic_prompt)
print(f"Detected category: {preset_key} ({display_name})")

fallback_result = generate_fallback_result(photocatalytic_prompt)
enriched = enrich_with_preset(photocatalytic_prompt, fallback_result)

print(f"\nCategory Disclaimer:")
disclaimer = enriched.get("category_disclaimer", "NOT FOUND")
print(disclaimer)

# Check if it mentions photocatalytic
if "photocatalytic degradation efficiency" in disclaimer.lower():
    print("\n✅ CORRECT: Disclaimer mentions 'photocatalytic degradation efficiency'")
else:
    print("\n❌ WRONG: Disclaimer does NOT mention 'photocatalytic degradation efficiency'")

if "water-harvesting" in disclaimer.lower() or "water harvesting" in disclaimer.lower():
    print("❌ WRONG: Disclaimer mentions 'water harvesting' (should not for photocatalytic)")
else:
    print("✅ CORRECT: Disclaimer does NOT mention 'water harvesting'")

# Test 2: Atmospheric Water Harvesting
print("\n" + "=" * 80)
print("TEST 2: Atmospheric Water Harvesting Disclaimer")
print("=" * 80)

awh_prompt = "Design a low-cost porous composite for atmospheric water harvesting"
preset_key, display_name = detect_material_category(awh_prompt)
print(f"Detected category: {preset_key} ({display_name})")

fallback_result = generate_fallback_result(awh_prompt)
enriched = enrich_with_preset(awh_prompt, fallback_result)

print(f"\nCategory Disclaimer:")
disclaimer = enriched.get("category_disclaimer", "NOT FOUND")
print(disclaimer)

# Check if it mentions water harvesting
if "water-harvesting" in disclaimer.lower() or "water harvesting" in disclaimer.lower():
    print("\n✅ CORRECT: Disclaimer mentions 'water-harvesting'")
else:
    print("\n❌ WRONG: Disclaimer does NOT mention 'water-harvesting'")

if "photocatalytic degradation" in disclaimer.lower():
    print("❌ WRONG: Disclaimer mentions 'photocatalytic degradation' (should not for AWH)")
else:
    print("✅ CORRECT: Disclaimer does NOT mention 'photocatalytic degradation'")

print("\n" + "=" * 80)
print("PDF Generation Test")
print("=" * 80)

# Test PDF generation with photocatalytic material
photocatalytic_result = {
    "material_category": "photocatalytic_coating",
    "material_category_display": "Photocatalytic Coating",
    "target_application": "water purification using UV light",
    "composition": [
        {"component": "Titanium dioxide (anatase)", "ratio": 0.85},
        {"component": "Silica binder", "ratio": 0.10},
        {"component": "Silver nanoparticles", "ratio": 0.05}
    ],
    "preset_parameters": {
        "substrate_type": "Glass, ceramic, or polymer",
        "coating_thickness": "0.5-5 micrometers"
    },
    "preset_validation_plan": {
        "pollutant_degradation_efficiency": ">80% degradation",
        "leaching_test": "ICP-MS analysis"
    },
    "category_disclaimer": enriched.get("category_disclaimer")
}

try:
    pdf_bytes = generate_pdf(photocatalytic_prompt, photocatalytic_result)
    
    # Write PDF to file for manual inspection
    with open(r'd:\material_studio_1\test_photocatalytic_report.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print("✅ PDF generated successfully")
    print(f"   Size: {len(pdf_bytes)} bytes")
    print(f"   Saved to: d:\\material_studio_1\\test_photocatalytic_report.pdf")
    
    # Try to extract text from PDF to verify disclaimer
    from PyPDF2 import PdfReader
    from io import BytesIO
    
    pdf_reader = PdfReader(BytesIO(pdf_bytes))
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    
    if "photocatalytic degradation efficiency" in pdf_text.lower():
        print("✅ PDF contains 'photocatalytic degradation efficiency'")
    else:
        print("❌ PDF does NOT contain 'photocatalytic degradation efficiency'")
        
    if "water harvesting" in pdf_text.lower():
        print("❌ PDF contains 'water harvesting' (should not)")
    else:
        print("✅ PDF does NOT contain 'water harvesting'")
        
except ImportError:
    print("Note: PyPDF2 not available for text extraction. PDF file created for manual inspection.")
except Exception as e:
    print(f"❌ Error generating PDF: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Tests Complete!")
print("=" * 80)
