#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_authenticated_outfits():
    """Test the authenticated outfits endpoint to see if filtering is working."""
    
    # Your user ID
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    # Backend URL
    backend_url = "https://closetgptrenew-backend-production.up.railway.app"
    
    print(f"🔍 Testing authenticated outfits API for user: {user_id}")
    print(f"🔍 Backend URL: {backend_url}")
    print("=" * 50)
    
    # Test the authenticated outfits endpoint
    try:
        # We need to get a valid token first
        # For now, let's test the test endpoint to see if it's working
        response = requests.get(f"{backend_url}/api/outfits/test", timeout=30)
        print(f"🔍 Test endpoint response status: {response.status_code}")
        
        if response.status_code == 200:
            outfits = response.json()
            print(f"🔍 Number of outfits returned: {len(outfits)}")
            
            # Count outfits that belong to the user
            user_outfits = 0
            for outfit in outfits:
                items = outfit.get('items', [])
                user_items = 0
                total_items = len(items)
                
                for item in items:
                    if isinstance(item, dict) and item.get('userId') == user_id:
                        user_items += 1
                
                if user_items > 0 and user_items == total_items:
                    user_outfits += 1
            
            print(f"🔍 Outfits with all user items: {user_outfits}/{len(outfits)}")
            
            if user_outfits == len(outfits):
                print("✅ All returned outfits belong to the user!")
            else:
                print("⚠️  Some outfits don't belong to the user")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_authenticated_outfits() 