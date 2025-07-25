#!/usr/bin/env python3
"""
Test script for the forgotten gems endpoint
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:3001"

def test_forgotten_gems_endpoint():
    """Test the forgotten gems endpoint"""
    
    print("🧪 Testing Forgotten Gems Endpoint")
    print("=" * 50)
    
    # Test 1: Check if endpoint exists in OpenAPI docs
    print("\n1. Checking OpenAPI documentation...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            
            # Check if forgotten gems endpoint exists
            forgotten_gems_path = '/api/wardrobe/forgotten-gems'
            if forgotten_gems_path in paths:
                print("✅ Forgotten gems endpoint found in OpenAPI docs")
                endpoint_info = paths[forgotten_gems_path]
                print(f"   Methods available: {list(endpoint_info.keys())}")
            else:
                print("❌ Forgotten gems endpoint not found in OpenAPI docs")
                print(f"   Available paths: {list(paths.keys())[:10]}...")
        else:
            print(f"❌ Failed to get OpenAPI docs: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking OpenAPI docs: {e}")
    
    # Test 2: Test endpoint without authentication (should fail)
    print("\n2. Testing endpoint without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/api/wardrobe/forgotten-gems")
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing unauthenticated request: {e}")
    
    # Test 3: Test endpoint with invalid token (should fail)
    print("\n3. Testing endpoint with invalid token...")
    try:
        headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{BASE_URL}/api/wardrobe/forgotten-gems", headers=headers)
        if response.status_code == 401:
            print("✅ Correctly rejects invalid token")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing invalid token: {e}")
    
    # Test 4: Check if rediscover endpoint exists
    print("\n4. Checking rediscover endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/wardrobe/forgotten-gems/rediscover", 
                               json={"item_id": "test"})
        if response.status_code == 401:
            print("✅ Rediscover endpoint exists and requires authentication")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing rediscover endpoint: {e}")
    
    # Test 5: Check if declutter endpoint exists
    print("\n5. Checking declutter endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/wardrobe/forgotten-gems/declutter", 
                               json={"item_id": "test"})
        if response.status_code == 401:
            print("✅ Declutter endpoint exists and requires authentication")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing declutter endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Forgotten Gems Endpoint Tests Complete!")
    print("\nNext steps:")
    print("1. Test with real authentication token")
    print("2. Test frontend integration")
    print("3. Verify data flow from backend to frontend")

if __name__ == "__main__":
    test_forgotten_gems_endpoint() 