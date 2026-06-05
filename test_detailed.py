#!/usr/bin/env python
"""Detailed test to debug connector issues"""

from scientific_data_connectors import (
    _make_request,
    lookup_pubchem
)
import json

print("🔍 Detailed Connector Debugging...\n")

# Test 1: PubChem - test the endpoint directly
print("1️⃣  Testing PubChem endpoint...")
url1 = "https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/water/property/MolecularFormula,MolecularWeight/JSON"
print(f"   URL: {url1}")
resp = _make_request(url1, timeout=15)
print(f"   Response: {json.dumps(resp, indent=2)[:500] if resp else 'None'}")

# Test 2: Try CID endpoint for water
print("\n2️⃣  Testing PubChem CID endpoint...")
url2 = "https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/water/cids/json?limit=5"
print(f"   URL: {url2}")
resp = _make_request(url2, timeout=15)
print(f"   Response: {json.dumps(resp, indent=2)[:500] if resp else 'None'}")

# Test 3: Crossref (known working)
print("\n3️⃣  Testing Crossref (baseline - should work)...")
url3 = "https://api.crossref.org/works?query=photocatalytic&rows=1"
print(f"   URL: {url3}")
resp = _make_request(url3, timeout=15)
if resp and 'message' in resp:
    print(f"   ✅ Response received - {resp['message']['total-results']} results found")
else:
    print(f"   Response: {json.dumps(resp, indent=2)[:200] if resp else 'None'}")

# Test 4: Direct lookup test
print("\n4️⃣  Testing lookup_pubchem('water')...")
try:
    result = lookup_pubchem('water')
    print(f"   Result: {json.dumps(result, indent=2)[:300]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
