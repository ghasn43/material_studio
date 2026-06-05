"""Debug classification issue"""
import sys
sys.path.insert(0, 'D:\\material_studio_1')

from category_registry import classify_material_hierarchically

user_request = """
I need a thermal insulation and waterproofing coating for a concrete roof in a humid climate.
The coating should have good reflectivity to reduce heat, strong adhesion to concrete,
and withstand UV exposure and temperature cycling. It must dry quickly between coats.
"""

result = classify_material_hierarchically(user_request)

print("Classification Result:")
print(f"  material_category: {result.get('material_category')}")
print(f"  confidence_score: {result.get('confidence_score')}")
print(f"  key_phrases_matched: {result.get('key_phrases_matched')}")
print(f"  all keys: {list(result.keys())}")
