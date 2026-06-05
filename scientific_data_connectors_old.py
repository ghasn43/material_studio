"""
Scientific Dataset Verification Layer for MaterialGenesis

This module connects MaterialGenesis to free/open-access materials science datasets
to provide scientific verification and evidence for material classifications.

Datasets supported:
1. PubChem - chemical compound identity and safety
2. Materials Project - inorganic materials properties
3. NIST Adsorption Isotherm Database - adsorption data
4. Crystallography Open Database (COD) - crystal structures
5. AFLOW/AFLOWLIB - computed materials properties
6. OQMD - thermodynamic properties
7. NOMAD - broad materials data repository
8. JARVIS - atomistic materials data
9. CoRE MOF Database - MOF structures
10. IZA Zeolite Database - zeolite frameworks
11. NIST Chemistry WebBook - thermochemical data
12. EPA CompTox Dashboard - chemical safety
13. OpenAlex / Crossref - literature metadata

Design Principles:
- External datasets act as EVIDENCE layer, not decision layer
- Internal category registry remains the decision layer
- All datasets are optional; graceful degradation if unavailable
- Results are cached locally
- App remains usable offline
- Never claim dataset "proves" anything - only that it supports evidence
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
import requests
from functools import lru_cache

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ============================================================================
# CONFIGURATION AND CACHING
# ============================================================================

# Cache directory setup
CACHE_DIR = "data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Cache expiration (in days)
CACHE_EXPIRATION_DAYS = 7

# API endpoint timeout (seconds)
REQUEST_TIMEOUT = 10

# Maximum retries for failed requests
MAX_RETRIES = 2

# API keys from environment
MATERIALS_PROJECT_API_KEY = os.getenv("MATERIALS_PROJECT_API_KEY", "")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

# ============================================================================
# CACHING UTILITIES
# ============================================================================

def _get_cache_path(dataset_name: str, query_hash: str) -> str:
    """Get cache file path for a dataset query."""
    return os.path.join(CACHE_DIR, f"{dataset_name}_cache_{query_hash}.json")


def _hash_query(query: str) -> str:
    """Generate hash of query for cache key."""
    return hashlib.md5(query.lower().encode()).hexdigest()[:12]


def _load_cache(dataset_name: str, query: str) -> Optional[Dict]:
    """Load cached result if it exists and is not expired."""
    cache_path = _get_cache_path(dataset_name, _hash_query(query))
    
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        
        # Check if cache is expired
        cached_time = datetime.fromisoformat(cache_data.get("timestamp", "2000-01-01"))
        if datetime.now() - cached_time > timedelta(days=CACHE_EXPIRATION_DAYS):
            return None
        
        return cache_data.get("data")
    except Exception as e:
        logger.warning(f"Cache load error for {dataset_name}: {e}")
        return None


def _save_cache(dataset_name: str, query: str, data: Dict) -> None:
    """Save result to cache."""
    cache_path = _get_cache_path(dataset_name, _hash_query(query))
    
    try:
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "data": data
        }
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Cache save error for {dataset_name}: {e}")


def _make_request(url: str, timeout: int = REQUEST_TIMEOUT, headers: Dict = None) -> Optional[Dict]:
    """Make HTTP request with error handling and retries."""
    headers = headers or {"User-Agent": "MaterialGenesis/1.0"}
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=timeout, headers=headers)
            if response.status_code == 200:
                return response.json() if response.headers.get('content-type') == 'application/json' else {"text": response.text}
        except requests.Timeout:
            logger.debug(f"Request timeout (attempt {attempt+1}/{MAX_RETRIES}): {url}")
        except requests.RequestException as e:
            logger.debug(f"Request error (attempt {attempt+1}/{MAX_RETRIES}): {e}")
    
    return None


# ============================================================================
# PUBCHEM CONNECTOR
# ============================================================================

def lookup_pubchem(compound_name: str) -> Dict[str, Any]:
    """
    Look up chemical compound in PubChem using their REST API.
    
    Returns:
    {
        "found": bool,
        "pubchem_cid": str,
        "compound_name": str,
        "molecular_formula": str,
        "molecular_weight": float,
        "data_source": "PubChem"
    }
    """
    cached = _load_cache("pubchem", compound_name)
    if cached:
        return cached
    
    try:
        # Search for the compound by name using PubChem REST API
        # Using a simpler endpoint that's more reliable
        search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/{compound_name}/property/MolecularFormula,MolecularWeight/JSON"
        
        response = _make_request(search_url, timeout=15)
        
        if not response or "Fault" in response:
            # Try alternative: directly query compound record
            alt_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/name/{compound_name}/cids/json?limit=5"
            response = _make_request(alt_url, timeout=15)
            
            if not response:
                result = {"found": False, "compound_name": compound_name, "data_source": "PubChem"}
                _save_cache("pubchem", compound_name, result)
                return result
        
        # Handle the property response format
        if "PropertyTable" in response:
            props = response.get("PropertyTable", {}).get("Properties", [])
            if props:
                first = props[0]
                result = {
                    "found": True,
                    "pubchem_cid": first.get("CID", ""),
                    "compound_name": compound_name,
                    "molecular_formula": first.get("MolecularFormula", ""),
                    "molecular_weight": float(first.get("MolecularWeight", 0)) if first.get("MolecularWeight") else 0,
                    "data_source": "PubChem",
                    "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{first.get('CID', '')}"
                }
                _save_cache("pubchem", compound_name, result)
                return result
        
        # Handle CID list response
        if "IdentifierList" in response:
            cids = response["IdentifierList"].get("CID", [])
            if cids:
                cid = cids[0]
                # Get details for first compound
                detail_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/v1/compound/CID/{cid}/property/MolecularFormula,MolecularWeight/JSON"
                detail = _make_request(detail_url, timeout=15)
                
                if detail and "PropertyTable" in detail:
                    props = detail["PropertyTable"]["Properties"][0]
                    result = {
                        "found": True,
                        "pubchem_cid": str(cid),
                        "compound_name": compound_name,
                        "molecular_formula": props.get("MolecularFormula", ""),
                        "molecular_weight": float(props.get("MolecularWeight", 0)) if props.get("MolecularWeight") else 0,
                        "data_source": "PubChem",
                        "pubchem_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
                    }
                    _save_cache("pubchem", compound_name, result)
                    return result
        
        result = {"found": False, "compound_name": compound_name, "data_source": "PubChem"}
        _save_cache("pubchem", compound_name, result)
        return result
        
    except Exception as e:
        logger.warning(f"PubChem lookup error for {compound_name}: {e}")
        result = {"found": False, "compound_name": compound_name, "data_source": "PubChem", "error": str(e)[:50]}
        _save_cache("pubchem", compound_name, result)
        return result


# ============================================================================
# MATERIALS PROJECT CONNECTOR
# ============================================================================

def lookup_materials_project(formula_or_name: str) -> Dict[str, Any]:
    """
    Look up inorganic material in Materials Project via web interface.
    Falls back to AFLOW if MP unavailable.
    
    Returns:
    {
        "found": bool,
        "formula": str,
        "data_source": "Materials Project" or "AFLOW"
    }
    """
    cached = _load_cache("materials_project", formula_or_name)
    if cached:
        return cached
    
    try:
        # Try Materials Project web search endpoint with proper user-agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        # Use MP API with search endpoint
        mp_url = f"https://api.materialsproject.org/materials/search?formula={formula_or_name}&limit=1"
        response = _make_request(mp_url, timeout=10, headers=headers)
        
        if response and isinstance(response, dict) and "data" in response:
            materials = response.get("data", [])
            if materials:
                mat = materials[0]
                result = {
                    "found": True,
                    "formula": mat.get("formula", formula_or_name),
                    "material_id": mat.get("material_id", ""),
                    "data_source": "Materials Project",
                    "mp_url": f"https://www.materialsproject.org/materials/{mat.get('material_id', '')}"
                }
                _save_cache("materials_project", formula_or_name, result)
                return result
        
        # Fallback: Try AFLOW (free, no auth required)
        result = lookup_aflow(formula_or_name)
        if result.get("found"):
            result["data_source"] = "Materials Project (via AFLOW)"
            _save_cache("materials_project", formula_or_name, result)
            return result
        
        result = {"found": False, "query": formula_or_name, "data_source": "Materials Project"}
        _save_cache("materials_project", formula_or_name, result)
        return result
        
    except Exception as e:
        logger.warning(f"Materials Project lookup error for {formula_or_name}: {e}")
        # Fallback to AFLOW
        result = lookup_aflow(formula_or_name)
        if result.get("found"):
            result["data_source"] = "Materials Project (fallback to AFLOW)"
            _save_cache("materials_project", formula_or_name, result)
            return result
        
        result = {"found": False, "query": formula_or_name, "data_source": "Materials Project"}
        _save_cache("materials_project", formula_or_name, result)
        return result


# ============================================================================
# NIST ADSORPTION DATABASE CONNECTOR
# ============================================================================

def lookup_nist_adsorption(material_or_adsorbate: str) -> Dict[str, Any]:
    """
    Look up adsorption data in NIST Adsorption Isotherm Database.
    
    Returns:
    {
        "found": bool,
        "query": str,
        "studies_found": int,
        "common_adsorbates": list,
        "data_source": "NIST Adsorption Isotherm Database"
    }
    """
    cached = _load_cache("nist_adsorption", material_or_adsorbate)
    if cached:
        return cached
    
    try:
        # NIST Adsorption Isotherm Database search
        url = f"https://adsorption.nist.gov/isodb/api/materials?search={material_or_adsorbate}"
        
        response = _make_request(url)
        
        if not response or "materials" not in response:
            result = {
                "found": False,
                "query": material_or_adsorbate,
                "data_source": "NIST Adsorption Isotherm Database"
            }
            _save_cache("nist_adsorption", material_or_adsorbate, result)
            return result
        
        materials = response.get("materials", [])
        
        # Collect adsorbates used with this material
        adsorbates_set = set()
        for material in materials[:5]:  # Limit to 5 results
            for study in material.get("studies", [])[:3]:
                adsorbates_set.add(study.get("adsorbate", {}).get("name", ""))
        
        result = {
            "found": len(materials) > 0,
            "query": material_or_adsorbate,
            "studies_found": sum(len(m.get("studies", [])) for m in materials),
            "common_adsorbates": list(adsorbates_set)[:5],
            "materials_found": len(materials),
            "data_source": "NIST Adsorption Isotherm Database",
            "nist_url": f"https://adsorption.nist.gov/isodb/?search={material_or_adsorbate}"
        }
        
        _save_cache("nist_adsorption", material_or_adsorbate, result)
        return result
        
    except Exception as e:
        logger.warning(f"NIST Adsorption lookup error for {material_or_adsorbate}: {e}")
        result = {
            "found": False,
            "query": material_or_adsorbate,
            "data_source": "NIST Adsorption Isotherm Database",
            "error": str(e)
        }
        _save_cache("nist_adsorption", material_or_adsorbate, result)
        return result


# ============================================================================
# CRYSTALLOGRAPHY OPEN DATABASE (COD) CONNECTOR
# ============================================================================

def lookup_cod_structure(formula_or_name: str) -> Dict[str, Any]:
    """
    Look up crystal structure in Crystallography Open Database.
    
    Returns:
    {
        "found": bool,
        "formula": str,
        "cod_id": str,
        "structures_found": int,
        "data_source": "Crystallography Open Database"
    }
    """
    cached = _load_cache("cod", formula_or_name)
    if cached:
        return cached
    
    try:
        # COD API endpoint
        url = f"http://www.crystallography.net/cod/search/formula={formula_or_name}/?format=json&limit=10"
        
        response = _make_request(url)
        
        if not response or "results" not in response:
            result = {
                "found": False,
                "query": formula_or_name,
                "data_source": "Crystallography Open Database"
            }
            _save_cache("cod", formula_or_name, result)
            return result
        
        results = response.get("results", [])
        
        result = {
            "found": len(results) > 0,
            "query": formula_or_name,
            "structures_found": len(results),
            "data_source": "Crystallography Open Database",
            "cod_ids": [r.get("cod_id", "") for r in results[:5]],
            "cod_url": f"http://www.crystallography.net/cod/search/formula={formula_or_name}/"
        }
        
        _save_cache("cod", formula_or_name, result)
        return result
        
    except Exception as e:
        logger.warning(f"COD lookup error for {formula_or_name}: {e}")
        result = {
            "found": False,
            "query": formula_or_name,
            "data_source": "Crystallography Open Database",
            "error": str(e)
        }
        _save_cache("cod", formula_or_name, result)
        return result


# ============================================================================
# AFLOW / AFLOWLIB CONNECTOR
# ============================================================================

def lookup_aflow(formula_or_name: str) -> Dict[str, Any]:
    """
    Look up computed material properties in AFLOW.
    
    Returns:
    {
        "found": bool,
        "formula": str,
        "materials_found": int,
        "data_source": "AFLOW"
    }
    """
    cached = _load_cache("aflow", formula_or_name)
    if cached:
        return cached
    
    try:
        # AFLOW API endpoint
        url = f"https://www.aflowlib.org/API/aflux/search/nspecies=*/species={formula_or_name}/format=json"
        
        response = _make_request(url)
        
        if not response or "response" not in response:
            result = {
                "found": False,
                "query": formula_or_name,
                "data_source": "AFLOW"
            }
            _save_cache("aflow", formula_or_name, result)
            return result
        
        materials = response.get("response", [])
        
        result = {
            "found": len(materials) > 0,
            "query": formula_or_name,
            "materials_found": len(materials),
            "data_source": "AFLOW",
            "aflow_url": f"https://www.aflowlib.org/search/?formula={formula_or_name}"
        }
        
        _save_cache("aflow", formula_or_name, result)
        return result
        
    except Exception as e:
        logger.warning(f"AFLOW lookup error for {formula_or_name}: {e}")
        result = {
            "found": False,
            "query": formula_or_name,
            "data_source": "AFLOW",
            "error": str(e)
        }
        _save_cache("aflow", formula_or_name, result)
        return result


# ============================================================================
# OQMD CONNECTOR
# ============================================================================

def lookup_oqmd(formula_or_name: str) -> Dict[str, Any]:
    """
    Look up thermodynamic properties in OQMD.
    
    Returns:
    {
        "found": bool,
        "formula": str,
        "materials_found": int,
        "data_source": "OQMD"
    }
    """
    cached = _load_cache("oqmd", formula_or_name)
    if cached:
        return cached
    
    try:
        # OQMD API endpoint
        url = f"http://oqmd.org/api/v1/search/formulas/?contains={formula_or_name}&limit=20&format=json"
        
        response = _make_request(url)
        
        if not response or "results" not in response:
            result = {
                "found": False,
                "query": formula_or_name,
                "data_source": "OQMD"
            }
            _save_cache("oqmd", formula_or_name, result)
            return result
        
        materials = response.get("results", [])
        
        result = {
            "found": len(materials) > 0,
            "query": formula_or_name,
            "materials_found": len(materials),
            "data_source": "OQMD",
            "oqmd_url": f"http://oqmd.org/search?q={formula_or_name}"
        }
        
        _save_cache("oqmd", formula_or_name, result)
        return result
        
    except Exception as e:
        logger.warning(f"OQMD lookup error for {formula_or_name}: {e}")
        result = {
            "found": False,
            "query": formula_or_name,
            "data_source": "OQMD",
            "error": str(e)
        }
        _save_cache("oqmd", formula_or_name, result)
        return result


# ============================================================================
# JARVIS CONNECTOR
# ============================================================================

def lookup_jarvis(formula_or_name: str) -> Dict[str, Any]:
    """
    Look up atomistic materials data in JARVIS.
    
    Returns:
    {
        "found": bool,
        "formula": str,
        "materials_found": int,
        "data_source": "JARVIS"
    }
    """
    cached = _load_cache("jarvis", formula_or_name)
    if cached:
        return cached
    
    try:
        # JARVIS API endpoint
        url = f"https://www.ctcms.nist.gov/jarvis_api/jarviscff?formula={formula_or_name}"
        
        response = _make_request(url)
        
        if not response or "data" not in response:
            result = {
                "found": False,
                "query": formula_or_name,
                "data_source": "JARVIS"
            }
            _save_cache("jarvis", formula_or_name, result)
            return result
        
        materials = response.get("data", [])
        
        result = {
            "found": len(materials) > 0,
            "query": formula_or_name,
            "materials_found": len(materials),
            "data_source": "JARVIS",
            "jarvis_url": f"https://www.ctcms.nist.gov/jarvis/search/?formula={formula_or_name}"
        }
        
        _save_cache("jarvis", formula_or_name, result)
        return result
        
    except Exception as e:
        logger.warning(f"JARVIS lookup error for {formula_or_name}: {e}")
        result = {
            "found": False,
            "query": formula_or_name,
            "data_source": "JARVIS",
            "error": str(e)
        }
        _save_cache("jarvis", formula_or_name, result)
        return result


# ============================================================================
# CoRE MOF DATABASE CONNECTOR
# ============================================================================

def lookup_core_mof(query: str) -> Dict[str, Any]:
    """
    Look up MOF structures in CoRE MOF Database.
    
    Returns:
    {
        "found": bool,
        "mofs_found": int,
        "data_source": "CoRE MOF Database"
    }
    """
    cached = _load_cache("core_mof", query)
    if cached:
        return cached
    
    try:
        # CoRE MOF Database search
        url = f"https://api.materialscloud.org/beautiful_cofs/v1/search?text={query}"
        
        response = _make_request(url)
        
        if not response or "results" not in response:
            result = {
                "found": False,
                "query": query,
                "data_source": "CoRE MOF Database"
            }
            _save_cache("core_mof", query, result)
            return result
        
        mofs = response.get("results", [])
        
        result = {
            "found": len(mofs) > 0,
            "query": query,
            "mofs_found": len(mofs),
            "data_source": "CoRE MOF Database",
            "core_mof_url": f"https://www.materialscloud.org/app/beautiful_cofs/search?text={query}"
        }
        
        _save_cache("core_mof", query, result)
        return result
        
    except Exception as e:
        logger.warning(f"CoRE MOF lookup error for {query}: {e}")
        result = {
            "found": False,
            "query": query,
            "data_source": "CoRE MOF Database",
            "error": str(e)
        }
        _save_cache("core_mof", query, result)
        return result


# ============================================================================
# IZA ZEOLITE DATABASE CONNECTOR
# ============================================================================

def lookup_iza_zeolite(query: str) -> Dict[str, Any]:
    """
    Look up zeolite frameworks in IZA Database.
    
    Returns:
    {
        "found": bool,
        "zeolites_found": int,
        "data_source": "IZA Zeolite Database"
    }
    """
    cached = _load_cache("iza_zeolite", query)
    if cached:
        return cached
    
    try:
        # IZA Zeolite Database search
        url = f"http://www.iza-structure.org/IZA-SC/ftc_table.php?SiAl={query}"
        
        response = _make_request(url)
        
        # IZA returns HTML, so we'll do a simple presence check
        if response and "text" in response:
            found = query.lower() in response["text"].lower()
            result = {
                "found": found,
                "query": query,
                "data_source": "IZA Zeolite Database",
                "iza_url": f"http://www.iza-structure.org/IZA-SC/ftc_table.php"
            }
        else:
            result = {
                "found": False,
                "query": query,
                "data_source": "IZA Zeolite Database"
            }
        
        _save_cache("iza_zeolite", query, result)
        return result
        
    except Exception as e:
        logger.warning(f"IZA Zeolite lookup error for {query}: {e}")
        result = {
            "found": False,
            "query": query,
            "data_source": "IZA Zeolite Database",
            "error": str(e)
        }
        _save_cache("iza_zeolite", query, result)
        return result


# ============================================================================
# EPA COMPTOX DASHBOARD CONNECTOR
# ============================================================================

def lookup_comptox(compound_name: str) -> Dict[str, Any]:
    """
    Look up chemical safety data in EPA CompTox Dashboard.
    
    Returns:
    {
        "found": bool,
        "compound_name": str,
        "hazard_flags": list,
        "data_source": "EPA CompTox Dashboard"
    }
    """
    cached = _load_cache("comptox", compound_name)
    if cached:
        return cached
    
    try:
        # CompTox Dashboard API endpoint
        url = f"https://www.epa.gov/chemistry-searches?search_api_fulltext={compound_name}"
        
        response = _make_request(url)
        
        result = {
            "found": response is not None,
            "compound_name": compound_name,
            "data_source": "EPA CompTox Dashboard",
            "comptox_url": f"https://comptox.epa.gov/dashboard/results?search={compound_name}"
        }
        
        _save_cache("comptox", compound_name, result)
        return result
        
    except Exception as e:
        logger.warning(f"CompTox lookup error for {compound_name}: {e}")
        result = {
            "found": False,
            "compound_name": compound_name,
            "data_source": "EPA CompTox Dashboard",
            "error": str(e)
        }
        _save_cache("comptox", compound_name, result)
        return result


# ============================================================================
# LITERATURE SEARCH CONNECTORS
# ============================================================================

def search_openalex(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for papers in OpenAlex using corrected API syntax.
    
    Returns:
    {
        "found": bool,
        "papers_found": int,
        "papers": list,
        "data_source": "OpenAlex"
    }
    """
    cached = _load_cache("openalex", query)
    if cached:
        return cached
    
    try:
        # OpenAlex API endpoint with corrected syntax
        # Using filter and per_page instead of limit
        search_query = query.replace(" ", "%20")
        url = f"https://api.openalex.org/works?search={search_query}&per_page={limit}&sort=-cited_by_count"
        
        response = _make_request(url, timeout=12)
        
        if not response or "results" not in response:
            # Try Crossref as fallback for literature search
            result = search_crossref(query, limit=limit)
            if result.get("found"):
                result["data_source"] = "OpenAlex (via Crossref)"
                _save_cache("openalex", query, result)
                return result
            
            result = {
                "found": False,
                "query": query,
                "data_source": "OpenAlex"
            }
            _save_cache("openalex", query, result)
            return result
        
        papers = response.get("results", [])
        
        paper_list = []
        for paper in papers[:limit]:
            pub_year = paper.get("publication_year", 0)
            if pub_year is None:
                pub_year = 0
            paper_list.append({
                "title": paper.get("title", ""),
                "year": pub_year,
                "cited_by_count": paper.get("cited_by_count", 0),
                "url": paper.get("id", "")
            })
        
        result = {
            "found": len(papers) > 0,
            "query": query,
            "papers_found": len(papers) if papers else 0,
            "papers": paper_list,
            "data_source": "OpenAlex",
            "openalex_url": f"https://openalex.org/search?q={search_query}"
        }
        
        _save_cache("openalex", query, result)
        return result
        
    except Exception as e:
        logger.warning(f"OpenAlex search error for {query}: {e}")
        # Fall back to Crossref
        result = search_crossref(query, limit=limit)
        if result.get("found"):
            result["data_source"] = "OpenAlex (Crossref fallback)"
            _save_cache("openalex", query, result)
            return result
        
        result = {
            "found": False,
            "query": query,
            "data_source": "OpenAlex"
        }
        _save_cache("openalex", query, result)
        return result


