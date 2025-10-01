#!/usr/bin/env python3
"""
Comprehensive Edge Case Testing for Multi-Layered Scoring System
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
        "userId": "test-user"
    }

# Create diverse wardrobe for testing
WARDROBE = [
    # Warm skin tone items
    create_item("warm1", "Coral Wrap Top", "shirt", "Coral", ["classic"], ["casual"]),
    create_item("warm2", "Golden Yellow Sweater", "sweater", "Golden Yellow", ["casual"], ["casual"]),
    create_item("warm3", "Rust Colored Blazer", "jacket", "Rust", ["formal"], ["business"]),
    
    # Cool skin tone items
    create_item("cool1", "Navy Blue Shirt", "shirt", "Navy", ["classic"], ["business"]),
    create_item("cool2", "Emerald Cardigan", "sweater", "Emerald", ["casual"], ["casual"]),
    create_item("cool3", "Purple Jacket", "jacket", "Purple", ["trendy"], ["party"]),
    
    # Layering items
    create_item("base1", "White Tank Top", "shirt", "White", ["minimal"], ["casual"]),
    create_item("mid1", "Gray Cardigan", "sweater", "Gray", ["casual"], ["casual"]),
    create_item("outer1", "Black Wool Coat", "jacket", "Black", ["formal"], ["business", "formal"]),
    
    # Body type specific
    create_item("fitted1", "Fitted V-Neck Top", "shirt", "Blue", ["classic"], ["business"]),
    create_item("wrap1", "Wrap Dress", "dress", "Red", ["classic"], ["party"]),
    create_item("high_waist1", "High Waist Straight Pants", "pants", "Black", ["formal"], ["business"]),
    
    # Height specific
    create_item("maxi1", "Maxi Dress", "dress", "Navy", ["casual"], ["casual"]),
    create_item("crop1", "Crop Top", "shirt", "White", ["trendy"], ["casual"]),
    
    # Various bottoms
    create_item("pants1", "Black Dress Pants", "pants", "Black", ["formal"], ["business", "formal"]),
    create_item("pants2", "Blue Jeans", "pants", "Blue", ["casual"], ["casual"]),
    create_item("pants3", "Khaki Chinos", "pants", "Khaki", ["casual"], ["business"]),
    
    # Various shoes
    create_item("shoes1", "Black Heels", "shoes", "Black", ["formal"], ["business", "formal"]),
    create_item("shoes2", "White Sneakers", "shoes", "White", ["casual"], ["casual", "athletic"]),
    create_item("shoes3", "Brown Boots", "shoes", "Brown", ["casual"], ["casual"]),
]

EDGE_TEST_CASES = [
    {
        "name": "Extreme Cold - Minimalist Style",
        "occasion": "Business",
        "style": "Minimalist",
        "mood": "Professional",
        "weather": {"temperature": 10, "condition": "snow"},
        "user_profile": {
            "bodyType": "Rectangle",
            "height": "5'8\" - 5'11\"",
            "weight": "150-200 lbs",
            "gender": "Female",
            "skinTone": "Cool"
        },
        "expected": {
            "min_items": 3,
            "max_items": 5,  # Minimalist but cold
            "should_have_outerwear": True,
            "color_preference": "cool tones"
        }
    },
    {
        "name": "Extreme Heat - Multiple Layers Attempt",
        "occasion": "Casual",
        "style": "Classic",
        "mood": "Relaxed",
        "weather": {"temperature": 95, "condition": "sunny"},
        "user_profile": {
            "bodyType": "Hourglass",
            "height": "5'0\" - 5'3\"",
            "weight": "120-150 lbs",
            "gender": "Female",
            "skinTone": "Warm"
        },
        "expected": {
            "min_items": 3,
            "max_items": 3,  # No layering in extreme heat
            "should_have_outerwear": False,
            "color_preference": "warm tones"
        }
    },
    {
        "name": "Mild Temp with Light Jacket (65-80F)",
        "occasion": "Business",
        "style": "Classic",
        "mood": "Professional",
        "weather": {"temperature": 72, "condition": "clear"},
        "user_profile": {
            "bodyType": "Pear",
            "height": "5'4\" - 5'7\"",
            "weight": "120-150 lbs",
            "gender": "Female",
            "skinTone": "Neutral"
        },
        "expected": {
            "min_items": 3,
            "max_items": 4,  # Light jacket optional
            "should_have_outerwear": True,  # Should recommend light jacket
            "color_preference": "neutral"
        }
    },
    {
        "name": "Short Height - Proportions Test",
        "occasion": "Party",
        "style": "Trendy",
        "mood": "Bold",
        "weather": {"temperature": 68, "condition": "clear"},
        "user_profile": {
            "bodyType": "Hourglass",
            "height": "5'0\" - 5'3\"",  # Short
            "weight": "100-120 lbs",
            "gender": "Female",
            "skinTone": "Light"
        },
        "expected": {
            "min_items": 3,
            "max_items": 4,
            "should_avoid": ["maxi", "oversized"],
            "should_prefer": ["high waist", "crop"]
        }
    },
    {
        "name": "Tall Height - Long Items Test",
        "occasion": "Casual",
        "style": "Casual",
        "mood": "Relaxed",
        "weather": {"temperature": 70, "condition": "clear"},
        "user_profile": {
            "bodyType": "Rectangle",
            "height": "5'10\" - 6'0\"",  # Tall
            "weight": "150-175 lbs",
            "gender": "Female",
            "skinTone": "Deep"
        },
        "expected": {
            "min_items": 3,
            "max_items": 4,
            "should_prefer": ["maxi", "long"],
            "color_preference": "jewel tones"
        }
    },
    {
        "name": "Plus Size - Flattering Cuts",
        "occasion": "Business",
        "style": "Classic",
        "mood": "Confident",
        "weather": {"temperature": 68, "condition": "clear"},
        "user_profile": {
            "bodyType": "Apple",
            "height": "5'4\" - 5'7\"",
            "weight": "201-250 lbs",  # Plus size
            "gender": "Female",
            "skinTone": "Warm"
        },
        "expected": {
            "min_items": 3,
            "max_items": 5,
            "should_prefer": ["structured", "wrap", "vneck"],
            "should_avoid": ["tight", "bodycon"]
        }
    },
    {
        "name": "Formal Winter Event - Maximum Layering",
        "occasion": "Wedding",
        "style": "Formal",
        "mood": "Elegant",
        "weather": {"temperature": 25, "condition": "snow"},
        "user_profile": {
            "bodyType": "Inverted Triangle",
            "height": "5'8\" - 5'11\"",
            "weight": "150-200 lbs",
            "gender": "Female",
            "skinTone": "Cool"
        },
        "expected": {
            "min_items": 5,
            "max_items": 6,  # Formal + cold = maximum layers
            "should_have_outerwear": True,
            "color_preference": "cool tones"
        }
    },
    {
        "name": "Athletic - Minimal Layers",
        "occasion": "Athletic",
        "style": "Athletic",
        "mood": "Active",
        "weather": {"temperature": 60, "condition": "clear"},
        "user_profile": {
            "bodyType": "Athletic",
            "height": "5'8\" - 5'11\"",
            "weight": "150-175 lbs",
            "gender": "Female",
            "skinTone": "Neutral"
        },
        "expected": {
            "min_items": 3,
            "max_items": 4,  # Athletic reduces layers
            "should_have_outerwear": False,
            "mobility": "high"
        }
    },
    {
        "name": "Warm Skin + Cool Colors (Should Penalize)",
        "occasion": "Casual",
        "style": "Classic",
        "mood": "Relaxed",
        "weather": {"temperature": 70, "condition": "clear"},
        "user_profile": {
            "bodyType": "Average",
            "height": "5'4\" - 5'7\"",
            "weight": "120-150 lbs",
            "gender": "Female",
            "skinTone": "Warm"  # Should avoid cool colors
        },
        "expected": {
            "should_avoid_colors": ["purple", "icy blue", "cool pink"],
            "should_prefer_colors": ["coral", "golden yellow", "rust"]
        }
    },
    {
        "name": "Empty/Minimal Wardrobe",
        "occasion": "Casual",
        "style": "Casual",
        "mood": "Relaxed",
        "weather": {"temperature": 70, "condition": "clear"},
        "wardrobe_override": WARDROBE[:3],  # Only 3 items
        "user_profile": {
            "bodyType": "Average",
            "height": "Average",
            "weight": "Average",
            "gender": "Female",
            "skinTone": "Medium"
        },
        "expected": {
            "min_items": 3,
            "should_succeed": True
        }
    }
]

def run_edge_test(test_case, index):
    """Run a single edge case test"""
    print(f"\n{'='*70}")
    print(f"🧪 TEST {index + 1}/{len(EDGE_TEST_CASES)}: {test_case['name']}")
    print(f"{'='*70}")
    
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    payload = {
        "occasion": test_case["occasion"],
        "style": test_case["style"],
        "mood": test_case["mood"],
        "weather": test_case["weather"],
        "wardrobe": test_case.get("wardrobe_override", WARDROBE),
        "user_profile": test_case["user_profile"]
    }
    
    print(f"📋 Configuration:")
    print(f"   Occasion: {test_case['occasion']}, Style: {test_case['style']}")
    print(f"   Weather: {test_case['weather']['temperature']}°F, {test_case['weather']['condition']}")
    print(f"   Body: {test_case['user_profile']['bodyType']}, Height: {test_case['user_profile']['height']}")
    print(f"   Skin Tone: {test_case['user_profile']['skinTone']}")
    
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
            
            print(f"\n✅ SUCCESS")
            print(f"   Strategy: {strategy}")
            print(f"   Items: {len(items)}")
            
            # Validate expectations
            expected = test_case.get('expected', {})
            passed_checks = []
            failed_checks = []
            
            # Check item count
            if 'min_items' in expected:
                if len(items) >= expected['min_items']:
                    passed_checks.append(f"Item count >= {expected['min_items']}")
                else:
                    failed_checks.append(f"Item count {len(items)} < minimum {expected['min_items']}")
            
            if 'max_items' in expected:
                if len(items) <= expected['max_items']:
                    passed_checks.append(f"Item count <= {expected['max_items']}")
                else:
                    failed_checks.append(f"Item count {len(items)} > maximum {expected['max_items']}")
            
            # Check for outerwear
            if 'should_have_outerwear' in expected:
                has_outerwear = any('jacket' in item.get('type', '').lower() or 
                                  'coat' in item.get('name', '').lower() or
                                  'blazer' in item.get('name', '').lower()
                                  for item in items)
                if expected['should_have_outerwear'] == has_outerwear:
                    passed_checks.append(f"Outerwear expectation met: {has_outerwear}")
                else:
                    failed_checks.append(f"Outerwear mismatch: expected {expected['should_have_outerwear']}, got {has_outerwear}")
            
            # Print items
            print(f"\n   Generated Items:")
            for i, item in enumerate(items, 1):
                print(f"      {i}. {item.get('name', 'Unknown')} ({item.get('type', 'unknown')}) - {item.get('color', 'no color')}")
            
            # Print validation results
            if passed_checks:
                print(f"\n   ✅ Passed Checks:")
                for check in passed_checks:
                    print(f"      • {check}")
            
            if failed_checks:
                print(f"\n   ❌ Failed Checks:")
                for check in failed_checks:
                    print(f"      • {check}")
            
            return {
                "test": test_case['name'],
                "status": "success" if not failed_checks else "partial",
                "items": len(items),
                "passed_checks": len(passed_checks),
                "failed_checks": len(failed_checks)
            }
            
        else:
            print(f"\n❌ FAILED: HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Raw: {response.text[:200]}")
            
            return {
                "test": test_case['name'],
                "status": "failed",
                "error": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        print(f"\n💥 EXCEPTION: {e}")
        return {
            "test": test_case['name'],
            "status": "exception",
            "error": str(e)
        }

def main():
    print("🚀 EDGE CASE & STRESS TESTING - Multi-Layered Scoring System")
    print("=" * 70)
    print(f"Total Test Cases: {len(EDGE_TEST_CASES)}")
    print("=" * 70)
    
    results = []
    for i, test_case in enumerate(EDGE_TEST_CASES):
        result = run_edge_test(test_case, i)
        results.append(result)
        time.sleep(1)  # Rate limiting
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 EDGE CASE TEST SUMMARY")
    print(f"{'='*70}")
    
    success_count = sum(1 for r in results if r["status"] == "success")
    partial_count = sum(1 for r in results if r["status"] == "partial")
    failed_count = sum(1 for r in results if r["status"] in ["failed", "exception"])
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Fully Passed: {success_count}")
    print(f"⚠️  Partially Passed: {partial_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"Success Rate: {((success_count + partial_count) / len(results) * 100):.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        status_emoji = "✅" if result["status"] == "success" else "⚠️" if result["status"] == "partial" else "❌"
        print(f"{status_emoji} {result['test']}: {result['status']}")
        if result["status"] == "partial":
            print(f"   Passed: {result.get('passed_checks', 0)}, Failed: {result.get('failed_checks', 0)}")

if __name__ == "__main__":
    main()
