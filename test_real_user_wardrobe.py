#!/usr/bin/env python3
"""
Test Real User Wardrobe

Test the user's actual wardrobe with their real user ID.
"""

import requests
import json

def test_real_user_wardrobe():
    """Test the user's real wardrobe with their actual user ID"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print("🔍 TESTING REAL USER WARDROBE")
    print("=" * 60)
    print(f"👤 User ID: {user_id}")
    
    try:
        # Fetch real wardrobe data
        response = requests.get(
            "https://closetgptrenew-backend-production.up.railway.app/api/wardrobe/",
            headers={"Authorization": f"Bearer {user_id}"},
            timeout=30
        )
        
        print(f"📊 Wardrobe API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            wardrobe_data = response.json()
            print(f"📋 Full wardrobe response: {wardrobe_data}")
            
            if 'items' in wardrobe_data:
                items = wardrobe_data['items']
                print(f"✅ SUCCESS: Found {len(items)} real wardrobe items")
                
                if len(items) > 0:
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
                        headers={"Authorization": f"Bearer {user_id}"},
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
                    
                    return items
                else:
                    print(f"❌ Empty wardrobe ({len(items)} items)")
                    return []
            else:
                print(f"❌ No 'items' key in response: {wardrobe_data}")
                return []
                
        else:
            print(f"❌ FAILED: {response.status_code}")
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
    test_real_user_wardrobe()



