#!/usr/bin/env python3

import requests
import time
import json

# Test the backend outfits endpoint with authentication timeout
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_auth_timeout():
    """Test if the backend outfits endpoint times out with authentication"""
    
    print("🔍 Testing backend outfits endpoint with authentication timeout...")
    
    # Test the main outfits endpoint without auth (should be fast)
    try:
        start_time = time.time()
        outfits_response = requests.get(f"{base_url}/api/outfits/", timeout=30)
        outfits_time = time.time() - start_time
        print(f"Main outfits endpoint (no auth): {outfits_response.status_code} in {outfits_time:.2f}s")
        if outfits_response.status_code != 200:
            print(f"  Error: {outfits_response.text}")
    except Exception as e:
        print(f"Main outfits endpoint failed: {e}")
    
    # Test the test endpoint (should be fast)
    try:
        start_time = time.time()
        test_response = requests.get(f"{base_url}/api/outfits/test", timeout=30)
        test_time = time.time() - start_time
        print(f"Test endpoint: {test_response.status_code} in {test_time:.2f}s")
        if test_response.status_code == 200:
            test_data = test_response.json()
            print(f"  Found {len(test_data)} outfits")
    except Exception as e:
        print(f"Test endpoint failed: {e}")
    
    # Test the debug endpoint (should be fast)
    try:
        start_time = time.time()
        debug_response = requests.get(f"{base_url}/api/outfits/debug", timeout=30)
        debug_time = time.time() - start_time
        print(f"Debug endpoint: {debug_response.status_code} in {debug_time:.2f}s")
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f"  Debug info: {json.dumps(debug_data, indent=2)}")
    except Exception as e:
        print(f"Debug endpoint failed: {e}")

if __name__ == "__main__":
    test_auth_timeout() 