#!/usr/bin/env python
"""
Simplified Unit Test Suite for Dataset Connectors
Focuses on PubChem (verified working) and verification workflow
"""

import unittest
from scientific_data_connectors import (
    lookup_pubchem,
    search_crossref,
    search_openalex,
    verify_with_free_datasets,
    _save_cache,
    _load_cache,
    DATASET_ROUTING,
)


class TestPubChemConnector(unittest.TestCase):
    """PubChem chemical compound lookups - VERIFIED WORKING"""
    
    def test_pubchem_water_lookup(self):
        """Test PubChem finds water (H2O)"""
        result = lookup_pubchem("water")
        self.assertTrue(result['found'])
        self.assertIsNotNone(result['pubchem_cid'])
        self.assertEqual(result['molecular_formula'], 'H2O')
    
    def test_pubchem_tio2_lookup(self):
        """Test PubChem finds titanium dioxide"""
        result = lookup_pubchem("titanium dioxide")
        self.assertTrue(result['found'])
        self.assertEqual(result['molecular_formula'], 'O2Ti')
    
    def test_pubchem_sio2_lookup(self):
        """Test PubChem finds silicon dioxide"""
        result = lookup_pubchem("silicon dioxide")
        self.assertTrue(result['found'])
        self.assertEqual(result['molecular_formula'], 'O2Si')
    
    def test_pubchem_carbon_lookup(self):
        """Test PubChem finds activated carbon"""
        result = lookup_pubchem("activated carbon")
        self.assertTrue(result['found'])
        self.assertIsNotNone(result['pubchem_cid'])
    
    def test_pubchem_nonexistent_compound(self):
        """Test PubChem returns False for fake compounds"""
        result = lookup_pubchem("xyzabc123fakematerial")
        self.assertFalse(result['found'])
    
    def test_pubchem_response_structure(self):
        """Test PubChem response contains required fields"""
        result = lookup_pubchem("water")
        required_fields = ['found', 'pubchem_cid', 'molecular_formula', 'molecular_weight']
        for field in required_fields:
            self.assertIn(field, result)


class TestVerificationWorkflow(unittest.TestCase):
    """Material verification workflow - ALL CATEGORIES"""
    
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
        self.assertTrue(len(result['components_verified']) > 0)
    
    def test_water_harvesting_verification(self):
        """Test atmospheric water harvesting material verification"""
        material_data = {
            'name': 'AWH Material',
            'components': ['Activated Carbon', 'Silica Gel', 'Polymer']
        }
        result = verify_with_free_datasets(material_data, 'atmospheric_water_harvesting_material')
        
        self.assertEqual(result['verification_status'], 'pass')
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
        """Test thermal insulation material verification"""
        material_data = {
            'name': 'Thermal Insulator',
            'components': ['Aerogel', 'Glass Fiber']
        }
        result = verify_with_free_datasets(material_data, 'thermal_insulation_composite')
        
        self.assertIsInstance(result['components_verified'], list)
        self.assertIn('evidence_summary', result)
    
    def test_self_cleaning_verification(self):
        """Test self-cleaning coating verification"""
        material_data = {
            'name': 'Self-Cleaning Coating',
            'components': ['Titanium Dioxide', 'Silane']
        }
        result = verify_with_free_datasets(material_data, 'self_cleaning_building_coating')
        
        self.assertIn('evidence_summary', result)
    
    def test_verification_has_all_fields(self):
        """Test verification result has all required fields"""
        material_data = {
            'name': 'Test Material',
            'components': ['TiO2', 'SiO2']
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
            self.assertIn(field, result)


class TestCacheSystem(unittest.TestCase):
    """Cache functionality"""
    
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
    """Category to dataset routing"""
    
    def test_all_categories_mapped(self):
        """Test all categories have dataset assignments"""
        categories = list(DATASET_ROUTING.keys())
        
        for category in categories:
            self.assertIn(category, DATASET_ROUTING)
            self.assertIsInstance(DATASET_ROUTING[category], list)
            self.assertGreater(len(DATASET_ROUTING[category]), 0)
    
    def test_dataset_routing_structure(self):
        """Test DATASET_ROUTING has tuples of (name, function)"""
        for category, datasets in DATASET_ROUTING.items():
            for dataset_name, lookup_func in datasets:
                self.assertIsInstance(dataset_name, str)
                self.assertTrue(callable(lookup_func))


class TestErrorHandling(unittest.TestCase):
    """Error handling and edge cases"""
    
    def test_pubchem_empty_string(self):
        """Test PubChem handles empty string"""
        result = lookup_pubchem("")
        self.assertIn('found', result)
    
    def test_pubchem_special_characters(self):
        """Test PubChem handles special characters"""
        result = lookup_pubchem("α-iron oxide")
        self.assertIsInstance(result, dict)
    
    def test_verification_empty_components(self):
        """Test verification with empty components"""
        material_data = {
            'name': 'Test',
            'components': []
        }
        result = verify_with_free_datasets(material_data, 'photocatalytic_coating')
        self.assertIn('verification_status', result)
    
    def test_verification_invalid_category(self):
        """Test verification with invalid category"""
        material_data = {
            'name': 'Test',
            'components': ['TiO2']
        }
        result = verify_with_free_datasets(material_data, 'invalid_category')
        self.assertIsInstance(result, dict)


class TestMultiComponentVerification(unittest.TestCase):
    """Verification of materials with multiple components"""
    
    def test_three_component_material(self):
        """Test material with 3 components"""
        material_data = {
            'name': 'Complex Material',
            'components': ['TiO2', 'SiO2', 'Al2O3']
        }
        result = verify_with_free_datasets(material_data, 'photocatalytic_coating')
        
        verified_count = len(result['components_verified'])
        not_found_count = len(result['components_not_found'])
        total = verified_count + not_found_count
        
        self.assertLessEqual(total, 3)
    
    def test_five_component_material(self):
        """Test material with 5 components"""
        material_data = {
            'name': 'Complex Composite',
            'components': ['Component1', 'Component2', 'Component3', 'Component4', 'Component5']
        }
        result = verify_with_free_datasets(material_data, 'thermal_insulation_composite')
        
        self.assertIsInstance(result['components_verified'], list)
        self.assertIsInstance(result['components_not_found'], list)


# ============================================================================
# TEST STATISTICS
# ============================================================================

def run_tests_with_summary():
    """Run tests and print summary statistics"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPubChemConnector))
    suite.addTests(loader.loadTestsFromTestCase(TestVerificationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestCategoryDatasetMapping))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiComponentVerification))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 80)
    
    return result


if __name__ == '__main__':
    run_tests_with_summary()
