from category_registry import classify_material_hierarchically, run_three_stage_verification, apply_category_preset

prompt = 'roof-applied waterproof thermal insulation coating for concrete rooftop with water leakage prevention'

# Classification
cls_result = classify_material_hierarchically(prompt)
cat = cls_result.get('specific_preset')
conf = cls_result.get('confidence_score')

print(f'Category: {cat}')
print(f'Confidence: {conf}')

# Verification with stored confidence
data = {'material_category': cat, 'composition': [{'component': 'A', 'ratio': 1.0}]}
apply_category_preset(data, cat)

v_result = run_three_stage_verification(prompt, cat, data, stored_confidence=conf)
print(f'Verification Status: {v_result.get("overall_status")}')
print(f'Export Blocked: {v_result.get("blocked_export")}')

if cat == 'roof_waterproofing_thermal_insulation_coating' and v_result.get('overall_status') == 'pass':
    print('[SUCCESS] Fix is working!')
else:
    print('[ERROR] Fix needs more work')
