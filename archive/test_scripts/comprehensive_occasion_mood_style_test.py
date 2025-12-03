#!/usr/bin/env python3
"""
Comprehensive test of all occasion, mood, and style combinations
"""

import requests
import json
import time
from itertools import product

def comprehensive_test():
    """Test all combinations of occasion, mood, and style"""
    
    print("🧪 COMPREHENSIVE OCCASION-MOOD-STYLE TEST")
    print("=" * 80)
    print()
    
    # Define all test categories
    occasions = [
        "athletic", "business", "casual", "formal", "date", "evening", 
        "party", "travel", "workout", "interview", "weekend", "loungewear"
    ]
    
    moods = [
        "energetic", "relaxed", "confident", "comfortable", "stylish", 
        "professional", "playful", "elegant", "bold", "neutral"
    ]
    
    styles = [
        "athletic", "business", "casual", "formal", "streetwear", 
        "vintage", "modern", "minimalist", "bohemian", "classic"
    ]
    
    # Create comprehensive test wardrobe with rich metadata
    test_wardrobe = [
        # Athletic Items
        {
            "id": "athletic_shirt_1",
            "name": "Blue Athletic Shirt",
            "type": "shirt",
            "color": "Blue",
            "brand": "Nike",
            "occasion": ["athletic", "workout", "gym"],
            "style": ["athletic", "sporty"],
            "season": ["spring", "summer", "fall"],
            "imageUrl": "https://example.com/athletic_shirt.jpg",
            "userId": "test_user"
        },
        {
            "id": "athletic_pants_1",
            "name": "Black Athletic Pants",
            "type": "pants",
            "color": "Black",
            "brand": "Adidas",
            "occasion": ["athletic", "workout", "gym"],
            "style": ["athletic", "sporty"],
            "season": ["spring", "fall", "winter"],
            "imageUrl": "https://example.com/athletic_pants.jpg",
            "userId": "test_user"
        },
        {
            "id": "athletic_shoes_1",
            "name": "White Running Shoes",
            "type": "sneakers",
            "color": "White",
            "brand": "Nike",
            "occasion": ["athletic", "casual", "workout"],
            "style": ["athletic", "sporty"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/running_shoes.jpg",
            "userId": "test_user"
        },
        
        # Business Items
        {
            "id": "business_shirt_1",
            "name": "White Dress Shirt",
            "type": "shirt",
            "color": "White",
            "brand": "Brooks Brothers",
            "occasion": ["business", "formal", "interview"],
            "style": ["formal", "professional", "classic"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/dress_shirt.jpg",
            "userId": "test_user"
        },
        {
            "id": "business_pants_1",
            "name": "Gray Dress Pants",
            "type": "pants",
            "color": "Gray",
            "brand": "Hugo Boss",
            "occasion": ["business", "formal", "interview"],
            "style": ["formal", "professional", "classic"],
            "season": ["spring", "fall", "winter"],
            "imageUrl": "https://example.com/dress_pants.jpg",
            "userId": "test_user"
        },
        {
            "id": "business_shoes_1",
            "name": "Brown Oxford Shoes",
            "type": "shoes",
            "color": "Brown",
            "brand": "Allen Edmonds",
            "occasion": ["business", "formal", "interview"],
            "style": ["formal", "professional", "classic"],
            "season": ["spring", "fall", "winter"],
            "imageUrl": "https://example.com/oxford_shoes.jpg",
            "userId": "test_user"
        },
        
        # Casual Items
        {
            "id": "casual_shirt_1",
            "name": "Red T-Shirt",
            "type": "shirt",
            "color": "Red",
            "brand": "Gap",
            "occasion": ["casual", "weekend", "loungewear"],
            "style": ["casual", "relaxed", "comfortable"],
            "season": ["spring", "summer"],
            "imageUrl": "https://example.com/tshirt.jpg",
            "userId": "test_user"
        },
        {
            "id": "casual_pants_1",
            "name": "Blue Jeans",
            "type": "jeans",
            "color": "Blue",
            "brand": "Levi's",
            "occasion": ["casual", "weekend", "date"],
            "style": ["casual", "relaxed", "classic"],
            "season": ["spring", "fall", "winter"],
            "imageUrl": "https://example.com/jeans.jpg",
            "userId": "test_user"
        },
        {
            "id": "casual_shoes_1",
            "name": "White Canvas Sneakers",
            "type": "sneakers",
            "color": "White",
            "brand": "Converse",
            "occasion": ["casual", "weekend", "travel"],
            "style": ["casual", "classic", "vintage"],
            "season": ["spring", "summer", "fall"],
            "imageUrl": "https://example.com/canvas_sneakers.jpg",
            "userId": "test_user"
        },
        
        # Formal Items
        {
            "id": "formal_dress_1",
            "name": "Black Evening Dress",
            "type": "dress",
            "color": "Black",
            "brand": "Calvin Klein",
            "occasion": ["formal", "evening", "party"],
            "style": ["formal", "elegant", "classic"],
            "season": ["fall", "winter"],
            "imageUrl": "https://example.com/evening_dress.jpg",
            "userId": "test_user"
        },
        {
            "id": "formal_shoes_1",
            "name": "Black Heels",
            "type": "heels",
            "color": "Black",
            "brand": "Jimmy Choo",
            "occasion": ["formal", "evening", "party"],
            "style": ["formal", "elegant", "classic"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/heels.jpg",
            "userId": "test_user"
        },
        
        # Date/Evening Items
        {
            "id": "date_blouse_1",
            "name": "Silk Blouse",
            "type": "blouse",
            "color": "Pink",
            "brand": "Equipment",
            "occasion": ["date", "evening", "business_casual"],
            "style": ["elegant", "feminine", "classic"],
            "season": ["spring", "summer"],
            "imageUrl": "https://example.com/silk_blouse.jpg",
            "userId": "test_user"
        },
        {
            "id": "date_skirt_1",
            "name": "Black Pencil Skirt",
            "type": "skirt",
            "color": "Black",
            "brand": "Ann Taylor",
            "occasion": ["date", "business", "evening"],
            "style": ["elegant", "professional", "classic"],
            "season": ["spring", "summer", "fall", "winter"],
            "imageUrl": "https://example.com/pencil_skirt.jpg",
            "userId": "test_user"
        },
        
        # Loungewear Items
        {
            "id": "lounge_hoodie_1",
            "name": "Gray Hoodie",
            "type": "hoodie",
            "color": "Gray",
            "brand": "Champion",
            "occasion": ["loungewear", "casual", "weekend"],
            "style": ["comfortable", "relaxed", "casual"],
            "season": ["fall", "winter"],
            "imageUrl": "https://example.com/hoodie.jpg",
            "userId": "test_user"
        },
        {
            "id": "lounge_pants_1",
            "name": "Black Sweatpants",
            "type": "sweatpants",
            "color": "Black",
            "brand": "Lululemon",
            "occasion": ["loungewear", "casual", "athletic"],
            "style": ["comfortable", "relaxed", "athletic"],
            "season": ["fall", "winter"],
            "imageUrl": "https://example.com/sweatpants.jpg",
            "userId": "test_user"
        }
    ]
    
    print(f"📦 Test Wardrobe: {len(test_wardrobe)} items with rich metadata")
    print(f"🎯 Testing {len(occasions)} occasions × {len(moods)} moods × {len(styles)} styles = {len(occasions) * len(moods) * len(styles)} total combinations")
    print()
    
    # Select representative test combinations (not all combinations to avoid timeout)
    test_combinations = [
        # Athletic combinations
        ("athletic", "energetic", "athletic"),
        ("workout", "energetic", "sporty"),
        ("gym", "energetic", "athletic"),
        
        # Business combinations
        ("business", "confident", "professional"),
        ("business", "professional", "formal"),
        ("interview", "confident", "classic"),
        
        # Casual combinations
        ("casual", "relaxed", "casual"),
        ("weekend", "comfortable", "casual"),
        ("loungewear", "comfortable", "relaxed"),
        
        # Formal combinations
        ("formal", "elegant", "formal"),
        ("evening", "elegant", "classic"),
        ("party", "bold", "stylish"),
        
        # Date combinations
        ("date", "confident", "elegant"),
        ("date", "stylish", "classic"),
        
        # Travel combinations
        ("travel", "comfortable", "casual"),
        ("travel", "relaxed", "practical"),
        
        # Mixed combinations
        ("business", "playful", "modern"),
        ("casual", "stylish", "streetwear"),
        ("formal", "bold", "modern")
    ]
    
    print(f"🧪 Running {len(test_combinations)} representative test combinations...")
    print()
    
    base_url = "https://closetgptrenew-backend-production.up.railway.app"
    results = []
    
    for i, (occasion, mood, style) in enumerate(test_combinations, 1):
        print(f"🧪 TEST {i:2d}: {occasion.upper()} + {mood.upper()} + {style.upper()}")
        print("-" * 60)
        
        # Prepare request
        request_data = {
            "occasion": occasion,
            "style": style,
            "mood": mood,
            "wardrobe": test_wardrobe,
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
                    "favoriteColors": ["blue", "black", "white", "gray"],
                    "preferredBrands": ["Nike", "Adidas", "Brooks Brothers", "Hugo Boss"]
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
            
            if response.status_code == 200:
                data = response.json()
                
                if "items" in data and data["items"]:
                    generated_items = [item.get("name", "Unknown") for item in data["items"]]
                    generated_types = [item.get("type", "unknown") for item in data["items"]]
                    
                    # Analyze appropriateness
                    appropriateness = analyze_outfit_appropriateness(
                        occasion, mood, style, generated_items, generated_types, test_wardrobe
                    )
                    
                    print(f"✅ SUCCESS: Generated {len(data['items'])} items")
                    print(f"🎯 Items: {', '.join(generated_items)}")
                    print(f"📊 Appropriateness: {appropriateness['score']}/10")
                    print(f"💡 Analysis: {appropriateness['analysis']}")
                    
                    results.append({
                        "test": f"{occasion}+{mood}+{style}",
                        "status": "PASSED",
                        "items": generated_items,
                        "appropriateness": appropriateness,
                        "occasion": occasion,
                        "mood": mood,
                        "style": style
                    })
                else:
                    print("❌ FAILED: No items generated")
                    results.append({
                        "test": f"{occasion}+{mood}+{style}",
                        "status": "FAILED",
                        "items": [],
                        "appropriateness": {"score": 0, "analysis": "No items generated"},
                        "occasion": occasion,
                        "mood": mood,
                        "style": style
                    })
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                results.append({
                    "test": f"{occasion}+{mood}+{style}",
                    "status": "FAILED",
                    "items": [],
                    "appropriateness": {"score": 0, "analysis": f"HTTP {response.status_code}"},
                    "occasion": occasion,
                    "mood": mood,
                    "style": style
                })
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "test": f"{occasion}+{mood}+{style}",
                "status": "ERROR",
                "items": [],
                "appropriateness": {"score": 0, "analysis": f"Error: {e}"},
                "occasion": occasion,
                "mood": mood,
                "style": style
            })
        
        print(f"⏱️ Waiting 1 second...")
        time.sleep(1)
    
    # Analysis and Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] in ["FAILED", "ERROR"])
    
    print(f"✅ PASSED: {passed}/{len(results)} tests ({passed/len(results)*100:.1f}%)")
    print(f"❌ FAILED: {failed}/{len(results)} tests ({failed/len(results)*100:.1f}%)")
    print()
    
    # Appropriateness analysis
    appropriateness_scores = [r["appropriateness"]["score"] for r in results if r["status"] == "PASSED"]
    if appropriateness_scores:
        avg_appropriateness = sum(appropriateness_scores) / len(appropriateness_scores)
        print(f"📊 Average Appropriateness Score: {avg_appropriateness:.1f}/10")
        print(f"🎯 High Quality (8-10): {sum(1 for s in appropriateness_scores if s >= 8)}/{len(appropriateness_scores)}")
        print(f"⚠️ Medium Quality (6-7): {sum(1 for s in appropriateness_scores if s >= 6 and s < 8)}/{len(appropriateness_scores)}")
        print(f"❌ Low Quality (0-5): {sum(1 for s in appropriateness_scores if s < 6)}/{len(appropriateness_scores)}")
        print()
    
    # Occasion-specific analysis
    print("🎯 OCCASION-SPECIFIC ANALYSIS:")
    print("-" * 40)
    for occasion in ["athletic", "business", "casual", "formal", "date", "loungewear"]:
        occasion_results = [r for r in results if r["occasion"] == occasion and r["status"] == "PASSED"]
        if occasion_results:
            avg_score = sum(r["appropriateness"]["score"] for r in occasion_results) / len(occasion_results)
            print(f"  {occasion.upper():12}: {avg_score:.1f}/10 ({len(occasion_results)} tests)")
        else:
            print(f"  {occasion.upper():12}: No successful tests")
    
    print()
    print("🔍 DETAILED RESULTS:")
    print("-" * 40)
    for result in results:
        status_emoji = {"PASSED": "✅", "FAILED": "❌", "ERROR": "❌"}
        print(f"{status_emoji[result['status']]} {result['test']:30} | {result['appropriateness']['score']}/10 | {result['appropriateness']['analysis']}")
    
    print()
    if passed >= len(results) * 0.8 and (not appropriateness_scores or avg_appropriateness >= 7):
        print("🎉 COMPREHENSIVE TEST PASSED!")
        print("✅ Metadata-first filtering is working excellently across all occasions")
        print("✅ Generated outfits are highly appropriate for their contexts")
    elif passed >= len(results) * 0.6:
        print("⚠️ COMPREHENSIVE TEST PARTIALLY PASSED")
        print("✅ Most tests working, but some improvements needed")
    else:
        print("❌ COMPREHENSIVE TEST NEEDS WORK")
        print("🔧 Significant issues with metadata-first filtering")
    
    print(f"\n📝 Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

def analyze_outfit_appropriateness(occasion, mood, style, generated_items, generated_types, wardrobe):
    """Analyze how appropriate the generated outfit is for the given context"""
    score = 5  # Start with neutral score
    analysis_parts = []
    
    # Create item lookup
    item_lookup = {item["name"]: item for item in wardrobe}
    
    # Check occasion appropriateness
    occasion_score = 0
    for item_name in generated_items:
        if item_name in item_lookup:
            item = item_lookup[item_name]
            item_occasions = item.get("occasion", [])
            if occasion in item_occasions:
                occasion_score += 2
            elif any(occ in item_occasions for occ in ["casual", "weekend"] if occasion in ["casual", "weekend"]):
                occasion_score += 1
            elif any(occ in item_occasions for occ in ["business", "formal"] if occasion in ["business", "formal"]):
                occasion_score += 1
    
    if occasion_score > 0:
        score += min(3, occasion_score)
        analysis_parts.append(f"occasion-appropriate (+{min(3, occasion_score)})")
    
    # Check style appropriateness
    style_score = 0
    for item_name in generated_items:
        if item_name in item_lookup:
            item = item_lookup[item_name]
            item_styles = item.get("style", [])
            if style in item_styles:
                style_score += 1
            elif any(s in item_styles for s in ["classic", "casual"] if style in ["classic", "casual"]):
                style_score += 0.5
    
    if style_score > 0:
        score += min(2, style_score)
        analysis_parts.append(f"style-appropriate (+{min(2, style_score):.1f})")
    
    # Check completeness (has top, bottom, shoes)
    has_top = any(t in generated_types for t in ["shirt", "blouse", "dress", "hoodie", "tank"])
    has_bottom = any(t in generated_types for t in ["pants", "jeans", "skirt", "sweatpants"])
    has_shoes = any(t in generated_types for t in ["shoes", "sneakers", "heels"])
    
    completeness_bonus = 0
    if has_top and has_bottom:
        completeness_bonus += 1
        analysis_parts.append("complete (+1)")
    if has_shoes:
        completeness_bonus += 1
        analysis_parts.append("has shoes (+1)")
    
    score += completeness_bonus
    
    # Check for obvious mismatches
    if occasion in ["athletic", "workout"] and any("heels" in item or "dress" in item for item in generated_items):
        score -= 2
        analysis_parts.append("inappropriate items (-2)")
    elif occasion in ["business", "formal"] and any("sweatpants" in item or "hoodie" in item for item in generated_items):
        score -= 2
        analysis_parts.append("inappropriate items (-2)")
    
    score = max(0, min(10, score))  # Clamp between 0-10
    
    analysis = "; ".join(analysis_parts) if analysis_parts else "neutral"
    
    return {"score": score, "analysis": analysis}

if __name__ == "__main__":
    comprehensive_test()

