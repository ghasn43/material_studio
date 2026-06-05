#!/usr/bin/env python
"""Direct test of Crossref API"""

import requests

print("Testing Crossref API directly...\n")

url = "https://api.crossref.org/works?query=photocatalytic&rows=1"
print(f"URL: {url}\n")

try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse keys: {list(data.keys())}")
        print(f"Message keys: {list(data.get('message', {}).keys())[:10]}")
        print(f"Total results: {data.get('message', {}).get('total-results', 0)}")
        items = data.get('message', {}).get('items', [])
        print(f"Items returned: {len(items)}")
        if items:
            print(f"First title: {items[0].get('title', [''])[0][:80]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
