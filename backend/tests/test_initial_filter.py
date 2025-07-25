import pytest
from src.services.initial_filter import light_filtering
from tests.test_helpers import create_test_clothing_item, create_test_weather_data

class TestInitialFilter:
    """Test the light filtering phase."""
    
    def test_light_filtering_basic(self):
        items = [
            create_test_clothing_item(id="1", name="Test Shirt", type="shirt", seasonal_score=0.8),
            create_test_clothing_item(id="2", name="Test Pants", type="pants", seasonal_score=0.6),
            create_test_clothing_item(id="3", name="Test Shoes", type="shoes", seasonal_score=0.3),
        ]
        context = {"weather": create_test_weather_data(temperature=70, condition="clear")}
        filtered = light_filtering(items, context)
        assert len(filtered) == 2
        assert filtered[0].id == "1"
        assert filtered[1].id == "2"
    
    def test_light_filtering_empty_input(self):
        items = []
        context = {"weather": create_test_weather_data(temperature=70, condition="clear")}
        filtered = light_filtering(items, context)
        assert len(filtered) == 0
    
    def test_light_filtering_all_low_scores(self):
        items = [
            create_test_clothing_item(id="1", name="Test Shirt", type="shirt", seasonal_score=0.2),
            create_test_clothing_item(id="2", name="Test Pants", type="pants", seasonal_score=0.1),
        ]
        context = {"weather": create_test_weather_data(temperature=70, condition="clear")}
        filtered = light_filtering(items, context)
        assert len(filtered) == 0

if __name__ == "__main__":
    pytest.main([__file__]) 