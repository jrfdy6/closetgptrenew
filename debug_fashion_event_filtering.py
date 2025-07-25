#!/usr/bin/env python3
"""
Debug script to test filtering logic for Fashion Event with Business Casual style
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.outfit_service import OutfitService
from types.weather import WeatherData
from types.user_profile import UserProfile
from types.clothing_item import ClothingItem, ClothingType

def create_test_wardrobe():
    """Create a test wardrobe with various items including bottoms."""
    return [
        # Tops
        ClothingItem(
            id="test-shirt-1",
            name="A slim, long, solid, smooth dress shirt",
            type=ClothingType.SHIRT,
            color="white",
            style=["business casual", "formal"],
            occasion=["fashion event", "business", "formal"],
            season=["spring", "summer"],
            imageUrl="https://example.com/shirt.jpg",
            dominantColors=[{"r": 255, "g": 255, "b": 255}]
        ),
        
        # Bottoms - These should be available for Fashion Event
        ClothingItem(
            id="test-pants-1",
            name="Slim Fit Chinos",
            type=ClothingType.PANTS,
            color="navy",
            style=["business casual", "smart casual"],
            occasion=["fashion event", "business", "casual"],
            season=["spring", "summer"],
            imageUrl="https://example.com/pants.jpg",
            dominantColors=[{"r": 30, "g": 30, "b": 60}]
        ),
        ClothingItem(
            id="test-pants-2",
            name="Tailored Trousers",
            type=ClothingType.PANTS,
            color="black",
            style=["business casual", "formal"],
            occasion=["fashion event", "business", "formal"],
            season=["all"],
            imageUrl="https://example.com/trousers.jpg",
            dominantColors=[{"r": 0, "g": 0, "b": 0}]
        ),
        ClothingItem(
            id="test-jeans-1",
            name="Dark Wash Jeans",
            type=ClothingType.JEANS,
            color="blue",
            style=["business casual", "casual"],
            occasion=["fashion event", "casual"],
            season=["all"],
            imageUrl="https://example.com/jeans.jpg",
            dominantColors=[{"r": 0, "g": 0, "b": 128}]
        ),
        
        # Shoes
        ClothingItem(
            id="test-shoes-1",
            name="A solid, smooth toe shoes by SUICOKE",
            type=ClothingType.SHOES,
            color="black",
            style=["casual"],
            occasion=["casual"],
            season=["all"],
            imageUrl="https://example.com/shoes.jpg",
            dominantColors=[{"r": 0, "g": 0, "b": 0}]
        ),
        ClothingItem(
            id="test-shoes-2",
            name="Leather Oxfords",
            type=ClothingType.DRESS_SHOES,
            color="brown",
            style=["business casual", "formal"],
            occasion=["fashion event", "business", "formal"],
            season=["all"],
            imageUrl="https://example.com/oxfords.jpg",
            dominantColors=[{"r": 139, "g": 69, "b": 19}]
        ),
        
        # Accessories
        ClothingItem(
            id="test-belt-1",
            name="A solid, smooth belt",
            type=ClothingType.BELT,
            color="brown",
            style=["business casual", "formal"],
            occasion=["fashion event", "business", "formal"],
            season=["all"],
            imageUrl="https://example.com/belt.jpg",
            dominantColors=[{"r": 139, "g": 69, "b": 19}]
        )
    ]

def debug_filtering():
    """Debug the filtering logic step by step."""
    print("🔍 Debugging Fashion Event + Business Casual Filtering")
    print("=" * 60)
    
    # Create test data
    wardrobe = create_test_wardrobe()
    weather = WeatherData(temperature=83.8, condition="sunny", humidity=60)
    user_profile = UserProfile(
        id="test-user",
        name="Test User",
        email="test@example.com",
        bodyType="athletic",
        skinTone="medium",
        height=175,
        weight=70,
        preferences={
            "style": ["business casual"],
            "colors": ["blue", "white", "black"],
            "occasions": ["fashion event"]
        },
        stylePreferences=["business casual"],
        fitPreference="fitted",
        createdAt=1234567890,
        updatedAt=1234567890
    )
    
    outfit_service = OutfitService()
    
    print(f"📋 Initial wardrobe: {len(wardrobe)} items")
    for item in wardrobe:
        print(f"   - {item.name} ({item.type}) - Style: {item.style}, Occasion: {item.occasion}")
    
    print(f"\n🎯 Target: Fashion Event + Business Casual + 83.8°F")
    
    # Test weather filtering
    print(f"\n🌡️  Testing weather filtering...")
    weather_filtered = outfit_service._filter_by_weather_strict(wardrobe, weather)
    print(f"After weather filtering: {len(weather_filtered)} items")
    for item in weather_filtered:
        print(f"   - {item.name} ({item.type})")
    
    # Test occasion filtering
    print(f"\n🎉 Testing occasion filtering...")
    occasion_filtered = outfit_service._filter_by_occasion_strict(weather_filtered, "Fashion Event")
    print(f"After occasion filtering: {len(occasion_filtered)} items")
    for item in occasion_filtered:
        print(f"   - {item.name} ({item.type})")
    
    # Test style filtering
    print(f"\n👔 Testing style filtering...")
    style_matrix = outfit_service._get_style_compatibility_matrix("Business Casual")
    style_filtered = outfit_service._filter_by_style_strict(occasion_filtered, "Business Casual", style_matrix)
    print(f"After style filtering: {len(style_filtered)} items")
    for item in style_filtered:
        print(f"   - {item.name} ({item.type})")
    
    # Test personal preferences filtering
    print(f"\n👤 Testing personal preferences filtering...")
    pref_filtered = outfit_service._filter_by_personal_preferences(style_filtered, user_profile)
    print(f"After personal preferences filtering: {len(pref_filtered)} items")
    for item in pref_filtered:
        print(f"   - {item.name} ({item.type})")
    
    # Check what categories we have
    print(f"\n📊 Category breakdown:")
    categories = {'top': [], 'bottom': [], 'shoes': [], 'accessory': []}
    for item in pref_filtered:
        item_type = item.type.lower()
        if 'shirt' in item_type or 'blouse' in item_type:
            categories['top'].append(item)
        elif 'pants' in item_type or 'jeans' in item_type or 'shorts' in item_type or 'skirt' in item_type:
            categories['bottom'].append(item)
        elif 'shoes' in item_type or 'sneakers' in item_type or 'boots' in item_type:
            categories['shoes'].append(item)
        elif 'belt' in item_type or 'watch' in item_type or 'necklace' in item_type:
            categories['accessory'].append(item)
    
    for category, items in categories.items():
        print(f"   {category.capitalize()}: {len(items)} items")
        for item in items:
            print(f"     - {item.name}")
    
    # Test the full pipeline
    print(f"\n🚀 Testing full outfit generation pipeline...")
    result = outfit_service._generate_outfit_refined_pipeline(
        occasion="Fashion Event",
        weather=weather,
        wardrobe=wardrobe,
        user_profile=user_profile,
        style="Business Casual",
        mood="energetic"
    )
    
    if result.get("success"):
        selected_items = result["items"]
        print(f"✅ Generated outfit with {len(selected_items)} items:")
        for item in selected_items:
            print(f"   - {item.name} ({item.type})")
    else:
        print(f"❌ Failed to generate outfit: {result.get('message')}")

if __name__ == "__main__":
    debug_filtering() 