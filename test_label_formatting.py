"""Test the protected label formatting."""

from category_registry import format_parameter_label

# Test cases
tests = [
    ('ph_working_range', 'pH Working Range'),
    ('k_na_selectivity', 'K+/Na+ Selectivity'),
    ('k_mg_selectivity', 'K+/Mg2+ Selectivity'),
    ('k_ca_selectivity', 'K+/Ca2+ Selectivity'),
    ('scaling_fouling_resistance', 'Scaling / Fouling Resistance'),
    ('leaching_safety_and_mechanical_stability', 'Leaching Safety & Mechanical Stability'),
    ('initial_potassium_concentration', 'Initial Potassium Concentration'),
    ('ph_dependence', 'pH Dependence'),
    ('potassium_uptake_capacity', 'Potassium Uptake Capacity'),  # Not protected, so title case
]

print("\n" + "="*80)
print("LABEL FORMATTING TEST")
print("="*80 + "\n")

passed = 0
for label, expected in tests:
    result = format_parameter_label(label)
    status = "✓" if result == expected else "✗"
    print(f"{status} {label}")
    print(f"   Expected: {expected}")
    print(f"   Got:      {result}")
    if result == expected:
        passed += 1
    print()

print(f"Result: {passed}/{len(tests)} tests passed\n")
