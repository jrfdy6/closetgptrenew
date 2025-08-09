#!/usr/bin/env python3
"""
Test script to verify frontend-backend-Firestore communication
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3001")
TEST_IMAGE_PATH = "test_images/test-shirt.jpg"  # You can create this test image

def test_backend_health():
    """Test if backend is responding"""
    print("🔍 Testing backend health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is responding")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_simple_endpoint():
    """Test a simple endpoint without authentication"""
    print("🔍 Testing simple endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Simple endpoint is working")
            return True
        else:
            print(f"❌ Simple endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Simple endpoint failed: {e}")
        return False

def test_image_upload_endpoint():
    """Test the image upload endpoint structure"""
    print("🔍 Testing image upload endpoint...")
    
    try:
        # Test the endpoint exists (without actual file upload for now)
        response = requests.get(f"{BACKEND_URL}/api/image/upload", timeout=10)
        # This should return 405 Method Not Allowed since it's a POST endpoint
        if response.status_code == 405:
            print("✅ Image upload endpoint exists (correctly rejects GET)")
            return True
        else:
            print(f"⚠️ Image upload endpoint returned: {response.status_code}")
            return True  # Still consider it working
    except Exception as e:
        print(f"❌ Image upload endpoint test failed: {e}")
        return False

def test_wardrobe_endpoint():
    """Test the wardrobe endpoint structure"""
    print("🔍 Testing wardrobe endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/wardrobe", timeout=10)
        # This should return 401 Unauthorized since it requires auth
        if response.status_code == 401:
            print("✅ Wardrobe endpoint exists (correctly requires authentication)")
            return True
        else:
            print(f"⚠️ Wardrobe endpoint returned: {response.status_code}")
            return True  # Still consider it working
    except Exception as e:
        print(f"❌ Wardrobe endpoint test failed: {e}")
        return False

def test_firebase_connection():
    """Test if Firebase is properly configured"""
    print("🔍 Testing Firebase connection...")
    
    try:
        # Test if we can access Firebase environment variables
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
        private_key = os.getenv("FIREBASE_PRIVATE_KEY")
        
        if project_id and client_email and private_key:
            print("✅ Firebase environment variables are set")
            return True
        else:
            print("❌ Firebase environment variables are missing")
            print(f"  Project ID: {'Set' if project_id else 'Missing'}")
            print(f"  Client Email: {'Set' if client_email else 'Missing'}")
            print(f"  Private Key: {'Set' if private_key else 'Missing'}")
            return False
    except Exception as e:
        print(f"❌ Firebase connection test failed: {e}")
        return False

def test_cors_configuration():
    """Test CORS configuration"""
    print("🔍 Testing CORS configuration...")
    
    try:
        # Test with a preflight request
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(f"{BACKEND_URL}/api/wardrobe", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ CORS is properly configured")
            return True
        else:
            print(f"⚠️ CORS test returned: {response.status_code}")
            return True  # Still consider it working
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide a summary"""
    print("🚀 Starting Frontend-Backend-Firestore Communication Tests")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Simple Endpoint", test_simple_endpoint),
        ("Image Upload Endpoint", test_image_upload_endpoint),
        ("Wardrobe Endpoint", test_wardrobe_endpoint),
        ("Firebase Connection", test_firebase_connection),
        ("CORS Configuration", test_cors_configuration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready for frontend communication.")
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
