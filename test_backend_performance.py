#!/usr/bin/env python3

import requests
import time
import json

# Test the backend performance
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_backend_performance():
    """Test the backend response time"""
    
    print("🔍 Testing backend performance...")
    
    # Test the health endpoint first
    try:
        start_time = time.time()
        health_response = requests.get(f"{base_url}/health", timeout=10)
        health_time = time.time() - start_time
        print(f"Health endpoint: {health_response.status_code} in {health_time:.2f}s")
    except Exception as e:
        print(f"Health endpoint failed: {e}")
    
    # Test the debug endpoint
    try:
        start_time = time.time()
        debug_response = requests.get(f"{base_url}/api/outfits/debug", timeout=10)
        debug_time = time.time() - start_time
        print(f"Debug endpoint: {debug_response.status_code} in {debug_time:.2f}s")
    except Exception as e:
        print(f"Debug endpoint failed: {e}")
    
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
    
    # Test the main outfits endpoint (this might be slow)
    try:
        start_time = time.time()
        outfits_response = requests.get(f"{base_url}/api/outfits/", timeout=30)
        outfits_time = time.time() - start_time
        print(f"Main outfits endpoint: {outfits_response.status_code} in {outfits_time:.2f}s")
        if outfits_response.status_code == 200:
            outfits_data = outfits_response.json()
            print(f"  Found {len(outfits_data)} outfits")
        else:
            print(f"  Error: {outfits_response.text}")
    except Exception as e:
        print(f"Main outfits endpoint failed: {e}")

if __name__ == "__main__":
    test_backend_performance() 