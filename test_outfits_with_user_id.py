#!/usr/bin/env python3

import requests
import json

# Test the outfits endpoint with a specific user ID
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_outfits_with_user_id():
    """Test the outfits endpoint with a specific user ID"""
    
    print("🔍 Testing outfits endpoint with user ID...")
    
    # Your actual user ID from the debug output
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    # Try to get outfits for this specific user
    try:
        # First, let's check if there are any outfits for this user by looking at the test endpoint
        test_response = requests.get(f"{base_url}/api/outfits/test", timeout=10)
        print(f"Test outfits endpoint status: {test_response.status_code}")
        if test_response.status_code == 200:
            test_data = test_response.json()
            print(f"Found {len(test_data)} outfits in test endpoint")
            
            # Check if any of these outfits belong to our user
            user_outfits = [outfit for outfit in test_data if outfit.get('user_id') == user_id]
            print(f"Found {len(user_outfits)} outfits for user {user_id}")
            
            if user_outfits:
                print(f"First user outfit: {json.dumps(user_outfits[0], indent=2, default=str)}")
        else:
            print(f"Test endpoint error: {test_response.text}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_outfits_with_user_id() 