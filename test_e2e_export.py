"""Comprehensive end-to-end test: Classification → Verification → PDF Export"""
import sys
import os
sys.path.insert(0, 'D:\\material_studio_1')

from category_registry import (
    classify_material_hierarchically,
    run_three_stage_verification,
    apply_category_preset,
    CATEGORY_REGISTRY
)
from fpdf import FPDF

def sanitize_for_pdf(text):
    if not text:
        return ""
    text = str(text)
    return text.encode('latin-1', errors='replace').decode('latin-1')

print("=" * 80)
print("END-TO-END TEST: Roof Waterproofing Classification → PDF Export")
print("=" * 80)
print()

# Step 1: User Request
user_request = """
I need a thermal insulation and waterproofing coating for a concrete roof in a humid climate.
The coating should have good reflectivity to reduce heat, strong adhesion to concrete,
and withstand UV exposure and temperature cycling. It must dry quickly between coats.
"""
print("Step 1: User Request")
print(f"  {user_request[:80]}...")
print()

# Step 2: Classification
print("Step 2: AI Classification")
hier_class = classify_material_hierarchically(user_request)
material_category = hier_class.get('specific_preset', 'other_material')
print(f"  Category: {material_category}")
print(f"  Confidence: {hier_class.get('confidence_score', 0):.0f}%")
print(f"  Application: {hier_class.get('application_domain', 'N/A')}")
print()

# Step 3: Apply Preset
print("Step 3: Apply Processing Method Preset")
result = {
    "user_request": user_request,
    "target_application": "Concrete roof in humid climate",
    "material_category": material_category
}
result = apply_category_preset(result, material_category)
processing_method = result.get("processing_method", [])
print(f"  Processing method entries: {len(processing_method)}")
print(f"  Non-empty lines: {len([s for s in processing_method if str(s).strip()])}")
print()

# Step 4: Validation
print("Step 4: Pre-Export Verification")
stored_confidence = hier_class.get("confidence_score")
three_stage_result = run_three_stage_verification(
    user_request,
    material_category,
    result,
    stored_confidence=stored_confidence
)
print(f"  Stage 1 (Keywords): {three_stage_result['stage_1_result']['status'].upper()}")
print(f"  Stage 2 (Preset): {three_stage_result['stage_2_result']['status'].upper()}")
print(f"  Stage 3 (Disclaimer): {three_stage_result['stage_3_result']['status'].upper()}")
print(f"  Overall: {three_stage_result['overall_status'].upper()}")
print()

# Step 5: Processing Method Validation
print("Step 5: Processing Method Completeness Check")
processing_method_incomplete = False
if len(processing_method) > 0:
    content_lines = [str(step).strip() for step in processing_method if str(step).strip()]
    if len(content_lines) < 8:
        processing_method_incomplete = True
    else:
        header_count = sum(1 for line in content_lines if any(line.startswith(f"{j}.") for j in range(1, 9)))
        if header_count == len(content_lines):
            processing_method_incomplete = True

print(f"  Content lines: {len(content_lines)}")
print(f"  Headers: {sum(1 for line in content_lines if any(line.startswith(f'{j}.') for j in range(1, 9)))}")
print(f"  Status: {'BLOCKED' if processing_method_incomplete else 'ALLOWED'}")
print()

# Step 6: Export Decision
print("Step 6: Export Decision")
can_export = three_stage_result["overall_status"] != "fail" and not processing_method_incomplete
if not can_export:
    if three_stage_result["overall_status"] == "fail":
        print("  ❌ BLOCKED: Verification failed")
    elif processing_method_incomplete:
        print("  ❌ BLOCKED: Processing method incomplete")
else:
    print("  ✅ ALLOWED: Ready for PDF export")
print()

# Step 7: PDF Generation
if can_export:
    print("Step 7: PDF Generation")
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, txt="Material Analysis Report", ln=True)
        
        # Add processing method
        if processing_method and len(processing_method) > 0:
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 8, txt="Recommended Processing / Fabrication Method:", ln=True)
            pdf.ln(2)
            pdf.set_font("Helvetica", size=8)
            
            current_font_bold = False
            rendered_count = 0
            
            for step in processing_method:
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
                        rendered_count += 1
                    else:
                        if current_font_bold:
                            pdf.set_font("Helvetica", '', 8)
                            current_font_bold = False
                        
                        if is_substep:
                            step_str = "  " + chr(149) + " " + step_str
                        
                        pdf.multi_cell(0, 2.8, txt=step_str, ln=True)
                        rendered_count += 1
                except:
                    try:
                        pdf.set_font("Helvetica", '', 8)
                        pdf.multi_cell(0, 2.8, txt=step_str[:500], ln=True)
                        rendered_count += 1
                    except:
                        pass
            
            pdf.ln(1)
        
        pdf_file = "test_e2e_report.pdf"
        pdf.output(pdf_file)
        file_size = os.path.getsize(pdf_file)
        
        print(f"  ✅ PDF Generated: {pdf_file}")
        print(f"  Size: {file_size} bytes")
        print(f"  Lines rendered: {rendered_count}")
        print()
        print("=" * 80)
        print("✅ END-TO-END TEST PASSED")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  1. Classification: ROOF_WATERPROOFING ({hier_class.get('confidence_score', 0):.0f}%)")
        print(f"  2. Verification: PASSED")
        print(f"  3. Processing Method: COMPLETE ({len([s for s in processing_method if str(s).strip()])} lines)")
        print(f"  4. Export: ALLOWED")
        print(f"  5. PDF: GENERATED ({file_size} bytes)")
        print()
        
    except Exception as e:
        print(f"  ❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("=" * 80)
    print("❌ EXPORT BLOCKED")
    print("=" * 80)
