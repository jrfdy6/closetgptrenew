#!/usr/bin/env python3
"""
Debug Real Wardrobe Data

Check what's happening with the user's actual 150+ wardrobe items.
"""

import requests
import json

def check_real_wardrobe():
    """Check the user's real wardrobe data"""
    
    print("🔍 CHECKING REAL WARDROBE DATA")
    print("=" * 60)
    
    try:
        # Fetch real wardrobe data
        response = requests.get(
            "https://closetgptrenew-backend-production.up.railway.app/api/wardrobe/",
            headers={"Authorization": "Bearer test"},
            timeout=30
        )
        
        print(f"📊 Wardrobe API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            wardrobe_data = response.json()
            print(f"📋 Full wardrobe response: {wardrobe_data}")
            
            if 'items' in wardrobe_data:
                items = wardrobe_data['items']
                print(f"✅ SUCCESS: Found {len(items)} real wardrobe items")
                
                # Show sample items
                print(f"\n📋 SAMPLE REAL WARDROBE ITEMS:")
                for i, item in enumerate(items[:5], 1):
                    print(f"   {i}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                    print(f"      Occasion: {item.get('occasion', [])}")
                    print(f"      Style: {item.get('style', [])}")
                    print(f"      Mood: {item.get('mood', [])}")
                    print()
                
                # Count items by type
                type_counts = {}
                for item in items:
                    item_type = item.get('type', 'unknown')
                    type_counts[item_type] = type_counts.get(item_type, 0) + 1
                
                print(f"📊 REAL WARDROBE TYPE BREAKDOWN:")
                for item_type, count in type_counts.items():
                    print(f"   {item_type}: {count} items")
                
                # Test outfit generation with real wardrobe
                print(f"\n🚀 TESTING OUTFIT GENERATION WITH REAL WARDROBE:")
                
                test_request = {
                    "occasion": "casual",
                    "style": "casual", 
                    "mood": "comfortable",
                    "weather": {
                        "temperature": 70,
                        "condition": "clear"
                    },
                    "wardrobe": items,
                    "user_profile": {
                        "body_type": "average",
                        "skin_tone": "medium",
                        "gender": "male",
                        "height": "average",
                        "weight": "average"
                    }
                }
                
                outfit_response = requests.post(
                    "https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate",
                    json=test_request,
                    headers={"Authorization": "Bearer test"},
                    timeout=30
                )
                
                print(f"📊 Outfit Generation Response Status: {outfit_response.status_code}")
                
                if outfit_response.status_code == 200:
                    result = outfit_response.json()
                    print(f"✅ SUCCESS!")
                    print(f"   Strategy: {result.get('metadata', {}).get('generation_strategy', 'unknown')}")
                    print(f"   Items: {len(result.get('items', []))}")
                    for item in result.get('items', []):
                        print(f"     - {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                else:
                    print(f"❌ FAILED: {outfit_response.status_code}")
                    try:
                        error_detail = outfit_response.json()
                        print(f"   Error: {error_detail}")
                    except:
                        print(f"   Error: {outfit_response.text}")
                
            else:
                print(f"❌ No 'items' key in response: {wardrobe_data}")
                
        else:
            print(f"❌ FAILED: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error: {response.text}")
                
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

if __name__ == "__main__":
    check_real_wardrobe()
