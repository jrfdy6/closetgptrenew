#!/usr/bin/env python3
"""
Test script to verify outfit retrieval works correctly
"""

import requests
import json

# Backend API endpoint
API_BASE_URL = "http://localhost:3001"

def test_outfit_retrieval():
    """Test that we can retrieve an outfit after generation"""
    print("🧪 Testing outfit retrieval...")
    
    try:
        # First, generate an outfit
        print("📤 Generating test outfit...")
        
        # Create test data
        wardrobe = [
            {
                "id": "test-shirt-1",
                "name": "test-shirt-1",
                "type": "shirt",
                "color": "blue",
                "style": ["casual"],
                "occasion": ["casual"],
                "season": ["spring", "summer"],
                "imageUrl": "https://example.com/shirt.jpg",
                "dominantColors": [
                    {"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}
                ],
                "matchingColors": [
                    {"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}
                ],
                "tags": ["casual", "comfortable"],
                "createdAt": 1640995200,
                "updatedAt": 1640995200,
                "userId": "test-user"
            }
        ]
        
        user_profile = {
            "id": "test-user-123",
            "name": "Test User",
            "email": "test@example.com",
            "gender": "male",
            "preferences": {
                "style": ["casual"],
                "colors": ["blue"],
                "occasions": ["casual"]
            },
            "measurements": {
                "height": 175,
                "weight": 70,
                "bodyType": "athletic",
                "skinTone": "medium"
            },
            "stylePreferences": ["casual"],
            "bodyType": "athletic",
            "skinTone": "medium",
            "createdAt": 1640995200,
            "updatedAt": 1640995200
        }
        
        weather = {
            "temperature": 75.0,
            "condition": "sunny",
            "location": "test-location",
            "humidity": 50.0,
            "wind_speed": 5.0,
            "precipitation": 0.0
        }
        
        # Generate outfit
        generation_payload = {
            "occasion": "casual",
            "weather": weather,
            "wardrobe": wardrobe,
            "user_profile": user_profile,
            "likedOutfits": [],
            "trendingStyles": [],
            "style": "casual",
            "mood": "relaxed"
        }
        
        generation_response = requests.post(
            f"{API_BASE_URL}/api/outfit/generate",
            json=generation_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if generation_response.status_code != 200:
            print(f"❌ Failed to generate outfit: {generation_response.status_code}")
            print(f"   Response: {generation_response.text}")
            return False
        
        outfit_data = generation_response.json()
        outfit_id = outfit_data.get('id')
        
        if not outfit_id:
            print("❌ No outfit ID returned from generation")
            return False
        
        print(f"✅ Generated outfit with ID: {outfit_id}")
        
        # Now try to retrieve the outfit
        print(f"📥 Retrieving outfit {outfit_id}...")
        
        retrieval_response = requests.get(
            f"{API_BASE_URL}/api/outfit/{outfit_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if retrieval_response.status_code == 200:
            retrieved_outfit = retrieval_response.json()
            print(f"✅ Successfully retrieved outfit")
            print(f"   Name: {retrieved_outfit.get('name', 'N/A')}")
            print(f"   Items count: {len(retrieved_outfit.get('items', []))}")
            print(f"   Occasion: {retrieved_outfit.get('occasion', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to retrieve outfit: {retrieval_response.status_code}")
            print(f"   Response: {retrieval_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Outfit Retrieval")
    print("=" * 40)
    
    success = test_outfit_retrieval()
    
    if success:
        print("\n✅ Outfit retrieval is working correctly!")
        print("🎉 The fix is successful.")
    else:
        print("\n❌ Outfit retrieval failed.")
        print("🔧 The fix may need additional work.")

if __name__ == "__main__":
    main() 