#!/usr/bin/env python
"""Debug _make_request function"""

from scientific_data_connectors import _make_request
import json

print("Testing _make_request function...\n")

url = "https://api.crossref.org/works?query=photocatalytic&rows=1"
print(f"URL: {url}\n")

result = _make_request(url, timeout=12)
print(f"Result type: {type(result)}")
print(f"Result: {json.dumps(result, indent=2)[:500] if result else 'None'}")
