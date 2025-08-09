#!/usr/bin/env python3

import requests
import json

# Test to simulate the frontend authentication flow
base_url = "https://closetgpt-frontend-jb6n38zyg-johnnie-fields-projects.vercel.app"

def test_frontend_auth():
    """Test the frontend API route to see what's happening"""
    
    print("🔍 Testing frontend API route...")
    
    # Test the frontend outfits API route
    try:
        # This should return a 500 error based on the logs
        outfits_response = requests.get(f"{base_url}/api/outfits", timeout=10)
        print(f"Frontend outfits API status: {outfits_response.status_code}")
        if outfits_response.status_code == 200:
            outfits_data = outfits_response.json()
            print(f"Frontend API found {len(outfits_data)} outfits")
        else:
            print(f"Frontend API error: {outfits_response.text}")
    except Exception as e:
        print(f"Frontend API failed: {e}")
    
    # Test the backend directly to compare
    backend_url = "https://closetgptrenew-backend-production.up.railway.app"
    try:
        backend_response = requests.get(f"{backend_url}/api/outfits/", timeout=10)
        print(f"Backend outfits API status: {backend_response.status_code}")
        if backend_response.status_code == 200:
            backend_data = backend_response.json()
            print(f"Backend API found {len(backend_data)} outfits")
        else:
            print(f"Backend API error: {backend_response.text}")
    except Exception as e:
        print(f"Backend API failed: {e}")

if __name__ == "__main__":
    test_frontend_auth() 