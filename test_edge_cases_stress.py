#!/usr/bin/env python3
"""
Comprehensive Edge Case and Stress Testing for Semantic Filtering System
Tests boundary conditions, malformed data, and system limits
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BACKEND_URL = "https://closetgptrenew-backend-production.up.railway.app"
TIMEOUT = 30

print("🧪 SEMANTIC FILTERING - EDGE CASES & STRESS TESTS")
print("=" * 80)
print()

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0

def run_test(test_name, test_func):
    """Helper to run a test and track results"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    print(f"Test {total_tests}: {test_name}")
    print("-" * 80)
    try:
        result = test_func()
        if result:
            print("✅ PASS")
            passed_tests += 1
        else:
            print("❌ FAIL")
            failed_tests += 1
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        failed_tests += 1
    print()
    return result

# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_empty_wardrobe():
    """Test with empty wardrobe array"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "wardrobe": []
        },
        timeout=TIMEOUT
    )
    result = response.status_code == 200 and response.json()['summary']['total_items'] == 0
    print(f"   Status: {response.status_code}, Items: {response.json()['summary']['total_items']}")
    return result

def test_null_style_fields():
    """Test items with null/missing style fields"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "wardrobe": [
                {"id": "test1", "name": "Item 1", "season": ["all"]},
                {"id": "test2", "name": "Item 2", "style": None, "season": ["all"]},
                {"id": "test3", "name": "Item 3", "style": [], "season": ["all"]}
            ]
        },
        timeout=TIMEOUT
    )
    result = response.status_code == 200
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Processed: {data['summary']['total_items']} items")
    print(f"   No crashes with null/empty styles: {result}")
    return result

def test_malformed_style_data():
    """Test with malformed style data types"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "wardrobe": [
                {"id": "test1", "name": "Item 1", "style": "Classic", "season": ["all"]},  # String instead of array
                {"id": "test2", "name": "Item 2", "style": 123, "season": ["all"]},  # Number
                {"id": "test3", "name": "Item 3", "style": ["Classic", None, ""], "season": ["all"]}  # Mixed
            ]
        },
        timeout=TIMEOUT
    )
    result = response.status_code == 200
    print(f"   Status: {response.status_code}")
    print(f"   Handled malformed data: {result}")
    return result

def test_case_sensitivity():
    """Test case variations in style names"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "CLASSIC",  # Uppercase
            "wardrobe": [
                {"id": "test1", "name": "Item 1", "style": ["classic"], "occasion": ["business"], "mood": ["professional"], "season": ["all"]},
                {"id": "test2", "name": "Item 2", "style": ["Classic"], "occasion": ["business"], "mood": ["professional"], "season": ["all"]},
                {"id": "test3", "name": "Item 3", "style": ["CLASSIC"], "occasion": ["business"], "mood": ["professional"], "season": ["all"]},
                {"id": "test4", "name": "Item 4", "style": ["ClAsSiC"], "occasion": ["business"], "mood": ["professional"], "season": ["all"]}
            ]
        },
        timeout=TIMEOUT
    )
    data = response.json()
    all_passed = data['summary']['valid_items'] == 4
    print(f"   Status: {response.status_code}")
    print(f"   All case variations matched: {all_passed} ({data['summary']['valid_items']}/4)")
    return all_passed

