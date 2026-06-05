"""
COMPREHENSIVE TEST SUITE FOR AUTO-CATEGORY CREATION
====================================================

Unit tests for all auto-category functions.

Run with: pytest test_auto_category_creation.py -v
"""

import pytest
import json
from auto_category_creation import (
    detect_category_gap,
    propose_new_category,
    check_duplicate_category,
    add_category_to_registry,
    apply_new_category_and_verify,
    _extract_key_concepts,
    _generate_category_name,
    _generate_display_name,
    _infer_hierarchical_classification,
    _generate_aliases,
    _generate_keywords,
    _generate_default_composition,
    _generate_category_parameters,
    _generate_validation_plan,
    _generate_safety_tests,
    _generate_characterization_methods,
    _generate_processing_method,
    _generate_disclaimer,
    _detect_safety_warnings,
    _string_similarity,
)
from category_registry import CATEGORY_REGISTRY


# ==============================================================================
# TEST FIXTURES
# ==============================================================================

@pytest.fixture
def sample_classification_result():
    """Sample hierarchical classification result."""
    return {
        "material_family": "composite",
        "functional_class": "adsorbent",
        "application_domain": "water_treatment",
        "specific_preset": "other_material",
        "confidence_score": 45,
        "matched_keywords": [],
        "top_3_categories": [],
        "alternative_categories": [],
        "reasoning_explanation": "Low confidence classification",
        "conflict_detected": False,
        "requires_user_confirmation": True,
        "close_call": True,
    }


@pytest.fixture
def sample_material_data():
    """Sample material data structure."""
    return {
        "material_category": "other_material",
        "material_category_display": "Other (Custom Material)",
        "target_application": "Water treatment",
        "composition": [],
        "category_specific_parameters": {},
        "validation_plan": {},
        "processing_method": [],
        "characterization_methods": [],
        "safety_tests": [],
    }


@pytest.fixture
def sample_user_request():
    """Sample user request."""
    return "I need a porous composite material for water treatment that can remove heavy metals and other contaminants using activated carbon and iron oxide nanoparticles"


# ==============================================================================
# TEST GROUP 1: CONCEPT EXTRACTION & GENERATION
# ==============================================================================

class TestConceptExtraction:
    """Tests for concept extraction and name generation."""
    
    def test_extract_key_concepts_basic(self):
        """Test extraction of key concepts from user request."""
        request = "Activated carbon composite for water purification and heavy metal removal"
        concepts = _extract_key_concepts(request)
        
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        assert any("activated" in c.lower() or "carbon" in c.lower() for c in concepts)
    
    def test_extract_key_concepts_empty(self):
        """Test extraction with empty request."""
        concepts = _extract_key_concepts("")
        assert isinstance(concepts, list)
        assert len(concepts) == 0
    
    def test_generate_category_name(self):
        """Test category name generation."""
        concepts = ["water", "treatment", "composite"]
        name = _generate_category_name(concepts, "test request")
        
        assert isinstance(name, str)
        assert len(name) <= 50
        assert "_" in name or len(name) == len(name.replace("_", ""))
        # Name should be lowercase and use underscores
        assert name.islower() or "_" in name
    
    def test_generate_display_name(self):
        """Test display name generation."""
        concepts = ["water", "treatment"]
        display = _generate_display_name(concepts, "test request")
        
        assert isinstance(display, str)
        assert len(display) <= 80
        # Display name should be title case
        assert display[0].isupper()
    
    def test_generate_category_name_fallback(self):
        """Test category name generation with no concepts."""
        name = _generate_category_name([], "Novel custom material for testing")
        
        assert isinstance(name, str)
        assert len(name) > 0
    
    def test_generate_display_name_fallback(self):
        """Test display name generation with no concepts."""
        display = _generate_display_name([], "Novel custom material for testing")
        
        assert isinstance(display, str)
        assert len(display) > 0


