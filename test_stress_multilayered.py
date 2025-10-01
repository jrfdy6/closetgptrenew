#!/usr/bin/env python3
"""
Stress Testing for Multi-Layered Scoring System
Tests system under heavy load and extreme conditions
"""

import requests
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://closetgptrenew-backend-production.up.railway.app"

# Generate large wardrobe for stress testing
def generate_large_wardrobe(size=100):
    """Generate a large wardrobe for stress testing"""
    colors = ["Red", "Blue", "Green", "Black", "White", "Navy", "Gray", "Brown", "Purple", "Pink"]
    types = ["shirt", "pants", "shoes", "jacket", "sweater", "dress"]
    styles = ["classic", "casual", "formal", "trendy", "athletic"]
    occasions = ["casual", "business", "formal", "athletic", "party"]
    
    wardrobe = []
    for i in range(size):
        wardrobe.append({
            "id": f"item_{i}",
            "name": f"Item {i} - {random.choice(types)}",
            "type": random.choice(types),
            "color": random.choice(colors),
            "style": [random.choice(styles)],
            "occasion": [random.choice(occasions)],
            "season": ["spring", "summer", "fall", "winter"],
            "dominantColors": [{"name": random.choice(colors), "hex": "#000000"}],
            "matchingColors": [{"name": random.choice(colors), "hex": "#000000"}],
            "userId": "stress-test-user"
        })
    
    return wardrobe

