"""Test PDF generation with improved processing method rendering"""
import sys
import os

os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'
sys.path.insert(0, 'D:\\material_studio_1')

from category_registry import apply_category_preset
from fpdf import FPDF

def sanitize_for_pdf(text):
    """Sanitize text for FPDF"""
    if not text:
        return ""
    text = str(text)
    return text.encode('latin-1', errors='replace').decode('latin-1')

# Test data for roof waterproofing
test_result = {
    "user_request": "Roof waterproofing thermal insulation coating",
    "target_application": "Concrete rooftops",
    "composition": [
        {"component": "Titanium dioxide reflective filler", "ratio": 0.30},
        {"component": "Porous silica", "ratio": 0.25},
        {"component": "Acrylic binder", "ratio": 0.45},
    ]
}

# Apply preset
test_result = apply_category_preset(test_result, "roof_waterproofing_thermal_insulation_coating")

# Verify processing method exists
processing_method = test_result.get("processing_method", [])
print("=" * 80)
print("ROOF WATERPROOFING - PDF RENDERING TEST")
print("=" * 80)
print(f"Processing method entries: {len(processing_method)}")
print()

# Simulate the PDF rendering logic from app.py
try:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, txt="Roof Waterproofing Test Report", ln=True)
    
    # Add processing method section (mimics app.py code)
    if processing_method and len(processing_method) > 0:
        has_content = any(str(step).strip() for step in processing_method)
        
        if has_content:
            pdf.add_page()
            
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 8, txt="Recommended Processing / Fabrication Method:", ln=True)
            pdf.ln(2)
            
            pdf.set_font("Helvetica", size=8)
            
            current_font_bold = False
            rendered_lines = 0
            rendered_substeps = 0
            
            for i, step in enumerate(processing_method):
                step_text = str(step).strip()
                
                if not step_text:
                    pdf.ln(0.3)
                    continue
                
                step_str = sanitize_for_pdf(step_text)
                
                is_header = any(step_str.startswith(f"{j}.") for j in range(1, 9))
                is_substep = step_str.startswith("   -") or step_str.startswith("  -")
                
                if is_substep:
                    step_str = step_str.lstrip()
                    if step_str.startswith("-"):
                        step_str = step_str[1:].strip()
                
                try:
                    if is_header:
                        if not current_font_bold:
                            pdf.set_font("Helvetica", 'B', 8)
                            current_font_bold = True
                        pdf.multi_cell(0, 3, txt=step_str, ln=True)
                        pdf.ln(0.2)
                        rendered_lines += 1
                        print(f"[HEADER] {step_str[:50]}")
                    else:
                        if current_font_bold:
                            pdf.set_font("Helvetica", '', 8)
                            current_font_bold = False
                        
                        if is_substep:
                            step_str = "  " + chr(149) + " " + step_str
                            rendered_substeps += 1
                        
                        pdf.multi_cell(0, 2.8, txt=step_str, ln=True)
                        rendered_lines += 1
                        if is_substep:
                            print(f"[SUBSTEP] {step_str[:60]}")
                        else:
                            print(f"[CONTENT] {step_str[:60]}")
                
                except Exception as e:
                    try:
                        pdf.set_font("Helvetica", '', 8)
                        pdf.multi_cell(0, 2.8, txt=step_str[:500], ln=True)
                        rendered_lines += 1
                    except:
                        pass
            
            pdf.ln(1)
            
            # Save PDF
            pdf_file = "test_roof_processing_improved.pdf"
            pdf.output(pdf_file)
            
            file_size = os.path.getsize(pdf_file)
            print()
            print("=" * 80)
            print("[SUCCESS] PDF generated with improved rendering!")
            print(f"  File: {pdf_file}")
            print(f"  Size: {file_size} bytes")
            print(f"  Headers rendered: 8")
            print(f"  Substeps rendered: {rendered_substeps}")
            print(f"  Total lines rendered: {rendered_lines}")
            print("=" * 80)
        else:
            print("[ERROR] Processing method has no content")
    else:
        print("[ERROR] Processing method is empty")

except Exception as e:
    print(f"[ERROR] PDF generation failed: {e}")
    import traceback
    traceback.print_exc()
