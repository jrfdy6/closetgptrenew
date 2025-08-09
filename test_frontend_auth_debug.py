#!/usr/bin/env python3

import requests
import json

# Test to debug the frontend authentication flow
frontend_url = "https://closetgpt-frontend-jb6n38zyg-johnnie-fields-projects.vercel.app"

def test_frontend_auth_debug():
    """Test to debug the frontend authentication flow"""
    
    print("🔍 Testing frontend authentication flow...")
    
    # Test the frontend API route without auth (should return 403 or fallback)
    try:
        response = requests.get(f"{frontend_url}/api/outfits", timeout=30)
        print(f"Frontend API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Frontend API returned {len(data)} outfits")
            
            # Check if these are real outfits or mock outfits
            if data and len(data) > 0:
                first_outfit = data[0]
                print(f"First outfit keys: {list(first_outfit.keys())}")
                
                if 'items' in first_outfit and first_outfit['items']:
                    first_item = first_outfit['items'][0]
                    print(f"First item keys: {list(first_item.keys())}")
                    if 'userId' in first_item:
                        print(f"First item userId: {first_item['userId']}")
                    else:
                        print("First item has no userId field")
        else:
            print(f"Frontend API error: {response.text}")
    except Exception as e:
        print(f"Frontend API failed: {e}")
    
    # Test the backend directly to compare
    backend_url = "https://closetgptrenew-backend-production.up.railway.app"
    try:
        response = requests.get(f"{backend_url}/api/outfits/test", timeout=30)
        print(f"Backend test endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Backend test endpoint returned {len(data)} outfits")
            
            # Check if these are real outfits
            if data and len(data) > 0:
                first_outfit = data[0]
                print(f"Backend first outfit keys: {list(first_outfit.keys())}")
                
                if 'items' in first_outfit and first_outfit['items']:
                    first_item = first_outfit['items'][0]
                    print(f"Backend first item keys: {list(first_item.keys())}")
                    if 'userId' in first_item:
                        print(f"Backend first item userId: {first_item['userId']}")
                    else:
                        print("Backend first item has no userId field")
        else:
            print(f"Backend test endpoint error: {response.text}")
    except Exception as e:
        print(f"Backend test endpoint failed: {e}")

if __name__ == "__main__":
    test_frontend_auth_debug() 