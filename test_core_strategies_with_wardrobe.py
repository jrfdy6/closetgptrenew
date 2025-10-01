#!/usr/bin/env python3
"""
Test suite for core strategies with mock wardrobe items
"""

import requests
import json
import time

BASE_URL = "https://closetgptrenew-backend-production.up.railway.app"

# Mock wardrobe items for testing
MOCK_WARDROBE = [
    {
        "id": "shirt_1",
        "name": "Classic White Button-Up Shirt",
        "type": "shirt",
        "color": "White",
        "style": "classic",
        "occasion": "business,casual",
        "brand": "Brooks Brothers",
        "wearCount": 5,
        "favorite_score": 0.8,
        "quality_score": 0.9,
        "pairability_score": 0.85,
        "seasonal_score": 0.7,
        "temperatureCompatibility": {"minTemp": 15, "maxTemp": 25},
        "season": ["spring", "summer", "fall"],
        "tags": ["formal", "professional", "versatile"],
        "imageUrl": "https://example.com/shirt1.jpg"
    },
    {
        "id": "pants_1", 
        "name": "Navy Dress Pants",
        "type": "pants",
        "color": "Navy Blue",
        "style": "classic",
        "occasion": "business,formal",
        "brand": "J.Crew",
        "wearCount": 8,
        "favorite_score": 0.9,
        "quality_score": 0.85,
        "pairability_score": 0.9,
        "seasonal_score": 0.8,
        "temperatureCompatibility": {"minTemp": 10, "maxTemp": 20},
        "season": ["fall", "winter", "spring"],
        "tags": ["formal", "professional", "classic"],
        "imageUrl": "https://example.com/pants1.jpg"
    },
    {
        "id": "shoes_1",
        "name": "Black Oxford Shoes",
        "type": "shoes", 
        "color": "Black",
        "style": "classic",
        "occasion": "business,formal",
        "brand": "Cole Haan",
        "wearCount": 12,
        "favorite_score": 0.85,
        "quality_score": 0.9,
        "pairability_score": 0.95,
        "seasonal_score": 0.75,
        "temperatureCompatibility": {"minTemp": 5, "maxTemp": 25},
        "season": ["fall", "winter", "spring"],
        "tags": ["formal", "professional", "classic"],
        "imageUrl": "https://example.com/shoes1.jpg"
    },
    {
        "id": "sneakers_1",
        "name": "White Athletic Sneakers", 
        "type": "shoes",
        "color": "White",
        "style": "athletic",
        "occasion": "casual,athletic",
        "brand": "Nike",
        "wearCount": 15,
        "favorite_score": 0.9,
        "quality_score": 0.8,
        "pairability_score": 0.7,
        "seasonal_score": 0.9,
        "temperatureCompatibility": {"minTemp": 0, "maxTemp": 30},
        "season": ["spring", "summer", "fall"],
        "tags": ["athletic", "casual", "comfortable"],
        "imageUrl": "https://example.com/sneakers1.jpg"
    },
    {
        "id": "jacket_1",
        "name": "Navy Blazer",
        "type": "jacket",
        "color": "Navy Blue", 
        "style": "classic",
        "occasion": "business,formal",
        "brand": "Ralph Lauren",
        "wearCount": 6,
        "favorite_score": 0.85,
        "quality_score": 0.9,
        "pairability_score": 0.9,
        "seasonal_score": 0.7,
        "temperatureCompatibility": {"minTemp": 10, "maxTemp": 20},
        "season": ["fall", "winter", "spring"],
        "tags": ["formal", "professional", "versatile"],
        "imageUrl": "https://example.com/jacket1.jpg"
    }
]

# Test scenarios
TEST_SCENARIOS = [
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
        "name": "Casual + Streetwear",
        "occasion": "Casual",
        "style": "Streetwear",
        "mood": "Relaxed"
    }
]

