#!/usr/bin/env python
"""Find working PubChem endpoints"""

import requests
import json

print("🔍 Testing PubChem Endpoints...\n")

# Try different PubChem endpoint formats
pubchem_urls = [
    "https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/water/JSON",  # Simple full record
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/water/JSON",  # Alternative format
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/176/JSON",  # Direct CID (water = 176)
    "https://api.pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/water/JSON",  # Alternative host
]

for url in pubchem_urls:
    try:
        resp = requests.get(url, timeout=10)
        print(f"Status {resp.status_code}: {url.split('/')[-2]}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✅ SUCCESS - Keys: {list(data.keys())[:5]}")
            # Try to extract formula
            if "PC_Compounds" in data:
                print(f"  Found PC_Compounds data")
            if "Record" in data:
                print(f"  Found Record data")
    except Exception as e:
        print(f"Status XXX: {type(e).__name__}: {url.split('/')[-2]}")

print("\n" + "="*60)
print("\n🔍 Testing Alternative Material Databases...\n")

alternatives = [
    ("OQMD", "https://oqmd.org/api/v1/materials/?composition=TiO2&limit=5"),
    ("COD", "https://www.crystallography.net/cod/search/formula/TiO2/limit:5/jsonapi"),
    ("Wikidata", "https://www.wikidata.org/w/api.php?action=query&titles=titanium_dioxide&format=json"),
]

for name, url in alternatives:
    try:
        resp = requests.get(url, timeout=10)
        print(f"{name:15} → Status {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   Keys: {list(data.keys())[:3]}")
    except Exception as e:
        print(f"{name:15} → ERROR: {type(e).__name__}")
