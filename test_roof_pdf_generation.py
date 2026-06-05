"""Test PDF generation with roof waterproofing processing method"""
import sys
import os

# Suppress Streamlit warnings when running in bare mode
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'

sys.path.insert(0, 'D:\\material_studio_1')

from category_registry import apply_category_preset
from fpdf import FPDF

def sanitize_for_pdf(text):
    """Sanitize text for FPDF compatibility"""
    if not text:
        return ""
    text = str(text)
    # Remove problematic unicode characters but keep common ones
    return text.encode('latin-1', errors='replace').decode('latin-1')

# Create test material data
test_result = {
    "user_request": "Design a roof-applied waterproof thermal insulation coating for concrete rooftops",
    "target_application": "Concrete rooftops with waterproofing and thermal insulation requirements",
    "composition": [
        {"component": "Titanium dioxide or aluminum oxide reflective filler", "ratio": 0.30},
        {"component": "Hydrophobic porous silica or treated perlite", "ratio": 0.25},
        {"component": "Acrylic or styrene-acrylic weather-resistant binder", "ratio": 0.20},
        {"component": "SBR or EVA elastomeric waterproofing additive", "ratio": 0.15},
        {"component": "UV stabilizer and silane water-repellent additive", "ratio": 0.10},
    ]
}

# Apply category preset (this adds processing_method to result)
test_result = apply_category_preset(test_result, "roof_waterproofing_thermal_insulation_coating")

print("Testing PDF generation with roof waterproofing processing method...")
print("=" * 80)

# Get processing method
processing_method = test_result.get("processing_method", [])
print(f"Processing method steps: {len(processing_method)}")

# Simulate PDF generation (simplified version from app.py)
try:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, txt="Roof Waterproofing & Thermal Insulation Coating", ln=True)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.ln(5)
    pdf.cell(0, 8, txt="Recommended Processing / Fabrication Method:", ln=True)
    pdf.ln(2)
    
    # Use small font for processing steps
    pdf.set_font("Helvetica", size=8)
    
    step_count = 0
    for step in processing_method:
        step_text = str(step).strip()
        if not step_text:
            pdf.ln(0.5)
            continue
        
        # Sanitize
        step_str = sanitize_for_pdf(step_text)
        
        # Check if main step header
        is_header = any(step_str.startswith(f"{j}.") for j in range(1, 9))
        
        try:
            if is_header:
                pdf.set_font("Helvetica", 'B', 8)
                pdf.multi_cell(0, 3, txt=step_str)
                step_count += 1
            else:
                pdf.set_font("Helvetica", size=8)
                if step_str.startswith("-"):
                    pdf.cell(0, 2, txt=f"  {step_str}", ln=True)
                else:
                    pdf.multi_cell(0, 2.5, txt=step_str)
        except Exception as e:
            print(f"[WARNING] PDF cell error: {e}")
            continue
    
    # Save PDF
    pdf_file = "test_roof_waterproofing_report.pdf"
    pdf.output(pdf_file)
    
    file_size = os.path.getsize(pdf_file)
    print()
    print(f"[SUCCESS] PDF generated successfully!")
    print(f"  File: {pdf_file}")
    print(f"  Size: {file_size} bytes")
    print(f"  Steps rendered: {step_count} main steps")
    print(f"  Total lines: {len(processing_method)} entries")
    
except Exception as e:
    print(f"[ERROR] PDF generation failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("[OK] Processing method PDF generation test complete")
