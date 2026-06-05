#!/usr/bin/env python
"""Direct test of URLs with status codes"""

import requests

print("🔍 Testing Raw HTTP Status Codes...\n")

urls = [
    ("PubChem - property", "https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/water/property/MolecularFormula,MolecularWeight/JSON"),
    ("PubChem - cids", "https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/water/cids/json?limit=5"),
    ("OpenAlex - search", "https://api.openalex.org/works?search=photocatalysis&per_page=5"),
    ("Crossref - query", "https://api.crossref.org/works?query=photocatalytic&rows=1"),
    ("AFLOW - search", "https://www.aflowlib.org/API/aflux/v1.0/?catalog=icsd&formula=TiO2&format=json&limit=5"),
]

for name, url in urls:
    try:
        resp = requests.head(url, timeout=10)  # HEAD to avoid downloading full response
        print(f"{name:30} → Status {resp.status_code}")
    except requests.Timeout:
        print(f"{name:30} → TIMEOUT")
    except Exception as e:
        print(f"{name:30} → ERROR: {type(e).__name__}")

print("\n" + "="*60)
print("\nNow trying GET requests for working ones:\n")

working_urls = [
    ("Crossref", "https://api.crossref.org/works?query=photocatalytic&rows=1"),
    ("AFLOW", "https://www.aflowlib.org/API/aflux/v1.0/?catalog=icsd&formula=TiO2&format=json&limit=5"),
]

for name, url in working_urls:
    try:
        resp = requests.get(url, timeout=10)
        print(f"✅ {name:30} → Status {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json() if 'application/json' in resp.headers.get('content-type', '') else None
            if data:
                print(f"   Data keys: {list(data.keys())[:5]}")
    except Exception as e:
        print(f"❌ {name:30} → {type(e).__name__}")
