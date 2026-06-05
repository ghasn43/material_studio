from auto_category_creation import check_duplicate_category, _string_similarity
from category_registry import CATEGORY_REGISTRY

proposed = {
    'display_name': 'Atmospheric Water Harvesting Material',
    'priority_keywords': ['atmospheric water', 'moisture capture', 'water harvesting'],
    'material_family': 'composite',
    'functional_class': 'adsorbent',
    'application_domain': 'awh'
}

# First check string similarity
existing_display = CATEGORY_REGISTRY.get("atmospheric_water_harvesting_material", {}).get("display_name", "").lower()
proposed_display = proposed['display_name'].lower()

sim = _string_similarity(proposed_display, existing_display)
print(f"Display name similarity: {sim}")
print(f"  Proposed: {proposed_display}")
print(f"  Existing: {existing_display}")

# Check keyword overlap
proposed_kw = set(w.lower() for w in proposed.get('priority_keywords', []))
existing_kw = set(w.lower() for w in CATEGORY_REGISTRY.get("atmospheric_water_harvesting_material", {}).get("priority_keywords", []))
overlap = proposed_kw & existing_kw
print(f"\nKeyword overlap: {len(overlap)} out of {len(proposed_kw)}")
print(f"  Proposed keywords: {proposed_kw}")
print(f"  Overlapping: {overlap}")

# Now run the duplicate detection
result = check_duplicate_category(proposed, CATEGORY_REGISTRY)
print(f"\nDuplicate found: {result['duplicate_found']}")
print(f"Similar categories: {len(result['similar_categories'])}")
if result['similar_categories']:
    for cat in result['similar_categories'][:3]:
        print(f"  - {cat.get('display_name')}: {cat.get('similarity_score')} ({cat.get('category_key')})")