def test_unicode_and_special_chars():
    """Test unicode and special characters in styles"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "wardrobe": [
                {"id": "test1", "name": "Item 1", "style": ["Clässic"], "occasion": [], "mood": [], "season": ["all"]},
                {"id": "test2", "name": "Item 2", "style": ["Classic™"], "occasion": [], "mood": [], "season": ["all"]},
                {"id": "test3", "name": "Item 3", "style": ["Classic  "], "occasion": [], "mood": [], "season": ["all"]},  # Extra spaces
                {"id": "test4", "name": "Item 4", "style": ["  Classic"], "occasion": [], "mood": [], "season": ["all"]}  # Leading spaces
            ]
        },
        timeout=TIMEOUT
    )
    result = response.status_code == 200
    print(f"   Status: {response.status_code}")
    print(f"   Handled special characters: {result}")
    return result

def test_very_long_style_names():
    """Test extremely long style names"""
    long_style = "A" * 1000
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "wardrobe": [
                {"id": "test1", "name": "Item 1", "style": [long_style], "season": ["all"]}
            ]
        },
        timeout=TIMEOUT
    )
    result = response.status_code == 200
    print(f"   Status: {response.status_code}")
    print(f"   Handled 1000-char style name: {result}")
    return result

def test_semantic_vs_traditional_difference():
    """Verify semantic actually matches more than traditional"""
    # Semantic mode
    response_sem = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "occasion": "business",
            "mood": "professional",
            "wardrobe": [
                {"id": "bc1", "name": "BC Item", "style": ["Business Casual"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]},
                {"id": "sc1", "name": "SC Item", "style": ["Smart Casual"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]},
                {"id": "prep1", "name": "Preppy Item", "style": ["Preppy"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]}
            ]
        },
        timeout=TIMEOUT
    )
    
    # Traditional mode
    response_trad = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=false",
        json={
            "style": "classic",
            "occasion": "business",
            "mood": "professional",
            "wardrobe": [
                {"id": "bc1", "name": "BC Item", "style": ["Business Casual"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]},
                {"id": "sc1", "name": "SC Item", "style": ["Smart Casual"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]},
                {"id": "prep1", "name": "Preppy Item", "style": ["Preppy"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]}
            ]
        },
        timeout=TIMEOUT
    )
    
    sem_valid = response_sem.json()['summary']['valid_items']
    trad_valid = response_trad.json()['summary']['valid_items']
    
    result = sem_valid > trad_valid
    print(f"   Semantic matched: {sem_valid} items")
    print(f"   Traditional matched: {trad_valid} items")
    print(f"   Semantic matches MORE: {result}")
    return result

def test_all_filters_combined():
    """Test with all filters active (style, occasion, mood, season)"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "occasion": "business",
            "mood": "professional",
            "wardrobe": [
                {"id": "perfect", "name": "Perfect Match", "style": ["Classic"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]},
                {"id": "style_miss", "name": "Style Miss", "style": ["Athletic"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]},
                {"id": "occasion_miss", "name": "Occasion Miss", "style": ["Classic"], "occasion": ["Casual"], "mood": ["Professional"], "season": ["all"]},
                {"id": "mood_miss", "name": "Mood Miss", "style": ["Classic"], "occasion": ["Business"], "mood": ["Relaxed"], "season": ["all"]}
            ]
        },
        timeout=TIMEOUT
    )
    data = response.json()
    result = data['summary']['valid_items'] == 1  # Only perfect match should pass
    print(f"   Valid items: {data['summary']['valid_items']}/4 (expected 1)")
    print(f"   Correct filtering: {result}")
    return result

def test_missing_required_fields():
    """Test items missing required fields"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "wardrobe": [
                {"id": "test1"},  # Only ID
                {"name": "No ID Item", "style": ["Classic"]},  # No ID
                {}  # Empty object
            ]
        },
        timeout=TIMEOUT
    )
    result = response.status_code == 200  # Should not crash
    print(f"   Status: {response.status_code}")
    print(f"   Handled missing fields without crashing: {result}")
    return result

# ============================================================================
# STRESS TESTS
# ============================================================================

def test_large_wardrobe():
    """Test with large wardrobe (500 items)"""
    wardrobe = []
    for i in range(500):
        wardrobe.append({
            "id": f"item_{i}",
            "name": f"Item {i}",
            "style": ["Classic" if i % 2 == 0 else "Casual"],
            "occasion": ["Business"],
            "mood": ["Professional"],
            "season": ["all"]
        })
    
    start_time = time.time()
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "occasion": "business",
            "mood": "professional",
            "wardrobe": wardrobe
        },
        timeout=TIMEOUT
    )
    elapsed = time.time() - start_time
    
    result = response.status_code == 200
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Processed: {data['summary']['total_items']} items")
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Performance acceptable (<30s): {elapsed < 30}")
    return result and elapsed < 30

def test_concurrent_requests():
    """Test multiple concurrent requests"""
    def make_request(i):
        response = requests.post(
            f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
            json={
                "style": "classic",
                "wardrobe": [
                    {"id": f"test_{i}", "name": f"Item {i}", "style": ["Classic"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]}
                ]
            },
            timeout=TIMEOUT
        )
        return response.status_code == 200
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(20)]
        results = [f.result() for f in as_completed(futures)]
    elapsed = time.time() - start_time
    
    success_count = sum(results)
    result = success_count == 20
    print(f"   Successful requests: {success_count}/20")
    print(f"   Total time: {elapsed:.2f}s")
    print(f"   All succeeded: {result}")
    return result

def test_rapid_mode_switching():
    """Test rapidly switching between semantic and traditional modes"""
    results = []
    for i in range(10):
        semantic = i % 2 == 0
        response = requests.post(
            f"{BACKEND_URL}/api/outfits/debug-filter?semantic={str(semantic).lower()}",
            json={
                "style": "classic",
                "wardrobe": [
                    {"id": "test", "name": "Item", "style": ["Business Casual"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]}
                ]
            },
            timeout=TIMEOUT
        )
        results.append(response.status_code == 200)
    
    result = all(results)
    print(f"   All 10 rapid requests succeeded: {result}")
    return result

def test_extreme_style_combinations():
    """Test items with many different style tags"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "wardrobe": [
                {
                    "id": "multi_style",
                    "name": "Multi-Style Item",
                    "style": ["Classic", "Business Casual", "Smart Casual", "Preppy", "Traditional", "Minimalist"],
                    "occasion": ["Business"],
                    "mood": ["Professional"],
                    "season": ["all"]
                }
            ]
        },
        timeout=TIMEOUT
    )
    data = response.json()
    result = data['summary']['valid_items'] == 1  # Should match via Classic
    print(f"   Status: {response.status_code}")
    print(f"   Matched multi-style item: {result}")
    return result

