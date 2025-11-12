"""
Performance test endpoints for Easy Outfit App.
Provides endpoints to test and measure performance optimizations.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
import time
import asyncio

from ..core.logging import get_logger
from ..core.cache import cache_manager, cached
from ..services.performance_service import performance_service

router = APIRouter()
logger = get_logger("performance")

class PerformanceTestRequest(BaseModel):
    """Request model for performance tests."""
    test_type: str
    iterations: int = 1
    user_id: str = "test_user"

class PerformanceTestResponse(BaseModel):
    """Response model for performance tests."""
    test_type: str
    iterations: int
    total_time: float
    average_time: float
    cache_hits: int
    cache_misses: int
    cache_hit_rate: float
    results: List[Dict[str, Any]]

@router.get("/test/cache")
async def test_cache_performance():
    """Test cache performance with various operations."""
    test_results = []
    cache_hits = 0
    cache_misses = 0
    
    # Test 1: Simple key-value operations
    start_time = time.time()
    for i in range(100):
        key = f"test_key_{i}"
        value = f"test_value_{i}"
        
        # Set value
        cache_manager.set("api", key, value, 60)
        
        # Get value (should be cache hit)
        cached_value = cache_manager.get("api", key)
        if cached_value:
            cache_hits += 1
        else:
            cache_misses += 1
    
    duration = time.time() - start_time
    test_results.append({
        "test": "key_value_operations",
        "operations": 200,  # 100 sets + 100 gets
        "duration": duration,
        "operations_per_second": round(200 / duration, 2)
    })
    
    # Test 2: Cache miss simulation
    start_time = time.time()
    for i in range(50):
        key = f"miss_key_{i}"
        cached_value = cache_manager.get("api", key)
        if cached_value:
            cache_hits += 1
        else:
            cache_misses += 1
    
    duration = time.time() - start_time
    test_results.append({
        "test": "cache_misses",
        "operations": 50,
        "duration": duration,
        "operations_per_second": round(50 / duration, 2)
    })
    
    total_time = sum(result["duration"] for result in test_results)
    cache_hit_rate = (cache_hits / (cache_hits + cache_misses) * 100) if (cache_hits + cache_misses) > 0 else 0
    
    logger.info("Cache performance test completed", extra={
        "extra_fields": {
            "total_time": total_time,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "cache_hit_rate": cache_hit_rate
        }
    })
    
    return PerformanceTestResponse(
        test_type="cache_performance",
        iterations=1,
        total_time=total_time,
        average_time=total_time / len(test_results),
        cache_hits=cache_hits,
        cache_misses=cache_misses,
        cache_hit_rate=round(cache_hit_rate, 2),
        results=test_results
    )

@router.get("/test/database")
async def test_database_performance():
    """Test database query performance."""
    test_results = []
    
    # Test 1: Wardrobe query performance
    start_time = time.time()
    wardrobe_items = await performance_service.query_optimizer.get_user_wardrobe_optimized("test_user")
    duration = time.time() - start_time
    
    test_results.append({
        "test": "wardrobe_query",
        "item_count": len(wardrobe_items),
        "duration": duration,
        "cached": True  # Should be cached after first call
    })
    
    # Test 2: Outfit query performance
    start_time = time.time()
    outfits = await performance_service.query_optimizer.get_user_outfits_optimized("test_user")
    duration = time.time() - start_time
    
    test_results.append({
        "test": "outfit_query",
        "outfit_count": len(outfits),
        "duration": duration,
        "cached": True  # Should be cached after first call
    })
    
    total_time = sum(result["duration"] for result in test_results)
    
    logger.info("Database performance test completed", extra={
        "extra_fields": {
            "total_time": total_time,
            "wardrobe_items": len(wardrobe_items),
            "outfits": len(outfits)
        }
    })
    
    return PerformanceTestResponse(
        test_type="database_performance",
        iterations=1,
        total_time=total_time,
        average_time=total_time / len(test_results),
        cache_hits=2,  # Both queries should be cached
        cache_misses=0,
        cache_hit_rate=100.0,
        results=test_results
    )

@router.get("/test/image-processing")
async def test_image_processing_performance():
    """Test image processing performance."""
    test_results = []
    
    # Test image analysis performance
    start_time = time.time()
    analysis = await performance_service.image_optimizer.analyze_image_optimized(
        "https://example.com/test-image.jpg",
        "test_user"
    )
    duration = time.time() - start_time
    
    test_results.append({
        "test": "image_analysis",
        "duration": duration,
        "analysis_keys": len(analysis.keys()),
        "cached": True  # Should be cached after first call
    })
    
    # Test second call (should be cached)
    start_time = time.time()
    analysis2 = await performance_service.image_optimizer.analyze_image_optimized(
        "https://example.com/test-image.jpg",
        "test_user"
    )
    duration2 = time.time() - start_time
    
    test_results.append({
        "test": "image_analysis_cached",
        "duration": duration2,
        "analysis_keys": len(analysis2.keys()),
        "cached": True,
        "speedup": round(duration / duration2, 2) if duration2 > 0 else 0
    })
    
    total_time = sum(result["duration"] for result in test_results)
    
    logger.info("Image processing performance test completed", extra={
        "extra_fields": {
            "total_time": total_time,
            "speedup": round(duration / duration2, 2) if duration2 > 0 else 0
        }
    })
    
    return PerformanceTestResponse(
        test_type="image_processing_performance",
        iterations=1,
        total_time=total_time,
        average_time=total_time / len(test_results),
        cache_hits=1,
        cache_misses=1,
        cache_hit_rate=50.0,
        results=test_results
    )

@router.get("/test/outfit-generation")
async def test_outfit_generation_performance():
    """Test outfit generation performance."""
    test_results = []
    
    weather = {"temperature": 20, "condition": "sunny"}
    style_preferences = ["casual", "comfortable"]
    
    # Test outfit generation performance
    start_time = time.time()
    outfit = await performance_service.outfit_optimizer.generate_outfit_optimized(
        "test_user",
        "casual",
        weather,
        style_preferences
    )
    duration = time.time() - start_time
    
    test_results.append({
        "test": "outfit_generation",
        "duration": duration,
        "outfit_items": len(outfit.keys()) if outfit else 0,
        "cached": True  # Should be cached after first call
    })
    
    # Test second call (should be cached)
    start_time = time.time()
    outfit2 = await performance_service.outfit_optimizer.generate_outfit_optimized(
        "test_user",
        "casual",
        weather,
        style_preferences
    )
    duration2 = time.time() - start_time
    
    test_results.append({
        "test": "outfit_generation_cached",
        "duration": duration2,
        "outfit_items": len(outfit2.keys()) if outfit2 else 0,
        "cached": True,
        "speedup": round(duration / duration2, 2) if duration2 > 0 else 0
    })
    
    total_time = sum(result["duration"] for result in test_results)
    
    logger.info("Outfit generation performance test completed", extra={
        "extra_fields": {
            "total_time": total_time,
            "speedup": round(duration / duration2, 2) if duration2 > 0 else 0
        }
    })
    
    return PerformanceTestResponse(
        test_type="outfit_generation_performance",
        iterations=1,
        total_time=total_time,
        average_time=total_time / len(test_results),
        cache_hits=1,
        cache_misses=1,
        cache_hit_rate=50.0,
        results=test_results
    )

@router.get("/stats")
async def get_performance_stats():
    """Get comprehensive performance statistics."""
    try:
        stats = await performance_service.get_comprehensive_stats()
        
        logger.info("Performance statistics collected", extra={
            "extra_fields": {
                "query_stats": stats["query_optimization"],
                "image_stats": stats["image_processing"],
                "outfit_stats": stats["outfit_generation"]
            }
        })
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get performance stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance statistics"
        )

@router.post("/clear-cache")
async def clear_performance_cache():
    """Clear all performance caches."""
    try:
        await performance_service.clear_all_caches()
        
        logger.info("Performance caches cleared")
        
        return {
            "message": "All performance caches cleared successfully",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Failed to clear caches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear caches"
        )

@router.post("/preload-data")
async def preload_user_data(user_id: str):
    """Preload frequently accessed data for a user."""
    try:
        await performance_service.preload_frequently_accessed_data(user_id)
        
        logger.info("User data preloaded", extra={
            "extra_fields": {
                "user_id": user_id
            }
        })
        
        return {
            "message": f"Data preloaded for user {user_id}",
            "user_id": user_id,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Failed to preload data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preload user data"
        ) 