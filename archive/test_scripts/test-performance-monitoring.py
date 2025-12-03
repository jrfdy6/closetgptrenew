#!/usr/bin/env python3
"""
Test script for performance monitoring (Option A - Metadata Only).

This script verifies that performance fields are returned ONLY in metadata,
not as top-level fields.

Usage:
    python test-performance-monitoring.py <firebase_token> [backend_url]

Example:
    python test-performance-monitoring.py "eyJhbGci..." https://closetgptrenew-production.up.railway.app
"""

import sys
import json
import time
import requests
from typing import Dict, Any, Optional

# Default backend URL
DEFAULT_BACKEND_URL = "https://closetgptrenew-production.up.railway.app"

def test_outfit_generation(
    firebase_token: str,
    backend_url: str = DEFAULT_BACKEND_URL,
    bypass_cache: bool = False
) -> Dict[str, Any]:
    """
    Test outfit generation endpoint and return response.
    
    Args:
        firebase_token: Firebase authentication token
        backend_url: Backend API URL
        bypass_cache: Whether to bypass cache for this request
    
    Returns:
        Response JSON as dictionary
    """
    url = f"{backend_url}/api/outfits/generate"
    
    headers = {
        "Authorization": f"Bearer {firebase_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "occasion": "casual",
        "style": "casual",
        "mood": "comfortable",
        "bypass_cache": bypass_cache
    }
    
    print(f"📤 POST {url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    elapsed_time = time.time() - start_time
    
    print(f"⏱️  Request took {elapsed_time:.2f}s")
    print(f"📥 Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Error: {response.text}")
        return {}
    
    return response.json()

def validate_performance_metadata(response: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate that performance fields exist in metadata and NOT as top-level fields.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        "metadata_has_generation_duration": False,
        "metadata_has_is_slow": False,
        "metadata_has_cache_hit": False,
        "metadata_has_generation_attempts": False,
        "top_level_has_generation_duration": False,
        "top_level_has_is_slow": False,
        "top_level_has_cache_hit": False,
        "top_level_has_generation_attempts": False,
    }
    
    metadata = response.get("metadata", {})
    
    # Check metadata fields
    if "generation_duration" in metadata:
        results["metadata_has_generation_duration"] = True
        duration = metadata["generation_duration"]
        print(f"   ✅ metadata.generation_duration = {duration} (type: {type(duration).__name__})")
    else:
        print(f"   ❌ metadata.generation_duration MISSING")
    
    if "is_slow" in metadata:
        results["metadata_has_is_slow"] = True
        is_slow = metadata["is_slow"]
        print(f"   ✅ metadata.is_slow = {is_slow} (type: {type(is_slow).__name__})")
    else:
        print(f"   ❌ metadata.is_slow MISSING")
    
    if "cache_hit" in metadata:
        results["metadata_has_cache_hit"] = True
        cache_hit = metadata["cache_hit"]
        print(f"   ✅ metadata.cache_hit = {cache_hit} (type: {type(cache_hit).__name__})")
    else:
        print(f"   ❌ metadata.cache_hit MISSING")
    
    if "generation_attempts" in metadata:
        results["metadata_has_generation_attempts"] = True
        attempts = metadata["generation_attempts"]
        print(f"   ✅ metadata.generation_attempts = {attempts} (type: {type(attempts).__name__})")
    else:
        print(f"   ❌ metadata.generation_attempts MISSING")
    
    # Check top-level fields (should NOT exist for Option A)
    if "generation_duration" in response:
        results["top_level_has_generation_duration"] = True
        print(f"   ⚠️  WARNING: Top-level generation_duration found (should be in metadata only)")
    else:
        print(f"   ✅ Top-level generation_duration NOT present (correct for Option A)")
    
    if "is_slow" in response:
        results["top_level_has_is_slow"] = True
        print(f"   ⚠️  WARNING: Top-level is_slow found (should be in metadata only)")
    else:
        print(f"   ✅ Top-level is_slow NOT present (correct for Option A)")
    
    if "cache_hit" in response:
        results["top_level_has_cache_hit"] = True
        print(f"   ⚠️  WARNING: Top-level cache_hit found (should be in metadata only)")
    else:
        print(f"   ✅ Top-level cache_hit NOT present (correct for Option A)")
    
    if "generation_attempts" in response:
        results["top_level_has_generation_attempts"] = True
        print(f"   ⚠️  WARNING: Top-level generation_attempts found (should be in metadata only)")
    else:
        print(f"   ✅ Top-level generation_attempts NOT present (correct for Option A)")
    
    return results

def main():
    """Main test function."""
    if len(sys.argv) < 2:
        print("Usage: python test-performance-monitoring.py <firebase_token> [backend_url]")
        sys.exit(1)
    
    firebase_token = sys.argv[1]
    backend_url = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_BACKEND_URL
    
    print("=" * 80)
    print("🧪 Performance Monitoring Test (Option A - Metadata Only)")
    print("=" * 80)
    print()
    
    # Test 1: Cache Miss (bypass cache)
    print("📋 TEST 1: Cache Miss (bypass_cache=True)")
    print("-" * 80)
    response1 = test_outfit_generation(firebase_token, backend_url, bypass_cache=True)
    
    if not response1:
        print("❌ Test 1 failed: No response received")
        sys.exit(1)
    
    print("\n🔍 Validating performance metadata...")
    results1 = validate_performance_metadata(response1)
    
    print("\n" + "=" * 80)
    
    # Test 2: Cache Hit (use cache)
    print("\n📋 TEST 2: Cache Hit (bypass_cache=False)")
    print("-" * 80)
    time.sleep(1)  # Small delay between requests
    response2 = test_outfit_generation(firebase_token, backend_url, bypass_cache=False)
    
    if not response2:
        print("❌ Test 2 failed: No response received")
        sys.exit(1)
    
    print("\n🔍 Validating performance metadata...")
    results2 = validate_performance_metadata(response2)
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    # Test 1 Summary
    print("\n✅ TEST 1 (Cache Miss) Results:")
    test1_passed = (
        results1["metadata_has_generation_duration"] and
        results1["metadata_has_is_slow"] and
        results1["metadata_has_cache_hit"] and
        results1["metadata_has_generation_attempts"] and
        not results1["top_level_has_generation_duration"] and
        not results1["top_level_has_is_slow"] and
        not results1["top_level_has_cache_hit"] and
        not results1["top_level_has_generation_attempts"]
    )
    
    if test1_passed:
        print("   ✅ PASSED: All performance fields in metadata, none at top-level")
    else:
        print("   ❌ FAILED: Some assertions failed")
    
    # Test 2 Summary
    print("\n✅ TEST 2 (Cache Hit) Results:")
    test2_passed = (
        results2["metadata_has_generation_duration"] and
        results2["metadata_has_is_slow"] and
        results2["metadata_has_cache_hit"] and
        results2["metadata_has_generation_attempts"] and
        not results2["top_level_has_generation_duration"] and
        not results2["top_level_has_is_slow"] and
        not results2["top_level_has_cache_hit"] and
        not results2["top_level_has_generation_attempts"]
    )
    
    if test2_passed:
        print("   ✅ PASSED: All performance fields in metadata, none at top-level")
    else:
        print("   ❌ FAILED: Some assertions failed")
    
    # Cache hit verification
    if results2["metadata_has_cache_hit"]:
        cache_hit_value = response2.get("metadata", {}).get("cache_hit", False)
        if cache_hit_value:
            print("\n   🎯 Cache hit detected: generation_duration should be 0.0 or very small")
            duration = response2.get("metadata", {}).get("generation_duration", -1)
            if duration == 0.0 or duration < 0.1:
                print(f"   ✅ Cache hit confirmed: generation_duration = {duration}")
            else:
                print(f"   ⚠️  Cache hit but generation_duration = {duration} (expected ~0.0)")
    
    print("\n" + "=" * 80)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()

