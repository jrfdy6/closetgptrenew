#!/usr/bin/env python3
"""
Test script to verify occasion and style mappings are working correctly
with the actual app constants.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.outfit_service import OutfitService
from src.types.wardrobe import ClothingItem
from src.types.weather import WeatherData
from src.types.profile import UserProfile
from src.types.outfit_rules import OccasionType

def test_occasion_mappings():
    """Test that occasion mappings work with actual app occasions."""
    service = OutfitService()
    
    # Test occasions from the app
    test_occasions = [
        "Casual",
        "Business Casual", 
        "Formal",
        "Gala",
        "Party",
        "Date Night",
        "Work",
        "Interview",
        "Brunch",
        "Wedding Guest",
        "Cocktail",
        "Travel",
        "Airport",
        "Loungewear",
        "Beach",
        "Vacation",
        "Festival",
        "Rainy Day",
        "Snow Day",
        "Hot Weather",
        "Cold Weather",
        "Night Out",
        "Athletic / Gym",
        "School",
        "Holiday",
        "Concert",
        "Errands",
        "Chilly Evening",
        "Museum / Gallery",
        "First Date",
        "Business Formal",
        "Funeral / Memorial",
        "Fashion Event",
        "Outdoor Gathering"
    ]
    
    print("🧪 Testing occasion appropriateness calculation...")
    
    # Create a mock item for testing
    mock_item = ClothingItem(
        id="test-item-1",
        name="Test Shirt",
        type="shirt",
        color="blue",
        season=["spring", "summer"],
        imageUrl="test.jpg",
        userId="test-user",
        dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
        matchingColors=[{"name": "navy", "hex": "#000080", "rgb": [0, 0, 128]}],
        occasion=["casual", "business casual"],
        style=["classic", "comfortable"],
        tags=[],
        createdAt=1234567890,
        updatedAt=1234567890
    )
    
    mock_weather = WeatherData(
        temperature=70.0,
        condition="sunny",
        location="New York",
        humidity=50.0,
        wind_speed=10.0,
        precipitation=0.0
    )
    
    mock_user = UserProfile(
        id="test-user",
        name="Test User",
        email="test@example.com",
        bodyType="average",
        skinTone="medium",
        stylePreferences=["classic", "comfortable"],
        measurements={"height": 170, "weight": 70, "bodyType": "average"},
        createdAt=1234567890,
        updatedAt=1234567890
    )
    
    results = {}
    
    for occasion in test_occasions:
        try:
            # Test the occasion appropriateness calculation
            appropriateness = service._calculate_occasion_appropriateness_enhanced([mock_item], occasion)
            results[occasion] = appropriateness
            print(f"✅ {occasion}: {appropriateness:.3f}")
        except Exception as e:
            print(f"❌ {occasion}: Error - {e}")
            results[occasion] = None
    
    # Check results
    successful_tests = sum(1 for score in results.values() if score is not None)
    total_tests = len(test_occasions)
    
    print(f"\n📊 Results Summary:")
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    print(f"❌ Failed tests: {total_tests - successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("🎉 All occasion mappings working correctly!")
        return True
    else:
        print("⚠️  Some occasion mappings need attention")
        return False

def test_style_compatibility():
    """Test that style compatibility matrix works with actual app styles."""
    service = OutfitService()
    
    # Test styles from the app
    test_styles = [
        "Dark Academia",
        "Old Money", 
        "Streetwear",
        "Y2K",
        "Minimalist",
        "Boho",
        "Preppy",
        "Grunge",
        "Classic",
        "Techwear",
        "Androgynous",
        "Coastal Chic",
        "Business Casual",
        "Avant-Garde",
        "Cottagecore",
        "Edgy",
        "Athleisure",
        "Casual Cool",
        "Romantic",
        "Artsy"
    ]
    
    print("\n🧪 Testing style compatibility matrix...")
    
    results = {}
    
    for style in test_styles:
        try:
            # Test the style compatibility matrix
            matrix = service._get_style_compatibility_matrix(style)
            approved_count = len(matrix.get("approved_items", []))
            banned_count = len(matrix.get("banned_items", []))
            results[style] = {"approved": approved_count, "banned": banned_count}
            print(f"✅ {style}: {approved_count} approved, {banned_count} banned")
        except Exception as e:
            print(f"❌ {style}: Error - {e}")
            results[style] = None
    
    # Check results
    successful_tests = sum(1 for result in results.values() if result is not None)
    total_tests = len(test_styles)
    
    print(f"\n📊 Style Compatibility Results:")
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    print(f"❌ Failed tests: {total_tests - successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("🎉 All style compatibility mappings working correctly!")
        return True
    else:
        print("⚠️  Some style compatibility mappings need attention")
        return False

if __name__ == "__main__":
    print("🚀 Testing Occasion and Style Mappings")
    print("=" * 50)
    
    occasion_success = test_occasion_mappings()
    style_success = test_style_compatibility()
    
    print("\n" + "=" * 50)
    print("🎯 Final Results:")
    print(f"Occasion Mappings: {'✅ PASS' if occasion_success else '❌ FAIL'}")
    print(f"Style Compatibility: {'✅ PASS' if style_success else '❌ FAIL'}")
    
    if occasion_success and style_success:
        print("\n🎉 All tests passed! Mappings are working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the mappings.")
        sys.exit(1) 