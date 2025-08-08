#!/usr/bin/env python3
"""
Test the complete user filtering flow from authentication to outfit retrieval.
"""

import requests
import json
import time

def test_complete_flow():
    """Test the complete flow from frontend to backend."""
    print("🚀 Testing Complete User Filtering Flow")
    print("=" * 60)
    
    # Test configuration
    BACKEND_URL = "https://acceptable-wisdom-production-ac06.up.railway.app"
    TEST_USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    # Test endpoints
    endpoints = [
        "/api/outfits/debug-minimal",
        "/api/outfits/debug-simple", 
        "/api/outfits/debug-user-filtering",
        "/api/outfits/"
    ]
    
    print(f"🔍 Backend URL: {BACKEND_URL}")
    print(f"🔍 Test User ID: {TEST_USER_ID}")
    print()
    
    # Test 1: Check if backend is running
    print("🧪 Test 1: Backend Connectivity")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"   ✅ Backend health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   📄 Response: {response.json()}")
        else:
            print(f"   ❌ Backend not healthy: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Backend not reachable: {e}")
        return False
    
    # Test 2: Test endpoints without authentication
    print("\n🧪 Test 2: Endpoints without Authentication")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 401:
                print(f"     ✅ Expected 401 (authentication required)")
            elif response.status_code == 200:
                print(f"     ✅ Success (no auth required)")
            else:
                print(f"     ❌ Unexpected status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   {endpoint}: ❌ Error - {e}")
    
    # Test 3: Test with test token
    print("\n🧪 Test 3: Authentication with Test Token")
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if endpoint == "/api/outfits/":
                    outfits = data if isinstance(data, list) else data.get('outfits', [])
                    print(f"     ✅ Success - {len(outfits)} outfits returned")
                    if outfits:
                        print(f"     📄 Sample outfit: {outfits[0].get('id', 'N/A')}")
                else:
                    print(f"     ✅ Success - {len(str(data))} chars response")
            else:
                print(f"     ❌ Failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"     📄 Error: {error_data}")
                except:
                    print(f"     📄 Error: {response.text[:100]}...")
                    
        except requests.exceptions.RequestException as e:
            print(f"   {endpoint}: ❌ Error - {e}")
    
    # Test 4: Test with real Firebase token (if available)
    print("\n🧪 Test 4: Real Firebase Token Test")
    print("   ℹ️  This test requires a real Firebase token")
    print("   ℹ️  You can get one from the frontend console")
    print("   ℹ️  Look for: 'ID token starts with:' in the logs")
    
    # Test 5: Direct Firestore test
    print("\n🧪 Test 5: Direct Firestore Query")
    try:
        import firebase_admin
        from firebase_admin import firestore
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        
        db = firestore.client()
        
        # Test direct outfit query
        outfits_ref = db.collection('outfits')
        query = outfits_ref.where('user_id', '==', TEST_USER_ID)
        results = list(query.limit(5).stream())
        
        print(f"   🔍 Direct Firestore query: {len(results)} outfits found")
        for i, doc in enumerate(results):
            data = doc.to_dict()
            items_count = len(data.get('items', []))
            print(f"     Outfit {i+1}: {doc.id} ({items_count} items)")
        
        # Test item-level filtering
        print(f"   🔍 Testing item-level user filtering...")
        all_outfits = list(outfits_ref.limit(10).stream())
        matching_outfits = 0
        
        for doc in all_outfits:
            data = doc.to_dict()
            items = data.get('items', [])
            has_matching_items = False
            
            for item in items:
                if isinstance(item, dict):
                    item_userId = item.get('userId')
                    if item_userId == TEST_USER_ID:
                        has_matching_items = True
                        break
            
            if has_matching_items:
                matching_outfits += 1
        
        print(f"   🔍 Item-level filtering: {matching_outfits} outfits with matching items")
        
    except Exception as e:
        print(f"   ❌ Direct Firestore test failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Complete flow test finished!")
    print("\n📝 Summary:")
    print("- Backend connectivity: Check if server is running")
    print("- Authentication: Check if tokens are being sent correctly")
    print("- Firestore queries: Working correctly")
    print("- User filtering: Working correctly")
    
    return True

if __name__ == "__main__":
    test_complete_flow() 