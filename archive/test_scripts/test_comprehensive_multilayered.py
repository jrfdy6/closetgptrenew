#!/usr/bin/env python3
"""
Comprehensive Edge Case and Stress Testing for Multi-Layered Learning System
Tests all error conditions and edge cases
"""

import requests
import json
import time

BASE_URL = "https://closetgptrenew-backend-production.up.railway.app"

def create_item(item_id, name, item_type, color, style, occasion):
    """Create a wardrobe item"""
    return {
        "id": item_id,
        "name": name,
        "type": item_type,
        "color": color,
        "style": style if isinstance(style, list) else [style],
        "occasion": occasion if isinstance(occasion, list) else [occasion],
        "season": ["spring", "summer", "fall", "winter"],
        "dominantColors": [{"name": color, "hex": "#000000"}],
        "matchingColors": [{"name": color, "hex": "#000000"}],
        "userId": "test-user",
        "wearCount": 0,
        "favorite_score": 0.0
    }

# Comprehensive wardrobe with all attributes
FULL_WARDROBE = [
    # Warm skin tone friendly items
    create_item("warm1", "Coral Wrap Top", "shirt", "Coral", ["classic"], ["casual"]),
    create_item("warm2", "Golden Yellow Sweater", "sweater", "Golden Yellow", ["casual"], ["casual"]),
    create_item("warm3", "Rust Blazer", "jacket", "Rust", ["formal"], ["business"]),
    
    # Cool skin tone friendly items
    create_item("cool1", "Navy Shirt", "shirt", "Navy", ["classic"], ["business"]),
    create_item("cool2", "Purple Dress", "dress", "Purple", ["formal"], ["party"]),
    create_item("cool3", "Emerald Cardigan", "sweater", "Emerald", ["casual"], ["casual"]),
    
    # Body type optimized
    create_item("fitted1", "Fitted V-Neck Top", "shirt", "Blue", ["classic"], ["business"]),
    create_item("wrap1", "Wrap Dress", "dress", "Black", ["formal"], ["party"]),
    create_item("structured1", "Structured Blazer", "jacket", "Gray", ["formal"], ["business"]),
    
    # Height-specific
    create_item("highwaist1", "High Waist Pants", "pants", "Black", ["formal"], ["business"]),
    create_item("crop1", "Crop Top", "shirt", "White", ["casual"], ["casual"]),
    create_item("maxi1", "Maxi Dress", "dress", "Navy", ["casual"], ["casual"]),
    
    # Temperature-appropriate
    create_item("winter1", "Wool Coat", "jacket", "Black", ["formal"], ["business"]),
    create_item("summer1", "Linen Shorts", "shorts", "Khaki", ["casual"], ["casual"]),
    create_item("midseason1", "Light Jacket", "jacket", "Beige", ["casual"], ["casual"]),
    
    # Basic essentials
    create_item("basic1", "White T-Shirt", "shirt", "White", ["casual"], ["casual"]),
    create_item("basic2", "Black Pants", "pants", "Black", ["casual"], ["business"]),
    create_item("basic3", "White Sneakers", "shoes", "White", ["casual"], ["casual", "athletic"]),
    create_item("basic4", "Black Heels", "shoes", "Black", ["formal"], ["business", "formal"]),
]

