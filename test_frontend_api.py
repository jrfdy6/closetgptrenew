#!/usr/bin/env python3
"""
Test script to verify frontend API endpoint handles null bodyType values correctly
"""

import requests
import json

# Frontend API endpoint (assuming it's running on port 3000)
FRONTEND_API_URL = "http://localhost:3000/api/outfit/generate"

def create_test_wardrobe_data():
    """Create test wardrobe data with proper color objects"""
    return [
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
        },
        {
            "id": "test-pants-1",
            "name": "test-pants-1",
            "type": "pants",
            "color": "black",
            "style": ["casual"],
            "occasion": ["casual"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/pants.jpg",
            "dominantColors": [
                {"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}
            ],
            "matchingColors": [
                {"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}
            ],
            "tags": ["casual", "versatile"],
            "createdAt": 1640995200,
            "updatedAt": 1640995200,
            "userId": "test-user"
        }
    ]

def create_test_user_profile(profile_type="complete"):
    """Create test user profile with different completeness levels"""
    base_profile = {
        "id": "test-user-123",
        "name": "Test User",
        "email": "test@example.com",
        "gender": "male",
        "preferences": {
            "style": ["casual"],
            "colors": ["blue", "black"],
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
    
    if profile_type == "complete":
        return base_profile
    
    elif profile_type == "minimal":
        return {
            **base_profile,
            "preferences": {
                "style": ["casual"],
                "colors": ["blue"],
                "occasions": ["casual"]
            },
            "stylePreferences": ["casual"]
        }
    
    elif profile_type == "incomplete":
        return {
            **base_profile,
            "gender": None,
            "preferences": {
                "style": [],
                "colors": [],
                "occasions": []
            },
            "measurements": {
                "height": 0,
                "weight": 0,
                "bodyType": None,  # This should be handled by frontend fallback
                "skinTone": None
            },
            "stylePreferences": [],
            "bodyType": None,      # This should be handled by frontend fallback
            "skinTone": None
        }
    
    else:
        raise ValueError(f"Unknown profile type: {profile_type}")

def create_test_weather_data():
    """Create test weather data"""
    return {
        "temperature": 75.0,
        "condition": "sunny",
        "location": "test-location",
        "humidity": 50.0,
        "wind_speed": 5.0,
        "precipitation": 0.0
    }

def test_frontend_api_with_null_bodytype():
    """Test that frontend API handles null bodyType correctly"""
    print("🧪 Testing frontend API with null bodyType...")
    
    try:
        # Prepare test data with null bodyType
        wardrobe = create_test_wardrobe_data()
        user_profile = create_test_user_profile("incomplete")  # This has null bodyType
        weather = create_test_weather_data()
        
        # Create request payload
        payload = {
            "occasion": "casual",
            "weather": weather,
            "wardrobe": wardrobe,
            "userProfile": user_profile,  # Note: frontend expects userProfile, not user_profile
            "likedOutfits": [],
            "trendingStyles": [],
            "style": "casual",
            "mood": "relaxed"
        }
        
        print(f"📤 Sending payload with null bodyType: {user_profile['bodyType']}")
        
        # Make API request to frontend
        response = requests.post(
            FRONTEND_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            outfit_data = response.json()
            print(f"✅ Successfully generated outfit through frontend API")
            print(f"   Outfit ID: {outfit_data.get('id', 'N/A')}")
            print(f"   Outfit name: {outfit_data.get('name', 'N/A')}")
            print(f"   Items count: {len(outfit_data.get('items', []))}")
            return True
        else:
            print(f"❌ Frontend API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to frontend API. Make sure the frontend is running on port 3000.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Frontend API with Null BodyType")
    print("=" * 50)
    
    # Test frontend API with null bodyType
    success = test_frontend_api_with_null_bodytype()
    
    if success:
        print("\n✅ Frontend API correctly handles null bodyType values!")
        print("🎉 The fix is working properly.")
    else:
        print("\n❌ Frontend API failed to handle null bodyType values.")
        print("🔧 The fix may need additional work.")

if __name__ == "__main__":
    main() 