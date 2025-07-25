#!/usr/bin/env python3
"""
Debug script to test outfit saving and retrieval.
Tests the complete flow from outfit generation to saving to retrieval.
"""

import asyncio
import sys
import os
import time
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.outfit_service import OutfitService
from src.types.wardrobe import ClothingItem, ClothingType, Season, StyleTag, Color
from src.types.profile import UserProfile
from src.types.weather import WeatherData
from src.config.firebase import db

class OutfitSavingDebugger:
    def __init__(self):
        self.outfit_service = OutfitService()
        self.test_user_id = "debug_test_user_123"
        
    def create_test_user_profile(self) -> UserProfile:
        """Create a test user profile."""
        return UserProfile(
            id=self.test_user_id,
            name="Debug Test User",
            email="debug@test.com",
            gender="male",
            bodyType="athletic",
            skinTone="medium",
            stylePreferences=["casual", "classic"],
            budget="medium",
            favoriteBrands=["Nike", "Adidas"],
            createdAt=int(time.time()),
            updatedAt=int(time.time())
        )
    
    def create_test_wardrobe(self) -> list[ClothingItem]:
        """Create a test wardrobe with a few items."""
        return [
            ClothingItem(
                id="test_shirt_1",
                name="Test Shirt",
                type=ClothingType.SHIRT,
                color="blue",
                season=[Season.SPRING, Season.SUMMER],
                style=[StyleTag.CASUAL],
                imageUrl="https://example.com/shirt.jpg",
                tags=["cotton", "short-sleeve"],
                dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
                matchingColors=[],
                occasion=["casual"],
                createdAt=int(time.time()),
                updatedAt=int(time.time()),
                userId=self.test_user_id
            ),
            ClothingItem(
                id="test_pants_1",
                name="Test Pants",
                type=ClothingType.PANTS,
                color="black",
                season=[Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                style=[StyleTag.CASUAL],
                imageUrl="https://example.com/pants.jpg",
                tags=["cotton", "jeans"],
                dominantColors=[{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                matchingColors=[],
                occasion=["casual"],
                createdAt=int(time.time()),
                updatedAt=int(time.time()),
                userId=self.test_user_id
            ),
            ClothingItem(
                id="test_shoes_1",
                name="Test Shoes",
                type=ClothingType.SHOES,
                color="white",
                season=[Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER],
                style=[StyleTag.CASUAL],
                imageUrl="https://example.com/shoes.jpg",
                tags=["sneakers", "comfortable"],
                dominantColors=[{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
                matchingColors=[],
                occasion=["casual"],
                createdAt=int(time.time()),
                updatedAt=int(time.time()),
                userId=self.test_user_id
            )
        ]
    
    def create_test_weather(self) -> WeatherData:
        """Create test weather data."""
        return WeatherData(
            temperature=70.0,
            condition="sunny",
            humidity=50,
            wind_speed=5,
            precipitation=0,
            location="Test City"
        )
    
    async def test_outfit_generation_and_saving(self):
        """Test the complete outfit generation and saving flow."""
        print("🧪 Starting outfit generation and saving debug test...")
        
        # Create test data
        user_profile = self.create_test_user_profile()
        wardrobe = self.create_test_wardrobe()
        weather = self.create_test_weather()
        
        print(f"📋 Test data created:")
        print(f"   - User ID: {user_profile.id}")
        print(f"   - Wardrobe items: {len(wardrobe)}")
        print(f"   - Weather: {weather.temperature}°F, {weather.condition}")
        
        try:
            # Generate outfit
            print("\n🎨 Generating outfit...")
            outfit_result = await self.outfit_service.generate_outfit(
                occasion="Casual",
                weather=weather,
                wardrobe=wardrobe,
                user_profile=user_profile,
                likedOutfits=[],
                trendingStyles=[],
                style="Casual",
                mood="relaxed"
            )
            
            print(f"✅ Outfit generated successfully!")
            print(f"   - Outfit ID: {outfit_result.id}")
            print(f"   - Name: {outfit_result.name}")
            print(f"   - Items: {len(outfit_result.items)}")
            print(f"   - Was successful: {outfit_result.wasSuccessful}")
            
            # Check if user_id is in the outfit data
            outfit_dict = outfit_result.dict()
            print(f"\n🔍 Checking outfit data structure:")
            print(f"   - All keys: {list(outfit_dict.keys())}")
            print(f"   - Has 'user_id': {'user_id' in outfit_dict}")
            if 'user_id' in outfit_dict:
                print(f"   - user_id value: {outfit_dict['user_id']}")
            else:
                print(f"   - ❌ user_id is missing from outfit data!")
            
            # Wait a moment for Firestore to process
            print("\n⏳ Waiting for Firestore to process...")
            await asyncio.sleep(2)
            
            # Try to retrieve the outfit
            print("\n📥 Retrieving outfit from Firestore...")
            retrieved_outfit = await self.outfit_service.get_outfit(outfit_result.id)
            
            if retrieved_outfit:
                print(f"✅ Outfit retrieved successfully!")
                retrieved_dict = retrieved_outfit.dict()
                print(f"   - Retrieved outfit ID: {retrieved_outfit.id}")
                print(f"   - Retrieved outfit keys: {list(retrieved_dict.keys())}")
                print(f"   - Has 'user_id': {'user_id' in retrieved_dict}")
                if 'user_id' in retrieved_dict:
                    print(f"   - Retrieved user_id: {retrieved_dict['user_id']}")
                else:
                    print(f"   - ❌ user_id is missing from retrieved outfit!")
            else:
                print(f"❌ Failed to retrieve outfit!")
            
            # Test getting outfits by user
            print(f"\n👤 Testing get_outfits_by_user for user {self.test_user_id}...")
            user_outfits = await self.outfit_service.get_outfits_by_user(self.test_user_id)
            print(f"   - Found {len(user_outfits)} outfits for user")
            
            if user_outfits:
                latest_outfit = user_outfits[0]
                latest_dict = latest_outfit.dict()
                print(f"   - Latest outfit ID: {latest_outfit.id}")
                print(f"   - Latest outfit keys: {list(latest_dict.keys())}")
                print(f"   - Has 'user_id': {'user_id' in latest_dict}")
                if 'user_id' in latest_dict:
                    print(f"   - Latest outfit user_id: {latest_dict['user_id']}")
                else:
                    print(f"   - ❌ user_id is missing from latest outfit!")
            
            # Check raw Firestore data
            print(f"\n🔥 Checking raw Firestore data...")
            doc_ref = self.outfit_service.collection.document(outfit_result.id)
            doc = doc_ref.get()
            
            if doc.exists:
                raw_data = doc.to_dict()
                print(f"   - Raw Firestore keys: {list(raw_data.keys())}")
                print(f"   - Has 'user_id': {'user_id' in raw_data}")
                if 'user_id' in raw_data:
                    print(f"   - Raw user_id: {raw_data['user_id']}")
                else:
                    print(f"   - ❌ user_id is missing from raw Firestore data!")
                    
                # Check for other user-related fields
                user_fields = [key for key in raw_data.keys() if 'user' in key.lower()]
                print(f"   - All user-related fields: {user_fields}")
            else:
                print(f"   - ❌ Document not found in Firestore!")
            
            return outfit_result
            
        except Exception as e:
            print(f"❌ Error during outfit generation and saving: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def test_serialization(self):
        """Test the serialization process specifically."""
        print("\n🔧 Testing serialization process...")
        
        # Create test outfit data
        test_outfit_data = {
            "id": "test_serialization_123",
            "name": "Test Serialization Outfit",
            "description": "Testing serialization",
            "items": [],
            "explanation": "Test",
            "pieces": [],
            "styleTags": [],
            "colorHarmony": "",
            "styleNotes": "",
            "occasion": "Casual",
            "season": "spring",
            "style": "Casual",
            "mood": "Neutral",
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "wasSuccessful": True,
            "baseItemId": None,
            "validationErrors": [],
            "userFeedback": None,
            "user_id": self.test_user_id,  # This should be preserved
            "metadata": {}
        }
        
        print(f"   - Original data has user_id: {'user_id' in test_outfit_data}")
        print(f"   - Original user_id value: {test_outfit_data.get('user_id')}")
        
        # Test serialization
        serialized_data = self.outfit_service.to_dict_recursive(test_outfit_data)
        print(f"   - Serialized data has user_id: {'user_id' in serialized_data}")
        if 'user_id' in serialized_data:
            print(f"   - Serialized user_id value: {serialized_data['user_id']}")
        else:
            print(f"   - ❌ user_id lost during serialization!")
        
        # Test saving to Firestore
        print(f"\n💾 Testing Firestore save...")
        doc_ref = self.outfit_service.collection.document(test_outfit_data["id"])
        doc_ref.set(serialized_data)
        
        # Wait and retrieve
        await asyncio.sleep(1)
        doc = doc_ref.get()
        if doc.exists:
            retrieved_data = doc.to_dict()
            print(f"   - Retrieved data has user_id: {'user_id' in retrieved_data}")
            if 'user_id' in retrieved_data:
                print(f"   - Retrieved user_id value: {retrieved_data['user_id']}")
            else:
                print(f"   - ❌ user_id lost during Firestore save/retrieve!")
        else:
            print(f"   - ❌ Document not found after save!")
        
        # Clean up test document
        doc_ref.delete()
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        print(f"\n🧹 Cleaning up test data...")
        
        # Delete test outfits
        user_outfits = await self.outfit_service.get_outfits_by_user(self.test_user_id)
        for outfit in user_outfits:
            try:
                self.outfit_service.collection.document(outfit.id).delete()
                print(f"   - Deleted outfit {outfit.id}")
            except Exception as e:
                print(f"   - Failed to delete outfit {outfit.id}: {e}")
        
        print(f"   - Cleanup completed")

async def main():
    """Main debug function."""
    debugger = OutfitSavingDebugger()
    
    try:
        # Test serialization first
        await debugger.test_serialization()
        
        # Test complete flow
        outfit = await debugger.test_outfit_generation_and_saving()
        
        # Clean up
        await debugger.cleanup_test_data()
        
        print(f"\n🎉 Debug test completed!")
        
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 