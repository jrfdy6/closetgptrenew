#!/usr/bin/env python3
"""
Comprehensive Production Deployment Test
Tests all critical functionality of the ClosetGPT API
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BACKEND_URL = "https://closetgptrenew-backend-production.up.railway.app"
FRONTEND_URL = "https://closetgpt-frontend.vercel.app"

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data}")
            return True
        else:
            print(f"❌ Backend Health Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Health Error: {e}")
        return False

def test_backend_root():
    """Test backend root endpoint"""
    print("🔍 Testing Backend Root...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Root: {data}")
            return True
        else:
            print(f"❌ Backend Root Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend Root Error: {e}")
        return False

def test_frontend_health():
    """Test frontend health"""
    print("🔍 Testing Frontend Health...")
    try:
        response = requests.head(f"{FRONTEND_URL}", timeout=10)
        if response.status_code == 200:
            print(f"✅ Frontend Health: {response.status_code}")
            return True
        else:
            print(f"⚠️  Frontend Health: {response.status_code} - {response.headers.get('x-vercel-error', 'Unknown')}")
            return False
    except Exception as e:
        print(f"❌ Frontend Health Error: {e}")
        return False

def test_cors_configuration():
    """Test CORS configuration"""
    print("🔍 Testing CORS Configuration...")
    try:
        response = requests.options(f"{BACKEND_URL}/", timeout=10)
        cors_headers = response.headers.get('access-control-allow-origin', '')
        if cors_headers:
            print(f"✅ CORS Configured: {cors_headers}")
            return True
        else:
            print("⚠️  CORS Headers Not Found")
            return False
    except Exception as e:
        print(f"❌ CORS Test Error: {e}")
        return False

def test_environment_variables():
    """Test environment variable accessibility"""
    print("🔍 Testing Environment Variables...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            port = data.get('port', 'unknown')
            print(f"✅ Environment Variables: PORT={port}")
            return True
        else:
            print("❌ Environment Variables Test Failed")
            return False
    except Exception as e:
        print(f"❌ Environment Variables Error: {e}")
        return False

def test_api_documentation():
    """Test API documentation availability"""
    print("🔍 Testing API Documentation...")
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API Documentation Available")
            return True
        else:
            print(f"⚠️  API Documentation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Documentation Error: {e}")
        return False

def test_openapi_spec():
    """Test OpenAPI specification"""
    print("🔍 Testing OpenAPI Specification...")
    try:
        response = requests.get(f"{BACKEND_URL}/openapi.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            title = data.get('info', {}).get('title', 'Unknown')
            print(f"✅ OpenAPI Spec: {title}")
            return True
        else:
            print(f"❌ OpenAPI Spec Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenAPI Spec Error: {e}")
        return False

def main():
    """Run comprehensive production tests"""
    print("🚀 Starting Comprehensive Production Deployment Test")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Backend Root", test_backend_root),
        ("Frontend Health", test_frontend_health),
        ("CORS Configuration", test_cors_configuration),
        ("Environment Variables", test_environment_variables),
        ("API Documentation", test_api_documentation),
        ("OpenAPI Specification", test_openapi_spec),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} Exception: {e}")
            results.append((test_name, False))
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Production deployment is working correctly.")
    elif passed >= total * 0.7:
        print("⚠️  MOST TESTS PASSED. Some issues need attention.")
    else:
        print("🚨 MANY TESTS FAILED. Production deployment has issues.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 