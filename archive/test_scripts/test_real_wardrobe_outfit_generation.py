#!/usr/bin/env python3
"""
Test Real Wardrobe Outfit Generation

Use the user's real wardrobe data from debug endpoint to test outfit generation.
"""

import requests
import json

def test_real_wardrobe_outfit_generation():
    """Test outfit generation with user's real wardrobe data"""
    
    user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    
    print("🔍 TESTING REAL WARDROBE OUTFIT GENERATION")
    print("=" * 60)
    print(f"👤 User ID: {user_id}")
    
    # First, get the debug data to see the real wardrobe structure
    try:
        debug_response = requests.get(
            "https://closetgptrenew-backend-production.up.railway.app/api/wardrobe/debug",
            timeout=30
        )
        
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            sample_items = debug_data.get('sample_items', [])
            
            # Filter items for our user
            user_items = [item for item in sample_items if item.get('userId') == user_id]
            
            print(f"📊 Found {len(user_items)} sample items for user {user_id}")
            
            if len(user_items) > 0:
                # Show the real items
                print(f"\n📋 YOUR REAL WARDROBE ITEMS:")
                for i, item in enumerate(user_items, 1):
                    print(f"   {i}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                    print(f"      Occasion: {item.get('occasion', [])}")
                    print(f"      Style: {item.get('style', [])}")
                    print(f"      Mood: {item.get('mood', [])}")
                    print(f"      Brand: {item.get('brand', 'Unknown')}")
                    print()
                
                # Test outfit generation with real wardrobe items
                print(f"\n🚀 TESTING OUTFIT GENERATION WITH YOUR REAL WARDROBE:")
                
                # Convert debug items to proper format for outfit generation
                formatted_items = []
                for item in user_items:
                    formatted_item = {
                        'id': item.get('id'),
                        'name': item.get('name'),
                        'type': item.get('type'),
                        'color': item.get('color', 'Unknown'),
                        'occasion': item.get('occasion', []),
                        'style': item.get('style', []),
                        'mood': item.get('mood', []),
                        'brand': item.get('brand', ''),
                        'season': item.get('season', []),
                        'imageUrl': item.get('imageUrl', ''),
                        'userId': item.get('userId'),
                        'temperature_range': item.get('temperature_range', [50, 80]),
                        'weather_conditions': item.get('weather_conditions', ['clear']),
                        'favorite': item.get('favorite', False),
                        'usage_count': item.get('usage_count', 0),
                        'wearCount': item.get('wearCount', 0)
                    }
                    formatted_items.append(formatted_item)
                
                test_request = {
                    "occasion": "casual",
                    "style": "casual", 
                    "mood": "comfortable",
                    "weather": {
                        "temperature": 70,
                        "condition": "clear"
                    },
                    "wardrobe": formatted_items,
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
                
                return formatted_items
            else:
                print(f"❌ No items found for user {user_id}")
                return []
        else:
            print(f"❌ Debug endpoint failed: {debug_response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        return []

if __name__ == "__main__":
    test_real_wardrobe_outfit_generation()



