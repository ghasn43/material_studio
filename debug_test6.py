#!/usr/bin/env python
"""
Debug test to see what's happening in Test 6
"""

import sys
sys.path.insert(0, '/d/material_studio_1')

from category_registry import detect_category_conflicts

user_request = """Design a pre-treatment media for desalination systems using activated carbon, iron oxide, porous silica, 
and mineral stabilizers to reduce organic matter, suspended solids, and selected metal contaminants before membrane 
desalination. The material should improve membrane lifetime and reduce fouling risk. Testing is required for contaminant 
removal, pressure drop, media regeneration, microbial growth risk, leaching, and compatibility with seawater or brackish water."""

request_lower = user_request.lower()

print("=" * 100)
print("DEBUG TEST 6: Heavy Metal Adsorbent Category with Desalination Prompt")
print("=" * 100)

print(f"\nRequest keywords check:")
print(f"  Contains 'selected metal contaminants': {'selected metal contaminants' in request_lower}")
print(f"  Contains 'seawater': {'seawater' in request_lower}")
print(f"  Contains 'membrane desalination': {'membrane desalination' in request_lower}")

# Test thermal insulation keywords
thermal_keywords = [
    "thermal insulation", "insulation composite", "reduce heat transfer",
    "thermal conductivity", "compressive strength", "flexural strength",
    "flame response", "fire-safe", "fire-resistant", "fire safety",
    "indoor air safety", "aging stability", "building insulation",
    "lightweight insulation", "thermal stability", "temperature resistance",
    "building material", "heat transfer"
]

thermal_match = any(kw.lower() in request_lower for kw in thermal_keywords)
print(f"\n  Thermal insulation match: {thermal_match}")

# Test desalination keywords
desalination_keywords = [
    "desalination pre-treatment", "pre-treatment media", "pretreatment media",
    "before membrane desalination", "improve membrane lifetime", "reduce fouling risk",
    "pressure drop", "media regeneration", "microbial growth risk",
    "seawater compatibility", "brackish water compatibility",
    "suspended solids", "organic matter removal", "desalination pretreatment",
    "pre-treatment desalination", "ro pretreatment", "nf pretreatment",
    "membrane fouling reduction", "activated carbon", "iron oxide",
    "porous silica", "mineral stabilizers"
]

desalination_match = any(kw.lower() in request_lower for kw in desalination_keywords)
print(f"  Desalination pretreatment match: {desalination_match}")

matched_keywords = [kw for kw in desalination_keywords if kw.lower() in request_lower]
print(f"  Matched desalination keywords: {matched_keywords[:5]}...")

# Test heavy metal keywords
heavy_metal_keywords = [
    "lead", "cadmium", "arsenic", "chromium", "mercury",
    "heavy metal removal", "toxic metal", "metal adsorption",
    "pb2+", "cd2+", "as3+", "cr6+"
]

heavy_metal_match = any(kw.lower() in request_lower for kw in heavy_metal_keywords)
print(f"  Heavy metal focus match: {heavy_metal_match}")

print(f"\nCalling detect_category_conflicts with selected_category='adsorbent_heavy_metals':")
result = detect_category_conflicts(user_request, "adsorbent_heavy_metals")

print(f"\nResult:")
print(f"  Conflict detected: {result['conflict_detected']}")
print(f"  Blocked export: {result['blocked_export']}")
print(f"  Recommended category: {result['recommended_category']}")
print(f"  Conflict reason: {result['conflict_reason']}")
