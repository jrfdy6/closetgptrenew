#!/usr/bin/env python3

import requests
import json

# Test the outfits endpoint
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_outfits_endpoint():
    """Test the outfits endpoint to see what's happening"""
    
    print("🔍 Testing outfits endpoint...")
    
    # Test the health endpoint first
    try:
        health_response = requests.get(f"{base_url}/api/outfits/health", timeout=10)
        print(f"Health check status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health response: {health_response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test the debug endpoint
    try:
        debug_response = requests.get(f"{base_url}/api/outfits/debug", timeout=10)
        print(f"Debug endpoint status: {debug_response.status_code}")
        if debug_response.status_code == 200:
            print(f"Debug response: {debug_response.json()}")
    except Exception as e:
        print(f"Debug endpoint failed: {e}")
    
    # Test the main outfits endpoint (without auth for now)
    try:
        outfits_response = requests.get(f"{base_url}/api/outfits/", timeout=10)
        print(f"Outfits endpoint status: {outfits_response.status_code}")
        if outfits_response.status_code == 200:
            outfits_data = outfits_response.json()
            print(f"Found {len(outfits_data)} outfits")
            if outfits_data:
                print(f"First outfit: {json.dumps(outfits_data[0], indent=2, default=str)}")
        else:
            print(f"Error response: {outfits_response.text}")
    except Exception as e:
        print(f"Outfits endpoint failed: {e}")

if __name__ == "__main__":
    test_outfits_endpoint() 