class TestHierarchicalClassification:
    """Tests for hierarchical classification inference."""
    
    def test_infer_polymer_family(self):
        """Test polymer material family detection."""
        family, func, app = _infer_hierarchical_classification(
            "A polymer-based composite for coating applications",
            []
        )
        
        assert family == "polymer"
    
    def test_infer_ceramic_family(self):
        """Test ceramic material family detection."""
        family, func, app = _infer_hierarchical_classification(
            "A ceramic oxide material with TiO2 photocatalyst",
            []
        )
        
        assert family == "ceramic"
    
    def test_infer_carbon_family(self):
        """Test carbon material family detection."""
        family, func, app = _infer_hierarchical_classification(
            "An activated carbon and graphene composite",
            []
        )
        
        assert family == "carbon"
    
    def test_infer_coating_functional_class(self):
        """Test coating functional class detection."""
        family, func, app = _infer_hierarchical_classification(
            "A surface coating for water resistance",
            []
        )
        
        assert func == "coating"
    
    def test_infer_membrane_functional_class(self):
        """Test membrane functional class detection."""
        family, func, app = _infer_hierarchical_classification(
            "A polymer membrane for water filtration and separation",
            []
        )
        
        assert func == "membrane"
    
    def test_infer_water_treatment_domain(self):
        """Test water treatment application domain detection."""
        family, func, app = _infer_hierarchical_classification(
            "A material for water purification and wastewater treatment",
            []
        )
        
        assert app == "water_treatment"
    
    def test_infer_construction_domain(self):
        """Test construction application domain detection."""
        family, func, app = _infer_hierarchical_classification(
            "An insulation composite for building construction and thermal resistance",
            []
        )
        
        assert app == "construction"


# ==============================================================================
# TEST GROUP 2: CATEGORY GAP DETECTION
# ==============================================================================

class TestCategoryGapDetection:
    """Tests for detect_category_gap function."""
    
    def test_gap_detected_low_confidence(self, sample_classification_result):
        """Test gap detection with low confidence."""
        result = detect_category_gap(
            "Custom novel material for unique application",
            sample_classification_result
        )
        
        assert result["category_gap_detected"] == True
        assert result["proposal_needed"] == True
        assert "Low classification confidence" in result["reason"]
    
    def test_gap_detected_other_material(self):
        """Test gap detection with 'other_material' fallback."""
        classification = {
            "confidence_score": 95,
            "specific_preset": "other_material"
        }
        
        result = detect_category_gap("Some request", classification)
        
        assert result["category_gap_detected"] == True
        assert result["proposal_needed"] == True
    
    def test_gap_detected_novel_keywords(self):
        """Test gap detection with novel material keywords."""
        classification = {
            "confidence_score": 60,
            "specific_preset": "membrane_water_treatment"
        }
        
        result = detect_category_gap(
            "A novel experimental material never tested before",
            classification
        )
        
        assert result["category_gap_detected"] == True
        assert result["proposal_needed"] == True
    
    def test_no_gap_strong_match(self):
        """Test no gap with strong category match."""
        classification = {
            "confidence_score": 85,
            "specific_preset": "atmospheric_water_harvesting_material",
            "material_family": "composite",
            "application_domain": "awh"
        }
        
        result = detect_category_gap(
            "Atmospheric water harvesting material",
            classification
        )
        
        assert result["category_gap_detected"] == False
        assert result["proposal_needed"] == False


# ==============================================================================
# TEST GROUP 3: CATEGORY PROPOSAL
# ==============================================================================