def make_request(test_id, wardrobe_size, occasion, style, temp):
    """Make a single API request"""
    headers = {
        "Authorization": "Bearer test",
        "Content-Type": "application/json"
    }
    
    payload = {
        "occasion": occasion,
        "style": style,
        "mood": "Confident",
        "weather": {"temperature": temp, "condition": "clear"},
        "wardrobe": generate_large_wardrobe(wardrobe_size),
        "user_profile": {
            "bodyType": random.choice(["Hourglass", "Pear", "Apple", "Rectangle", "Average"]),
            "height": random.choice(["5'0\" - 5'3\"", "5'4\" - 5'7\"", "5'8\" - 5'11\""]),
            "weight": random.choice(["100-120 lbs", "120-150 lbs", "150-200 lbs"]),
            "gender": "Female",
            "skinTone": random.choice(["Warm", "Cool", "Neutral", "Deep", "Light"])
        }
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/outfits/generate",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            items = result.get('items', [])
            strategy = result.get('metadata', {}).get('generation_strategy', 'unknown')
            
            return {
                "test_id": test_id,
                "status": "success",
                "wardrobe_size": wardrobe_size,
                "items_generated": len(items),
                "strategy": strategy,
                "duration": duration
            }
        else:
            return {
                "test_id": test_id,
                "status": "failed",
                "wardrobe_size": wardrobe_size,
                "error": f"HTTP {response.status_code}",
                "duration": duration
            }
            
    except Exception as e:
        end_time = time.time()
        return {
            "test_id": test_id,
            "status": "exception",
            "wardrobe_size": wardrobe_size,
            "error": str(e),
            "duration": end_time - start_time
        }

def test_large_wardrobe():
    """Test with increasingly large wardrobes"""
    print("\n🔬 STRESS TEST 1: Large Wardrobe Sizes")
    print("=" * 70)
    
    wardrobe_sizes = [10, 50, 100, 200, 500]
    results = []
    
    for size in wardrobe_sizes:
        print(f"\n📦 Testing wardrobe size: {size} items")
        
        result = make_request(
            test_id=f"size_{size}",
            wardrobe_size=size,
            occasion="Business",
            style="Classic",
            temp=70
        )
        
        results.append(result)
        
        if result["status"] == "success":
            print(f"   ✅ Success in {result['duration']:.2f}s - {result['items_generated']} items generated")
        else:
            print(f"   ❌ Failed: {result.get('error', 'unknown')} in {result['duration']:.2f}s")
        
        time.sleep(1)
    
    return results

def test_concurrent_requests():
    """Test concurrent requests"""
    print("\n🔬 STRESS TEST 2: Concurrent Requests")
    print("=" * 70)
    
    num_concurrent = 10
    print(f"\n📡 Sending {num_concurrent} concurrent requests...")
    
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = []
        
        for i in range(num_concurrent):
            future = executor.submit(
                make_request,
                test_id=f"concurrent_{i}",
                wardrobe_size=50,
                occasion=random.choice(["Business", "Casual", "Formal"]),
                style=random.choice(["Classic", "Casual", "Formal"]),
                temp=random.randint(30, 90)
            )
            futures.append(future)
        
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            status_emoji = "✅" if result["status"] == "success" else "❌"
            print(f"{status_emoji} Test {result['test_id']}: {result['status']} ({result['duration']:.2f}s)")
    
    return results

def test_extreme_temperatures():
    """Test extreme temperature scenarios"""
    print("\n🔬 STRESS TEST 3: Extreme Temperatures")
    print("=" * 70)
    
    temps = [-20, 0, 25, 50, 75, 90, 110]
    results = []
    
    for temp in temps:
        print(f"\n🌡️  Testing temperature: {temp}°F")
        
        result = make_request(
            test_id=f"temp_{temp}",
            wardrobe_size=50,
            occasion="Casual",
            style="Classic",
            temp=temp
        )
        
        results.append(result)
        
        if result["status"] == "success":
            print(f"   ✅ Success - {result['items_generated']} items ({result['duration']:.2f}s)")
        else:
            print(f"   ❌ Failed: {result.get('error', 'unknown')}")
        
        time.sleep(0.5)
    
    return results

def test_rapid_fire():
    """Test rapid sequential requests"""
    print("\n🔬 STRESS TEST 4: Rapid Fire (20 requests)")
    print("=" * 70)
    
    num_requests = 20
    results = []
    
    start_time = time.time()
    
    for i in range(num_requests):
        result = make_request(
            test_id=f"rapid_{i}",
            wardrobe_size=30,
            occasion=random.choice(["Business", "Casual"]),
            style=random.choice(["Classic", "Casual"]),
            temp=70
        )
        
        results.append(result)
        
        if (i + 1) % 5 == 0:
            print(f"   Completed {i + 1}/{num_requests} requests...")
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    success_count = sum(1 for r in results if r["status"] == "success")
    avg_duration = sum(r["duration"] for r in results) / len(results)
    
    print(f"\n   ✅ Completed {success_count}/{num_requests} requests")
    print(f"   ⏱️  Total time: {total_duration:.2f}s")
    print(f"   ⏱️  Average request time: {avg_duration:.2f}s")
    print(f"   ⚡ Requests per second: {num_requests / total_duration:.2f}")
    
    return results

def main():
    print("🚀 STRESS TESTING - Multi-Layered Scoring System")
    print("=" * 70)
    print("⚠️  This will generate significant load on the system")
    print("=" * 70)
    
    all_results = {
        "large_wardrobe": [],
        "concurrent": [],
        "extreme_temps": [],
        "rapid_fire": []
    }
    
    # Run all stress tests
    all_results["large_wardrobe"] = test_large_wardrobe()
    time.sleep(2)
    
    all_results["concurrent"] = test_concurrent_requests()
    time.sleep(2)
    
    all_results["extreme_temps"] = test_extreme_temperatures()
    time.sleep(2)
    
    all_results["rapid_fire"] = test_rapid_fire()
    
    # Overall summary
    print(f"\n{'='*70}")
    print("📊 OVERALL STRESS TEST SUMMARY")
    print(f"{'='*70}")
    
    total_tests = sum(len(results) for results in all_results.values())
    total_success = sum(
        sum(1 for r in results if r["status"] == "success")
        for results in all_results.values()
    )
    
    print(f"\nTotal Requests: {total_tests}")
    print(f"✅ Successful: {total_success}")
    print(f"❌ Failed: {total_tests - total_success}")
    print(f"Success Rate: {(total_success / total_tests * 100):.1f}%")
    
    # Performance stats
    all_durations = [
        r["duration"] for results in all_results.values()
        for r in results if r["status"] == "success"
    ]
    
    if all_durations:
        print(f"\n⏱️  Performance Metrics:")
        print(f"   Average Response Time: {sum(all_durations) / len(all_durations):.2f}s")
        print(f"   Fastest Response: {min(all_durations):.2f}s")
        print(f"   Slowest Response: {max(all_durations):.2f}s")
    
    # Test-specific summaries
    print(f"\n📋 Test-Specific Results:")
    for test_name, results in all_results.items():
        success = sum(1 for r in results if r["status"] == "success")
        total = len(results)
        print(f"   {test_name}: {success}/{total} passed ({(success/total*100):.1f}%)")

if __name__ == "__main__":
    main()
