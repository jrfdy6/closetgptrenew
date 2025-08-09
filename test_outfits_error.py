#!/usr/bin/env python3

import requests
import json

# Test to see what's causing the 500 error
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_outfits_error():
    """Test to see what's causing the 500 error on outfits endpoint"""
    
    print("🔍 Testing outfits endpoint for 500 error...")
    
    # Test the health endpoint first
    try:
        health_response = requests.get(f"{base_url}/api/outfits/health", timeout=10)
        print(f"Health endpoint status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health response: {health_response.json()}")
    except Exception as e:
        print(f"Health endpoint failed: {e}")
    
    # Test the debug endpoint
    try:
        debug_response = requests.get(f"{base_url}/api/outfits/debug", timeout=10)
        print(f"Debug endpoint status: {debug_response.status_code}")
        if debug_response.status_code == 200:
            print(f"Debug response: {debug_response.json()}")
    except Exception as e:
        print(f"Debug endpoint failed: {e}")
    
    # Test the test endpoint (should work without auth)
    try:
        test_response = requests.get(f"{base_url}/api/outfits/test", timeout=10)
        print(f"Test endpoint status: {test_response.status_code}")
        if test_response.status_code == 200:
            test_data = test_response.json()
            print(f"Test endpoint found {len(test_data)} outfits")
        else:
            print(f"Test endpoint error: {test_response.text}")
    except Exception as e:
        print(f"Test endpoint failed: {e}")
    
    # Test the main outfits endpoint (this should give us the 500 error details)
    try:
        outfits_response = requests.get(f"{base_url}/api/outfits/", timeout=10)
        print(f"Main outfits endpoint status: {outfits_response.status_code}")
        if outfits_response.status_code == 200:
            outfits_data = outfits_response.json()
            print(f"Main endpoint found {len(outfits_data)} outfits")
        else:
            print(f"Main endpoint error: {outfits_response.text}")
    except Exception as e:
        print(f"Main endpoint failed: {e}")

if __name__ == "__main__":
    test_outfits_error() 