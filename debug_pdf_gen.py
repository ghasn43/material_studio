import sys
sys.path.insert(0, 'D:\\material_studio_1')

from category_registry import apply_category_preset
from app import generate_pdf

result = {
    'material_category': 'atmospheric_water_harvesting_material',
    'user_request': 'Test',
    'target_application': 'Test',
    'composition': [
        {'component': 'Component A', 'ratio': 0.5},
        {'component': 'Component B', 'ratio': 0.5}
    ]
}

apply_category_preset(result, 'atmospheric_water_harvesting_material')

three_stage_result = {
    'overall_status': 'pass',
    'stage_1_result': {'status': 'pass', 'keyword_match_percentage': 95, 'matched_keywords': []},
    'stage_2_result': {'status': 'pass', 'reason': 'OK'},
    'stage_3_result': {'status': 'pass', 'reason': 'OK'},
    'stage_4_result': {'status': 'pass', 'datasets_queried': [], 'components_checked': 0, 'components_verified': 0, 'materials_found': 0, 'literature_hits': 0, 'evidence_summary': 'OK'}
}

try:
    pdf_bytes = generate_pdf('Test', result, three_stage_result)
    print(f'Success: {len(pdf_bytes)} bytes')
except Exception as e:
    import traceback
    traceback.print_exc()
