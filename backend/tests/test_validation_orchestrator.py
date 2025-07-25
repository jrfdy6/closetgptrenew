import pytest
from src.services.validators.individual_rules import (
    has_required_categories, has_min_items, 
    is_occasion_appropriate, meets_layer_count
)
from tests.test_helpers import create_test_clothing_item

class TestValidationOrchestrator:
    """Test the validation orchestrator and individual rules."""
    
    def test_has_required_categories(self):
        items = [
            create_test_clothing_item(id="1", type="shirt", name="Test Shirt"),
            create_test_clothing_item(id="2", type="pants", name="Test Pants"),
            create_test_clothing_item(id="3", type="shoes", name="Test Shoes"),
        ]
        assert has_required_categories(items) == True
    
    def test_has_required_categories_missing(self):
        items = [
            create_test_clothing_item(id="1", type="shirt", name="Test Shirt"),
            create_test_clothing_item(id="2", type="pants", name="Test Pants"),
        ]
        assert has_required_categories(items) == False
    
    def test_has_min_items(self):
        items = [
            create_test_clothing_item(id="1", type="shirt", name="Test Shirt"),
            create_test_clothing_item(id="2", type="pants", name="Test Pants"),
            create_test_clothing_item(id="3", type="shoes", name="Test Shoes"),
        ]
        assert has_min_items(items, min_items=3) == True
        assert has_min_items(items, min_items=4) == False
    
    def test_is_occasion_appropriate(self):
        items = [
            create_test_clothing_item(id="1", type="shirt", name="Test Shirt"),
            create_test_clothing_item(id="2", type="pants", name="Test Pants"),
        ]
        context = {"occasion": "casual"}
        assert is_occasion_appropriate(items, context) == True
    
    def test_meets_layer_count(self):
        items = [
            create_test_clothing_item(id="1", type="shirt", name="Test Shirt"),
            create_test_clothing_item(id="2", type="pants", name="Test Pants"),
        ]
        context = {"layers": 2}
        assert meets_layer_count(items, context) == True

if __name__ == "__main__":
    pytest.main([__file__]) 