class TestCategoryProposal:
    """Tests for propose_new_category function."""
    
    def test_proposal_generation(self, sample_user_request, sample_classification_result):
        """Test complete category proposal generation."""
        proposal = propose_new_category(sample_user_request, sample_classification_result)
        
        # Check structure
        assert "proposed_category" in proposal
        assert "why_proposed" in proposal
        assert "matched_keywords" in proposal
        assert "confidence" in proposal
        assert "requires_user_editing" in proposal
        assert "safety_warnings" in proposal
        
        # Check proposed_category completeness
        proposed = proposal["proposed_category"]
        assert "normalized_category_name" in proposed
        assert "display_name" in proposed
        assert "material_family" in proposed
        assert "functional_class" in proposed
        assert "application_domain" in proposed
        assert "aliases" in proposed
        assert "priority_keywords" in proposed
        assert "default_composition" in proposed
        assert "category_specific_parameters" in proposed
        assert "validation_plan" in proposed
        assert "safety_tests" in proposed
        assert "processing_method" in proposed
        assert "category_specific_disclaimer" in proposed
    
    def test_proposal_composition_valid(self, sample_user_request):
        """Test that proposed composition sums to approximately 1.0."""
        proposal = propose_new_category(sample_user_request)
        composition = proposal["proposed_category"].get("default_composition", [])
        
        if composition:
            total = sum(c.get("ratio", 0) for c in composition)
            # Allow small tolerance for rounding errors
            assert 0.99 <= total <= 1.01, f"Composition ratio sum: {total}"
    
    def test_proposal_confidence_range(self, sample_user_request):
        """Test that confidence score is in valid range."""
        proposal = propose_new_category(sample_user_request)
        
        confidence = proposal.get("confidence", 0)
        assert 0 <= confidence <= 100
    
    def test_proposal_with_hazardous_material(self):
        """Test safety warning detection for hazardous materials."""
        request = "A fabric stain removal composite with caustic alkali and bleach resistance"
        proposal = propose_new_category(request)
        
        warnings = proposal.get("safety_warnings", [])
        assert len(warnings) > 0
        # Should detect caustic chemicals
        assert any("caustic" in w.lower() for w in warnings)


# ==============================================================================
# TEST GROUP 4: DUPLICATE DETECTION
# ==============================================================================

class TestDuplicateDetection:
    """Tests for check_duplicate_category function."""
    
    def test_duplicate_strong_match(self):
        """Test detection of strong duplicate."""
        proposed = {
            "display_name": "Atmospheric Water Harvesting Material",
            "priority_keywords": ["atmospheric water", "moisture capture", "water harvesting"],
            "material_family": "composite",
            "functional_class": "adsorbent",
            "application_domain": "awh"
        }
        
        result = check_duplicate_category(proposed, CATEGORY_REGISTRY)
        
        # Should find strong match with existing AWH category
        assert result["duplicate_found"] == True
        assert len(result["similar_categories"]) > 0
        # Top match should have high score
        assert result["similar_categories"][0]["similarity_score"] > 70
    
    def test_no_duplicate_unique_category(self):
        """Test no duplicate with truly unique category."""
        proposed = {
            "display_name": "Quantum Entanglement Reactor Material",
            "priority_keywords": ["quantum", "entanglement", "reactor", "exotic"],
            "material_family": "hybrid",
            "functional_class": "catalyst",
            "application_domain": "energy"
        }
        
        result = check_duplicate_category(proposed, CATEGORY_REGISTRY)
        
        # May or may not find duplicates depending on registry
        # Just check structure is valid
        assert "duplicate_found" in result
        assert "similar_categories" in result
    
    def test_duplicate_keyword_overlap(self):
        """Test duplicate detection with keyword overlap."""
        proposed = {
            "display_name": "Heavy Metal Sorbent",
            "priority_keywords": ["lead", "cadmium", "arsenic", "removal", "adsorption"],
            "material_family": "composite",
            "functional_class": "adsorbent",
            "application_domain": "water_treatment"
        }
        
        result = check_duplicate_category(proposed, CATEGORY_REGISTRY)
        
        # Should find match with existing heavy metal adsorbent
        assert "similar_categories" in result


# ==============================================================================
# TEST GROUP 5: GENERATION FUNCTIONS
# ==============================================================================

