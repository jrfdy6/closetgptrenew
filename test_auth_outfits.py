#!/usr/bin/env python3

import requests
import json

# Test the outfits endpoint with authentication
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_auth_outfits():
    """Test the outfits endpoint with authentication"""
    
    print("🔍 Testing outfits endpoint with authentication...")
    
    # Your actual user ID
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    # Test the debug endpoint to see the current state
    try:
        debug_response = requests.get(f"{base_url}/api/outfits/debug", timeout=10)
        print(f"Debug endpoint status: {debug_response.status_code}")
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f"Debug info: {json.dumps(debug_data, indent=2)}")
    except Exception as e:
        print(f"Debug endpoint failed: {e}")
    
    # Test the main outfits endpoint without auth (should return 403)
    try:
        outfits_response = requests.get(f"{base_url}/api/outfits/", timeout=10)
        print(f"Main outfits endpoint status (no auth): {outfits_response.status_code}")
        if outfits_response.status_code != 200:
            print(f"Main endpoint error: {outfits_response.text}")
    except Exception as e:
        print(f"Main endpoint failed: {e}")
    
    # Test the test endpoint (should work without auth)
    try:
        test_response = requests.get(f"{base_url}/api/outfits/test", timeout=10)
        print(f"Test outfits endpoint status: {test_response.status_code}")
        if test_response.status_code == 200:
            test_data = test_response.json()
            print(f"Test endpoint found {len(test_data)} outfits")
            
            # Check if any of these outfits have items belonging to our user
            user_outfits = []
            for outfit in test_data:
                items = outfit.get('items', [])
                for item in items:
                    if isinstance(item, dict) and item.get('userId') == user_id:
                        user_outfits.append(outfit)
                        break
            
            print(f"Found {len(user_outfits)} outfits with items belonging to user {user_id}")
            
            if user_outfits:
                print(f"First user outfit: {json.dumps(user_outfits[0], indent=2, default=str)}")
        else:
            print(f"Test endpoint error: {test_response.text}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_auth_outfits() 