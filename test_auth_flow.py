#!/usr/bin/env python3

import requests
import json

# Test the authentication flow step by step
frontend_url = "https://closetgpt-frontend-jb6n38zyg-johnnie-fields-projects.vercel.app"
backend_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_auth_flow():
    """Test the authentication flow step by step"""
    
    print("🔍 Testing authentication flow...")
    
    # Test 1: Frontend API route without auth (should return 403)
    print("\n1. Testing frontend API route without auth:")
    try:
        response = requests.get(f"{frontend_url}/api/outfits", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Backend API route without auth (should return 403)
    print("\n2. Testing backend API route without auth:")
    try:
        response = requests.get(f"{backend_url}/api/outfits/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Backend test endpoint (should work without auth)
    print("\n3. Testing backend test endpoint:")
    try:
        response = requests.get(f"{backend_url}/api/outfits/test", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} outfits")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Backend debug endpoint (should work without auth)
    print("\n4. Testing backend debug endpoint:")
    try:
        response = requests.get(f"{backend_url}/api/outfits/debug", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Debug info: {json.dumps(data, indent=2)}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_auth_flow() 