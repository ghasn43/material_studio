#!/usr/bin/env python
"""Test the new working connectors"""

from scientific_data_connectors import (
    lookup_pubchem, 
    search_crossref,
    search_openalex,
    verify_with_free_datasets
)
import json

print("🧪 Testing NEW Working Connectors...\n")
print("=" * 60)

# Test 1: PubChem
print("\n1️⃣  Testing PubChem (water)...")
try:
    result = lookup_pubchem('water')
    print(f"   Found: {result.get('found')}")
    if result.get('found'):
        print(f"   ✅ CID: {result.get('pubchem_cid')}, Formula: {result.get('molecular_formula')}")
    else:
        print(f"   Status: {result.get('data_source')}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Crossref (known working)
print("\n2️⃣  Testing Crossref (photocatalytic)...")
try:
    result = search_crossref('photocatalytic', limit=3)
    print(f"   Found: {result.get('found')}")
    print(f"   ✅ Papers found: {result.get('papers_found', 0)}")
    if result.get('papers'):
        print(f"   First paper: {result['papers'][0].get('title', '')[:60]}...")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: OpenAlex
print("\n3️⃣  Testing OpenAlex (photocatalytic)...")
try:
    result = search_openalex('photocatalytic', limit=3)
    print(f"   Found: {result.get('found')}")
    print(f"   Papers found: {result.get('papers_found', 0)}")
    if result.get('papers'):
        print(f"   ✅ First paper: {result['papers'][0].get('title', '')[:60]}...")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Full Verification
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
    print(f"   Status: {result.get('verification_status')}")
    print(f"   ✅ Datasets: {len(result.get('datasets_queried', []))} databases")
    print(f"   Components verified: {len(result.get('components_verified', []))} of {result.get('components_checked', 0)}")
    print(f"   Literature hits: {result.get('literature_hits', 0)}")
    print(f"   Evidence: {result.get('evidence_summary', '')[:100]}...")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("✅ Test Complete!")