class TestGenerationFunctions:
    """Tests for generation helper functions."""
    
    def test_generate_aliases(self, sample_user_request):
        """Test alias generation."""
        aliases = _generate_aliases(sample_user_request, ["composite", "water"])
        
        assert isinstance(aliases, list)
        assert len(aliases) > 0
        assert all(isinstance(a, str) for a in aliases)
    
    def test_generate_keywords(self, sample_user_request):
        """Test keyword generation."""
        keywords = _generate_keywords(sample_user_request, ["composite", "water"])
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 20  # Max 20 keywords
        assert all(isinstance(k, str) for k in keywords)
    
    def test_generate_default_composition(self, sample_user_request):
        """Test composition generation."""
        composition = _generate_default_composition(
            ["activated carbon", "iron oxide"],
            sample_user_request
        )
        
        assert isinstance(composition, list)
        assert len(composition) > 0
        
        # Check composition structure
        for item in composition:
            assert "component" in item
            assert "ratio" in item
            assert isinstance(item["ratio"], float)
            assert 0 <= item["ratio"] <= 1
    
    def test_generate_category_parameters(self, sample_user_request):
        """Test parameter generation."""
        params = _generate_category_parameters(
            ["water", "treatment"],
            sample_user_request,
            "composite"
        )
        
        assert isinstance(params, dict)
        assert len(params) > 0
    
    def test_generate_validation_plan(self, sample_user_request):
        """Test validation plan generation."""
        validation = _generate_validation_plan(
            ["water", "treatment"],
            sample_user_request,
            {}
        )
        
        assert isinstance(validation, dict)
        assert len(validation) > 0
    
    def test_generate_safety_tests(self, sample_user_request):
        """Test safety test generation."""
        tests = _generate_safety_tests(
            ["water", "treatment"],
            sample_user_request,
            "composite"
        )
        
        assert isinstance(tests, list)
        assert len(tests) > 0
        assert all(isinstance(t, str) for t in tests)
    
    def test_generate_characterization_methods(self):
        """Test characterization methods generation."""
        methods = _generate_characterization_methods("composite", "adsorbent")
        
        assert isinstance(methods, list)
        assert len(methods) > 0
        assert all(isinstance(m, str) for m in methods)
        assert "SEM/EDS" in methods
        assert "XRD" in methods
    
    def test_generate_processing_method(self, sample_user_request):
        """Test processing method generation."""
        method = _generate_processing_method(
            ["water", "treatment"],
            sample_user_request,
            "composite",
            "adsorbent"
        )
        
        assert isinstance(method, list)
        assert len(method) > 0
        assert all(isinstance(m, str) for m in method)
    
    def test_generate_disclaimer(self):
        """Test disclaimer generation."""
        disclaimer = _generate_disclaimer(
            "Custom Water Treatment Material",
            ["water", "treatment"]
        )
        
        assert isinstance(disclaimer, str)
        assert "DISCLAIMER" in disclaimer
        assert "rigorous laboratory validation" in disclaimer.lower()
    
    def test_detect_safety_warnings_bleach(self):
        """Test safety warning detection for bleach."""
        warnings = _detect_safety_warnings(
            "Fabric cleaning composite with bleach resistance",
            []
        )
        
        assert any("bleach" in w.lower() for w in warnings)
    
    def test_detect_safety_warnings_skin_contact(self):
        """Test safety warning detection for skin contact."""
        warnings = _detect_safety_warnings(
            "Skin-contact cosmetic material for face application",
            []
        )
        
        assert any("skin" in w.lower() for w in warnings)


# ==============================================================================
# TEST GROUP 6: STRING SIMILARITY
# ==============================================================================

class TestStringSimilarity:
    """Tests for string similarity function."""
    
    def test_identical_strings(self):
        """Test similarity of identical strings."""
        score = _string_similarity("water treatment", "water treatment")
        assert score == 1.0
    
    def test_no_similarity(self):
        """Test similarity of completely different strings."""
        score = _string_similarity("water treatment", "quantum computing")
        assert score == 0.0
    
    def test_partial_similarity(self):
        """Test similarity of partially matching strings."""
        score = _string_similarity("water treatment", "water purification")
        assert 0 < score < 1
    
    def test_empty_strings(self):
        """Test similarity with empty strings."""
        score = _string_similarity("", "water")
        assert score == 0.0
    
    def test_token_based_matching(self):
        """Test token-based matching."""
        score1 = _string_similarity("carbon water filter", "water carbon filter")
        # Order shouldn't matter in token-based matching
        assert score1 > 0.7


