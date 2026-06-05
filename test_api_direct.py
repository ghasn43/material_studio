#!/usr/bin/env python
"""Diagnostic test to check API connectivity"""

import requests
import json

print("🔍 Checking API Connectivity...\n")

# Test 1: PubChem
print("1️⃣  PubChem (Water)...")
try:
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/water/cids/JSON"
    response = requests.get(url, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Connected - Found CIDs: {data.get('IdentifierList', {}).get('CID', [])[:3]}")
    else:
        print(f"   ❌ Error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Connection failed: {type(e).__name__}: {str(e)[:80]}")

# Test 2: OpenAlex
print("\n2️⃣  OpenAlex (photocatalysis)...")
try:
    url = "https://api.openalex.org/works?search=photocatalysis&limit=1"
    response = requests.get(url, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Connected - Found {data.get('meta', {}).get('count', 0)} results")
    else:
        print(f"   ❌ Error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Connection failed: {type(e).__name__}: {str(e)[:80]}")

# Test 3: Materials Project (free endpoint)
print("\n3️⃣  Materials Project (free API)...")
try:
    url = "https://www.materialsproject.org/rest/v2/api_check"
    response = requests.get(url, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Connection failed: {type(e).__name__}: {str(e)[:80]}")

# Test 4: Crossref (Literature)
print("\n4️⃣  Crossref (photocatalytic)...")
try:
    url = "https://api.crossref.org/works?query=photocatalytic&rows=1"
    response = requests.get(url, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        count = data.get('message', {}).get('total-results', 0)
        print(f"   ✅ Connected - Found {count} results")
    else:
        print(f"   ❌ Error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Connection failed: {type(e).__name__}: {str(e)[:80]}")

print("\n" + "="*60)
print("✅ Diagnostic Test Complete\n")
