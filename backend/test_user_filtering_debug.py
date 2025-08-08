#!/usr/bin/env python3
"""
Test script to trigger user filtering debug logs.
This will call the /api/outfits/debug-user-filtering endpoint to show detailed logs.
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://acceptable-wisdom-production-ac06.up.railway.app"  # Production backend with latest code
TEST_USER_ID = "test_user_123"  # You can change this to test with different user IDs

def test_user_filtering_debug():
    """Test the user filtering debug endpoint."""
    print("🔍 Testing User Filtering Debug")
    print("=" * 60)
    print(f"📅 Test started at: {datetime.now()}")
    print(f"🎯 Backend URL: {BACKEND_URL}")
    print(f"👤 Test User ID: {TEST_USER_ID}")
    print()
    
    try:
        # Call the debug endpoint
        url = f"{BACKEND_URL}/api/outfits/debug-user-filtering"
        
        # For this test, we'll simulate the authentication by adding a header
        # In a real scenario, you'd need to get a proper JWT token
        headers = {
            "Content-Type": "application/json",
            "X-User-ID": TEST_USER_ID  # This is a simplified approach for testing
        }
        
        print(f"🌐 Making request to: {url}")
        print(f"📋 Headers: {headers}")
        print()
        
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Debug data received:")
            print(json.dumps(data, indent=2))
            
            # Summary
            print("\n📈 Summary:")
            print(f"   - Current User ID: {data.get('current_user_id')}")
            print(f"   - Total Outfits Analyzed: {data.get('total_outfits_analyzed')}")
            print(f"   - Direct User ID Matches: {data.get('outfits_with_direct_user_id_match')}")
            print(f"   - Item UserId Matches: {data.get('outfits_with_item_userId_match')}")
            print(f"   - No Matches: {data.get('outfits_with_no_match')}")
            
            # Show detailed analysis for first few outfits
            detailed_analysis = data.get('detailed_analysis', [])
            if detailed_analysis:
                print(f"\n🔍 Detailed Analysis (showing first 3 outfits):")
                for i, outfit in enumerate(detailed_analysis[:3]):
                    print(f"   Outfit {i+1}: {outfit['outfit_id']}")
                    print(f"     - user_id: '{outfit['outfit_user_id']}'")
                    print(f"     - userId: '{outfit['outfit_userId']}'")
                    print(f"     - Items: {outfit['items_count']}")
                    print(f"     - Direct Match: {outfit['direct_match']}")
                    print(f"     - Item Match: {outfit['item_match']}")
                    print()
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to backend")
        print("   Make sure the backend is running on the correct port")
        print("   You can start it with: cd backend && python -m uvicorn src.app_full:app --reload")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_with_real_user():
    """Test with a real user ID from your database."""
    print("\n" + "=" * 60)
    print("🔍 Testing with Real User ID")
    print("=" * 60)
    
    # You can modify this to use a real user ID from your database
    real_user_id = input("Enter a real user ID to test with (or press Enter to skip): ").strip()
    
    if real_user_id:
        print(f"👤 Testing with real user ID: {real_user_id}")
        
        try:
            url = f"{BACKEND_URL}/api/outfits/debug-user-filtering"
            headers = {
                "Content-Type": "application/json",
                "X-User-ID": real_user_id
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Real user test successful!")
                print(f"   - User ID: {data.get('current_user_id')}")
                print(f"   - Outfits Found: {data.get('total_outfits_analyzed')}")
                print(f"   - Direct Matches: {data.get('outfits_with_direct_user_id_match')}")
                print(f"   - Item Matches: {data.get('outfits_with_item_userId_match')}")
            else:
                print(f"❌ Real user test failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Real user test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting User Filtering Debug Test")
    print("This script will call the debug endpoint to show detailed logs")
    print("Make sure your backend is running and accessible")
    print()
    
    # Test with default user ID
    test_user_filtering_debug()
    
    # Optionally test with real user ID
    test_with_real_user()
    
    print("\n✅ Test completed!")
    print("📝 Check the backend logs for detailed debugging information")
    print("🔍 Look for lines starting with '🔍 DEBUG:' in the backend console") 