from app import detect_material_category

test_prompts = [
    "Design a potassium salt recovery material from mineral-rich brine",
    "I need a K+ selective adsorbent for potash brine with crown ether functional groups",
    "Create a material for selective potassium capture from Dead Sea brine competing with sodium and magnesium",
    "Potassium recovery system for brine using functionalized porous silica",
    "Design an ion-exchange material for potassium recovery with magnesium competition",
]

print("\n" + "=" * 80)
print("VERIFICATION: Keyword Detection for Potassium Brine Separation")
print("=" * 80 + "\n")

for i, prompt in enumerate(test_prompts, 1):
    category_key, display_name = detect_material_category(prompt)
    status = "[OK]" if category_key == "potassium_brine_separation_material" else "[FAIL]"
    print(f"{status} [{i}] {prompt}")
    print(f"   -> {display_name}\n")

print("=" * 80)
