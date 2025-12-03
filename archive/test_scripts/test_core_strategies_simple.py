#!/usr/bin/env python3
"""
Simple test suite for core strategies using requests
"""

import requests
import json
import time

BASE_URL = "https://closetgptrenew-backend-production.up.railway.app"

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
            print(f"   Item Types: {item_types}")
            
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
                "response_time": response_time
            }
        else:
            print(f"   ❌ Failed: HTTP {response.status_code} - {response.text}")
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
    print("🚀 Starting Core Strategy Test Suite")
    print("=" * 50)
    
    results = []
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n📋 Test {i}/{len(TEST_SCENARIOS)}")
        result = test_outfit_generation(scenario)
        results.append(result)
        
        # Small delay between tests
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
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
