#!/usr/bin/env python3
"""
Test script for robust outfit generation API with real authentication.
"""

import requests
import json
import time

# Your real Firebase user ID
USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
BASE_URL = "https://closetgptrenew-backend-production.up.railway.app"

def test_robust_generation():
    """Test robust outfit generation with various scenarios."""
    
    # Test scenarios
    test_cases = [
        {
            "name": "Business Professional",
            "data": {
                "occasion": "business",
                "style": "professional", 
                "mood": "confident",
                "generation_mode": "robust",
                "user_id": USER_ID
            }
        },
        {
            "name": "Casual Weekend",
            "data": {
                "occasion": "casual",
                "style": "casual",
                "mood": "comfortable", 
                "generation_mode": "robust",
                "user_id": USER_ID
            }
        },
        {
            "name": "Formal Event",
            "data": {
                "occasion": "formal",
                "style": "elegant",
                "mood": "sophisticated",
                "generation_mode": "robust", 
                "user_id": USER_ID
            }
        },
        {
            "name": "Athletic Workout",
            "data": {
                "occasion": "athletic",
                "style": "athletic",
                "mood": "energetic",
                "generation_mode": "robust",
                "user_id": USER_ID
            }
        }
    ]
    
    print("🧪 Testing Robust Outfit Generation API")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"   Occasion: {test_case['data']['occasion']}")
        print(f"   Style: {test_case['data']['style']}")
        print(f"   Mood: {test_case['data']['mood']}")
        
        try:
            # Test the main hybrid endpoint
            response = requests.post(
                f"{BASE_URL}/api/outfits/generate",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer test-token"  # You'll need a real token
                },
                json=test_case['data'],
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success!")
                print(f"   Items: {len(data.get('items', []))}")
                print(f"   Confidence: {data.get('confidence_score', 'N/A')}")
                print(f"   Strategy: {data.get('metadata', {}).get('generation_strategy', 'N/A')}")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Rate limiting
    
    print("\n🎉 Testing Complete!")

def test_simple_vs_robust():
    """Compare simple vs robust generation."""
    
    test_data = {
        "occasion": "business",
        "style": "professional",
        "mood": "confident",
        "user_id": USER_ID
    }
    
    print("\n🔄 Comparing Simple vs Robust Generation")
    print("=" * 50)
    
    # Test simple generation
    print("\n📝 Testing Simple Generation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/outfits/generate-simple",
            headers={
                "Content-Type": "application/json", 
                "Authorization": "Bearer test-token"
            },
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Simple: {len(data.get('items', []))} items, confidence: {data.get('confidence_score', 'N/A')}")
        else:
            print(f"   ❌ Simple failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Simple error: {e}")
    
    # Test robust generation
    print("\n🚀 Testing Robust Generation...")
    try:
        test_data["generation_mode"] = "robust"
        response = requests.post(
            f"{BASE_URL}/api/outfits/generate-robust",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test-token"
            },
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Robust: {len(data.get('items', []))} items, confidence: {data.get('confidence_score', 'N/A')}")
            print(f"   Strategy: {data.get('metadata', {}).get('generation_strategy', 'N/A')}")
        else:
            print(f"   ❌ Robust failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Robust error: {e}")

if __name__ == "__main__":
    test_robust_generation()
    test_simple_vs_robust()
