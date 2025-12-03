#!/usr/bin/env python3
"""
Performance Test for Outfit Generation
Tests caching and performance improvements.
"""

import asyncio
import time
import sys
import os

# Add the backend src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

async def test_caching_performance():
    """Test the caching performance improvements."""
    print("⚡ Testing Caching Performance")
    print("=" * 40)
    
    try:
        from routes.outfits import get_user_wardrobe_cached, get_user_profile_cached
        
        # Test wardrobe caching
        print("\n🔍 Testing Wardrobe Caching...")
        
        # First call (cache miss)
        start_time = time.time()
        wardrobe1 = await get_user_wardrobe_cached("test_user_123")
        first_call_time = time.time() - start_time
        
        # Second call (cache hit)
        start_time = time.time()
        wardrobe2 = await get_user_wardrobe_cached("test_user_123")
        second_call_time = time.time() - start_time
        
        speedup = first_call_time / second_call_time if second_call_time > 0 else 0
        
        print(f"   First call (cache miss): {first_call_time:.3f}s")
        print(f"   Second call (cache hit): {second_call_time:.3f}s")
        print(f"   Speedup: {speedup:.1f}x")
        
        if speedup > 1.5:
            print("✅ Wardrobe caching working well")
            wardrobe_success = True
        else:
            print("⚠️  Wardrobe caching not showing expected speedup")
            wardrobe_success = False
        
        # Test profile caching
        print("\n🔍 Testing Profile Caching...")
        
        # First call (cache miss)
        start_time = time.time()
        profile1 = await get_user_profile_cached("test_user_123")
        first_call_time = time.time() - start_time
        
        # Second call (cache hit)
        start_time = time.time()
        profile2 = await get_user_profile_cached("test_user_123")
        second_call_time = time.time() - start_time
        
        speedup = first_call_time / second_call_time if second_call_time > 0 else 0
        
        print(f"   First call (cache miss): {first_call_time:.3f}s")
        print(f"   Second call (cache hit): {second_call_time:.3f}s")
        print(f"   Speedup: {speedup:.1f}x")
        
        if speedup > 1.5:
            print("✅ Profile caching working well")
            profile_success = True
        else:
            print("⚠️  Profile caching not showing expected speedup")
            profile_success = False
        
        return wardrobe_success and profile_success
        
    except ImportError as e:
        print(f"❌ Could not import caching functions: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing caching: {e}")
        return False

async def test_validation_performance():
    """Test validation performance."""
    print("\n🔍 Testing Validation Performance...")
    
    try:
        from services.outfit_validation_service import OutfitValidationService
        from custom_types.wardrobe import ClothingItem
        
        validation_service = OutfitValidationService()
        
        # Create test items
        test_items = []
        for i in range(10):  # Test with 10 items
            item = ClothingItem(
                id=f"item_{i}",
                name=f"Test Item {i}",
                type="blazer" if i % 2 == 0 else "cargo pants",
                color="navy" if i % 2 == 0 else "khaki",
                imageUrl=f"https://example.com/item{i}.jpg",
                style=["formal"] if i % 2 == 0 else ["casual"],
                occasion=["business"] if i % 2 == 0 else ["casual"],
                brand="Test Brand",
                wearCount=i,
                favorite_score=0.5 + (i * 0.05),
                tags=["test"],
                metadata={}
            )
            test_items.append(item)
        
        # Test validation performance
        start_time = time.time()
        filtered_items, errors = validation_service._enforce_inappropriate_combinations(test_items)
        validation_time = time.time() - start_time
        
        print(f"   Validated {len(test_items)} items in {validation_time:.3f}s")
        print(f"   Filtered to {len(filtered_items)} items")
        print(f"   Generated {len(errors)} error messages")
        
        if validation_time < 0.1:  # Should be very fast
            print("✅ Validation performance is good")
            return True
        else:
            print("⚠️  Validation might be slow")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import validation service: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        return False

async def main():
    """Run performance tests."""
    print("🚀 Starting Outfit Generation Performance Tests")
    print("=" * 50)
    
    # Test caching performance
    caching_passed = await test_caching_performance()
    
    # Test validation performance
    validation_passed = await test_validation_performance()
    
    # Overall results
    print(f"\n🎯 PERFORMANCE TEST RESULTS")
    print("=" * 50)
    print(f"Caching Performance: {'✅ PASSED' if caching_passed else '❌ FAILED'}")
    print(f"Validation Performance: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
    
    if caching_passed and validation_passed:
        print("\n🎉 All performance tests passed! The optimizations are working well.")
    else:
        print("\n⚠️  Some performance tests failed. Consider further optimizations.")

if __name__ == "__main__":
    asyncio.run(main())
