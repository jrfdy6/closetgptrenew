#!/usr/bin/env python3

import requests
import json

def test_feedback_endpoint():
    """Test the feedback endpoint to see if it's accessible."""
    
    backend_url = "http://localhost:3001"
    endpoint = f"{backend_url}/api/feedback/outfit"
    
    print(f"🔍 Testing feedback endpoint: {endpoint}")
    print("=" * 50)
    
    # Test data
    test_payload = {
        "outfit_id": "test_outfit_id",
        "feedback_type": "like",
        "rating": 5,
        "context_data": {
            "user_agent": "test_script",
            "platform": "test"
        }
    }
    
    print(f"Test payload: {json.dumps(test_payload, indent=2)}")
    print()
    
    try:
        # Test without authentication (should fail with 401)
        print("1. Testing without authentication (should fail):")
        response = requests.post(endpoint, json=test_payload)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
        
        # Test with invalid authentication (should fail with 401)
        print("2. Testing with invalid authentication (should fail):")
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.post(endpoint, json=test_payload, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print()
        
        # Test endpoint accessibility
        print("3. Testing endpoint accessibility:")
        try:
            response = requests.get(f"{backend_url}/health")
            print(f"   Health check status: {response.status_code}")
            print(f"   Health check response: {response.text}")
        except Exception as e:
            print(f"   Health check failed: {e}")
        
    except Exception as e:
        print(f"Error testing endpoint: {e}")

if __name__ == "__main__":
    test_feedback_endpoint() 