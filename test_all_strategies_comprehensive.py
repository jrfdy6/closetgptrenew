#!/usr/bin/env python3
"""
Comprehensive test to verify ALL core strategies are running
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

def test_all_strategies():
    """Run multiple tests to see strategy distribution"""
    
    # Create a large diverse wardrobe
    wardrobe = []
    
    # 20 shirts in various styles
    for i in range(20):
        wardrobe.append(create_simple_item(
            f"shirt_{i}", 
            f"Shirt {i}", 
            "shirt", 
            ["White", "Blue", "Black", "Gray", "Red"][i % 5],
            [["classic"], ["casual"], ["athletic"], ["formal"], ["streetwear"]][i % 5],
            [["business"], ["casual"], ["athletic"], ["formal"], ["party"]][i % 5]
        ))
    
    # 15 pants/shorts
    for i in range(15):
        wardrobe.append(create_simple_item(
            f"pants_{i}",
            f"Pants {i}",
            ["pants", "shorts", "jeans"][i % 3],
            ["Black", "Blue", "Khaki", "Gray"][i % 4],
            [["classic"], ["casual"], ["athletic"], ["formal"]][i % 4],
            [["business"], ["casual"], ["athletic"], ["formal"]][i % 4]
        ))
    
    # 15 shoes
    for i in range(15):
        wardrobe.append(create_simple_item(
            f"shoes_{i}",
            f"Shoes {i}",
            "shoes",
            ["Black", "White", "Brown", "Blue"][i % 4],
            [["classic"], ["casual"], ["athletic"], ["formal"]][i % 4],
            [["business"], ["casual"], ["athletic"], ["formal"]][i % 4]
        ))
    
    # Test cases covering different scenarios
    test_cases = [
        {"name": "Test 1", "occasion": "Athletic", "style": "Classic", "mood": "Bold"},
        {"name": "Test 2", "occasion": "Business", "style": "Formal", "mood": "Confident"},
        {"name": "Test 3", "occasion": "Casual", "style": "Casual", "mood": "Relaxed"},
        {"name": "Test 4", "occasion": "Party", "style": "Trendy", "mood": "Energetic"},
        {"name": "Test 5", "occasion": "Formal", "style": "Elegant", "mood": "Sophisticated"},
        {"name": "Test 6", "occasion": "Athletic", "style": "Sporty", "mood": "Active"},
        {"name": "Test 7", "occasion": "Business", "style": "Classic", "mood": "Professional"},
        {"name": "Test 8", "occasion": "Casual", "style": "Streetwear", "mood": "Cool"},
        {"name": "Test 9", "occasion": "Formal", "style": "Classic", "mood": "Refined"},
        {"name": "Test 10", "occasion": "Athletic", "style": "Athletic", "mood": "Dynamic"},
    ]
    
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    results = []
    strategies_seen = {}
    
    print("🚀 Comprehensive Strategy Test - Testing All Core Strategies")
    print("=" * 70)
    print(f"📦 Wardrobe size: {len(wardrobe)} items")
    print(f"🧪 Test cases: {len(test_cases)}")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{len(test_cases)}: {test_case['name']}")
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
                
                # Track strategies
                strategies_seen[strategy] = strategies_seen.get(strategy, 0) + 1
                
                print(f"   ✅ Success: {strategy}")
                print(f"   📋 Items: {len(items)}")
                
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
                    print(f"   Error: {error_detail.get('detail', error_detail)}")
                except:
                    print(f"   Raw: {response.text[:200]}")
                
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
        
        # Small delay between requests
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    
    successful = sum(1 for r in results if r["status"] == "success")
    total = len(results)
    success_rate = (successful / total) * 100 if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Strategy analysis
    print(f"\n🎯 STRATEGY DISTRIBUTION:")
    print("-" * 70)
    if strategies_seen:
        for strategy, count in sorted(strategies_seen.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / successful) * 100 if successful > 0 else 0
            print(f"  {strategy}: {count} times ({percentage:.1f}%)")
    else:
        print("  ❌ No strategies recorded")
    
    # Check if we're seeing variety
    print(f"\n🔍 STRATEGY DIVERSITY CHECK:")
    print("-" * 70)
    expected_strategies = [
        'cohesive_composition',
        'body_type_optimized',
        'style_profile_matched',
        'weather_adapted'
    ]
    
    for strategy in expected_strategies:
        if strategy in strategies_seen:
            print(f"  ✅ {strategy}: ACTIVE ({strategies_seen[strategy]} times)")
        else:
            print(f"  ❌ {strategy}: NOT SEEN")
    
    # Overall assessment
    print(f"\n🎯 ASSESSMENT:")
    print("-" * 70)
    unique_strategies = len(strategies_seen)
    if unique_strategies >= 4:
        print(f"  ✅ Excellent! All {unique_strategies} core strategies are running in parallel")
    elif unique_strategies >= 2:
        print(f"  ⚠️  Partial: Only {unique_strategies} strategies active, expected 4 core strategies")
    elif unique_strategies == 1:
        print(f"  ❌ Problem: Only 1 strategy ({list(strategies_seen.keys())[0]}) is being used")
        print(f"     This suggests parallel execution may not be working")
    else:
        print(f"  ❌ Critical: No strategies are working properly")
    
    return results, strategies_seen

if __name__ == "__main__":
    test_all_strategies()