def test_outfit_generation(scenario):
    """Test outfit generation for a specific scenario"""
    print(f"\n🧪 Testing: {scenario['name']}")
    print(f"   Occasion: {scenario['occasion']}, Style: {scenario['style']}, Mood: {scenario['mood']}")
    
    payload = {
        "occasion": scenario["occasion"],
        "style": scenario["style"],
        "mood": scenario["mood"],
        "weather": {
            "temperature": 70,
            "condition": "clear",
            "humidity": 65,
            "wind_speed": 5,
            "precipitation": 0
        },
        "wardrobe": MOCK_WARDROBE,
        "user_profile": {
            "bodyType": "Athletic",
            "skinTone": "Medium",
            "height": "5'10\"",
            "weight": "180 lbs",
            "gender": "Male",
            "style_preferences": ["classic", "athletic"]
        }
    }
    
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/outfits/generate", 
                               json=payload, headers=headers, timeout=30)
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            strategy = data.get('metadata', {}).get('generation_strategy', 'unknown')
            confidence = data.get('confidence_score', 0)
            item_count = len(data.get('items', []))
            
            print(f"   ✅ Success: {strategy} (confidence: {confidence:.2f}, items: {item_count}, time: {response_time:.2f}s)")
            
            # Check item types
            item_types = [item.get('type', 'unknown') for item in data.get('items', [])]
            item_names = [item.get('name', 'unknown') for item in data.get('items', [])]
            print(f"   Item Types: {item_types}")
            print(f"   Item Names: {item_names}")
            
            # Check if strategy is a core strategy
            core_strategies = ["cohesive_composition", "body_type_optimized", "style_profile_matched", "weather_adapted"]
            if strategy in core_strategies:
                print(f"   🎯 Core strategy used: {strategy}")
            elif strategy == "emergency_default":
                print(f"   ⚠️  Using emergency default - core strategies may have failed")
            else:
                print(f"   ❓ Other strategy: {strategy}")
                
            return {
                "status": "success",
                "strategy": strategy,
                "confidence": confidence,
                "item_count": item_count,
                "response_time": response_time,
                "items": data.get('items', [])
            }
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Error text: {response.text}")
            return {
                "status": "failed",
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
            
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return {
            "status": "exception", 
            "error": str(e)
        }

def main():
    """Run test suite"""
    print("🚀 Starting Core Strategy Test Suite with Mock Wardrobe")
    print("=" * 60)
    
    results = []
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n📋 Test {i}/{len(TEST_SCENARIOS)}")
        result = test_outfit_generation(scenario)
        results.append(result)
        
        # Small delay between tests
        time.sleep(3)
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    # Analyze results
    total_tests = len(results)
    successful_tests = len([r for r in results if r["status"] == "success"])
    emergency_defaults = len([r for r in results if r.get("strategy") == "emergency_default"])
    core_strategies = len([r for r in results if r.get("strategy") in ["cohesive_composition", "body_type_optimized", "style_profile_matched", "weather_adapted"]])
    
    strategy_counts = {}
    for result in results:
        if result["status"] == "success":
            strategy = result.get("strategy", "unknown")
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Success Rate: {successful_tests/total_tests:.1%}")
    print(f"Emergency Defaults: {emergency_defaults}")
    print(f"Core Strategies Used: {core_strategies}")
    
    print(f"\nStrategy Distribution:")
    for strategy, count in strategy_counts.items():
        print(f"  {strategy}: {count}")
    
    # Detailed results
    print(f"\nDetailed Results:")
    for i, (scenario, result) in enumerate(zip(TEST_SCENARIOS, results), 1):
        print(f"\n{i}. {scenario['name']}:")
        if result["status"] == "success":
            print(f"   Strategy: {result['strategy']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Items: {result['item_count']}")
            print(f"   Response Time: {result['response_time']:.2f}s")
        else:
            print(f"   Status: {result['status']}")
            print(f"   Error: {result.get('error', 'Unknown')}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    
    if emergency_defaults > 0:
        print(f"⚠️  {emergency_defaults} tests used emergency_default - core strategies need fixing")
        
    if core_strategies == 0:
        print(f"❌ No core strategies were used - all strategies are failing")
    elif core_strategies < successful_tests:
        print(f"⚠️  Only {core_strategies}/{successful_tests} tests used core strategies")
    else:
        print(f"✅ All successful tests used core strategies!")
        
    if successful_tests/total_tests < 0.8:
        print(f"❌ Low success rate ({successful_tests/total_tests:.1%}) - system needs debugging")
    elif successful_tests/total_tests < 1.0:
        print(f"⚠️  Some tests failed - investigate specific failures")
    else:
        print(f"✅ Perfect success rate!")

if __name__ == "__main__":
    main()
