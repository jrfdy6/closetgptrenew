#!/usr/bin/env python3
"""
Working Outfit Generation Test Script

This script tests the outfit generation function to identify issues with user profile setup.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_path)

def test_imports():
    """Test if we can import the required modules"""
    print("🔍 Testing imports...")
    
    try:
        # Import from the types package correctly
        import types
        from types import WeatherData, UserProfile, ClothingItem, ClothingType, Season, StyleTag
        print("✅ Types imported successfully")
        
        # Test service import
        from services.outfit_service import OutfitService
        print("✅ OutfitService imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_test_data():
    """Create test data for outfit generation"""
    print("\n🔧 Creating test data...")
    
    try:
        from types import WeatherData, UserProfile, ClothingItem, ClothingType, Season, StyleTag
        
        # Create test weather
        weather = WeatherData(
            temperature=75.0,
            condition="sunny",
            location="test-location",
            humidity=50.0,
            wind_speed=5.0,
            precipitation=0.0
        )
        print("✅ Weather data created")
        
        # Create test wardrobe
        wardrobe = [
            ClothingItem(
                id="test-shirt-1",
                name="Blue T-Shirt",
                type=ClothingType.SHIRT,
                color="blue",
                season=[Season.SPRING, Season.SUMMER],
                style=[StyleTag.CASUAL],
                imageUrl="",
                tags=[],
                dominantColors=["#0000FF"],
                matchingColors=[],
                occasion=["casual"],
                createdAt=int(datetime.now().timestamp()),
                updatedAt=int(datetime.now().timestamp()),
                userId="test-user"
            ),
            ClothingItem(
                id="test-pants-1",
                name="Black Jeans",
                type=ClothingType.PANTS,
                color="black",
                season=[Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                style=[StyleTag.CASUAL],
                imageUrl="",
                tags=[],
                dominantColors=["#000000"],
                matchingColors=[],
                occasion=["casual"],
                createdAt=int(datetime.now().timestamp()),
                updatedAt=int(datetime.now().timestamp()),
                userId="test-user"
            ),
            ClothingItem(
                id="test-shoes-1",
                name="White Sneakers",
                type=ClothingType.SHOES,
                color="white",
                season=[Season.SPRING, Season.SUMMER, Season.FALL],
                style=[StyleTag.CASUAL],
                imageUrl="",
                tags=[],
                dominantColors=["#FFFFFF"],
                matchingColors=[],
                occasion=["casual"],
                createdAt=int(datetime.now().timestamp()),
                updatedAt=int(datetime.now().timestamp()),
                userId="test-user"
            )
        ]
        print(f"✅ Wardrobe created with {len(wardrobe)} items")
        
        # Create test user profile
        profile = UserProfile(
            id="test-user-123",
            name="Test User",
            email="test@example.com",
            gender="male",
            preferences={
                "style": ["casual", "minimalist"],
                "colors": ["blue", "black", "white"],
                "occasions": ["casual", "work"]
            },
            measurements={
                "height": 175,
                "weight": 70,
                "bodyType": "athletic",
                "skinTone": "medium"
            },
            stylePreferences=["casual", "minimalist", "athletic"],
            bodyType="athletic",
            skinTone="medium",
            createdAt=int(datetime.now().timestamp()),
            updatedAt=int(datetime.now().timestamp())
        )
        print("✅ User profile created")
        
        return weather, wardrobe, profile
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

async def test_outfit_generation():
    """Test outfit generation with different profile configurations"""
    print("\n🧪 Testing outfit generation...")
    
    try:
        from services.outfit_service import OutfitService
        
        # Create outfit service
        outfit_service = OutfitService()
        print("✅ OutfitService created")
        
        # Get test data
        weather, wardrobe, profile = create_test_data()
        if not all([weather, wardrobe, profile]):
            print("❌ Failed to create test data")
            return False
        
        # Test 1: Complete profile
        print("\n📋 Test 1: Complete profile")
        try:
            outfit = await outfit_service.generate_outfit(
                occasion="casual",
                weather=weather,
                wardrobe=wardrobe,
                user_profile=profile,
                likedOutfits=[],
                trendingStyles=[],
                style="casual",
                mood="relaxed"
            )
            print(f"✅ Generated outfit with {len(outfit.items)} items")
            print(f"   Outfit ID: {outfit.id}")
            print(f"   Outfit name: {outfit.name}")
            print(f"   Items: {outfit.items}")
        except Exception as e:
            print(f"❌ Failed to generate outfit with complete profile: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 2: Minimal profile
        print("\n📋 Test 2: Minimal profile")
        try:
            from types import UserProfile
            minimal_profile = UserProfile(
                id="test-user-123",
                name="Test User",
                email="test@example.com",
                gender="male",
                preferences={
                    "style": ["casual"],
                    "colors": ["blue", "black"],
                    "occasions": ["casual"]
                },
                measurements={
                    "height": 175,
                    "weight": 70,
                    "bodyType": "athletic",
                    "skinTone": "medium"
                },
                stylePreferences=["casual"],
                bodyType="athletic",
                skinTone="medium",
                createdAt=int(datetime.now().timestamp()),
                updatedAt=int(datetime.now().timestamp())
            )
            
            outfit = await outfit_service.generate_outfit(
                occasion="casual",
                weather=weather,
                wardrobe=wardrobe,
                user_profile=minimal_profile,
                likedOutfits=[],
                trendingStyles=[]
            )
            print(f"✅ Generated outfit with minimal profile: {len(outfit.items)} items")
        except Exception as e:
            print(f"❌ Failed to generate outfit with minimal profile: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 3: Incomplete profile
        print("\n📋 Test 3: Incomplete profile")
        try:
            from types import UserProfile
            incomplete_profile = UserProfile(
                id="test-user-123",
                name="Test User",
                email="test@example.com",
                gender=None,
                preferences={
                    "style": [],
                    "colors": [],
                    "occasions": []
                },
                measurements={
                    "height": 0,
                    "weight": 0,
                    "bodyType": None,
                    "skinTone": None
                },
                stylePreferences=[],
                bodyType=None,
                skinTone=None,
                createdAt=int(datetime.now().timestamp()),
                updatedAt=int(datetime.now().timestamp())
            )
            
            outfit = await outfit_service.generate_outfit(
                occasion="casual",
                weather=weather,
                wardrobe=wardrobe,
                user_profile=incomplete_profile,
                likedOutfits=[],
                trendingStyles=[]
            )
            print(f"✅ Generated outfit with incomplete profile: {len(outfit.items)} items")
        except Exception as e:
            print(f"❌ Failed to generate outfit with incomplete profile: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in outfit generation test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_profile_field_issues():
    """Test specific profile field issues"""
    print("\n🔍 Testing profile field issues...")
    
    try:
        from services.outfit_service import OutfitService
        from types import UserProfile
        
        outfit_service = OutfitService()
        weather, wardrobe, _ = create_test_data()
        
        if not all([weather, wardrobe]):
            print("❌ Failed to create test data")
            return False
        
        # Test different problematic profile configurations
        test_cases = [
            {
                "name": "Missing gender",
                "profile": UserProfile(
                    id="test-user-123",
                    name="Test User",
                    email="test@example.com",
                    gender=None,
                    preferences={"style": ["casual"], "colors": ["blue"], "occasions": ["casual"]},
                    measurements={"height": 175, "weight": 70, "bodyType": "athletic", "skinTone": "medium"},
                    stylePreferences=["casual"],
                    bodyType="athletic",
                    skinTone="medium",
                    createdAt=int(datetime.now().timestamp()),
                    updatedAt=int(datetime.now().timestamp())
                )
            },
            {
                "name": "Empty style preferences",
                "profile": UserProfile(
                    id="test-user-123",
                    name="Test User",
                    email="test@example.com",
                    gender="male",
                    preferences={"style": [], "colors": ["blue"], "occasions": ["casual"]},
                    measurements={"height": 175, "weight": 70, "bodyType": "athletic", "skinTone": "medium"},
                    stylePreferences=[],
                    bodyType="athletic",
                    skinTone="medium",
                    createdAt=int(datetime.now().timestamp()),
                    updatedAt=int(datetime.now().timestamp())
                )
            },
            {
                "name": "Missing body type",
                "profile": UserProfile(
                    id="test-user-123",
                    name="Test User",
                    email="test@example.com",
                    gender="male",
                    preferences={"style": ["casual"], "colors": ["blue"], "occasions": ["casual"]},
                    measurements={"height": 175, "weight": 70, "bodyType": None, "skinTone": "medium"},
                    stylePreferences=["casual"],
                    bodyType=None,
                    skinTone="medium",
                    createdAt=int(datetime.now().timestamp()),
                    updatedAt=int(datetime.now().timestamp())
                )
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📋 Testing: {test_case['name']}")
            try:
                outfit = await outfit_service.generate_outfit(
                    occasion="casual",
                    weather=weather,
                    wardrobe=wardrobe,
                    user_profile=test_case["profile"],
                    likedOutfits=[],
                    trendingStyles=[]
                )
                print(f"✅ Success: {test_case['name']} - Generated outfit with {len(outfit.items)} items")
            except Exception as e:
                print(f"❌ Failed: {test_case['name']} - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in profile field test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function to run all tests"""
    print("🚀 Starting Outfit Generation Debug Tests")
    print("=" * 60)
    
    # Test imports first
    if not test_imports():
        print("❌ Import tests failed. Cannot proceed.")
        return
    
    # Test outfit generation
    if not await test_outfit_generation():
        print("❌ Outfit generation tests failed.")
        return
    
    # Test profile field issues
    if not await test_profile_field_issues():
        print("❌ Profile field tests failed.")
        return
    
    print("\n✅ All tests completed successfully!")
    print("🎉 The outfit generation system appears to be working correctly.")

if __name__ == "__main__":
    asyncio.run(main()) 