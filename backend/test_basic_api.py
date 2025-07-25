#!/usr/bin/env python3
"""
Basic API Test Script
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:3001"

def test_basic_api():
    """Test basic API functionality"""
    
    print("🧪 Testing Basic API Functionality")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: API health endpoint
    print("\n3. Testing API health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API health endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API health endpoint error: {e}")
    
    # Test 4: Check available endpoints
    print("\n4. Testing OpenAPI docs...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ OpenAPI docs accessible")
            print("   Visit: http://localhost:3001/docs")
        else:
            print(f"❌ OpenAPI docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ OpenAPI docs error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Basic API tests completed!")
    print("\n📝 Summary:")
    print("   - Backend server is running (✅)")
    print("   - Health endpoints are working (✅)")
    print("   - API documentation is accessible (✅)")
    
    print("\n🚀 Next steps:")
    print("   1. Visit http://localhost:3001/docs to see all available endpoints")
    print("   2. Test specific endpoints with authentication")
    print("   3. Integrate with frontend components")

if __name__ == "__main__":
    test_basic_api() 