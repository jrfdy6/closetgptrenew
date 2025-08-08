#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Backend API URL
BACKEND_URL = "https://closetgptrenew-backend-production.up.railway.app"

def check_wardrobe_items():
    """Check wardrobe items from test endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/outfits/test", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Wardrobe items (test endpoint): {len(data)} items")
            
            # Check if these are actually outfits or wardrobe items
            if data and len(data) > 0:
                first_item = data[0]
                print(f"📋 First item type: {first_item.get('type', 'Unknown')}")
                print(f"📋 First item name: {first_item.get('name', 'Unknown')}")
                print(f"📋 Has 'items' field: {'items' in first_item}")
                print(f"📋 Has 'occasion' field: {'occasion' in first_item}")
                
                # Check if these look like outfits or individual items
                if 'items' in first_item and isinstance(first_item['items'], list):
                    print("✅ These appear to be actual outfits")
                else:
                    print("❌ These appear to be wardrobe items, not outfits")
                    
        else:
            print(f"Error getting wardrobe items: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to backend: {e}")

def check_outfits_with_auth():
    """Check outfits with authentication (this will fail but show the structure)"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/outfits/", timeout=30)
        print(f"🔐 Outfits endpoint (no auth): {response.status_code}")
        if response.status_code == 401 or response.status_code == 403:
            print("✅ Endpoint requires authentication (expected)")
        else:
            data = response.json()
            print(f"📊 Actual outfits: {len(data) if isinstance(data, list) else 'Not a list'}")
    except Exception as e:
        print(f"Error checking outfits endpoint: {e}")

def main():
    print("🔍 Checking outfit vs wardrobe item discrepancy...")
    print("=" * 50)
    
    check_wardrobe_items()
    print()
    check_outfits_with_auth()
    
    print("\n" + "=" * 50)
    print("💡 ANALYSIS:")
    print("The frontend is calling the test endpoint which returns wardrobe items")
    print("These wardrobe items are being displayed as 'outfits' in the UI")
    print("This explains why you see 999+ items - they're individual clothing pieces")
    print("not actual outfits.")

if __name__ == "__main__":
    main() 