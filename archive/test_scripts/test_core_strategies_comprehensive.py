#!/usr/bin/env python3
"""
Comprehensive test suite for core strategies
Tests all core strategies: cohesive_composition, body_type_optimized, style_profile_matched, weather_adapted
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

BASE_URL = "https://closetgptrenew-backend-production.up.railway.app"

# Test scenarios covering different occasions and styles
TEST_SCENARIOS = [
    {
        "name": "Athletic + Classic",
        "occasion": "Athletic",
        "style": "Classic", 
        "mood": "Bold",
        "expected_strategies": ["body_type_optimized", "cohesive_composition", "style_profile_matched", "weather_adapted"]
    },
    {
        "name": "Business + Formal",
        "occasion": "Business",
        "style": "Formal",
        "mood": "Confident", 
        "expected_strategies": ["style_profile_matched", "cohesive_composition", "body_type_optimized"]
    },
    {
        "name": "Casual + Streetwear",
        "occasion": "Casual",
        "style": "Streetwear",
        "mood": "Relaxed",
        "expected_strategies": ["weather_adapted", "cohesive_composition", "style_profile_matched"]
    },
    {
        "name": "Party + Edgy",
        "occasion": "Party", 
        "style": "Edgy",
        "mood": "Bold",
        "expected_strategies": ["cohesive_composition", "style_profile_matched", "weather_adapted"]
    }
]

async def test_outfit_generation(session: aiohttp.ClientSession, scenario: Dict[str, Any]) -> Dict[str, Any]:
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
        async with session.post(f"{BASE_URL}/api/outfits/generate", 
                               json=payload, headers=headers) as response:
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status == 200:
                data = await response.json()
                strategy = data.get('metadata', {}).get('generation_strategy', 'unknown')
                confidence = data.get('confidence_score', 0)
                item_count = len(data.get('items', []))
                
                result = {
                    "status": "success",
                    "strategy": strategy,
                    "confidence": confidence,
                    "item_count": item_count,
                    "response_time": response_time,
                    "items": data.get('items', []),
                    "expected_strategies": scenario['expected_strategies']
                }
                
                print(f"   ✅ Success: {strategy} (confidence: {confidence:.2f}, items: {item_count}, time: {response_time:.2f}s)")
                
                # Check if strategy is one of the expected core strategies
                if strategy in scenario['expected_strategies']:
                    print(f"   🎯 Strategy matches expected: {strategy}")
                elif strategy == "emergency_default":
                    print(f"   ⚠️  Using emergency default - core strategies may have failed")
                else:
                    print(f"   ❓ Unexpected strategy: {strategy}")
                    
                return result
            else:
                error_text = await response.text()
                print(f"   ❌ Failed: HTTP {response.status} - {error_text}")
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status}",
                    "details": error_text,
                    "response_time": response_time
                }
                
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return {
            "status": "exception", 
            "error": str(e)
        }

async def analyze_results(results: list) -> Dict[str, Any]:
    """Analyze test results and provide insights"""
    total_tests = len(results)
    successful_tests = len([r for r in results if r["status"] == "success"])
    emergency_defaults = len([r for r in results if r.get("strategy") == "emergency_default"])
    core_strategies = len([r for r in results if r.get("strategy") in ["cohesive_composition", "body_type_optimized", "style_profile_matched", "weather_adapted"]])
    
    strategy_counts = {}
    for result in results:
        if result["status"] == "success":
            strategy = result.get("strategy", "unknown")
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    avg_response_time = sum(r.get("response_time", 0) for r in results if r.get("response_time")) / max(successful_tests, 1)
    avg_confidence = sum(r.get("confidence", 0) for r in results if r.get("confidence")) / max(successful_tests, 1)
    
    analysis = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "success_rate": successful_tests / total_tests,
        "emergency_defaults": emergency_defaults,
        "core_strategies_used": core_strategies,
        "strategy_distribution": strategy_counts,
        "avg_response_time": avg_response_time,
        "avg_confidence": avg_confidence
    }
    
    return analysis

async def main():
    """Run comprehensive test suite"""
    print("🚀 Starting Comprehensive Core Strategy Test Suite")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        results = []
        
        for i, scenario in enumerate(TEST_SCENARIOS, 1):
            print(f"\n📋 Test {i}/{len(TEST_SCENARIOS)}")
            result = await test_outfit_generation(session, scenario)
            results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        # Analyze results
        analysis = await analyze_results(results)
        
        print(f"Total Tests: {analysis['total_tests']}")
        print(f"Successful: {analysis['successful_tests']}")
        print(f"Success Rate: {analysis['success_rate']:.1%}")
        print(f"Emergency Defaults: {analysis['emergency_defaults']}")
        print(f"Core Strategies Used: {analysis['core_strategies_used']}")
        print(f"Average Response Time: {analysis['avg_response_time']:.2f}s")
        print(f"Average Confidence: {analysis['avg_confidence']:.2f}")
        
        print(f"\nStrategy Distribution:")
        for strategy, count in analysis['strategy_distribution'].items():
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
                
                # Check item types
                item_types = [item.get('type', 'unknown') for item in result.get('items', [])]
                print(f"   Item Types: {item_types}")
            else:
                print(f"   Status: {result['status']}")
                print(f"   Error: {result.get('error', 'Unknown')}")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        
        if analysis['emergency_defaults'] > 0:
            print(f"⚠️  {analysis['emergency_defaults']} tests used emergency_default - core strategies need fixing")
            
        if analysis['core_strategies_used'] == 0:
            print(f"❌ No core strategies were used - all strategies are failing")
        elif analysis['core_strategies_used'] < analysis['successful_tests']:
            print(f"⚠️  Only {analysis['core_strategies_used']}/{analysis['successful_tests']} tests used core strategies")
        else:
            print(f"✅ All successful tests used core strategies!")
            
        if analysis['success_rate'] < 0.8:
            print(f"❌ Low success rate ({analysis['success_rate']:.1%}) - system needs debugging")
        elif analysis['success_rate'] < 1.0:
            print(f"⚠️  Some tests failed - investigate specific failures")
        else:
            print(f"✅ Perfect success rate!")
            
        if analysis['avg_confidence'] < 0.5:
            print(f"⚠️  Low average confidence ({analysis['avg_confidence']:.2f}) - strategies may need improvement")
        else:
            print(f"✅ Good average confidence ({analysis['avg_confidence']:.2f})")

if __name__ == "__main__":
    asyncio.run(main())
