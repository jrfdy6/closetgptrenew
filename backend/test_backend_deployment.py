#!/usr/bin/env python3
"""
Test script to check backend deployment
"""

import requests
import json
import time

def test_backend_deployment():
    """Test if the backend is deployed and working"""
    
    base_url = "https://closetgptrenew-backend-production.up.railway.app"
    
    print("🧪 Testing Backend Deployment")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print("✅ Health check passed")
        else:
            print(f"   Response: {response.text}")
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"   Response: {response.text}")
            print("❌ Root endpoint failed")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: API health
    print("\n3. Testing API health...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ API health working")
        else:
            print(f"   Response: {response.text}")
            print("❌ API health failed")
    except Exception as e:
        print(f"❌ API health error: {e}")
    
    # Test 4: Wardrobe endpoint (should require auth)
    print("\n4. Testing wardrobe endpoint (should require auth)...")
    try:
        response = requests.get(f"{base_url}/api/wardrobe", timeout=10, allow_redirects=True)
        print(f"   Status: {response.status_code}")
        if response.status_code in [401, 403]:
            print("✅ Wardrobe endpoint correctly requires authentication")
        elif response.status_code == 200:
            print("✅ Wardrobe endpoint working (no auth required)")
        elif response.status_code == 404:
            print("❌ Wardrobe endpoint not found - router not loaded")
        else:
            print(f"   Response: {response.text}")
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Wardrobe endpoint error: {e}")
    
    # Test 5: Test with mock token
    print("\n5. Testing wardrobe with mock token...")
    try:
        headers = {"Authorization": "Bearer test"}
        response = requests.get(f"{base_url}/api/wardrobe", headers=headers, timeout=10, allow_redirects=True)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Items count: {data.get('count', 0)}")
            print("✅ Wardrobe endpoint working with test token")
        else:
            print(f"   Response: {response.text}")
            print("❌ Wardrobe endpoint failed")
    except Exception as e:
        print(f"❌ Wardrobe test error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Backend deployment testing complete!")

if __name__ == "__main__":
    test_backend_deployment() 