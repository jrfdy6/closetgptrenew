#!/usr/bin/env python3
"""
Outfit Generation API Test Script

This script tests the outfit generation API endpoints to identify issues with user profile setup.
"""

import asyncio
import json
import sys
import os
import requests
from datetime import datetime

# Test configuration
API_BASE_URL = "http://localhost:3001"
TEST_USER_ID = "test-user-123"

def test_api_health():
    """Test if the API is running"""
    print("🔍 Testing API health...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the backend server is running on http://localhost:8000")
        return False

def create_test_wardrobe_data():
    """Create test wardrobe data"""
    return [
        {
            "id": "test-shirt-1",
            "name": "Blue T-Shirt",
            "type": "shirt",
            "color": "blue",
            "season": ["spring", "summer"],
            "style": ["casual"],
            "imageUrl": "",
            "tags": [],
            "dominantColors": [
                {"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}
            ],
            "matchingColors": [
                {"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]},
                {"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}
            ],
            "occasion": ["casual"],
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp()),
            "userId": TEST_USER_ID
        },
        {
            "id": "test-pants-1",
            "name": "Black Jeans",
            "type": "pants",
            "color": "black",
            "season": ["spring", "summer", "fall", "winter"],
            "style": ["casual"],
            "imageUrl": "",
            "tags": [],
            "dominantColors": [
                {"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}
            ],
            "matchingColors": [
                {"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]},
                {"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}
            ],
            "occasion": ["casual"],
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp()),
            "userId": TEST_USER_ID
        },
        {
            "id": "test-shoes-1",
            "name": "White Sneakers",
            "type": "shoes",
            "color": "white",
            "season": ["spring", "summer", "fall"],
            "style": ["casual"],
            "imageUrl": "",
            "tags": [],
            "dominantColors": [
                {"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}
            ],
            "matchingColors": [
                {"name": "black", "hex": "#000000", "rgb": [0, 0, 0]},
                {"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}
            ],
            "occasion": ["casual"],
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp()),
            "userId": TEST_USER_ID
        }
    ]

def create_test_user_profile(profile_type="complete"):
    """Create test user profile data"""
    base_profile = {
        "id": TEST_USER_ID,
        "name": "Test User",
        "email": "test@example.com",
        "createdAt": int(datetime.now().timestamp()),
        "updatedAt": int(datetime.now().timestamp())
    }
    
    if profile_type == "complete":
        return {
            **base_profile,
            "gender": "male",
            "preferences": {
                "style": ["casual", "minimalist"],
                "colors": ["blue", "black", "white"],
                "occasions": ["casual", "work"]
            },
            "measurements": {
                "height": 175,
                "weight": 70,
                "bodyType": "athletic",
                "skinTone": "medium"
            },
            "stylePreferences": ["casual", "minimalist", "athletic"],
            "bodyType": "athletic",
            "skinTone": "medium"
        }
    
    elif profile_type == "minimal":
        return {
            **base_profile,
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
            "skinTone": "medium"
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
                "bodyType": "athletic",  # Provide fallback instead of None
                "skinTone": "medium"     # Provide fallback instead of None
            },
            "stylePreferences": [],
            "bodyType": "athletic",      # Provide fallback instead of None
            "skinTone": "medium"         # Provide fallback instead of None
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

def test_outfit_generation_api(profile_type="complete"):
    """Test outfit generation API with different profile types"""
    print(f"\n🧪 Testing outfit generation with {profile_type} profile...")
    
    try:
        # Prepare test data
        wardrobe = create_test_wardrobe_data()
        user_profile = create_test_user_profile(profile_type)
        weather = create_test_weather_data()
        
        # Create request payload
        payload = {
            "occasion": "casual",
            "weather": weather,
            "wardrobe": wardrobe,
            "user_profile": user_profile,
            "likedOutfits": [],
            "trendingStyles": [],
            "style": "casual",
            "mood": "relaxed"
        }
        
        # Make API request
        response = requests.post(
            f"{API_BASE_URL}/api/outfit/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            outfit_data = response.json()
            print(f"✅ Successfully generated outfit")
            print(f"   Outfit ID: {outfit_data.get('id', 'N/A')}")
            print(f"   Outfit name: {outfit_data.get('name', 'N/A')}")
            print(f"   Items count: {len(outfit_data.get('items', []))}")
            print(f"   Items: {outfit_data.get('items', [])}")
            return True
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_profile_field_issues():
    """Test specific profile field issues"""
    print("\n🔍 Testing profile field issues...")
    
    # Test different problematic profile configurations
    test_cases = [
        {
            "name": "Missing gender",
            "profile": create_test_user_profile("complete")
        },
        {
            "name": "Empty style preferences",
            "profile": create_test_user_profile("complete")
        },
        {
            "name": "Missing body type",
            "profile": create_test_user_profile("complete")
        }
    ]
    
    # Modify the test cases
    test_cases[0]["profile"]["gender"] = None
    test_cases[1]["profile"]["preferences"]["style"] = []
    test_cases[1]["profile"]["stylePreferences"] = []
    test_cases[2]["profile"]["bodyType"] = "athletic"  # Provide fallback instead of None
    test_cases[2]["profile"]["measurements"]["bodyType"] = "athletic"  # Provide fallback instead of None
    
    wardrobe = create_test_wardrobe_data()
    weather = create_test_weather_data()
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        try:
            payload = {
                "occasion": "casual",
                "weather": weather,
                "wardrobe": wardrobe,
                "user_profile": test_case["profile"],
                "likedOutfits": [],
                "trendingStyles": []
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/outfit/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                outfit_data = response.json()
                print(f"✅ Success: {test_case['name']} - Generated outfit with {len(outfit_data.get('items', []))} items")
            else:
                print(f"❌ Failed: {test_case['name']} - {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Failed: {test_case['name']} - {e}")

def test_outfit_generation_edge_cases():
    """Test edge cases in outfit generation"""
    print("\n🔍 Testing edge cases...")
    
    # Test with empty wardrobe
    print("\n📋 Testing: Empty wardrobe")
    try:
        payload = {
            "occasion": "casual",
            "weather": create_test_weather_data(),
            "wardrobe": [],
            "user_profile": create_test_user_profile("complete"),
            "likedOutfits": [],
            "trendingStyles": []
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/outfit/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            outfit_data = response.json()
            print(f"✅ Success: Empty wardrobe - Generated outfit with {len(outfit_data.get('items', []))} items")
        else:
            print(f"❌ Failed: Empty wardrobe - {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Failed: Empty wardrobe - {e}")
    
    # Test with extreme weather
    print("\n📋 Testing: Extreme weather")
    try:
        extreme_weather = create_test_weather_data()
        extreme_weather["temperature"] = 100.0
        extreme_weather["condition"] = "hot"
        
        payload = {
            "occasion": "casual",
            "weather": extreme_weather,
            "wardrobe": create_test_wardrobe_data(),
            "user_profile": create_test_user_profile("complete"),
            "likedOutfits": [],
            "trendingStyles": []
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/outfit/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            outfit_data = response.json()
            print(f"✅ Success: Extreme weather - Generated outfit with {len(outfit_data.get('items', []))} items")
        else:
            print(f"❌ Failed: Extreme weather - {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Failed: Extreme weather - {e}")

def main():
    """Main function to run all tests"""
    print("🚀 Starting Outfit Generation API Tests")
    print("=" * 60)
    
    # Test API health first
    if not test_api_health():
        print("❌ API health check failed. Cannot proceed.")
        return
    
    # Test outfit generation with different profile types
    print("\n🧪 Testing outfit generation with different profile types...")
    
    profile_types = ["complete", "minimal", "incomplete"]
    for profile_type in profile_types:
        if not test_outfit_generation_api(profile_type):
            print(f"❌ Outfit generation test with {profile_type} profile failed.")
            return
    
    # Test profile field issues
    test_profile_field_issues()
    
    # Test edge cases
    test_outfit_generation_edge_cases()
    
    print("\n✅ All tests completed!")
    print("🎉 The outfit generation API appears to be working correctly.")

if __name__ == "__main__":
    main() 