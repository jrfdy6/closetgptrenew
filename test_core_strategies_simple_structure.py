#!/usr/bin/env python3
"""
Test core strategies using the simple structure that works
"""

import requests
import json
import time

BASE_URL = "https://closetgptrenew-backend-production.up.railway.app"

def create_simple_item(item_id, name, item_type, color, style_list, occasion_list):
    """Create a simple wardrobe item that matches the working structure"""
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

def test_core_strategies():
    """Test core strategies with simple structure"""
    
    # Create a diverse wardrobe with simple structure
    wardrobe = [
        # Tops
        create_simple_item("shirt1", "Classic White Shirt", "shirt", "White", ["classic", "formal"], ["business", "formal"]),
        create_simple_item("shirt2", "Casual Blue Shirt", "shirt", "Blue", ["casual"], ["casual"]),
        create_simple_item("shirt3", "Athletic Tank Top", "shirt", "Black", ["athletic", "sporty"], ["athletic", "casual"]),
        create_simple_item("shirt4", "Polo Shirt", "shirt", "Navy", ["classic", "casual"], ["casual", "business"]),
        
        # Bottoms
        create_simple_item("pants1", "Dress Pants", "pants", "Black", ["formal", "classic"], ["business", "formal"]),
        create_simple_item("pants2", "Jeans", "pants", "Blue", ["casual"], ["casual"]),
        create_simple_item("pants3", "Athletic Shorts", "shorts", "Gray", ["athletic", "sporty"], ["athletic"]),
        create_simple_item("pants4", "Chinos", "pants", "Khaki", ["casual", "classic"], ["casual", "business"]),
        
        # Shoes
        create_simple_item("shoes1", "Dress Shoes", "shoes", "Black", ["formal", "classic"], ["business", "formal"]),
        create_simple_item("shoes2", "Sneakers", "shoes", "White", ["athletic", "casual"], ["athletic", "casual"]),
        create_simple_item("shoes3", "Loafers", "shoes", "Brown", ["classic", "casual"], ["business", "casual"]),
        create_simple_item("shoes4", "Running Shoes", "shoes", "Blue", ["athletic", "sporty"], ["athletic"]),
        
        # Outerwear
        create_simple_item("jacket1", "Blazer", "jacket", "Navy", ["formal", "classic"], ["business", "formal"]),
        create_simple_item("jacket2", "Casual Jacket", "jacket", "Gray", ["casual"], ["casual"]),
        create_simple_item("jacket3", "Athletic Jacket", "jacket", "Black", ["athletic", "sporty"], ["athletic"]),
    ]
    
    test_cases = [
        {
            "name": "Athletic + Classic",
            "occasion": "Athletic",
            "style": "Classic",
            "mood": "Bold"
        },
        {
            "name": "Business + Formal", 
            "occasion": "Business",
            "style": "Formal",
            "mood": "Confident"
        },
        {
            "name": "Casual + Casual",
            "occasion": "Casual",
            "style": "Casual", 
            "mood": "Relaxed"
        }
    ]
    
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    results = []
    
    print("🚀 Testing Core Strategies with Simple Structure")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{len(test_cases)}")
        print(f"🧪 Testing: {test_case['name']}")
        print(f"   Occasion: {test_case['occasion']}, Style: {test_case['style']}, Mood: {test_case['mood']}")
        
        payload = {
            "occasion": test_case["occasion"],
            "style": test_case["style"],
            "mood": test_case["mood"],
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
        
        try:
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
                
                print(f"   ✅ Success: {strategy} strategy")
                print(f"   📋 Items: {len(items)}")
                for j, item in enumerate(items):
                    print(f"     {j+1}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')})")
                
                results.append({
                    "test": test_case['name'],
                    "status": "success",
                    "strategy": strategy,
                    "items": len(items)
                })
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   📋 Error: {error_detail}")
                except:
                    print(f"   📋 Raw Response: {response.text}")
                
                results.append({
                    "test": test_case['name'],
                    "status": "failed",
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
            results.append({
                "test": test_case['name'],
                "status": "exception",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r["status"] == "success")
    total = len(results)
    success_rate = (successful / total) * 100 if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Strategy distribution
    strategies = {}
    for result in results:
        if result["status"] == "success":
            strategy = result["strategy"]
            strategies[strategy] = strategies.get(strategy, 0) + 1
    
    if strategies:
        print(f"\nStrategy Distribution:")
        for strategy, count in strategies.items():
            print(f"  {strategy}: {count}")
    
    print(f"\nDetailed Results:")
    for result in results:
        status_emoji = "✅" if result["status"] == "success" else "❌"
        print(f"{status_emoji} {result['test']}: {result['status']}")
        if result["status"] == "success":
            print(f"   Strategy: {result['strategy']}, Items: {result['items']}")
        else:
            print(f"   Error: {result['error']}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    if success_rate == 100:
        print("✅ All tests passed - core strategies are working!")
    elif success_rate >= 50:
        print("⚠️  Partial success - some core strategies need debugging")
    else:
        print("❌ Low success rate - core strategies need major fixes")
    
    return results

if __name__ == "__main__":
    test_core_strategies()