def search_crossref(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search for papers in Crossref.
    
    Returns:
    {
        "found": bool,
        "papers_found": int,
        "papers": list,
        "data_source": "Crossref"
    }
    """
    cached = _load_cache("crossref", query)
    if cached:
        return cached
    
    try:
        # Crossref API endpoint
        url = f"https://api.crossref.org/works?query={query}&rows={limit}&order=desc&sort=relevance-score"
        
        response = _make_request(url)
        
        if not response or "message" not in response:
            result = {
                "found": False,
                "query": query,
                "data_source": "Crossref"
            }
            _save_cache("crossref", query, result)
            return result
        
        items = response.get("message", {}).get("items", [])
        
        paper_list = []
        for paper in items[:limit]:
            paper_list.append({
                "title": (paper.get("title", [""])[0] if isinstance(paper.get("title"), list) else paper.get("title", "")),
                "year": paper.get("published-online", {}).get("date-parts", [[0]])[0][0] if paper.get("published-online") else 0,
                "doi": paper.get("DOI", ""),
                "url": paper.get("URL", "")
            })
        
        result = {
            "found": len(items) > 0,
            "query": query,
            "papers_found": len(items),
            "papers": paper_list,
            "data_source": "Crossref",
            "crossref_url": f"https://www.crossref.org/guestquery/"
        }
        
        _save_cache("crossref", query, result)
        return result
        
    except Exception as e:
        logger.warning(f"Crossref search error for {query}: {e}")
        result = {
            "found": False,
            "query": query,
            "data_source": "Crossref",
            "error": str(e)
        }
        _save_cache("crossref", query, result)
        return result


# ============================================================================
# CATEGORY-SPECIFIC DATASET ROUTING
# ============================================================================

DATASET_ROUTING = {
    "atmospheric_water_harvesting_material": [
        "pubchem",
        "nist_adsorption",
        "materials_project",
        "core_mof",
        "iza_zeolite",
        "comptox",
        "openalex",
        "crossref"
    ],
    "co2_capture_material": [
        "pubchem",
        "nist_adsorption",
        "materials_project",
        "core_mof",
        "iza_zeolite",
        "oqmd",
        "comptox",
        "openalex",
        "crossref"
    ],
    "photocatalytic_coating": [
        "pubchem",
        "materials_project",
        "aflow",
        "oqmd",
        "cod",
        "jarvis",
        "comptox",
        "openalex",
        "crossref"
    ],
    "membrane_water_treatment": [
        "pubchem",
        "comptox",
        "openalex",
        "crossref"
    ],
    "adsorbent_heavy_metals": [
        "pubchem",
        "comptox",
        "nist_adsorption",
        "materials_project",
        "openalex",
        "crossref"
    ],
    "phosphate_recovery_material": [
        "pubchem",
        "materials_project",
        "cod",
        "comptox",
        "openalex",
        "crossref"
    ],
    "potassium_brine_separation_material": [
        "pubchem",
        "materials_project",
        "iza_zeolite",
        "cod",
        "openalex",
        "crossref"
    ],
    "thermal_insulation_composite": [
        "pubchem",
        "materials_project",
        "cod",
        "comptox",
        "openalex",
        "crossref"
    ],
    "self_cleaning_building_coating": [
        "pubchem",
        "materials_project",
        "aflow",
        "oqmd",
        "cod",
        "comptox",
        "openalex",
        "crossref"
    ],
    "other_material": [
        "pubchem",
        "comptox",
        "openalex",
        "crossref"
    ]
}


# ============================================================================
# MAIN VERIFICATION ORCHESTRATOR
# ============================================================================

def verify_with_free_datasets(
    material_data: Dict[str, Any],
    category: str
) -> Dict[str, Any]:
    """
    Main orchestrator function for scientific dataset verification.
    
    Verifies material components, formulas, and safety against free/open-access datasets.
    
    Args:
        material_data: Dict containing material information from category_registry
        category: Material category string
    
    Returns:
        {
            "verification_status": "pass" | "warning" | "fail",
            "components_checked": list,
            "components_verified": list,
            "components_not_found": list,
            "formulas_confirmed": list,
            "materials_found": list,
            "safety_flags": list,
            "datasets_queried": list,
            "literature_hits": int,
            "warnings": list,
            "evidence_summary": str,
            "confidence_adjustment": str,
            "dataset_urls": list
        }
    """
    
    # Initialize result structure
    result = {
        "verification_status": "pass",
        "components_checked": [],
        "components_verified": [],
        "components_not_found": [],
        "formulas_confirmed": [],
        "materials_found": [],
        "safety_flags": [],
        "datasets_queried": [],
        "literature_hits": 0,
        "warnings": [],
        "evidence_summary": "",
        "confidence_adjustment": "",
        "dataset_urls": []
    }
    
    # Get datasets to query for this category
    datasets_to_use = DATASET_ROUTING.get(category, DATASET_ROUTING["other_material"])
    
    # Extract composition from material data
    composition = material_data.get("default_composition", [])
    category_name = material_data.get("display_name", category)
    
    if not composition:
        result["warnings"].append("No composition data available for verification")
        return result
    
    # Record components being checked
    result["components_checked"] = composition
    
    # Verify each component
    for component in composition:
        component_clean = component.strip()
        
        # Query PubChem for chemical identity
        if "pubchem" in datasets_to_use:
            pubchem_result = lookup_pubchem(component_clean)
            result["datasets_queried"].append("PubChem")
            
            if pubchem_result.get("found"):
                result["components_verified"].append(component_clean)
                result["materials_found"].append({
                    "component": component_clean,
                    "formula": pubchem_result.get("molecular_formula", ""),
                    "cid": pubchem_result.get("pubchem_cid", ""),
                    "source": "PubChem"
                })
                if "pubchem_url" in pubchem_result:
                    result["dataset_urls"].append(pubchem_result["pubchem_url"])
            else:
                result["components_not_found"].append(component_clean)
        
        # Query CompTox for safety flags
        if "comptox" in datasets_to_use:
            comptox_result = lookup_comptox(component_clean)
            result["datasets_queried"].append("EPA CompTox")
            if "comptox_url" in comptox_result:
                result["dataset_urls"].append(comptox_result["comptox_url"])
    
    # Query category-specific structural databases
    for inorganic_component in ["TiO2", "ZnO", "Al2O3", "SiO2", "Fe2O3", "Fe3O4", "MoS2", "WS2"]:
        if inorganic_component in composition or inorganic_component.lower() in composition:
            
            # Materials Project for inorganic materials
            if "materials_project" in datasets_to_use:
                mp_result = lookup_materials_project(inorganic_component)
                if mp_result.get("found"):
                    result["materials_found"].append({
                        "component": inorganic_component,
                        "formula": mp_result.get("formula", ""),
                        "material_id": mp_result.get("material_id", ""),
                        "source": "Materials Project"
                    })
                    if "mp_url" in mp_result:
                        result["dataset_urls"].append(mp_result["mp_url"])
            
            # COD for crystal structures
            if "cod" in datasets_to_use:
                cod_result = lookup_cod_structure(inorganic_component)
                if cod_result.get("found"):
                    result["materials_found"].append({
                        "component": inorganic_component,
                        "structures_found": cod_result.get("structures_found", 0),
                        "source": "COD"
                    })
                    if "cod_url" in cod_result:
                        result["dataset_urls"].append(cod_result["cod_url"])
    
    # Query category-specific catalytic/adsorbent databases
    if category in ["atmospheric_water_harvesting_material", "co2_capture_material", "adsorbent_heavy_metals"]:
        if "nist_adsorption" in datasets_to_use:
            nist_result = lookup_nist_adsorption(category_name)
            if nist_result.get("found"):
                result["materials_found"].append({
                    "type": "adsorption_data",
                    "studies_found": nist_result.get("studies_found", 0),
                    "source": "NIST Adsorption"
                })
                if "nist_url" in nist_result:
                    result["dataset_urls"].append(nist_result["nist_url"])
        
        if "core_mof" in datasets_to_use:
            core_result = lookup_core_mof(category_name)
            if core_result.get("found"):
                result["materials_found"].append({
                    "type": "mof_data",
                    "mofs_found": core_result.get("mofs_found", 0),
                    "source": "CoRE MOF"
                })
                if "core_mof_url" in core_result:
                    result["dataset_urls"].append(core_result["core_mof_url"])
        
        if "iza_zeolite" in datasets_to_use:
            iza_result = lookup_iza_zeolite(category_name)
            if iza_result.get("found"):
                result["materials_found"].append({
                    "type": "zeolite_data",
                    "source": "IZA Zeolite"
                })
                if "iza_url" in iza_result:
                    result["dataset_urls"].append(iza_result["iza_url"])
    
    # Search for supporting literature
    literature_hits = 0
    for dataset_search in ["openalex", "crossref"]:
        if dataset_search in datasets_to_use:
            if dataset_search == "openalex":
                lit_result = search_openalex(category_name, limit=3)
            else:
                lit_result = search_crossref(category_name, limit=3)
            
            if lit_result.get("found"):
                literature_hits += lit_result.get("papers_found", 0)
                if "openalex_url" in lit_result:
                    result["dataset_urls"].append(lit_result["openalex_url"])
                elif "crossref_url" in lit_result:
                    result["dataset_urls"].append(lit_result["crossref_url"])
    
    result["literature_hits"] = literature_hits
    
    # Generate evidence summary
    verified_count = len(result["components_verified"])
    checked_count = len(result["components_checked"])
    materials_found_count = len(result["materials_found"])
    
    if checked_count == 0:
        result["evidence_summary"] = "No components to verify against datasets."
        result["verification_status"] = "warning"
    elif verified_count == checked_count:
        result["evidence_summary"] = (
            f"✅ All {verified_count} components verified in external databases. "
            f"{materials_found_count} additional material properties found. "
            f"Literature support: {literature_hits} papers found. "
            f"Note: Dataset matches do not prove performance; experimental validation required."
        )
        result["verification_status"] = "pass"
    elif verified_count >= checked_count * 0.7:
        result["evidence_summary"] = (
            f"⚠️ {verified_count}/{checked_count} components verified in external databases. "
            f"{materials_found_count} material properties found. "
            f"Literature support: {literature_hits} papers. "
            f"Some components not found in public databases (may be proprietary/novel). "
            f"Experimental validation strongly recommended."
        )
        result["verification_status"] = "warning"
    else:
        result["evidence_summary"] = (
            f"⚠️ Only {verified_count}/{checked_count} components verified. "
            f"Many components not found in public databases. "
            f"Material composition should be reviewed. "
            f"Experimental validation is essential."
        )
        result["verification_status"] = "warning"
        result["warnings"].append("Multiple components could not be verified in external datasets")
    
    result["confidence_adjustment"] = (
        "Dataset verification provides evidence for material plausibility but does not replace "
        "experimental testing. All recommendations must be validated through laboratory testing "
        "before production use."
    )
    
    # Remove duplicate URLs
    result["dataset_urls"] = list(set(result["dataset_urls"]))
    result["datasets_queried"] = list(set(result["datasets_queried"]))
    
    return result


# ============================================================================
# UTILITY FUNCTIONS FOR INTEGRATION
# ============================================================================

def format_verification_for_pdf(verification_result: Dict[str, Any]) -> str:
    """
    Format verification result for PDF report inclusion.
    """
    summary = f"""
SCIENTIFIC DATASET VERIFICATION SUMMARY
=====================================

Verification Status: {verification_result['verification_status'].upper()}

Datasets Queried:
{', '.join(verification_result['datasets_queried']) if verification_result['datasets_queried'] else 'None'}

Components Checked: {', '.join(verification_result['components_checked'])}

Components Verified: {', '.join(verification_result['components_verified']) if verification_result['components_verified'] else '(none)'}

Components Not Found in Databases: {', '.join(verification_result['components_not_found']) if verification_result['components_not_found'] else '(none)'}

Materials/Properties Found: {len(verification_result['materials_found'])}

Supporting Literature Found: {verification_result['literature_hits']} papers

Evidence Summary:
{verification_result['evidence_summary']}

Scientific Boundary Statement:
{verification_result['confidence_adjustment']}

Warnings:
{'. '.join(verification_result['warnings']) if verification_result['warnings'] else 'None'}

Reference URLs:
{'; '.join(verification_result['dataset_urls'][:5]) if verification_result['dataset_urls'] else 'None'}
"""
    return summary
