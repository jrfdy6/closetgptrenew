#!/usr/bin/env python3
"""
Find Real User ID

Try to find the user's actual user ID that starts with 'dan...' and test their real wardrobe.
"""

import requests
import json

def find_real_user_id():
    """Try to find the real user ID and test their wardrobe"""
    
    print("🔍 FINDING REAL USER ID")
    print("=" * 60)
    
    # Common user ID patterns that start with 'dan'
    possible_user_ids = [
        "daniel",
        "daniel_user",
        "daniel_test",
        "dan_user",
        "dan_test", 
        "daniel123",
        "dan123",
        "daniel_fields",
        "dan_fields",
        "daniel.fields",
        "dan.fields",
        "daniel-fields",
        "dan-fields"
    ]
    
    # Test each possible user ID
    for user_id in possible_user_ids:
        print(f"🔍 Testing user ID: {user_id}")
        
        try:
            # Test wardrobe endpoint with this user ID
            response = requests.get(
                f"https://closetgptrenew-backend-production.up.railway.app/api/wardrobe/",
                headers={"Authorization": f"Bearer {user_id}"},
                timeout=10
            )
            
            if response.status_code == 200:
                wardrobe_data = response.json()
                items = wardrobe_data.get('items', [])
                
                if len(items) > 0:
                    print(f"✅ FOUND IT! User ID: {user_id}")
                    print(f"   Items: {len(items)}")
                    print(f"   Response: {wardrobe_data}")
                    
                    # Show sample items
                    print(f"\n📋 SAMPLE ITEMS:")
                    for i, item in enumerate(items[:3], 1):
                        print(f"   {i}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                    
                    # Test outfit generation with this user's wardrobe
                    print(f"\n🚀 TESTING OUTFIT GENERATION:")
                    
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
                        print(f"✅ OUTFIT GENERATION SUCCESS!")
                        print(f"   Strategy: {result.get('metadata', {}).get('generation_strategy', 'unknown')}")
                        print(f"   Items: {len(result.get('items', []))}")
                        for item in result.get('items', []):
                            print(f"     - {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                    else:
                        print(f"❌ Outfit generation failed: {outfit_response.status_code}")
                        try:
                            error_detail = outfit_response.json()
                            print(f"   Error: {error_detail}")
                        except:
                            print(f"   Error: {outfit_response.text}")
                    
                    return user_id, items
                else:
                    print(f"   Empty wardrobe ({len(items)} items)")
            else:
                print(f"   API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   Request failed: {e}")
    
    print(f"\n❌ No user ID found with wardrobe items")
    return None, []

if __name__ == "__main__":
    find_real_user_id()



