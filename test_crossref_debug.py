#!/usr/bin/env python
"""Debug search_crossref"""

from scientific_data_connectors import search_crossref, _make_request
import json

print("Debugging search_crossref...\n")

# Test _make_request directly
print("1️⃣  Testing _make_request directly...")
url = "https://api.crossref.org/works?query=photocatalytic&rows=5"
result = _make_request(url, timeout=12)
print(f"   Status: {result.get('status') if result else 'None'}")
if result:
    message = result.get('message', {})
    items = message.get('items', [])
    print(f"   Items count: {len(items)}")
    if items:
        print(f"   First title: {items[0].get('title', [''])[0][:60]}")

# Test search_crossref
print("\n2️⃣  Testing search_crossref...")
result = search_crossref('photocatalytic', limit=5)
print(f"   Found: {result.get('found')}")
print(f"   Papers found: {result.get('papers_found')}")
print(f"   Result: {json.dumps(result, indent=2)[:300]}")
