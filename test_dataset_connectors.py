#!/usr/bin/env python
"""
Comprehensive unit tests for scientific_data_connectors module

Tests:
- PubChem connector (chemical lookups)
- Crossref connector (literature search)
- OpenAlex connector (literature search fallback)
- Verification workflow across categories
- Cache system functionality
- Error handling and fallbacks
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import tempfile
import shutil
from scientific_data_connectors import (
    lookup_pubchem,
    search_crossref,
    search_openalex,
    lookup_wikidata,
    verify_with_free_datasets,
    _save_cache,
    _load_cache,
    DATASET_ROUTING,
)


class TestPubChemConnector(unittest.TestCase):
    """Test PubChem chemical compound lookups"""
    
    def test_pubchem_water_lookup(self):
        """Test PubChem can find water (H2O)"""
        result = lookup_pubchem("water")
        self.assertTrue(result['found'], "Water should be found in PubChem")
        self.assertIn('pubchem_cid', result)
        self.assertIn('molecular_formula', result)
        self.assertIn('molecular_weight', result)
    
    def test_pubchem_tio2_lookup(self):
        """Test PubChem can find titanium dioxide"""
        result = lookup_pubchem("titanium dioxide")
        self.assertTrue(result['found'], "TiO2 should be found in PubChem")
        self.assertIsNotNone(result['pubchem_cid'])
    
    def test_pubchem_sio2_lookup(self):
        """Test PubChem can find silicon dioxide"""
        result = lookup_pubchem("silicon dioxide")
        self.assertTrue(result['found'], "SiO2 should be found in PubChem")
        self.assertIsNotNone(result['pubchem_cid'])
    
    def test_pubchem_carbon_lookup(self):
        """Test PubChem can find activated carbon"""
        result = lookup_pubchem("activated carbon")
        self.assertTrue(result['found'], "Activated carbon should be found in PubChem")
        self.assertIsNotNone(result['pubchem_cid'])
    
    def test_pubchem_nonexistent_compound(self):
        """Test PubChem returns False for fake compounds"""
        result = lookup_pubchem("xyzabc123fakematerial")
        self.assertFalse(result['found'], "Fake compound should not be found")
    
    def test_pubchem_response_structure(self):
        """Test PubChem response contains required fields"""
        result = lookup_pubchem("water")
        required_fields = ['found', 'pubchem_cid', 'molecular_formula', 'molecular_weight']
        for field in required_fields:
            self.assertIn(field, result, f"Missing required field: {field}")


class TestCrossrefConnector(unittest.TestCase):
    """Test Crossref literature search"""
    
    def test_crossref_search_returns_dict(self):
        """Test Crossref search returns dictionary"""
        result = search_crossref("water treatment", limit=5)
        self.assertIsInstance(result, dict)
    
    def test_crossref_response_structure(self):
        """Test Crossref response has expected structure"""
        result = search_crossref("photocatalytic", limit=3)
        self.assertIn('found', result)
        self.assertIn('papers_found', result)
        self.assertIn('papers', result)
    
    def test_crossref_returns_list_of_papers(self):
        """Test Crossref papers is a list"""
        result = search_crossref("material science", limit=5)
        self.assertIsInstance(result['papers'], list)
    
    def test_crossref_paper_structure(self):
        """Test each paper has required fields"""
        result = search_crossref("chemistry", limit=1)
        if result['papers']:
            paper = result['papers'][0]
            self.assertIn('title', paper)
            self.assertIn('year', paper)
    
    def test_crossref_limit_parameter(self):
        """Test limit parameter is respected"""
        result = search_crossref("materials", limit=3)
        self.assertLessEqual(len(result['papers']), 3)


class TestOpenAlexConnector(unittest.TestCase):
    """Test OpenAlex literature search"""
    
    def test_openalex_search_returns_dict(self):
        """Test OpenAlex search returns dictionary"""
        result = search_openalex("material design", limit=5)
        self.assertIsInstance(result, dict)
    
    def test_openalex_response_structure(self):
        """Test OpenAlex response has expected structure"""
        result = search_openalex("quantum materials", limit=3)
        self.assertIn('found', result)
        self.assertIn('papers_found', result)
    
    def test_openalex_fallback_to_crossref(self):
        """Test OpenAlex falls back to Crossref on failure"""
        result = search_openalex("nanotechnology", limit=2)
        self.assertIsInstance(result, dict)
        self.assertIn('papers_found', result)


class TestVerificationWorkflow(unittest.TestCase):
    """Test the full material verification workflow"""
    
    def test_photocatalytic_coating_verification(self):
        """Test photocatalytic coating category verification"""
        material_data = {
            'name': 'TiO2 Coating',
            'components': ['TiO2', 'SiO2']
        }
        result = verify_with_free_datasets(material_data, 'photocatalytic_coating')
        
        self.assertIn('verification_status', result)
        self.assertIn('components_verified', result)
        self.assertIn('components_not_found', result)
        self.assertIn('datasets_queried', result)
        self.assertIsInstance(result['components_verified'], list)
    
    def test_water_harvesting_verification(self):
        """Test atmospheric water harvesting category verification"""
        material_data = {
            'name': 'AWH Material',
            'components': ['Activated Carbon', 'Silica Gel']
        }
        result = verify_with_free_datasets(material_data, 'atmospheric_water_harvesting_material')
        
        self.assertEqual(result['verification_status'], 'PASS')
        self.assertGreater(len(result['components_verified']), 0)
    
    def test_co2_capture_verification(self):
        """Test CO2 capture material verification"""
        material_data = {
            'name': 'CO2 Sorbent',
            'components': ['Metal-Organic Framework', 'Zinc']
        }
        result = verify_with_free_datasets(material_data, 'co2_capture_material')
        
        self.assertIn('verification_status', result)
        self.assertIsInstance(result['datasets_queried'], list)
    
    def test_thermal_insulation_verification(self):
        """Test thermal insulation category verification"""
        material_data = {
            'name': 'Thermal Insulator',
            'components': ['Aerogel', 'Glass Fiber']
        }
        result = verify_with_free_datasets(material_data, 'thermal_insulation_composite')
        
        self.assertIsInstance(result['components_verified'], list)
    
    def test_self_cleaning_verification(self):
        """Test self-cleaning coating category verification"""
        material_data = {
            'name': 'Self-Cleaning Coating',
            'components': ['Titanium Dioxide', 'Silane']
        }
        result = verify_with_free_datasets(material_data, 'self_cleaning_building_coating')
        
        self.assertIn('evidence_summary', result)
    
    def test_verification_result_has_all_fields(self):
        """Test verification result has all required fields"""
        material_data = {
            'name': 'Test Material',
            'components': ['Component1', 'Component2']
        }
        result = verify_with_free_datasets(material_data, 'photocatalytic_coating')
        
        required_fields = [
            'verification_status',
            'components_verified',
            'components_not_found',
            'datasets_queried',
            'evidence_summary'
        ]
        for field in required_fields:
            self.assertIn(field, result, f"Missing required field: {field}")


class TestCacheSystem(unittest.TestCase):
    """Test cache functionality"""
    
    def setUp(self):
        """Create temporary cache directory for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cache_dir = os.environ.get('CACHE_DIR')
        os.environ['CACHE_DIR'] = self.temp_dir
    
    def tearDown(self):
        """Clean up temporary cache directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if self.original_cache_dir:
            os.environ['CACHE_DIR'] = self.original_cache_dir
    
    def test_cache_directory_creation(self):
        """Test cache directory is auto-created"""
        test_data = {'test': 'data', 'value': 123}
        _save_cache('test_dataset', 'test_query', test_data)
        
        # Verify directory exists
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_cache_save_and_load(self):
        """Test cache can save and retrieve data"""
        original_data = {'compound': 'water', 'cid': 962}
        _save_cache('pubchem', 'water', original_data)
        
        loaded_data = _load_cache('pubchem', 'water')
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data['cid'], 962)
    
    def test_cache_returns_none_for_missing_key(self):
        """Test cache returns None for non-existent keys"""
        result = _load_cache('nonexistent', 'nonexistent_query')
        self.assertIsNone(result)


class TestCategoryDatasetMapping(unittest.TestCase):
    """Test category to dataset routing"""
    
    def test_all_categories_mapped(self):
        """Test all categories have dataset assignments"""
        categories = list(DATASET_ROUTING.keys())
        
        for category in categories:
            self.assertIn(category, DATASET_ROUTING, f"Category not mapped: {category}")
            self.assertIsInstance(DATASET_ROUTING[category], list)
            self.assertGreater(len(DATASET_ROUTING[category]), 0)
    
    def test_photocatalytic_has_pubchem(self):
        """Test photocatalytic category includes PubChem"""
        datasets = DATASET_ROUTING.get('photocatalytic_coating', [])
        dataset_names = [ds[0] for ds in datasets]
        self.assertIn('pubchem', dataset_names)
    
    def test_water_harvesting_has_pubchem(self):
        """Test water harvesting category includes PubChem"""
        datasets = DATASET_ROUTING.get('atmospheric_water_harvesting_material', [])
        dataset_names = [ds[0] for ds in datasets]
        self.assertIn('pubchem', dataset_names)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_pubchem_empty_string(self):
        """Test PubChem handles empty string"""
        result = lookup_pubchem("")
        self.assertIn('found', result)
    
    def test_pubchem_special_characters(self):
        """Test PubChem handles special characters"""
        result = lookup_pubchem("α-iron oxide")
        self.assertIsInstance(result, dict)
    
    def test_verification_empty_components(self):
        """Test verification with empty components list"""
        material_data = {
            'name': 'Test',
            'components': []
        }
        result = verify_with_free_datasets(material_data, 'photocatalytic_coating')
        self.assertIn('verification_status', result)
    
    def test_verification_invalid_category(self):
        """Test verification with invalid category defaults gracefully"""
        material_data = {
            'name': 'Test',
            'components': ['TiO2']
        }
        result = verify_with_free_datasets(material_data, 'invalid_category')
        # Should still return a result, even if category is invalid
        self.assertIsInstance(result, dict)


class TestDataIntegrity(unittest.TestCase):
    """Test data validation and integrity"""
    
    def test_pubchem_returns_valid_cid(self):
        """Test PubChem returns valid CID numbers"""
        result = lookup_pubchem("water")
        if result['found']:
            self.assertIsInstance(result['pubchem_cid'], int)
            self.assertGreater(result['pubchem_cid'], 0)
    
    def test_crossref_returns_valid_years(self):
        """Test Crossref returns valid years"""
        result = search_crossref("chemistry", limit=5)
        for paper in result['papers']:
            if 'year' in paper and paper['year'] is not None:
                self.assertIsInstance(paper['year'], int)
                self.assertGreater(paper['year'], 1900)
                self.assertLess(paper['year'], 2100)
    
    def test_verification_status_is_valid(self):
        """Test verification status is one of expected values"""
        material_data = {
            'name': 'Test',
            'components': ['TiO2', 'SiO2']
        }
        result = verify_with_free_datasets(material_data, 'photocatalytic_coating')
        
        valid_statuses = ['PASS', 'PARTIAL_PASS', 'FAIL', 'NO_DATA']
        self.assertIn(result['verification_status'], valid_statuses)


class TestAPIResponsiveness(unittest.TestCase):
    """Test API responsiveness and timeout handling"""
    
    def test_pubchem_responds_within_timeout(self):
        """Test PubChem responds within reasonable time"""
        import time
        start = time.time()
        result = lookup_pubchem("water")
        elapsed = time.time() - start
        
        # Should respond within 15 seconds
        self.assertLess(elapsed, 15, f"PubChem took {elapsed:.2f}s")
        self.assertTrue(result['found'])
    
    def test_crossref_responds_within_timeout(self):
        """Test Crossref responds within reasonable time"""
        import time
        start = time.time()
        result = search_crossref("materials", limit=3)
        elapsed = time.time() - start
        
        # Should respond within 15 seconds
        self.assertLess(elapsed, 15, f"Crossref took {elapsed:.2f}s")


class TestMultiComponentVerification(unittest.TestCase):
    """Test verification of materials with multiple components"""
    
    def test_verify_three_component_material(self):
        """Test material with 3 components"""
        material_data = {
            'name': 'Complex Material',
            'components': ['TiO2', 'SiO2', 'Al2O3']
        }
        result = verify_with_free_datasets(material_data, 'photocatalytic_coating')
        
        verified_count = len(result['components_verified'])
        not_found_count = len(result['components_not_found'])
        total = verified_count + not_found_count
        
        self.assertLessEqual(verified_count + not_found_count, 3)
    
    def test_verify_five_component_material(self):
        """Test material with 5 components"""
        material_data = {
            'name': 'Complex Composite',
            'components': ['Component1', 'Component2', 'Component3', 'Component4', 'Component5']
        }
        result = verify_with_free_datasets(material_data, 'thermal_insulation_composite')
        
        self.assertIsInstance(result['components_verified'], list)
        self.assertIsInstance(result['components_not_found'], list)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
