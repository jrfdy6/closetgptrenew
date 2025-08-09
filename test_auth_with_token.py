#!/usr/bin/env python3

import requests
import time
import json

# Test the backend outfits endpoint with a mock authentication token
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_auth_with_token():
    """Test the backend outfits endpoint with a mock authentication token"""
    
    print("🔍 Testing backend outfits endpoint with mock authentication token...")
    
    # Create a mock Firebase ID token (this won't work, but let's see what happens)
    mock_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vY2xvc2VncHRyZW5ldyIsImF1ZCI6ImNsb3NldGdwdHJlbmV3IiwiaWF0IjoxNzUwMTUxNjgwLCJleHAiOjE3NTAyMzc2ODAsInN1YiI6ImRBTnFqaUkwQ0tnYWl0eHpZdHcxYmh0dlFyRzMiLCJ1aWQiOiJkQU5xamlJMENrZ2FpdHh6WXR3MWJodHZRckczIn0.mock_signature"
    
    # Test the main outfits endpoint with mock auth
    try:
        start_time = time.time()
        outfits_response = requests.get(
            f"{base_url}/api/outfits/", 
            headers={'Authorization': f'Bearer {mock_token}'},
            timeout=30
        )
        outfits_time = time.time() - start_time
        print(f"Main outfits endpoint (mock auth): {outfits_response.status_code} in {outfits_time:.2f}s")
        if outfits_response.status_code == 200:
            outfits_data = outfits_response.json()
            print(f"  Found {len(outfits_data)} outfits")
        else:
            print(f"  Error: {outfits_response.text}")
    except Exception as e:
        print(f"Main outfits endpoint failed: {e}")
    
    # Test the test endpoint (should work without auth)
    try:
        start_time = time.time()
        test_response = requests.get(f"{base_url}/api/outfits/test", timeout=30)
        test_time = time.time() - start_time
        print(f"Test endpoint: {test_response.status_code} in {test_time:.2f}s")
        if test_response.status_code == 200:
            test_data = test_response.json()
            print(f"  Found {len(test_data)} outfits")
            
            # Check if these are real outfits or mock outfits
            if test_data:
                first_outfit = test_data[0]
                print(f"  First outfit keys: {list(first_outfit.keys())}")
                if 'items' in first_outfit and first_outfit['items']:
                    first_item = first_outfit['items'][0]
                    print(f"  First item keys: {list(first_item.keys())}")
                    if 'userId' in first_item:
                        print(f"  First item userId: {first_item['userId']}")
        else:
            print(f"  Error: {test_response.text}")
    except Exception as e:
        print(f"Test endpoint failed: {e}")

if __name__ == "__main__":
    test_auth_with_token() 