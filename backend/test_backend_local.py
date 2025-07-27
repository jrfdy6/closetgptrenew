#!/usr/bin/env python3
"""
Simple test script to verify the backend works locally
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_backend_health():
    """Test the backend health endpoint"""
    try:
        response = requests.get("http://localhost:8080/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_image_analysis_endpoint():
    """Test the image analysis endpoint"""
    try:
        # Test with a sample image URL
        test_data = {
            "image": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=400&fit=crop&crop=center"
        }
        
        response = requests.post(
            "http://localhost:8080/api/analyze-image",
            json=test_data,
            timeout=30
        )
        
        print(f"✅ Image analysis test: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Analysis result: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
        
        return True
    except Exception as e:
        print(f"❌ Image analysis test failed: {e}")
        return False

def main():
    print("🧪 Testing ClosetGPT Backend...")
    
    # Test health endpoint
    health_ok = test_backend_health()
    
    # Test image analysis
    analysis_ok = test_image_analysis_endpoint()
    
    if health_ok and analysis_ok:
        print("✅ All tests passed! Backend is working correctly.")
    else:
        print("❌ Some tests failed. Check the backend logs.")

if __name__ == "__main__":
    main() 