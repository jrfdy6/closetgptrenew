#!/usr/bin/env python3
"""
Debug script to test the forgotten gems endpoint
"""

import requests
import json
import sys

def test_forgotten_gems_endpoint():
    """Test the forgotten gems endpoint with proper authentication."""
    
    # Test the frontend API route
    print("🔍 Testing frontend API route...")
    
    # Test without authentication (should return 401)
    response = requests.get('http://localhost:3000/api/wardrobe/forgotten-gems')
    print(f"Frontend API (no auth): {response.status_code} - {response.text}")
    
    # Test with fake token (should return 401 from backend)
    headers = {'Authorization': 'Bearer fake-token'}
    response = requests.get('http://localhost:3000/api/wardrobe/forgotten-gems', headers=headers)
    print(f"Frontend API (fake token): {response.status_code} - {response.text}")
    
    # Test backend directly
    print("\n🔍 Testing backend API route...")
    
    # Test without authentication (should return 401)
    response = requests.get('http://localhost:3001/api/wardrobe/forgotten-gems')
    print(f"Backend API (no auth): {response.status_code} - {response.text}")
    
    # Test with fake token (should return 401)
    headers = {'Authorization': 'Bearer fake-token'}
    response = requests.get('http://localhost:3001/api/wardrobe/forgotten-gems', headers=headers)
    print(f"Backend API (fake token): {response.status_code} - {response.text}")
    
    print("\n✅ Debug test completed!")

if __name__ == "__main__":
    test_forgotten_gems_endpoint() 