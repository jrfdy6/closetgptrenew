#!/usr/bin/env python3
"""
Test to capture detailed error information from Railway logs
"""

import requests
import json
import time

BASE_URL = "https://closetgptrenew-backend-production.up.railway.app"

def create_simple_item(item_id, name, item_type, color, style_list, occasion_list):
    """Create a simple wardrobe item"""
    return {
        "id": item_id,
        "name": name,
        "type": item_type,
        "color": color,
        "style": style_list,
        "occasion": occasion_list,
        "season": ["spring", "summer", "fall", "winter"],
        "dominantColors": [{"name": color, "hex": "#000000"}],
        "matchingColors": [{"name": color, "hex": "#000000"}],
        "userId": "test-user"
    }

def test_strategy_failures():
    """Single test to check Railway logs for strategy failures"""
    
    # Create a diverse wardrobe
    wardrobe = [
        create_simple_item("shirt1", "Classic White Shirt", "shirt", "White", ["classic", "formal"], ["business", "formal"]),
        create_simple_item("shirt2", "Casual Blue Shirt", "shirt", "Blue", ["casual"], ["casual"]),
        create_simple_item("pants1", "Dress Pants", "pants", "Black", ["formal", "classic"], ["business", "formal"]),
        create_simple_item("pants2", "Jeans", "pants", "Blue", ["casual"], ["casual"]),
        create_simple_item("shoes1", "Dress Shoes", "shoes", "Black", ["formal", "classic"], ["business", "formal"]),
        create_simple_item("shoes2", "Sneakers", "shoes", "White", ["athletic", "casual"], ["athletic", "casual"]),
    ]
    
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
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
            "bodyType": "Average",
            "height": "5'8\" - 5'11\"",
            "weight": "150-200 lbs"
        }
    }
    
    print("🚀 Testing Strategy Execution")
    print("=" * 70)
    print("📝 This test will generate outfit and you should check Railway logs for:")
    print("   - 🚀 PARALLEL START messages for each strategy")
    print("   - ❌ PARALLEL xxx: Failed messages")
    print("   - ✅ PARALLEL GENERATED messages")
    print("   - 🔍 PARALLEL VALIDATED messages")
    print("   - 🏆 BEST CORE STRATEGY message")
    print("=" * 70)
    
    try:
        print(f"\n📡 Sending request...")
        response = requests.post(
            f"{BASE_URL}/api/outfits/generate",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            strategy = result.get('metadata', {}).get('generation_strategy', 'unknown')
            items = result.get('items', [])
            
            print(f"✅ Success: {strategy}")
            print(f"📋 Items: {len(items)}")
            for i, item in enumerate(items):
                print(f"  {i+1}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
            
            print(f"\n🔍 Now check Railway logs to see which strategies failed and why")
            print(f"   Look for logs timestamped around: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
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
    test_strategy_failures()