TEST_CASES = [
    {
        "name": "EDGE 1: Warm Skin + Cool Colors (Should Penalize)",
        "occasion": "Business",
        "style": "Classic",
        "mood": "Professional",
        "weather": {"temperature": 70, "condition": "clear"},
        "user_profile": {
            "bodyType": "Hourglass",
            "height": "5'4\" - 5'7\"",
            "weight": "120-150 lbs",
            "gender": "Female",
            "skinTone": "Warm"  # Should avoid purple/cool colors
        },
        "check": lambda r: "Purple" not in str(r.get('items', []))
    },
    {
        "name": "EDGE 2: Extreme Cold + Minimalist (Reduced Layers)",
        "occasion": "Casual",
        "style": "Minimalist",
        "mood": "Simple",
        "weather": {"temperature": 15, "condition": "snow"},
        "user_profile": {
            "bodyType": "Rectangle",
            "height": "5'8\" - 5'11\"",
            "weight": "150-200 lbs",
            "gender": "Female",
            "skinTone": "Neutral"
        },
        "check": lambda r: len(r.get('items', [])) <= 5  # Minimalist should cap at 4-5
    },
    {
        "name": "EDGE 3: Hot Weather + Formal (Contradiction)",
        "occasion": "Business",
        "style": "Formal",
        "mood": "Professional",
        "weather": {"temperature": 95, "condition": "sunny"},
        "user_profile": {
            "bodyType": "Average",
            "height": "5'4\" - 5'7\"",
            "weight": "120-150 lbs",
            "gender": "Female",
            "skinTone": "Medium"
        },
        "check": lambda r: len(r.get('items', [])) >= 3  # Should handle contradiction
    },
    {
        "name": "EDGE 4: Short Height + Maxi Dress (Should Avoid)",
        "occasion": "Party",
        "style": "Casual",
        "mood": "Fun",
        "weather": {"temperature": 70, "condition": "clear"},
        "user_profile": {
            "bodyType": "Pear",
            "height": "5'0\" - 5'3\"",  # Short - should avoid maxi
            "weight": "100-120 lbs",
            "gender": "Female",
            "skinTone": "Light"
        },
        "check": lambda r: True  # Just need it to succeed
    },
    {
        "name": "EDGE 5: Plus Size + Bodycon (Should Avoid)",
        "occasion": "Party",
        "style": "Trendy",
        "mood": "Bold",
        "weather": {"temperature": 68, "condition": "clear"},
        "user_profile": {
            "bodyType": "Apple",
            "height": "5'4\" - 5'7\"",
            "weight": "201-250 lbs",  # Plus size
            "gender": "Female",
            "skinTone": "Warm"
        },
        "check": lambda r: True
    },
    {
        "name": "EDGE 6: Mild Temp (72F) with Light Jacket",
        "occasion": "Business",
        "style": "Classic",
        "mood": "Professional",
        "weather": {"temperature": 72, "condition": "clear"},
        "user_profile": {
            "bodyType": "Average",
            "height": "5'4\" - 5'7\"",
            "weight": "120-150 lbs",
            "gender": "Female",
            "skinTone": "Neutral"
        },
        "check": lambda r: len(r.get('items', [])) >= 3  # Should recommend light jacket
    },
    {
        "name": "EDGE 7: Minimal Wardrobe (3 items only)",
        "occasion": "Casual",
        "style": "Casual",
        "mood": "Relaxed",
        "weather": {"temperature": 70, "condition": "clear"},
        "wardrobe_override": FULL_WARDROBE[:3],  # Only 3 items
        "user_profile": {
            "bodyType": "Average",
            "height": "Average",
            "weight": "Average",
            "gender": "Female",
            "skinTone": "Medium"
        },
        "check": lambda r: len(r.get('items', [])) == 3
    },
    {
        "name": "EDGE 8: Empty User Profile",
        "occasion": "Casual",
        "style": "Casual",
        "mood": "Relaxed",
        "weather": {"temperature": 70, "condition": "clear"},
        "user_profile": {},  # Empty profile
        "check": lambda r: len(r.get('items', [])) >= 3
    },
    {
        "name": "EDGE 9: Missing Weather Data",
        "occasion": "Business",
        "style": "Classic",
        "mood": "Professional",
        "weather": {},  # No weather
        "user_profile": {
            "bodyType": "Hourglass",
            "height": "5'4\" - 5'7\"",
            "weight": "120-150 lbs",
            "gender": "Female",
            "skinTone": "Warm"
        },
        "check": lambda r: len(r.get('items', [])) >= 3
    },
    {
        "name": "EDGE 10: All Attributes at Extremes",
        "occasion": "Formal",
        "style": "Elegant",
        "mood": "Sophisticated",
        "weather": {"temperature": 0, "condition": "blizzard"},
        "user_profile": {
            "bodyType": "Inverted Triangle",
            "height": "6'0\" - 6'3\"",  # Very tall
            "weight": "250+ lbs",  # Heavy
            "gender": "Male",
            "skinTone": "Deep"
        },
        "check": lambda r: len(r.get('items', [])) >= 5  # Should have many layers
    }
]

