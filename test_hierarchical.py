from category_registry import classify_material_hierarchically

test_prompts = [
    'potassium recovery from brine with K+ selectivity',
    'photocatalytic TiO2 coating for water purification',
    'membrane filtration for wastewater treatment',
    'atmospheric water harvesting device',
    'heavy metal adsorbent for lead and cadmium removal'
]

for prompt in test_prompts:
    result = classify_material_hierarchically(prompt)
    print(f"\n📝 Prompt: {prompt}")
    print(f"✅ Preset: {result.get('specific_preset')}")
    print(f"   Confidence: {result.get('confidence_score')}%")
    print(f"   Family: {result.get('material_family')}")
    print(f"   Functional: {result.get('functional_class')}")
    print(f"   Domain: {result.get('application_domain')}")
    if result.get('requires_user_confirmation'):
        print(f"   ⚠️  Requires confirmation")
