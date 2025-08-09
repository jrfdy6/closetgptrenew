#!/usr/bin/env python3

import requests
import json

# Test to examine the actual outfit data structure
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_outfit_data():
    """Test to examine the actual outfit data structure"""
    
    print("🔍 Examining outfit data structure...")
    
    try:
        test_response = requests.get(f"{base_url}/api/outfits/test", timeout=10)
        print(f"Test outfits endpoint status: {test_response.status_code}")
        if test_response.status_code == 200:
            test_data = test_response.json()
            print(f"Found {len(test_data)} outfits in test endpoint")
            
            if test_data:
                first_outfit = test_data[0]
                print(f"First outfit keys: {list(first_outfit.keys())}")
                print(f"First outfit user_id: {first_outfit.get('user_id', 'NOT_FOUND')}")
                print(f"First outfit name: {first_outfit.get('name', 'NO_NAME')}")
                
                # Check if user_id is in the items or elsewhere
                items = first_outfit.get('items', [])
                if items:
                    first_item = items[0]
                    print(f"First item keys: {list(first_item.keys())}")
                    print(f"First item user_id: {first_item.get('user_id', 'NOT_FOUND')}")
                    print(f"First item userId: {first_item.get('userId', 'NOT_FOUND')}")
        else:
            print(f"Test endpoint error: {test_response.text}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_outfit_data() 