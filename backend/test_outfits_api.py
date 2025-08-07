#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_outfits_api():
    """Test the deployed backend API to see what outfits are returned."""
    
    # Your user ID
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    # Backend URL
    backend_url = "https://closetgptrenew-backend-production.up.railway.app"
    
    print(f"🔍 Testing outfits API for user: {user_id}")
    print(f"🔍 Backend URL: {backend_url}")
    print("=" * 50)
    
    # Test the outfits test endpoint (no auth required)
    try:
        response = requests.get(f"{backend_url}/api/outfits/test", timeout=30)
        print(f"🔍 Response status: {response.status_code}")
        
        if response.status_code == 200:
            outfits = response.json()
            print(f"🔍 Number of outfits returned: {len(outfits)}")
            
            print("\n" + "=" * 50)
            print("📋 FIRST 10 OUTFITS:")
            for i, outfit in enumerate(outfits[:10]):
                print(f"\n{i+1}. {outfit.get('name', 'Unknown')}")
                print(f"   ID: {outfit.get('id', 'Unknown')}")
                print(f"   Style: {outfit.get('style', 'Unknown')}")
                print(f"   Occasion: {outfit.get('occasion', 'Unknown')}")
                print(f"   Items count: {len(outfit.get('items', []))}")
                
                # Check items for userId
                items = outfit.get('items', [])
                user_items = 0
                total_items = len(items)
                
                for item in items:
                    if isinstance(item, dict) and item.get('userId') == user_id:
                        user_items += 1
                
                print(f"   User items: {user_items}/{total_items}")
                
                # Show first few items
                print("   Items:")
                for j, item in enumerate(items[:3]):
                    item_name = item.get('name', 'Unknown') if isinstance(item, dict) else str(item)
                    item_user = item.get('userId', 'Unknown') if isinstance(item, dict) else 'Unknown'
                    print(f"     {j+1}. {item_name} (userId: {item_user})")
                
                if len(items) > 3:
                    print(f"     ... and {len(items) - 3} more items")
            
            print("\n" + "=" * 50)
            print("📊 ANALYSIS:")
            
            # Count outfits with user items
            outfits_with_user_items = 0
            outfits_with_all_user_items = 0
            
            for outfit in outfits:
                items = outfit.get('items', [])
                user_items = 0
                total_items = len(items)
                
                for item in items:
                    if isinstance(item, dict) and item.get('userId') == user_id:
                        user_items += 1
                
                if user_items > 0:
                    outfits_with_user_items += 1
                
                if user_items > 0 and user_items == total_items:
                    outfits_with_all_user_items += 1
            
            print(f"Total outfits: {len(outfits)}")
            print(f"Outfits with some user items: {outfits_with_user_items}")
            print(f"Outfits with ALL user items: {outfits_with_all_user_items}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_outfits_api() 