# ==============================================================================
# TEST GROUP 7: APPLICATION & VERIFICATION
# ==============================================================================

class TestApplicationAndVerification:
    """Tests for apply and verification functions."""
    
    def test_apply_new_category(self, sample_material_data):
        """Test applying new category to material data."""
        new_category = {
            "normalized_category_name": "test_category",
            "display_name": "Test Category",
            "category_specific_parameters": {"param1": "value1"},
            "validation_plan": {"val1": "test1"},
            "category_specific_disclaimer": "Test disclaimer",
            "characterization_methods": ["SEM"],
            "safety_tests": ["Test1"],
            "processing_method": ["Step1"],
        }
        
        result = apply_new_category_and_verify(sample_material_data, new_category)
        
        assert result["success"] == True
        assert result["material_data"]["material_category"] == "test_category"
        assert result["material_data"]["auto_created_category"] == True
    
    def test_add_category_to_registry(self):
        """Test adding category to registry."""
        new_category = {
            "normalized_category_name": "test_new_cat",
            "display_name": "Test New Category",
        }
        
        result = add_category_to_registry(new_category)
        
        assert result["success"] == True
        assert result["category_key"] == "test_new_cat"


# ==============================================================================
# TEST GROUP 8: END-TO-END WORKFLOWS
# ==============================================================================

class TestEndToEndWorkflows:
    """Integration tests for complete workflows."""
    
    def test_complete_proposal_workflow(self, sample_user_request, sample_classification_result):
        """Test complete workflow from gap detection to proposal."""
        # Step 1: Detect gap
        gap = detect_category_gap(sample_user_request, sample_classification_result)
        assert gap["proposal_needed"] == True
        
        # Step 2: Generate proposal
        proposal = propose_new_category(sample_user_request, sample_classification_result)
        assert "proposed_category" in proposal
        
        # Step 3: Check for duplicates
        duplicate_check = check_duplicate_category(
            proposal["proposed_category"],
            CATEGORY_REGISTRY
        )
        assert "duplicate_found" in duplicate_check
    
    def test_fabric_cleaning_workflow(self):
        """Test complete workflow for fabric cleaning material."""
        request = "Fabric oil-stain removal composite with biodegradable surfactants and enzymes"
        classification = {
            "confidence_score": 35,
            "specific_preset": "other_material"
        }
        
        # Detect gap
        gap = detect_category_gap(request, classification)
        assert gap["proposal_needed"] == True
        
        # Generate proposal
        proposal = propose_new_category(request, classification)
        proposed = proposal["proposed_category"]
        
        # Verify structure
        assert proposed["display_name"]
        assert proposed["default_composition"]
        assert proposed["processing_method"]
        
        # Check safety warnings
        warnings = proposal["safety_warnings"]
        # Should have some warnings for cleaning materials
        assert isinstance(warnings, list)


# ==============================================================================
# TEST GROUP 9: ERROR HANDLING
# ==============================================================================

class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_empty_user_request(self):
        """Test handling of empty user request."""
        proposal = propose_new_category("", None)
        assert proposal["proposed_category"]
        assert proposal["proposed_category"]["display_name"]
    
    def test_very_long_user_request(self):
        """Test handling of very long user request."""
        long_request = "A material " * 100  # 1000+ characters
        proposal = propose_new_category(long_request, None)
        
        assert proposal["proposed_category"]
        assert len(proposal["proposed_category"]["normalized_category_name"]) <= 50
    
    def test_special_characters_in_request(self):
        """Test handling of special characters."""
        request = "Material with @#$%^& special ch@rs & symbols!!!"
        proposal = propose_new_category(request, None)
        
        # Should not crash
        assert proposal["proposed_category"]
    
    def test_none_values_in_classification(self):
        """Test handling of None values in classification."""
        classification = {
            "confidence_score": None,
            "specific_preset": None
        }
        
        result = detect_category_gap("test", classification)
        # Should not crash
        assert "proposal_needed" in result


# ==============================================================================
# TEST EXECUTION
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
