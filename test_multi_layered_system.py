#!/usr/bin/env python3
"""
Test the new multi-layered scoring system
"""

import requests
import json

def test_multi_layered():
    """Test to verify multi-layered system is running"""
    
    url = "https://closetgptrenew-backend-production.up.railway.app/api/outfits/generate"
    
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    # Create diverse wardrobe
    wardrobe = [
        {
            "id": "shirt1",
            "name": "Fitted V-Neck Top",
            "type": "shirt",
            "color": "Blue",
            "style": ["classic", "formal"],
            "occasion": ["business", "formal"],
            "season": ["spring", "summer", "fall", "winter"],
            "dominantColors": [{"name": "Blue", "hex": "#0000FF"}],
            "matchingColors": [{"name": "Blue", "hex": "#0000FF"}],
            "userId": "test-user"
        },
        {
            "id": "pants1",
            "name": "High Waist Straight Pants",
            "type": "pants",
            "color": "Black",
            "style": ["formal", "classic"],
            "occasion": ["business", "formal"],
            "season": ["spring", "summer", "fall", "winter"],
            "dominantColors": [{"name": "Black", "hex": "#000000"}],
            "matchingColors": [{"name": "Black", "hex": "#000000"}],
            "userId": "test-user"
        },
        {
            "id": "shoes1",
            "name": "Classic Heels",
            "type": "shoes",
            "color": "Black",
            "style": ["formal", "classic"],
            "occasion": ["business", "formal"],
            "season": ["spring", "summer", "fall", "winter"],
            "dominantColors": [{"name": "Black", "hex": "#000000"}],
            "matchingColors": [{"name": "Black", "hex": "#000000"}],
            "userId": "test-user"
        }
    ]
    
    payload = {
        "occasion": "Business",
        "style": "Formal",
        "mood": "Confident",
        "weather": {
            "temperature": 70,
            "condition": "clear"
        },
        "wardrobe": wardrobe,
        "user_profile": {
            "bodyType": "Hourglass",
            "height": "5'4\" - 5'7\"",
            "weight": "120-150 lbs",
            "stylePreferences": {
                "favoriteColors": ["blue", "black"],
                "preferredBrands": []
            }
        }
    }
    
    print("🚀 Testing Multi-Layered Scoring System")
    print("=" * 70)
    print("📝 Check Railway logs for:")
    print("   - 🔬 PHASE 1: Multi-Layered Analysis & Scoring")
    print("   - 🚀 Running 3 analyzers in parallel...")
    print("   - 👤 BODY TYPE ANALYZER")
    print("   - 🎭 STYLE PROFILE ANALYZER")
    print("   - 🌤️ WEATHER ANALYZER")
    print("   - 🏆 Top 5 scored items")
    print("   - 🎨 PHASE 2: Cohesive Composition with Scored Items")
    print("=" * 70)
    
    try:
        print(f"\n📡 Sending request...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            strategy = result.get('metadata', {}).get('generation_strategy', 'unknown')
            items = result.get('items', [])
            
            print(f"\n✅ Success!")
            print(f"📋 Strategy: {strategy}")
            
            if strategy == "multi_layered_cohesive_composition":
                print(f"🎉 MULTI-LAYERED SYSTEM IS WORKING!")
            elif strategy == "cohesive_composition":
                print(f"⚠️  OLD SYSTEM STILL RUNNING (should be multi_layered_cohesive_composition)")
            else:
                print(f"❓ Unknown strategy: {strategy}")
            
            print(f"\n📋 Items: {len(items)}")
            for i, item in enumerate(items):
                print(f"  {i+1}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
            
            print(f"\n🔍 Check Railway logs timestamped around now for detailed scoring breakdown")
            
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {error_detail}")
            except:
                print(f"Raw: {response.text}")
                
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_multi_layered()
