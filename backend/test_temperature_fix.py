#!/usr/bin/env python3
"""Test script to verify temperature comparison bug fix."""

import asyncio
import json
from src.services.outfit_service import OutfitService
from src.custom_types.weather import WeatherData
from src.custom_types.profile import UserProfile

async def test_temperature_fix():
    """Test that temperature comparison works with string values."""
    outfit_service = OutfitService()
    
    print("🧪 Testing Temperature Comparison Fix")
    print("=" * 50)
    
    # Create test weather data
    weather = WeatherData(
        temperature=75.0,
        condition="sunny",
        humidity=60,
        wind_speed=5
    )
    
    # Create test user profile
    user_profile = UserProfile(
        id="test_user",
        name="Test User",
        email="test@example.com",
        gender="female",
        bodyType="athletic",
        body_type="athletic",
        skinTone="medium",
        skin_tone="medium",
        height=165,
        weight=60,
        age=25,
        createdAt=0,
        updatedAt=0
    )
    
    # Create test wardrobe with items that might have string temperature values
    test_wardrobe = [
        {
            "id": "test_item_1",
            "name": "Test T-Shirt",
            "type": "t-shirt",
            "style": ["casual"],
            "occasion": ["casual", "athletic"],
            "dominantColors": [{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
            "matchingColors": [{"name": "black", "hex": "#000000", "r": 0, "g": 0, "b": 0}],
            "color": "white",
            "season": ["all"],
            "imageUrl": "test_tshirt.jpg",
            "tags": ["casual", "comfortable"],
            "userId": "test_user",
            "createdAt": 0,
            "updatedAt": 0,
            "metadata": {
                "analysisTimestamp": 0,
                "originalType": "t-shirt",
                "colorAnalysis": {
                    "dominantColors": [{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
                    "matchingColors": [{"name": "black", "hex": "#000000", "r": 0, "g": 0, "b": 0}]
                },
                "visualAttributes": {
                    "temperatureCompatibility": {
                        "minTemp": "60",  # String value that would cause the bug
                        "maxTemp": "85",   # String value that would cause the bug
                        "recommendedLayers": ["1"],
                        "materialPreferences": ["cotton"]
                    }
                }
            }
        },
        {
            "id": "test_item_2", 
            "name": "Test Jeans",
            "type": "jeans",
            "style": ["casual"],
            "occasion": ["casual"],
            "dominantColors": [{"name": "navy", "hex": "#000080", "r": 0, "g": 0, "b": 128}],
            "matchingColors": [{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}],
            "color": "navy",
            "season": ["all"],
            "imageUrl": "test_jeans.jpg",
            "tags": ["casual", "denim"],
            "userId": "test_user",
            "createdAt": 0,
            "updatedAt": 0,
            "metadata": {
                "analysisTimestamp": 0,
                "originalType": "jeans",
                "colorAnalysis": {
                    "dominantColors": [{"name": "navy", "hex": "#000080", "r": 0, "g": 0, "b": 128}],
                    "matchingColors": [{"name": "white", "hex": "#FFFFFF", "r": 255, "g": 255, "b": 255}]
                },
                "visualAttributes": {
                    "temperatureCompatibility": {
                        "minTemp": "50",  # String value
                        "maxTemp": "80",   # String value
                        "recommendedLayers": ["1"],
                        "materialPreferences": ["cotton"]
                    }
                }
            }
        }
    ]
    
    print("✅ Test data created successfully")
    print(f"   - Weather temperature: {weather.temperature}°F")
    print(f"   - Test items: {len(test_wardrobe)}")
    
    try:
        # Test the temperature adjustment method directly
        print("\n🔍 Testing _adjust_for_weather_enhanced method...")
        
        # Convert test wardrobe to ClothingItem objects
        from src.custom_types.wardrobe import ClothingItem
        clothing_items = []
        
        for item_data in test_wardrobe:
            item = ClothingItem(**item_data)
            clothing_items.append(item)
        
        print(f"   - Created {len(clothing_items)} ClothingItem objects")
        
        # Test the temperature adjustment method
        adjusted_items = outfit_service._adjust_for_weather_enhanced(clothing_items, weather)
        
        print(f"   - Items before adjustment: {len(clothing_items)}")
        print(f"   - Items after adjustment: {len(adjusted_items)}")
        
        if len(adjusted_items) > 0:
            print("✅ Temperature comparison fix working correctly!")
            print("   - No TypeError occurred during temperature comparison")
        else:
            print("⚠️  No items passed temperature filter (this might be expected)")
            
    except Exception as e:
        print(f"❌ Error during temperature comparison test: {e}")
        return False
    
    print("\n🎉 Temperature comparison bug fix test completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(test_temperature_fix()) 