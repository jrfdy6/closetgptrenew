#!/usr/bin/env python3
"""
Investigate why the test results seem too good to be true
"""

import requests
import json
import time

def investigate_test_results():
    """Investigate the test results to see what's really happening"""
    
    print("🔍 INVESTIGATING TEST RESULTS - ARE THEY TOO GOOD?")
    print("=" * 70)
    print()
    
    # Test with a more realistic scenario that should fail
    problematic_test_cases = [
        {
            "name": "Business with Athletic Items",
            "occasion": "business",
            "style": "formal", 
            "mood": "professional",
            "wardrobe": [
                {
                    "id": "athletic_shirt",
                    "name": "Nike Athletic Tank Top",
                    "type": "tank",
                    "color": "Blue",
                    "brand": "Nike",
                    "occasion": ["athletic", "gym"],
                    "style": ["athletic", "sporty"],
                    "season": ["summer"],
                    "imageUrl": "https://example.com/tank.jpg",
                    "userId": "test_user"
                },
                {
                    "id": "athletic_shorts",
                    "name": "Adidas Basketball Shorts",
                    "type": "shorts",
                    "color": "Black",
                    "brand": "Adidas",
                    "occasion": ["athletic", "gym"],
                    "style": ["athletic", "sporty"],
                    "season": ["summer"],
                    "imageUrl": "https://example.com/shorts.jpg",
                    "userId": "test_user"
                },
                {
                    "id": "athletic_shoes",
                    "name": "Nike Running Shoes",
                    "type": "sneakers",
                    "color": "White",
                    "brand": "Nike",
                    "occasion": ["athletic", "gym"],
                    "style": ["athletic", "sporty"],
                    "season": ["spring", "summer", "fall", "winter"],
                    "imageUrl": "https://example.com/sneakers.jpg",
                    "userId": "test_user"
                }
            ],
            "should_fail": True,
            "reason": "Only athletic items for business occasion - should fail or be inappropriate"
        },
        {
            "name": "Formal with Casual Items",
            "occasion": "formal",
            "style": "elegant",
            "mood": "sophisticated", 
            "wardrobe": [
                {
                    "id": "casual_tshirt",
                    "name": "Graphic T-Shirt",
                    "type": "shirt",
                    "color": "Red",
                    "brand": "Gap",
                    "occasion": ["casual", "weekend"],
                    "style": ["casual", "relaxed"],
                    "season": ["summer"],
                    "imageUrl": "https://example.com/tshirt.jpg",
                    "userId": "test_user"
                },
                {
                    "id": "casual_jeans",
                    "name": "Ripped Jeans",
                    "type": "jeans",
                    "color": "Blue",
                    "brand": "Hollister",
                    "occasion": ["casual", "weekend"],
                    "style": ["casual", "relaxed"],
                    "season": ["spring", "summer", "fall"],
                    "imageUrl": "https://example.com/jeans.jpg",
                    "userId": "test_user"
                },
                {
                    "id": "casual_sneakers",
                    "name": "High-Top Sneakers",
                    "type": "sneakers",
                    "color": "Red",
                    "brand": "Vans",
                    "occasion": ["casual", "weekend"],
                    "style": ["casual", "streetwear"],
                    "season": ["spring", "summer", "fall"],
                    "imageUrl": "https://example.com/sneakers.jpg",
                    "userId": "test_user"
                }
            ],
            "should_fail": True,
            "reason": "Only casual items for formal occasion - should fail or be inappropriate"
        },
        {
            "name": "Athletic with Formal Items",
            "occasion": "athletic",
            "style": "sporty",
            "mood": "energetic",
            "wardrobe": [
                {
                    "id": "formal_shirt",
                    "name": "White Dress Shirt",
                    "type": "shirt",
                    "color": "White",
                    "brand": "Brooks Brothers",
                    "occasion": ["business", "formal"],
                    "style": ["formal", "professional"],
                    "season": ["spring", "summer", "fall", "winter"],
                    "imageUrl": "https://example.com/dress_shirt.jpg",
                    "userId": "test_user"
                },
                {
                    "id": "formal_pants",
                    "name": "Gray Dress Pants",
                    "type": "pants",
                    "color": "Gray",
                    "brand": "Hugo Boss",
                    "occasion": ["business", "formal"],
                    "style": ["formal", "professional"],
                    "season": ["spring", "fall", "winter"],
                    "imageUrl": "https://example.com/dress_pants.jpg",
                    "userId": "test_user"
                },
                {
                    "id": "formal_shoes",
                    "name": "Black Oxford Shoes",
                    "type": "shoes",
                    "color": "Black",
                    "brand": "Allen Edmonds",
                    "occasion": ["business", "formal"],
                    "style": ["formal", "professional"],
                    "season": ["spring", "fall", "winter"],
                    "imageUrl": "https://example.com/oxford.jpg",
                    "userId": "test_user"
                }
            ],
            "should_fail": True,
            "reason": "Only formal items for athletic occasion - should fail or be inappropriate"
        },
        {
            "name": "Empty Wardrobe",
            "occasion": "business",
            "style": "formal",
            "mood": "professional",
            "wardrobe": [],
            "should_fail": True,
            "reason": "Empty wardrobe should definitely fail"
        },
        {
            "name": "Single Item Wardrobe",
            "occasion": "business",
            "style": "formal", 
            "mood": "professional",
            "wardrobe": [
                {
                    "id": "single_shirt",
                    "name": "Blue Shirt",
                    "type": "shirt",
                    "color": "Blue",
                    "brand": "Unknown",
                    "occasion": ["casual"],
                    "style": ["casual"],
                    "season": ["summer"],
                    "imageUrl": "https://example.com/shirt.jpg",
                    "userId": "test_user"
                }
            ],
            "should_fail": True,
            "reason": "Single item should not make complete outfit"
        }
    ]
    
    base_url = "https://closetgptrenew-backend-production.up.railway.app"
    
    print("🧪 TESTING PROBLEMATIC SCENARIOS:")
    print("-" * 50)
    
    results = []
    
    for i, test_case in enumerate(problematic_test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['name']}")
        print("=" * 50)
        print(f"📋 Expected: {'FAIL' if test_case['should_fail'] else 'PASS'}")
        print(f"💡 Reason: {test_case['reason']}")
        print(f"📦 Wardrobe: {len(test_case['wardrobe'])} items")
        
        # Show wardrobe items
        for item in test_case['wardrobe']:
            print(f"   • {item['name']} ({item['type']}) - occasion: {item['occasion']}")
        
        # Prepare request
        request_data = {
            "occasion": test_case["occasion"],
            "style": test_case["style"],
            "mood": test_case["mood"],
            "wardrobe": test_case["wardrobe"],
            "weather": {
                "temperature": 72,
                "condition": "clear",
                "humidity": 50
            },
            "userProfile": {
                "id": "test_user",
                "bodyType": "Average",
                "height": "Average", 
                "weight": "Average",
                "stylePreferences": {
                    "favoriteColors": ["blue", "black", "white"],
                    "preferredBrands": ["Nike", "Adidas", "Brooks Brothers"]
                }
            }
        }
        
        try:
            # Make API call
            response = requests.post(
                f"{base_url}/api/outfits/generate",
                json=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer test"
                },
                timeout=30
            )
            
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "items" in data and data["items"]:
                    generated_items = [item.get("name", "Unknown") for item in data["items"]]
                    generated_types = [item.get("type", "unknown") for item in data["items"]]
                    
                    # Analyze if this should have failed
                    is_appropriate = analyze_appropriateness(
                        test_case["occasion"], 
                        test_case["wardrobe"], 
                        generated_items, 
                        generated_types
                    )
                    
                    print(f"✅ SUCCESS: Generated {len(data['items'])} items")
                    print(f"🎯 Items: {', '.join(generated_items)}")
                    print(f"📊 Appropriateness: {'APPROPRIATE' if is_appropriate else 'INAPPROPRIATE'}")
                    
                    # Check if result matches expectation
                    expected_to_fail = test_case["should_fail"]
                    actually_failed = False  # We got a successful response
                    
                    if expected_to_fail and actually_failed:
                        print("✅ CORRECT: Failed as expected")
                        result_status = "CORRECT_FAIL"
                    elif expected_to_fail and not actually_failed and not is_appropriate:
                        print("✅ CORRECT: Succeeded but generated inappropriate outfit")
                        result_status = "CORRECT_INAPPROPRIATE"
                    elif expected_to_fail and not actually_failed and is_appropriate:
                        print("❌ WRONG: Should have failed but generated appropriate outfit")
                        result_status = "WRONG_APPROPRIATE"
                    else:
                        print("✅ CORRECT: Succeeded and generated appropriate outfit")
                        result_status = "CORRECT_APPROPRIATE"
                    
                    results.append({
                        "test": test_case["name"],
                        "status": result_status,
                        "items": generated_items,
                        "expected_to_fail": expected_to_fail,
                        "is_appropriate": is_appropriate
                    })
                else:
                    print("❌ FAILED: No items generated")
                    expected_to_fail = test_case["should_fail"]
                    if expected_to_fail:
                        print("✅ CORRECT: Failed as expected")
                        result_status = "CORRECT_FAIL"
                    else:
                        print("❌ WRONG: Should have succeeded")
                        result_status = "WRONG_FAIL"
                    
                    results.append({
                        "test": test_case["name"],
                        "status": result_status,
                        "items": [],
                        "expected_to_fail": expected_to_fail,
                        "is_appropriate": False
                    })
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                expected_to_fail = test_case["should_fail"]
                if expected_to_fail:
                    print("✅ CORRECT: Failed as expected")
                    result_status = "CORRECT_FAIL"
                else:
                    print("❌ WRONG: Should have succeeded")
                    result_status = "WRONG_FAIL"
                
                results.append({
                    "test": test_case["name"],
                    "status": result_status,
                    "items": [],
                    "expected_to_fail": expected_to_fail,
                    "is_appropriate": False
                })
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            expected_to_fail = test_case["should_fail"]
            if expected_to_fail:
                print("✅ CORRECT: Failed as expected")
                result_status = "CORRECT_FAIL"
            else:
                print("❌ WRONG: Should have succeeded")
                result_status = "WRONG_FAIL"
            
            results.append({
                "test": test_case["name"],
                "status": result_status,
                "items": [],
                "expected_to_fail": expected_to_fail,
                "is_appropriate": False
            })
        
        print(f"⏱️ Waiting 1 second...")
        time.sleep(1)
    
    # Analysis
    print("\n" + "=" * 70)
    print("📊 INVESTIGATION RESULTS")
    print("=" * 70)
    
    correct_fails = sum(1 for r in results if r["status"] == "CORRECT_FAIL")
    correct_inappropriate = sum(1 for r in results if r["status"] == "CORRECT_INAPPROPRIATE")
    wrong_appropriate = sum(1 for r in results if r["status"] == "WRONG_APPROPRIATE")
    correct_appropriate = sum(1 for r in results if r["status"] == "CORRECT_APPROPRIATE")
    wrong_fails = sum(1 for r in results if r["status"] == "WRONG_FAIL")
    
    print(f"✅ CORRECT FAILS: {correct_fails}")
    print(f"✅ CORRECT INAPPROPRIATE: {correct_inappropriate}")
    print(f"❌ WRONG APPROPRIATE: {wrong_appropriate}")
    print(f"✅ CORRECT APPROPRIATE: {correct_appropriate}")
    print(f"❌ WRONG FAILS: {wrong_fails}")
    print()
    
    total_correct = correct_fails + correct_inappropriate + correct_appropriate
    total_wrong = wrong_appropriate + wrong_fails
    
    print(f"📊 CORRECT BEHAVIOR: {total_correct}/{len(results)} ({total_correct/len(results)*100:.1f}%)")
    print(f"📊 WRONG BEHAVIOR: {total_wrong}/{len(results)} ({total_wrong/len(results)*100:.1f}%)")
    print()
    
    print("🔍 DETAILED ANALYSIS:")
    print("-" * 30)
    for result in results:
        status_emoji = {
            "CORRECT_FAIL": "✅",
            "CORRECT_INAPPROPRIATE": "✅", 
            "WRONG_APPROPRIATE": "❌",
            "CORRECT_APPROPRIATE": "✅",
            "WRONG_FAIL": "❌"
        }
        print(f"{status_emoji[result['status']]} {result['test']:25} | {result['status']}")
    
    print()
    if wrong_appropriate > 0:
        print("🚨 ISSUES FOUND:")
        print("   • System is generating inappropriate outfits when it should fail")
        print("   • Filtering may be too permissive")
        print("   • Previous test results may be misleading")
    elif total_correct >= len(results) * 0.8:
        print("✅ SYSTEM BEHAVIOR IS CORRECT:")
        print("   • Appropriately fails when it should")
        print("   • Generates appropriate outfits when possible")
        print("   • Previous test results are likely accurate")
    else:
        print("⚠️ MIXED RESULTS:")
        print("   • Some correct behavior, some issues")
        print("   • Need to investigate further")

