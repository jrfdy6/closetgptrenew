#!/usr/bin/env python3

import requests
import json

# Test the debug fields endpoint
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_debug_fields():
    """Test the debug fields endpoint to see field names in outfits"""
    
    print("🔍 Testing debug fields endpoint...")
    
    try:
        debug_response = requests.get(f"{base_url}/api/outfits/debug-fields", timeout=10)
        print(f"Debug fields endpoint status: {debug_response.status_code}")
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f"Debug fields response: {json.dumps(debug_data, indent=2)}")
        else:
            print(f"Debug fields error: {debug_response.text}")
    except Exception as e:
        print(f"Debug fields failed: {e}")

if __name__ == "__main__":
    test_debug_fields() 