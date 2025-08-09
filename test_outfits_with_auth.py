#!/usr/bin/env python3

import requests
import json

# Test the outfits endpoint with authentication
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_outfits_with_auth():
    """Test the outfits endpoint with authentication to see what's happening"""
    
    print("🔍 Testing outfits endpoint with authentication...")
    
    # First, let's check if there are any outfits in the database without auth
    try:
        test_response = requests.get(f"{base_url}/api/outfits/test", timeout=10)
        print(f"Test outfits endpoint status: {test_response.status_code}")
        if test_response.status_code == 200:
            test_data = test_response.json()
            print(f"Test outfits found: {len(test_data)} outfits")
            if test_data:
                print(f"First test outfit: {json.dumps(test_data[0], indent=2, default=str)}")
        else:
            print(f"Test endpoint error: {test_response.text}")
    except Exception as e:
        print(f"Test endpoint failed: {e}")
    
    # Check the debug endpoint to see the current state
    try:
        debug_response = requests.get(f"{base_url}/api/outfits/debug", timeout=10)
        print(f"Debug endpoint status: {debug_response.status_code}")
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f"Debug info: {json.dumps(debug_data, indent=2)}")
    except Exception as e:
        print(f"Debug endpoint failed: {e}")

if __name__ == "__main__":
    test_outfits_with_auth() 