def analyze_appropriateness(occasion, wardrobe_items, generated_items, generated_types):
    """Analyze if generated outfit is appropriate for the occasion"""
    
    # Check if generated items match the occasion
    occasion_matches = 0
    for item in wardrobe_items:
        if item["name"] in generated_items:
            item_occasions = item.get("occasion", [])
            if occasion in item_occasions:
                occasion_matches += 1
            elif any(occ in item_occasions for occ in ["casual", "weekend"] if occasion in ["casual", "weekend"]):
                occasion_matches += 0.5
            elif any(occ in item_occasions for occ in ["business", "formal"] if occasion in ["business", "formal"]):
                occasion_matches += 0.5
    
    # Check for obvious mismatches
    if occasion in ["business", "formal"] and any("tank" in item or "shorts" in item or "sneakers" in item for item in generated_items):
        return False
    elif occasion in ["athletic", "gym"] and any("dress" in item or "heels" in item or "oxford" in item for item in generated_items):
        return False
    
    # Check completeness
    has_top = any(t in generated_types for t in ["shirt", "blouse", "dress", "tank"])
    has_bottom = any(t in generated_types for t in ["pants", "shorts", "skirt"])
    has_shoes = any(t in generated_types for t in ["shoes", "sneakers", "heels"])
    
    if not (has_top and has_bottom and has_shoes):
        return False
    
    # If most items match the occasion, it's appropriate
    return occasion_matches >= len(generated_items) * 0.6

if __name__ == "__main__":
    investigate_test_results()

