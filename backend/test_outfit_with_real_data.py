#!/usr/bin/env python3

import asyncio
import sys
import os
import json
import requests
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Initialize Firebase first
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate('firebase-credentials.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Now import the services
from services.outfit_service import OutfitService
from types.weather import WeatherData
from types.profile import UserProfile
from types.wardrobe import ClothingItem, ClothingType

class OutfitTester:
    def __init__(self):
        self.base_url = "http://localhost:3001"
        self.user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        
    def fetch_wardrobe_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch real wardrobe items from Firestore for the test user."""
        print(f"🔍 Fetching wardrobe items for user: {self.user_id}")
        
        wardrobe_ref = db.collection('wardrobe')
        wardrobe_docs = wardrobe_ref.where('userId', '==', self.user_id).limit(limit).stream()
        
        wardrobe_items = []
        for doc in wardrobe_docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            
            # Clean up the item data for API consumption
            cleaned_item = {
                'id': item_data.get('id'),
                'name': item_data.get('name', 'Unknown Item'),
                'type': item_data.get('type', 'other'),
                'color': item_data.get('color', 'unknown'),
                'season': item_data.get('season', ['all']),
                'style': item_data.get('style', []),
                'imageUrl': item_data.get('imageUrl', ''),
                'tags': item_data.get('tags', []),
                'dominantColors': item_data.get('dominantColors', []),
                'matchingColors': item_data.get('matchingColors', []),
                'occasion': item_data.get('occasion', []),
                'createdAt': item_data.get('createdAt', 1750531295),
                'updatedAt': item_data.get('updatedAt', 1750531295),
                'userId': item_data.get('userId', self.user_id),
                'metadata': item_data.get('metadata', {})
            }
            
            wardrobe_items.append(cleaned_item)
            print(f"  📦 Found item: {cleaned_item['name']} ({cleaned_item['type']})")
        
        print(f"✅ Found {len(wardrobe_items)} wardrobe items")
        return wardrobe_items
    
    def create_user_profile(self) -> Dict[str, Any]:
        """Create a user profile for testing."""
        return {
            "id": self.user_id,
            "name": "Test User",
            "email": "test@example.com",
            "gender": "male",
            "bodyType": "athletic",
            "skinTone": "medium",
            "stylePreferences": ["casual", "classic"],
            "budget": "medium",
            "favoriteBrands": ["Nike", "Adidas"],
            "createdAt": 1750531295,
            "updatedAt": 1750531295
        }
    
    def generate_outfit_via_api(self, wardrobe_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate an outfit using the API with real wardrobe items."""
        print(f"\n🎨 Generating outfit with {len(wardrobe_items)} wardrobe items...")
        
        payload = {
            "occasion": "Casual",
            "weather": {
                "temperature": 70.0,
                "condition": "sunny",
                "humidity": 50
            },
            "wardrobe": wardrobe_items,
            "user_profile": self.create_user_profile(),
            "likedOutfits": [],
            "trendingStyles": [],
            "style": "Casual",
            "mood": "relaxed"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/outfit/generate",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                outfit_data = response.json()
                print(f"✅ Outfit generated successfully!")
                print(f"   ID: {outfit_data.get('id')}")
                print(f"   Name: {outfit_data.get('name')}")
                print(f"   Items count: {len(outfit_data.get('items', []))}")
                print(f"   Was successful: {outfit_data.get('wasSuccessful')}")
                print(f"   Validation errors: {outfit_data.get('validationErrors', [])}")
                return outfit_data
            else:
                print(f"❌ Failed to generate outfit: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating outfit: {e}")
            return None
    
    def retrieve_outfit_via_api(self, outfit_id: str) -> Dict[str, Any]:
        """Retrieve an outfit using the API."""
        print(f"\n🔍 Retrieving outfit: {outfit_id}")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/outfit/{outfit_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                outfit_data = response.json()
                print(f"✅ Outfit retrieved successfully!")
                print(f"   Name: {outfit_data.get('name')}")
                print(f"   Items count: {len(outfit_data.get('items', []))}")
                print(f"   Was successful: {outfit_data.get('wasSuccessful')}")
                return outfit_data
            else:
                print(f"❌ Failed to retrieve outfit: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error retrieving outfit: {e}")
            return None
    
    async def test_outfit_service_directly(self, wardrobe_items: List[Dict[str, Any]]):
        """Test outfit generation and retrieval using the service directly."""
        print(f"\n🧪 Testing outfit service directly...")
        
        outfit_service = OutfitService()
        
        # Create test data
        weather = WeatherData(temperature=70.0, condition='sunny', humidity=50)
        user_profile = UserProfile(**self.create_user_profile())
        
        # Convert wardrobe items to ClothingItem objects
        clothing_items = []
        for item_data in wardrobe_items:
            try:
                clothing_items.append(ClothingItem(**item_data))
            except Exception as e:
                print(f"⚠️  Skipping item {item_data.get('id')}: {e}")
                continue
        
        print(f"✅ Converted {len(clothing_items)} items to ClothingItem objects")
        
        if len(clothing_items) < 2:
            print("❌ Not enough valid clothing items for testing")
            return
        
        # Generate outfit
        try:
            outfit = await outfit_service.generate_outfit(
                occasion='Casual',
                weather=weather,
                wardrobe=clothing_items,
                user_profile=user_profile,
                likedOutfits=[],
                trendingStyles=[],
                style='Casual',
                mood='relaxed'
            )
            
            print(f"✅ Outfit generated via service!")
            print(f"   ID: {outfit.id}")
            print(f"   Name: {outfit.name}")
            print(f"   Items count: {len(outfit.items)}")
            print(f"   Was successful: {outfit.wasSuccessful}")
            
            # Test retrieval
            retrieved_outfit = await outfit_service.get_outfit(outfit.id)
            if retrieved_outfit:
                print(f"✅ Successfully retrieved outfit via service: {retrieved_outfit.name}")
                print(f"   Items count: {len(retrieved_outfit.items)}")
                print(f"   Was successful: {retrieved_outfit.wasSuccessful}")
            else:
                print(f"❌ Failed to retrieve outfit via service")
                
        except Exception as e:
            print(f"❌ Error in service test: {e}")
            import traceback
            traceback.print_exc()
    
    def run_comprehensive_test(self):
        """Run the complete test suite."""
        print("🚀 Starting comprehensive outfit generation and retrieval test")
        print("=" * 60)
        
        # Step 1: Fetch real wardrobe items
        wardrobe_items = self.fetch_wardrobe_items(limit=10)
        
        if len(wardrobe_items) < 2:
            print("❌ Not enough wardrobe items for testing")
            return
        
        # Step 2: Test API generation and retrieval
        print("\n" + "=" * 60)
        print("📡 Testing API endpoints")
        print("=" * 60)
        
        outfit_data = self.generate_outfit_via_api(wardrobe_items)
        
        if outfit_data and outfit_data.get('id'):
            outfit_id = outfit_data['id']
            
            # Wait a moment for the outfit to be saved
            import time
            time.sleep(1)
            
            # Test retrieval
            retrieved_outfit = self.retrieve_outfit_via_api(outfit_id)
            
            if retrieved_outfit:
                print(f"\n🎉 SUCCESS: Outfit generation and retrieval via API works!")
            else:
                print(f"\n❌ FAILED: Outfit retrieval via API failed")
        else:
            print(f"\n❌ FAILED: Outfit generation via API failed")
        
        # Step 3: Test service directly
        print("\n" + "=" * 60)
        print("🔧 Testing service directly")
        print("=" * 60)
        
        asyncio.run(self.test_outfit_service_directly(wardrobe_items))
        
        print("\n" + "=" * 60)
        print("🏁 Test completed!")
        print("=" * 60)

def main():
    """Main function to run the test."""
    tester = OutfitTester()
    tester.run_comprehensive_test()

if __name__ == '__main__':
    main() 