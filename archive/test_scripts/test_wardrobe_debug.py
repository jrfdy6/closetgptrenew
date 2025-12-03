#!/usr/bin/env python3
"""
Test Wardrobe Debug Endpoint

Try the debug endpoint that might not require authentication.
"""

import requests
import json

def test_wardrobe_debug():
    """Test the wardrobe debug endpoint"""
    
    print("🔍 TESTING WARDROBE DEBUG ENDPOINT")
    print("=" * 60)
    
    try:
        # Try the debug endpoint
        response = requests.get(
            "https://closetgptrenew-backend-production.up.railway.app/api/wardrobe/debug",
            timeout=30
        )
        
        print(f"📊 Debug API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            debug_data = response.json()
            print(f"✅ SUCCESS: Debug endpoint worked")
            print(f"📋 Debug response: {debug_data}")
            
            # Check if there are any items
            if 'items' in debug_data and len(debug_data['items']) > 0:
                items = debug_data['items']
                print(f"📊 Found {len(items)} items in debug data")
                
                # Show sample items
                print(f"\n📋 SAMPLE ITEMS:")
                for i, item in enumerate(items[:3], 1):
                    print(f"   {i}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                
                return items
            else:
                print(f"❌ No items found in debug data")
                return []
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error: {response.text}")
            return []
                
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        return []

if __name__ == "__main__":
    test_wardrobe_debug()



