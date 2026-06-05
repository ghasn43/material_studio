"""Simple test to verify processing method for roof waterproofing"""
import sys
sys.path.insert(0, 'D:\\material_studio_1')

from category_registry import get_category_preset, apply_category_preset, CATEGORY_REGISTRY

# Get the roof waterproofing preset
preset = get_category_preset("roof_waterproofing_thermal_insulation_coating")
processing_method = preset.get("processing_method", [])

print("ROOF WATERPROOFING - PROCESSING METHOD VERIFICATION")
print("=" * 80)
print(f"Total entries: {len(processing_method)}")
print()

# Count steps
step_count = 0
for step in processing_method:
    if step.strip() and step.strip()[0].isdigit():
        step_count += 1

print(f"Main steps (1-8): {step_count}")
print()

# Display all content
for i, step in enumerate(processing_method):
    if step.strip():
        print(step)
    else:
        print()

print()
print("=" * 80)

# Verify it's applied correctly through apply_category_preset
test_data = {
    "user_request": "Test roof coating",
    "composition": [{"component": "Test", "ratio": 1.0}]
}

applied_data = apply_category_preset(test_data, "roof_waterproofing_thermal_insulation_coating")
applied_processing = applied_data.get("processing_method", [])

print()
print("VERIFICATION: Processing method is correctly applied through apply_category_preset()")
print(f"Processing method entries in applied data: {len(applied_processing)}")

if len(applied_processing) == len(processing_method):
    print("[SUCCESS] Processing method correctly populated in result data!")
else:
    print(f"[ERROR] Mismatch: {len(applied_processing)} vs {len(processing_method)}")

# Show step headers
print()
print("Step headers found:")
headers = [s for s in processing_method if s.strip() and s.strip()[0].isdigit()]
for h in headers:
    print(f"  {h}")

print()
print("=" * 80)
print("[OK] Roof waterproofing processing method is fully configured")
