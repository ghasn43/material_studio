#!/usr/bin/env python
"""Debug search_crossref with detailed error output"""

from scientific_data_connectors import _load_cache, _save_cache, _make_request
import json

def search_crossref_debug(query: str, limit: int = 5):
    """Search Crossref with detailed error output"""
    print(f"Searching for: {query}")
    
    cached = _load_cache("crossref", query)
    if cached:
        print("(Loaded from cache)")
        return cached
    
    try:
        url = f"https://api.crossref.org/works?query={query}&rows={limit}&order=desc&sort=relevance-score"
        print(f"URL: {url}")
        
        response = _make_request(url, timeout=12)
        print(f"Response type: {type(response)}")
        print(f"Response keys: {list(response.keys()) if response else 'None'}")
        
        if not response:
            print("Response is None/empty")
            result = {"found": False, "query": query, "data_source": "Crossref"}
            _save_cache("crossref", query, result)
            return result
        
        print(f"'message' in response: {'message' in response}")
        
        if "message" not in response:
            print("No 'message' key in response!")
            result = {"found": False, "query": query, "data_source": "Crossref"}
            _save_cache("crossref", query, result)
            return result
        
        items = response.get("message", {}).get("items", [])\n        print(f"Items found: {len(items)}")
        
        paper_list = []
        for idx, paper in enumerate(items[:limit]):
            print(f"  Processing paper {idx}...")
            print(f"    Has 'title': {'title' in paper}\")\n            print(f\"    Has 'published-online': {'published-online' in paper}\")\n            \n            title = paper.get(\"title\", [\"\"])[0][:100] if paper.get(\"title\") else \"\"\n            year = paper.get(\"published-online\", {}).get(\"date-parts\", [[0]])[0][0] if paper.get(\"published-online\") else 0\n            \n            paper_list.append({\n                \"title\": title,\n                \"year\": year,\n                \"doi\": paper.get(\"DOI\", \"\"),\n                \"url\": f\"https://doi.org/{paper.get('DOI', '')}\" if paper.get(\"DOI\") else \"\"\n            })\n        \n        result = {\n            \"found\": len(items) > 0,\n            \"query\": query,\n            \"papers_found\": len(items),\n            \"papers\": paper_list,\n            \"data_source\": \"Crossref\"\n        }\n        _save_cache(\"crossref\", query, result)\n        print(f\"Result: found={result['found']}, papers={len(paper_list)}\")\n        return result\n        \n    except Exception as e:\n        print(f\"EXCEPTION: {type(e).__name__}: {e}\")\n        import traceback\n        traceback.print_exc()\n        result = {\"found\": False, \"query\": query, \"data_source\": \"Crossref\"}\n        _save_cache(\"crossref\", query, result)\n        return result\n\nresult = search_crossref_debug('photocatalytic', limit=5)\nprint(f\"\\nFinal result: {json.dumps(result, indent=2)[:200]}\")\n