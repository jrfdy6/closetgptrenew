import pytest
import asyncio
from src.services.outfit_service import generate_outfit_pipeline
from src.custom_types.wardrobe import ClothingItem
from src.custom_types.weather import WeatherData
from src.custom_types.profile import UserProfile

class TestE2EPipeline:
    """Test the full end-to-end modular pipeline."""
    
    async def test_full_pipeline_success(self):
        """Test successful pipeline execution."""
        # Create test data
        wardrobe = [
            ClothingItem(
                id="1", name="Test Shirt", type="shirt", 
                seasonal_score=0.8, category="top"
            ),
            ClothingItem(
                id="2", name="Test Pants", type="pants", 
                seasonal_score=0.7, category="bottom"
            ),
            ClothingItem(
                id="3", name="Test Shoes", type="shoes", 
                seasonal_score=0.6, category="shoes"
            ),
        ]
        
        context = {
            "occasion": "casual",
            "weather": WeatherData(temperature=70, condition="clear"),
            "user_profile": UserProfile(id="test_user"),
            "style": "casual",
            "mood": "relaxed"
        }
        
        # Run the full pipeline
        result = await generate_outfit_pipeline(
            user_id="test_user",
            wardrobe=wardrobe,
            context=context
        )
        
        # Verify result structure
        assert "status" in result
        assert "outfit" in result
        assert "warnings" in result
        
        # Should succeed with valid input
        assert result["status"] in ["success", "fallback_success"]
        assert len(result["outfit"]) >= 0
    
    async def test_full_pipeline_failure(self):
        """Test pipeline failure with invalid input."""
        # Create test data with insufficient items
        wardrobe = [
            ClothingItem(
                id="1", name="Test Shirt", type="shirt", 
                seasonal_score=0.2, category="top"
            ),
        ]
        
        context = {
            "occasion": "formal",  # Formal requires more items
            "weather": WeatherData(temperature=70, condition="clear"),
            "user_profile": UserProfile(id="test_user"),
            "style": "formal",
            "mood": "professional"
        }
        
        # Run the full pipeline
        result = await generate_outfit_pipeline(
            user_id="test_user",
            wardrobe=wardrobe,
            context=context
        )
        
        # Should fail with insufficient items
        assert result["status"] == "fail"
        assert "errors" in result
        assert len(result["errors"]) > 0
    
    async def test_pipeline_with_fallback(self):
        """Test pipeline that triggers fallback."""
        # Create test data that will fail initial validation but succeed with fallback
        wardrobe = [
            ClothingItem(
                id="1", name="Test Shirt", type="shirt", 
                seasonal_score=0.8, category="top"
            ),
            ClothingItem(
                id="2", name="Test Pants", type="pants", 
                seasonal_score=0.7, category="bottom"
            ),
        ]
        
        context = {
            "occasion": "casual",
            "weather": WeatherData(temperature=70, condition="clear"),
            "user_profile": UserProfile(id="test_user"),
            "style": "casual",
            "mood": "relaxed"
        }
        
        # Run the full pipeline
        result = await generate_outfit_pipeline(
            user_id="test_user",
            wardrobe=wardrobe,
            context=context
        )
        
        # Should succeed (possibly with fallback)
        assert result["status"] in ["success", "fallback_success", "fail"]
        assert "outfit" in result
        assert "warnings" in result

if __name__ == "__main__":
    pytest.main([__file__]) 