def test_boundary_values():
    """Test boundary values for arrays"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "classic",
            "wardrobe": [
                {"id": "test1", "name": "Empty arrays", "style": [], "occasion": [], "mood": [], "season": []},
                {"id": "test2", "name": "Single values", "style": ["Classic"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]},
                {"id": "test3", "name": "Many values", "style": ["A", "B", "C", "D", "E", "F", "G", "H"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]}
            ]
        },
        timeout=TIMEOUT
    )
    result = response.status_code == 200
    print(f"   Status: {response.status_code}")
    print(f"   Handled boundary values: {result}")
    return result

def test_special_style_names():
    """Test styles with special characters and formatting"""
    response = requests.post(
        f"{BACKEND_URL}/api/outfits/debug-filter?semantic=true",
        json={
            "style": "business casual",  # With space
            "wardrobe": [
                {"id": "test1", "name": "Space", "style": ["Business Casual"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]},
                {"id": "test2", "name": "Underscore", "style": ["Business_Casual"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]},
                {"id": "test3", "name": "Hyphen", "style": ["Business-Casual"], "occasion": ["Business"], "mood": ["Professional"], "season": ["all"]}
            ]
        },
        timeout=TIMEOUT
    )
    data = response.json()
    # Should match at least space and underscore versions
    result = data['summary']['valid_items'] >= 2
    print(f"   Matched: {data['summary']['valid_items']}/3 variations")
    print(f"   Handled formatting variations: {result}")
    return result

# ============================================================================
# RUN ALL TESTS
# ============================================================================

print("=" * 80)
print("EDGE CASE TESTS")
print("=" * 80)
print()

run_test("Empty Wardrobe", test_empty_wardrobe)
run_test("Null/Missing Style Fields", test_null_style_fields)
run_test("Malformed Style Data Types", test_malformed_style_data)
run_test("Case Sensitivity", test_case_sensitivity)
run_test("Unicode and Special Characters", test_unicode_and_special_chars)
run_test("Very Long Style Names", test_very_long_style_names)
run_test("Semantic vs Traditional Difference", test_semantic_vs_traditional_difference)
run_test("All Filters Combined", test_all_filters_combined)
run_test("Missing Required Fields", test_missing_required_fields)
run_test("Boundary Values", test_boundary_values)
run_test("Special Style Name Formats", test_special_style_names)

print("=" * 80)
print("STRESS TESTS")
print("=" * 80)
print()

run_test("Large Wardrobe (500 items)", test_large_wardrobe)
run_test("Concurrent Requests (20 parallel)", test_concurrent_requests)
run_test("Rapid Mode Switching", test_rapid_mode_switching)
run_test("Extreme Style Combinations", test_extreme_style_combinations)

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("=" * 80)
print("🎯 FINAL TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {total_tests}")
print(f"✅ Passed: {passed_tests}")
print(f"❌ Failed: {failed_tests}")
print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
print("=" * 80)

if failed_tests == 0:
    print("🎉 ALL TESTS PASSED! System is production-ready!")
elif failed_tests <= 2:
    print("⚠️  Most tests passed. Minor issues detected.")
else:
    print("❌ Multiple failures detected. Review needed.")

print("=" * 80)

