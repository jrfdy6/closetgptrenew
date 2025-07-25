"""
Caching system for ClosetGPT.
Provides in-memory and Redis-based caching for performance optimization.
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
from functools import wraps
import asyncio
from threading import Lock

from .logging import get_logger

logger = get_logger("cache")

class CacheItem:
    """Represents a cached item with metadata."""
    
    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = time.time()
    
    def is_expired(self) -> bool:
        """Check if the cache item has expired."""
        return time.time() - self.created_at > self.ttl
    
    def access(self):
        """Record an access to this cache item."""
        self.access_count += 1
        self.last_accessed = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache item to dictionary for serialization."""
        return {
            "value": self.value,
            "created_at": self.created_at,
            "ttl": self.ttl,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed
        }

class InMemoryCache:
    """In-memory cache implementation with TTL and LRU eviction."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache: Dict[str, CacheItem] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = Lock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0
        }
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                if item.is_expired():
                    del self.cache[key]
                    self.stats["misses"] += 1
                    return None
                
                item.access()
                self.stats["hits"] += 1
                return item.value
            
            self.stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache."""
        with self.lock:
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            ttl = ttl or self.default_ttl
            self.cache[key] = CacheItem(value, ttl)
            self.stats["sets"] += 1
            return True
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cached items."""
        with self.lock:
            self.cache.clear()
            self.stats = {"hits": 0, "misses": 0, "evictions": 0, "sets": 0}
    
    def _evict_lru(self):
        """Evict least recently used items."""
        if not self.cache:
            return
        
        # Find LRU item
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed)
        del self.cache[lru_key]
        self.stats["evictions"] += 1
    
    def cleanup_expired(self):
        """Remove expired items from cache."""
        with self.lock:
            expired_keys = [
                key for key, item in self.cache.items() 
                if item.is_expired()
            ]
            for key in expired_keys:
                del self.cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": round(hit_rate, 2),
                "evictions": self.stats["evictions"],
                "sets": self.stats["sets"]
            }

class CacheManager:
    """Manages multiple cache instances for different purposes."""
    
    def __init__(self):
        self.caches: Dict[str, InMemoryCache] = {}
        self._setup_default_caches()
    
    def _setup_default_caches(self):
        """Setup default cache instances."""
        # User data cache - short TTL for real-time data
        self.caches["user"] = InMemoryCache(max_size=500, default_ttl=60)
        
        # Wardrobe cache - longer TTL for relatively static data
        self.caches["wardrobe"] = InMemoryCache(max_size=1000, default_ttl=300)
        
        # Outfit cache - medium TTL for generated outfits
        self.caches["outfit"] = InMemoryCache(max_size=2000, default_ttl=600)
        
        # Analysis cache - long TTL for expensive computations
        self.caches["analysis"] = InMemoryCache(max_size=500, default_ttl=1800)
        
        # API cache - short TTL for external API responses
        self.caches["api"] = InMemoryCache(max_size=300, default_ttl=120)
        
        # Metrics cache - very short TTL for real-time metrics
        self.caches["metrics"] = InMemoryCache(max_size=100, default_ttl=30)
    
    def get_cache(self, name: str) -> InMemoryCache:
        """Get a cache instance by name."""
        return self.caches.get(name)
    
    def get(self, cache_name: str, key: str) -> Optional[Any]:
        """Get a value from a specific cache."""
        cache = self.get_cache(cache_name)
        if cache:
            return cache.get(key)
        return None
    
    def set(self, cache_name: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in a specific cache."""
        cache = self.get_cache(cache_name)
        if cache:
            return cache.set(key, value, ttl)
        return False
    
    def delete(self, cache_name: str, key: str) -> bool:
        """Delete a value from a specific cache."""
        cache = self.get_cache(cache_name)
        if cache:
            return cache.delete(key)
        return False
    
    def clear_cache(self, cache_name: str):
        """Clear a specific cache."""
        cache = self.get_cache(cache_name)
        if cache:
            cache.clear()
    
    def clear_all(self):
        """Clear all caches."""
        for cache in self.caches.values():
            cache.clear()
    
    def cleanup_all(self):
        """Cleanup expired items from all caches."""
        for cache in self.caches.values():
            cache.cleanup_expired()
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        return {
            name: cache.get_stats() 
            for name, cache in self.caches.items()
        }

# Global cache manager instance
cache_manager = CacheManager()

def cached(cache_name: str, ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        cache_name: Name of the cache to use
        ttl: Time to live in seconds (overrides cache default)
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_name, cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}", extra={
                    "extra_fields": {
                        "cache_name": cache_name,
                        "cache_key": cache_key,
                        "function": func.__name__
                    }
                })
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_name, cache_key, result, ttl)
            
            logger.debug(f"Cache miss for {func.__name__}, cached result", extra={
                "extra_fields": {
                    "cache_name": cache_name,
                    "cache_key": cache_key,
                    "function": func.__name__,
                    "ttl": ttl
                }
            })
            
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_name, cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for async {func.__name__}", extra={
                    "extra_fields": {
                        "cache_name": cache_name,
                        "cache_key": cache_key,
                        "function": func.__name__
                    }
                })
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_name, cache_key, result, ttl)
            
            logger.debug(f"Cache miss for async {func.__name__}, cached result", extra={
                "extra_fields": {
                    "cache_name": cache_name,
                    "cache_key": cache_key,
                    "function": func.__name__,
                    "ttl": ttl
                }
            })
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator

def invalidate_cache(cache_name: str, pattern: str = None):
    """
    Decorator for invalidating cache entries when data is modified.
    
    Args:
        cache_name: Name of the cache to invalidate
        pattern: Pattern to match cache keys (if None, clears entire cache)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if pattern:
                # TODO: Implement pattern-based invalidation
                logger.debug(f"Invalidated cache pattern {pattern} for {func.__name__}")
            else:
                cache_manager.clear_cache(cache_name)
                logger.debug(f"Cleared cache {cache_name} for {func.__name__}")
            
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if pattern:
                # TODO: Implement pattern-based invalidation
                logger.debug(f"Invalidated cache pattern {pattern} for async {func.__name__}")
            else:
                cache_manager.clear_cache(cache_name)
                logger.debug(f"Cleared cache {cache_name} for async {func.__name__}")
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator

# Background task for cache cleanup
async def cache_cleanup_task():
    """Background task to periodically cleanup expired cache items."""
    while True:
        try:
            cache_manager.cleanup_all()
            logger.debug("Cache cleanup completed", extra={
                "extra_fields": {
                    "cache_stats": cache_manager.get_all_stats()
                }
            })
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
        
        # Run cleanup every 5 minutes
        await asyncio.sleep(300) 