#!/usr/bin/env python3
"""
Test fallback integration in the pipeline
"""

import asyncio
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.outfit_generation_pipeline_service import OutfitGenerationPipelineService
from src.custom_types.wardrobe import ClothingItem, Color, ClothingType
from src.custom_types.weather import WeatherData
from src.custom_types.profile import UserProfile

async def test_fallback_integration():
    """Test that fallback service is properly integrated into the pipeline."""
    
    # Create test data with all required fields
    current_time = int(time.time() * 1000)  # Current time in milliseconds
    
    test_item = ClothingItem(
        id="test-item-1",
        name="Test Shirt",
        type=ClothingType.SHIRT,
        color="blue",
        season=["spring", "summer"],
        imageUrl="test.jpg",
        tags=["casual", "comfortable"],
        style=["casual"],
        userId="test-user",
        dominantColors=[Color(name="blue", hex="#0000FF", rgb=[0, 0, 255])],
        matchingColors=[Color(name="blue", hex="#0000FF", rgb=[0, 0, 255])],
        occasion=["casual"],
        brand="Test Brand",
        createdAt=current_time,
        updatedAt=current_time
    )
    
    test_wardrobe = [test_item] * 5  # Create 5 test items
    
    weather = WeatherData(
        temperature=75.0,
        condition="sunny",
        humidity=50
    )
    
    user_profile = UserProfile(
        id="test-user",
        name="Test User",
        email="test@example.com",
        bodyType="athletic",
        skinTone="medium",
        stylePreferences=["casual"],
        createdAt=current_time,
        updatedAt=current_time
    )
    
    # Initialize pipeline service
    pipeline = OutfitGenerationPipelineService()
    
    print("🔄 Testing fallback integration...")
    
    try:
        # Test the pipeline with insufficient items (should trigger fallback)
        result = await pipeline.generate_outfit_refined_pipeline(
            occasion="formal",  # Formal requires more items
            weather=weather,
            wardrobe=test_wardrobe,
            user_profile=user_profile,
            style="casual",
            mood="neutral"
        )
        
        print(f"✅ Pipeline result: {result.get('success', False)}")
        print(f"📦 Items returned: {len(result.get('items', []))}")
        
        if result.get('success'):
            print("✅ Fallback integration test passed!")
            return True
        else:
            print(f"❌ Pipeline failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_fallback_integration()) 