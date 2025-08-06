#!/usr/bin/env python3
"""
Test script to verify wardrobe functionality in production
"""

import requests
import json
import os
from datetime import datetime

def test_wardrobe_production():
    """Test wardrobe functionality in production"""
    
    # Production backend URL
    base_url = "https://acceptable-wisdom-production-ac06.up.railway.app"
    
    print("🧪 Testing Wardrobe Production Functionality")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: API test
    print("\n2. Testing API endpoint...")
    try:
        response = requests.get(f"{base_url}/api/test", timeout=10)
        if response.status_code == 200:
            print("✅ API test passed")
        else:
            print(f"❌ API test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    # Test 3: Wardrobe endpoint (should require auth)
    print("\n3. Testing wardrobe endpoint (should require auth)...")
    try:
        response = requests.get(f"{base_url}/api/wardrobe", timeout=10)
        if response.status_code == 401 or response.status_code == 403:
            print("✅ Wardrobe endpoint correctly requires authentication")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            if response.status_code == 200:
                print("   This might indicate the endpoint is not properly protected")
    except Exception as e:
        print(f"❌ Wardrobe endpoint error: {e}")
    
    # Test 4: Test with mock token
    print("\n4. Testing wardrobe with mock token...")
    try:
        headers = {"Authorization": "Bearer test"}
        response = requests.get(f"{base_url}/api/wardrobe", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Wardrobe endpoint working with test token")
            print(f"   Items count: {data.get('count', 0)}")
            if data.get('errors'):
                print(f"   Errors: {len(data['errors'])}")
        else:
            print(f"❌ Wardrobe endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Wardrobe test error: {e}")
    
    # Test 5: Test outfit generation
    print("\n5. Testing outfit generation...")
    try:
        headers = {"Authorization": "Bearer test"}
        response = requests.get(f"{base_url}/api/outfits/generate", headers=headers, timeout=15)
        if response.status_code == 200:
            print("✅ Outfit generation working")
        else:
            print(f"⚠️  Outfit generation response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Outfit generation error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Production testing complete!")

if __name__ == "__main__":
    test_wardrobe_production() 