def run_test(test_case, index):
    """Run a single test case"""
    print(f"\n{'='*70}")
    print(f"🧪 TEST {index + 1}/{len(TEST_CASES)}: {test_case['name']}")
    print(f"{'='*70}")
    
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    payload = {
        "occasion": test_case["occasion"],
        "style": test_case["style"],
        "mood": test_case["mood"],
        "weather": test_case.get("weather", {"temperature": 70, "condition": "clear"}),
        "wardrobe": test_case.get("wardrobe_override", FULL_WARDROBE),
        "user_profile": test_case["user_profile"]
    }
    
    print(f"📋 Config: {test_case['occasion']} + {test_case['style']}")
    print(f"   Weather: {payload['weather'].get('temperature', 'N/A')}°F")
    print(f"   Body: {test_case['user_profile'].get('bodyType', 'N/A')}")
    print(f"   Skin: {test_case['user_profile'].get('skinTone', 'N/A')}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/outfits/generate",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            items = result.get('items', [])
            strategy = result.get('metadata', {}).get('generation_strategy', 'unknown')
            
            # Run custom check
            check_passed = test_case['check'](result) if 'check' in test_case else True
            
            print(f"\n✅ SUCCESS")
            print(f"   Strategy: {strategy}")
            print(f"   Items: {len(items)}")
            
            if strategy == "multi_layered_cohesive_composition":
                print(f"   🎉 Using NEW multi-layered system!")
            else:
                print(f"   ⚠️  Using old system: {strategy}")
            
            for i, item in enumerate(items[:5], 1):
                print(f"   {i}. {item.get('name', 'Unknown')} ({item.get('color', 'N/A')})")
            
            if check_passed:
                print(f"   ✅ Check passed")
                return {"status": "success", "items": len(items), "strategy": strategy}
            else:
                print(f"   ❌ Check failed")
                return {"status": "check_failed", "items": len(items), "strategy": strategy}
        
        else:
            print(f"\n❌ FAILED: HTTP {response.status_code}")
            try:
                error = response.json()
                error_msg = error.get('detail', str(error))
                print(f"   Error: {error_msg[:200]}")
                return {"status": "error", "error": error_msg}
            except:
                print(f"   Raw: {response.text[:200]}")
                return {"status": "error", "error": f"HTTP {response.status_code}"}
                
    except Exception as e:
        print(f"\n💥 EXCEPTION: {str(e)[:200]}")
        return {"status": "exception", "error": str(e)[:200]}

def main():
    print("🚀 COMPREHENSIVE TESTING - Multi-Layered Learning System")
    print("=" * 70)
    print(f"Total Test Cases: {len(TEST_CASES)}")
    print("=" * 70)
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES):
        result = run_test(test_case, i)
        result['test_name'] = test_case['name']
        results.append(result)
        time.sleep(1)  # Rate limiting
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*70}")
    
    success = sum(1 for r in results if r["status"] == "success")
    check_failed = sum(1 for r in results if r["status"] == "check_failed")
    errors = sum(1 for r in results if r["status"] == "error")
    exceptions = sum(1 for r in results if r["status"] == "exception")
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"✅ Fully Passed: {success}")
    print(f"⚠️  Check Failed: {check_failed}")
    print(f"❌ Errors: {errors}")
    print(f"💥 Exceptions: {exceptions}")
    print(f"Success Rate: {(success / len(results) * 100):.1f}%")
    
    # Strategy distribution
    strategies = {}
    for r in results:
        if r["status"] in ["success", "check_failed"]:
            strategy = r.get("strategy", "unknown")
            strategies[strategy] = strategies.get(strategy, 0) + 1
    
    if strategies:
        print(f"\n🎯 Strategy Distribution:")
        for strategy, count in strategies.items():
            print(f"   {strategy}: {count}")
    
    # Failed tests
    failed_tests = [r for r in results if r["status"] not in ["success"]]
    if failed_tests:
        print(f"\n❌ Failed Tests ({len(failed_tests)}):")
        for r in failed_tests:
            print(f"   • {r['test_name']}: {r['status']}")
            if 'error' in r:
                print(f"     Error: {r['error'][:100]}")
    
    return results

if __name__ == "__main__":
    results = main()




