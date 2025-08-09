#!/usr/bin/env python3

import requests
import json

# Test the outfits collection specifically
base_url = "https://closetgptrenew-backend-production.up.railway.app"

def test_outfits_collection():
    """Test to see if there are outfits in the outfits collection"""
    
    print("🔍 Testing outfits collection...")
    
    # Check if there are any outfits in the database
    try:
        # Try to get outfits without user filtering first
        test_response = requests.get(f"{base_url}/api/outfits/test", timeout=10)
        print(f"Test outfits endpoint status: {test_response.status_code}")
        if test_response.status_code == 200:
            test_data = test_response.json()
            print(f"Found {len(test_data)} outfits in test endpoint")
            
            # Check if these are real outfits or mock outfits
            if test_data:
                first_outfit = test_data[0]
                print(f"First outfit ID: {first_outfit.get('id', 'NO_ID')}")
                print(f"First outfit name: {first_outfit.get('name', 'NO_NAME')}")
                print(f"First outfit user_id: {first_outfit.get('user_id', 'NO_USER_ID')}")
                
                # Check if it has real items
                items = first_outfit.get('items', [])
                print(f"Number of items in first outfit: {len(items)}")
                if items:
                    first_item = items[0]
                    print(f"First item ID: {first_item.get('id', 'NO_ITEM_ID')}")
                    print(f"First item name: {first_item.get('name', 'NO_ITEM_NAME')}")
        else:
            print(f"Test endpoint error: {test_response.text}")
    except Exception as e:
        print(f"Test endpoint failed: {e}")

if __name__ == "__main__":
    test_outfits_collection() 