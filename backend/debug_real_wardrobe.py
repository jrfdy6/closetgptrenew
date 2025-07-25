#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def debug_real_wardrobe():
    """Debug the real wardrobe data to see what's causing dress pants to be selected."""
    print("🔍 Debugging real wardrobe data...")
    
    # First, let's get your actual wardrobe data
    try:
        response = requests.get(
            "http://localhost:3001/api/wardrobe",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            wardrobe_data = response.json()
            print(f"📋 Found {len(wardrobe_data)} items in your wardrobe")
            
            # Find dress pants and other formal items
            formal_items = []
            athletic_items = []
            
            for item in wardrobe_data:
                item_name = item.get('name', '').lower()
                item_type = item.get('type', '').lower()
                item_occasions = [occ.lower() for occ in item.get('occasion', [])]
                item_styles = [style.lower() for style in item.get('style', [])]
                item_tags = [tag.lower() for tag in item.get('tags', [])]
                
                # Check for formal items
                if any(term in item_name for term in ['dress', 'formal', 'business', 'slacks']) or \
                   any(term in item_type for term in ['dress', 'formal']) or \
                   any(term in item_occasions for term in ['business', 'formal', 'wedding', 'interview']):
                    formal_items.append({
                        'name': item.get('name'),
                        'type': item.get('type'),
                        'occasions': item.get('occasion', []),
                        'styles': item.get('style', []),
                        'tags': item.get('tags', []),
                        'subType': item.get('subType', 'N/A')
                    })
                
                # Check for athletic items
                athletic_keywords = ['athletic', 'gym', 'workout', 'running', 'sport', 'exercise', 'training']
                has_athletic_occasion = any(keyword in ' '.join(item_occasions) for keyword in athletic_keywords)
                has_athletic_style = any(keyword in ' '.join(item_styles) for keyword in athletic_keywords)
                has_athletic_tags = any(keyword in ' '.join(item_tags) for keyword in athletic_keywords)
                
                if has_athletic_occasion or has_athletic_style or has_athletic_tags:
                    athletic_items.append({
                        'name': item.get('name'),
                        'type': item.get('type'),
                        'occasions': item.get('occasion', []),
                        'styles': item.get('style', []),
                        'tags': item.get('tags', []),
                        'subType': item.get('subType', 'N/A')
                    })
            
            print(f"\n🎯 FORMAL ITEMS FOUND ({len(formal_items)}):")
            for item in formal_items:
                print(f"  📋 {item['name']} ({item['type']})")
                print(f"     Occasions: {item['occasions']}")
                print(f"     Styles: {item['styles']}")
                print(f"     Tags: {item['tags']}")
                print(f"     SubType: {item['subType']}")
                print()
            
            print(f"\n🏃 ATHLETIC ITEMS FOUND ({len(athletic_items)}):")
            for item in athletic_items:
                print(f"  📋 {item['name']} ({item['type']})")
                print(f"     Occasions: {item['occasions']}")
                print(f"     Styles: {item['styles']}")
                print(f"     Tags: {item['tags']}")
                print(f"     SubType: {item['subType']}")
                print()
            
            # Now test outfit generation with your real wardrobe
            print(f"\n🧪 TESTING OUTFIT GENERATION WITH REAL WARDROBE...")
            
            # Get user profile
            profile_response = requests.get(
                "http://localhost:3001/api/profile",
                headers={"Content-Type": "application/json"}
            )
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                
                # Test payload with real data
                payload = {
                    "occasion": "Athletic / Gym",
                    "mood": "energetic",
                    "style": "Athleisure",
                    "description": "Test outfit with real wardrobe",
                    "wardrobe": wardrobe_data,
                    "weather": {
                        "temperature": 81,
                        "condition": "sunny",
                        "location": "test",
                        "humidity": 50,
                        "wind_speed": 5,
                        "precipitation": 0
                    },
                    "user_profile": {
                        "id": profile_data.get('id'),
                        "name": profile_data.get('name'),
                        "email": profile_data.get('email'),
                        "preferences": profile_data.get('preferences', {}),
                        "measurements": profile_data.get('measurements', {}),
                        "stylePreferences": profile_data.get('stylePreferences', []),
                        "bodyType": profile_data.get('bodyType'),
                        "skinTone": profile_data.get('measurements', {}).get('skinTone'),
                        "createdAt": profile_data.get('createdAt'),
                        "updatedAt": profile_data.get('updatedAt')
                    },
                    "likedOutfits": [],
                    "trendingStyles": []
                }
                
                outfit_response = requests.post(
                    "http://localhost:3001/api/outfit/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if outfit_response.status_code == 200:
                    outfit_data = outfit_response.json()
                    print(f"✅ Outfit generation successful!")
                    print(f"🎯 Generated outfit ID: {outfit_data.get('id')}")
                    print(f"👕 Outfit name: {outfit_data.get('name')}")
                    
                    items = outfit_data.get('items', [])
                    print(f"📋 Number of items selected: {len(items)}")
                    
                    print(f"\n📝 SELECTED ITEMS:")
                    inappropriate_items = []
                    for i, item in enumerate(items):
                        print(f"  {i+1}. {item.get('name')} ({item.get('type')})")
                        
                        # Check if this is inappropriate for athletic wear
                        item_name = item.get('name', '').lower()
                        item_type = item.get('type', '').lower()
                        if any(term in item_name for term in ['dress shirt', 'dress pants', 'formal', 'business', 'slacks']) or \
                           any(term in item_type for term in ['dress_shirt', 'dress_pants', 'formal']):
                            inappropriate_items.append(item.get('name'))
                            print(f"     ⚠️  PROBLEMATIC ITEM DETECTED!")
                    
                    if inappropriate_items:
                        print(f"\n⚠️  WARNING: Inappropriate items for athletic wear: {inappropriate_items}")
                        print(f"🔍 This means the filtering is still not working correctly!")
                    else:
                        print(f"\n✅ All items are appropriate for athletic wear!")
                        
                else:
                    print(f"❌ Outfit generation failed: {outfit_response.status_code}")
                    print(f"Error: {outfit_response.text}")
            else:
                print(f"❌ Failed to get profile: {profile_response.status_code}")
                
        else:
            print(f"❌ Failed to get wardrobe: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    debug_real_wardrobe() 