#!/usr/bin/env python
"""Quick test to verify dataset connections are working"""

from scientific_data_connectors import (
    lookup_pubchem, 
    lookup_materials_project, 
    search_openalex,
    verify_with_free_datasets
)

print("🧪 Testing Dataset Connections...\n")
print("=" * 60)

# Test 1: PubChem
print("\n1️⃣  Testing PubChem API (query: 'water')...")
try:
    result = lookup_pubchem('water')
    print(f"   ✅ Connected: {result.get('found')}")
    if result.get('found'):
        print(f"   📊 Data: CID={result.get('pubchem_cid')}, Formula={result.get('molecular_formula')}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

# Test 2: Materials Project
print("\n2️⃣  Testing Materials Project API (query: 'TiO2')...")
try:
    result = lookup_materials_project('TiO2')
    print(f"   ✅ Connected: {result.get('found')}")
    if result.get('found'):
        print(f"   📊 Data: {result.get('materials_found', 0)} materials found")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

# Test 3: OpenAlex (Literature)
print("\n3️⃣  Testing OpenAlex API (query: 'photocatalysis')...")
try:
    result = search_openalex('photocatalysis', limit=3)
    print(f"   ✅ Connected: {result.get('found')}")
    if result.get('found'):
        print(f"   📊 Data: {result.get('papers_found', 0)} papers found")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

# Test 4: Full verification workflow
print("\n4️⃣  Testing Full Verification Workflow...")
try:
    test_material = {
        'name': 'TiO2 Photocatalytic Coating',
        'components': ['TiO2', 'SiO2', 'Binder'],
        'composition': [{'name': 'TiO2', 'percentage': 60}, 
                        {'name': 'SiO2', 'percentage': 30}, 
                        {'name': 'Binder', 'percentage': 10}]
    }
    result = verify_with_free_datasets(test_material, 'photocatalytic_coating')
    print(f"   ✅ Verification Status: {result.get('verification_status')}")
    print(f"   📊 Datasets Queried: {len(result.get('datasets_queried', []))} databases")
    print(f"   📊 Components Verified: {result.get('components_verified')}/{result.get('components_checked')}")
    print(f"   📚 Literature Hits: {result.get('literature_hits', 0)} papers")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("✅ Dataset Connection Test Complete!\n")
