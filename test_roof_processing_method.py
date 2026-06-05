from category_registry import get_category_preset
from app import generate_pdf, apply_category_preset

# Get the roof waterproofing preset
preset = get_category_preset("roof_waterproofing_thermal_insulation_coating")
processing_method = preset.get("processing_method", [])

print("Roof Waterproofing Processing Method:")
print("=" * 80)
print(f"Total steps: {len(processing_method)}")
print()

# Print each step
for step in processing_method:
    if step.strip():
        print(step)
    else:
        print()

print()
print("=" * 80)
print(f"[OK] Processing method has {len(processing_method)} entries")
print()

# Test PDF generation with roof waterproofing
print("Testing PDF generation...")
test_result = {
    "user_request": "Design a roof-applied waterproof thermal insulation coating",
    "target_application": "Concrete rooftops",
    "composition": [
        {"component": "Titanium dioxide reflective filler", "ratio": 0.30},
        {"component": "Porous silica", "ratio": 0.25},
        {"component": "Acrylic binder", "ratio": 0.45},
    ]
}

# Apply preset
test_result = apply_category_preset(test_result, "roof_waterproofing_thermal_insulation_coating")

# Generate PDF
try:
    pdf_bytes = generate_pdf(test_result, "Test Roof Waterproofing Report")
    print(f"[SUCCESS] PDF generated: {len(pdf_bytes)} bytes")
    
    # Save to file for verification
    with open("test_roof_waterproofing.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("[OK] PDF saved as test_roof_waterproofing.pdf")
except Exception as e:
    print(f"[ERROR] PDF generation failed: {e}")
    import traceback
    traceback.print_exc()
