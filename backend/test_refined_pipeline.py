#!/usr/bin/env python3
"""
Test script for the refined outfit generation pipeline.
Tests various scenarios to ensure the pipeline works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.outfit_service import OutfitService
from src.types.wardrobe import ClothingItem, ClothingType, Color
from src.types.profile import UserProfile
from src.types.weather import WeatherData
import time

def create_test_wardrobe():
    """Create a test wardrobe with various item types."""
    wardrobe = []
    
    # Athletic items
    wardrobe.append(ClothingItem(
        id="athletic_shirt_1",
        name="Nike Athletic T-Shirt",
        type=ClothingType.SHIRT,
        color="black",
        season=["summer", "spring"],
        tags=["athletic"],
        dominantColors=[Color(name="black", hex="#000000")],
        matchingColors=[Color(name="white", hex="#FFFFFF")],
        style=["athletic", "sport"],
        occasion=["athletic", "gym", "workout"],
        imageUrl="test_url",
        userId="test_user",
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    ))
    
    wardrobe.append(ClothingItem(
        id="athletic_shorts_1",
        name="Adidas Athletic Shorts",
        type=ClothingType.SHORTS,
        color="gray",
        season=["summer", "spring"],
        tags=["athletic"],
        dominantColors=[Color(name="gray", hex="#808080")],
        matchingColors=[Color(name="black", hex="#000000")],
        style=["athletic", "sport"],
        occasion=["athletic", "gym", "workout"],
        imageUrl="test_url",
        userId="test_user",
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    ))
    
    wardrobe.append(ClothingItem(
        id="athletic_shoes_1",
        name="Nike Running Shoes",
        type=ClothingType.SNEAKERS,
        color="white",
        season=["summer", "spring"],
        tags=["athletic"],
        dominantColors=[Color(name="white", hex="#FFFFFF")],
        matchingColors=[Color(name="black", hex="#000000")],
        style=["athletic", "sport"],
        occasion=["athletic", "gym", "workout"],
        imageUrl="test_url",
        userId="test_user",
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    ))
    
    # Business items
    wardrobe.append(ClothingItem(
        id="dress_shirt_1",
        name="White Dress Shirt",
        type=ClothingType.SHIRT,
        color="white",
        season=["spring", "fall"],
        tags=["business"],
        dominantColors=[Color(name="white", hex="#FFFFFF")],
        matchingColors=[Color(name="black", hex="#000000")],
        style=["business", "formal"],
        occasion=["work", "business", "formal"],
        imageUrl="test_url",
        userId="test_user",
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    ))
    
    wardrobe.append(ClothingItem(
        id="dress_pants_1",
        name="Black Dress Pants",
        type=ClothingType.PANTS,
        color="black",
        season=["spring", "fall", "winter"],
        tags=["business"],
        dominantColors=[Color(name="black", hex="#000000")],
        matchingColors=[Color(name="white", hex="#FFFFFF")],
        style=["business", "formal"],
        occasion=["work", "business", "formal"],
        imageUrl="test_url",
        userId="test_user",
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    ))
    
    wardrobe.append(ClothingItem(
        id="dress_shoes_1",
        name="Black Dress Shoes",
        type=ClothingType.DRESS_SHOES,
        color="black",
        season=["spring", "fall", "winter"],
        tags=["business"],
        dominantColors=[Color(name="black", hex="#000000")],
        matchingColors=[Color(name="white", hex="#FFFFFF")],
        style=["business", "formal"],
        occasion=["work", "business", "formal"],
        imageUrl="test_url",
        userId="test_user",
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    ))
    
    # Casual items
    wardrobe.append(ClothingItem(
        id="casual_tshirt_1",
        name="Blue Casual T-Shirt",
        type=ClothingType.SHIRT,
        color="blue",
        season=["summer", "spring"],
        tags=["casual"],
        dominantColors=[Color(name="blue", hex="#0000FF")],
        matchingColors=[Color(name="white", hex="#FFFFFF")],
        style=["casual", "everyday"],
        occasion=["casual", "everyday"],
        imageUrl="test_url",
        userId="test_user",
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    ))
    
    wardrobe.append(ClothingItem(
        id="jeans_1",
        name="Blue Jeans",
        type=ClothingType.PANTS,
        color="blue",
        season=["fall", "winter", "spring"],
        tags=["casual", "jeans"],
        dominantColors=[Color(name="blue", hex="#0000FF")],
        matchingColors=[Color(name="white", hex="#FFFFFF")],
        style=["casual", "everyday"],
        occasion=["casual", "everyday"],
        imageUrl="test_url",
        userId="test_user",
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    ))
    
    # Inappropriate items for testing filtering
    wardrobe.append(ClothingItem(
        id="sweater_hot",
        name="Wool Sweater",
        type=ClothingType.SWEATER,
        color="brown",
        season=["winter", "fall"],
        tags=["winter"],
        dominantColors=[Color(name="brown", hex="#8B4513")],
        matchingColors=[Color(name="white", hex="#FFFFFF")],
        style=["winter", "warm"],
        occasion=["winter", "cold"],
        imageUrl="test_url",
        userId="test_user",
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    ))
    
    return wardrobe

def create_test_user_profile():
    """Create a test user profile."""
    return UserProfile(
        id="test_user",
        name="Test User",
        email="test@example.com",
        bodyType="athletic",
        skinTone="medium",
        stylePreferences=["casual", "athletic"],
        createdAt=int(time.time()),
        updatedAt=int(time.time())
    )

def test_athletic_occasion():
    """Test athletic occasion with refined pipeline."""
    print("\n🧪 Testing Athletic Occasion")
    print("=" * 50)
    
    service = OutfitService()
    wardrobe = create_test_wardrobe()
    user_profile = create_test_user_profile()
    weather = WeatherData(temperature=75, condition="sunny", location="test", humidity=50)
    
    result = service._generate_outfit_refined_pipeline(
        occasion="Athletic / Gym",
        weather=weather,
        wardrobe=wardrobe,
        user_profile=user_profile,
        style="athletic"
    )
    
    print(f"Pipeline success: {result['success']}")
    if result['success']:
        items = result['items']
        print(f"Selected {len(items)} items:")
        for item in items:
            print(f"  - {item.name} ({item.type})")
        
        # Verify no inappropriate items
        inappropriate_items = [item for item in items if "dress" in item.name.lower() or "formal" in item.style]
        if inappropriate_items:
            print(f"❌ ERROR: Found inappropriate items: {[item.name for item in inappropriate_items]}")
        else:
            print("✅ No inappropriate items found")
    else:
        print(f"Pipeline failed: {result.get('message', 'Unknown error')}")

def test_business_occasion():
    """Test business occasion with refined pipeline."""
    print("\n🧪 Testing Business Occasion")
    print("=" * 50)
    
    service = OutfitService()
    wardrobe = create_test_wardrobe()
    user_profile = create_test_user_profile()
    weather = WeatherData(temperature=70, condition="cloudy", location="test", humidity=50)
    
    result = service._generate_outfit_refined_pipeline(
        occasion="Work",
        weather=weather,
        wardrobe=wardrobe,
        user_profile=user_profile,
        style="business"
    )
    
    print(f"Pipeline success: {result['success']}")
    if result['success']:
        items = result['items']
        print(f"Selected {len(items)} items:")
        for item in items:
            print(f"  - {item.name} ({item.type})")
        
        # Verify business-appropriate items
        business_items = [item for item in items if "dress" in item.name.lower() or "business" in item.style]
        if business_items:
            print(f"✅ Found business items: {[item.name for item in business_items]}")
        else:
            print("⚠️ No business-specific items found")
    else:
        print(f"Pipeline failed: {result.get('message', 'Unknown error')}")

def test_hot_weather_filtering():
    """Test hot weather filtering."""
    print("\n🧪 Testing Hot Weather Filtering")
    print("=" * 50)
    
    service = OutfitService()
    wardrobe = create_test_wardrobe()
    user_profile = create_test_user_profile()
    weather = WeatherData(temperature=90, condition="sunny", location="test", humidity=50)
    
    result = service._generate_outfit_refined_pipeline(
        occasion="Casual",
        weather=weather,
        wardrobe=wardrobe,
        user_profile=user_profile,
        style="casual"
    )
    
    print(f"Pipeline success: {result['success']}")
    if result['success']:
        items = result['items']
        print(f"Selected {len(items)} items:")
        for item in items:
            print(f"  - {item.name} ({item.type})")
        
        # Verify no hot weather inappropriate items
        hot_inappropriate = [item for item in items if "sweater" in item.name.lower() or "wool" in item.name.lower()]
        if hot_inappropriate:
            print(f"❌ ERROR: Found hot weather inappropriate items: {[item.name for item in hot_inappropriate]}")
        else:
            print("✅ No hot weather inappropriate items found")
    else:
        print(f"Pipeline failed: {result.get('message', 'Unknown error')}")

def test_insufficient_items():
    """Test handling of insufficient items."""
    print("\n🧪 Testing Insufficient Items")
    print("=" * 50)
    
    service = OutfitService()
    # Create minimal wardrobe with only 1 item
    minimal_wardrobe = [
        ClothingItem(
            id="single_item",
            name="Single T-Shirt",
            type=ClothingType.SHIRT,
            color="white",
            season=["summer", "spring"],
            tags=["casual"],
            dominantColors=[Color(name="white", hex="#FFFFFF")],
            matchingColors=[Color(name="black", hex="#000000")],
            style=["casual"],
            occasion=["casual"],
            imageUrl="test_url",
            userId="test_user",
            createdAt=int(time.time()),
            updatedAt=int(time.time())
        )
    ]
    user_profile = create_test_user_profile()
    weather = WeatherData(temperature=70, condition="sunny", location="test", humidity=50)
    
    result = service._generate_outfit_refined_pipeline(
        occasion="Casual",
        weather=weather,
        wardrobe=minimal_wardrobe,
        user_profile=user_profile,
        style="casual"
    )
    
    print(f"Pipeline success: {result['success']}")
    if not result['success']:
        print(f"Expected failure: {result.get('message', 'Unknown error')}")
        print(f"Missing items: {result.get('missing_items', [])}")
        print("✅ Correctly handled insufficient items")
    else:
        print("❌ ERROR: Should have failed with insufficient items")

def main():
    """Run all tests."""
    print("🎯 Testing Refined Outfit Generation Pipeline")
    print("=" * 60)
    
    test_athletic_occasion()
    test_business_occasion()
    test_hot_weather_filtering()
    test_insufficient_items()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 