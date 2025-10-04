#!/usr/bin/env python3
"""
Rate Limiting Middleware for FastAPI

This module provides comprehensive rate limiting to prevent abuse:
- Per-user rate limiting based on Firebase UID
- Different limits for different endpoints
- IP-based fallback for unauthenticated requests
- Configurable limits and time windows
- Redis backend for distributed rate limiting
"""

import time
import hashlib
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import auth as firebase_auth

logger = logging.getLogger(__name__)

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass

class RateLimiter:
    """Rate limiting implementation with configurable limits."""
    
    def __init__(self, redis_client=None):
        """
        Initialize rate limiter.
        
        Args:
            redis_client: Optional Redis client for distributed rate limiting
        """
        self.redis_client = redis_client
        self.memory_store = {}  # Fallback for local rate limiting
        
        # Default rate limits (requests per minute)
        self.default_limits = {
            "default": 60,  # 60 requests per minute
            "auth": 10,     # 10 auth attempts per minute
            "upload": 20,   # 20 uploads per minute
            "outfit_generation": 30,  # 30 outfit generations per minute
            "analytics": 100,  # 100 analytics events per minute
            "feedback": 50,    # 50 feedback submissions per minute
        }
        
        # Time window for rate limiting (in seconds)
        self.time_window = 60
        
        # Admin users get higher limits
        self.admin_multiplier = 5
    
    def get_user_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.
        Prioritizes Firebase UID, falls back to IP address.
        """
        try:
            # Try to get Firebase UID from Authorization header
            auth_header = request.headers.get("Authorization") if headers else None)
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    # Try with default settings first
                    decoded_token = firebase_auth.verify_id_token(token)
                    user_id = (decoded_token.get("uid") if decoded_token else None)
                    if user_id:
                        return f"user:{user_id}"
                except Exception as e:
                    # If it's a clock issue, try with more lenient settings
                    if "Token used too early" in str(e) or "clock" in str(e).lower():
                        logger.debug(f"Clock skew detected in rate limiter, trying with lenient settings: {e}")
                        try:
                            decoded_token = firebase_auth.verify_id_token(token, check_revoked=False)
                            user_id = (decoded_token.get("uid") if decoded_token else None)
                            if user_id:
                                return f"user:{user_id}"
                        except Exception as e2:
                            logger.debug(f"Still failed with lenient settings: {e2}")
                    else:
                        logger.debug(f"Could not extract user ID from token: {e}")
        except Exception as e:
            logger.debug(f"Could not extract user ID from token: {e}")
        
        # Fallback to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (common with proxies)
        forwarded_for = request.headers.get("X-Forwarded-For") if headers else None)
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP") if headers else None)
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def get_limit_for_endpoint(self, path: str) -> int:
        """Get rate limit for specific endpoint."""
        # Map endpoints to rate limit categories
        if path.startswith("/auth"):
            return self.default_limits["auth"]
        elif path.startswith("/upload") or "upload" in path:
            return self.default_limits["upload"]
        elif path.startswith("/outfit") or "outfit" in path:
            return self.default_limits["outfit_generation"]
        elif path.startswith("/analytics") or "analytics" in path:
            return self.default_limits["analytics"]
        elif path.startswith("/feedback") or "feedback" in path:
            return self.default_limits["feedback"]
        else:
            return self.default_limits["default"]
    
    def is_admin_user(self, request: Request) -> bool:
        """Check if user has admin privileges."""
        try:
            auth_header = request.headers.get("Authorization") if headers else None)
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    # Try with default settings first
                    decoded_token = firebase_auth.verify_id_token(token)
                    return (decoded_token.get("admin", False) if decoded_token else False)
                except Exception as e:
                    # If it's a clock issue, try with more lenient settings
                    if "Token used too early" in str(e) or "clock" in str(e).lower():
                        logger.debug(f"Clock skew detected in admin check, trying with lenient settings: {e}")
                        try:
                            decoded_token = firebase_auth.verify_id_token(token, check_revoked=False)
                            return (decoded_token.get("admin", False) if decoded_token else False)
                        except Exception as e2:
                            logger.debug(f"Still failed with lenient settings: {e2}")
                    else:
                        logger.debug(f"Could not verify admin status: {e}")
        except Exception:
            pass
        return False
    
    def check_rate_limit(self, identifier: str, limit: int, is_admin: bool = False) -> Dict[str, Any]:
        """
        Check if request is within rate limit.
        
        Returns:
            Dict with rate limit status and remaining requests
        """
        # Apply admin multiplier if user is admin
        if is_admin:
            limit = limit * self.admin_multiplier
        
        current_time = time.time()
        window_start = current_time - self.time_window
        
        if self.redis_client:
            return self._check_redis_rate_limit(identifier, limit, window_start)
        else:
            return self._check_memory_rate_limit(identifier, limit, window_start)
    
    def _check_redis_rate_limit(self, identifier: str, limit: int, window_start: float) -> Dict[str, Any]:
        """Check rate limit using Redis backend."""
        try:
            # Get current count from Redis
            key = f"rate_limit:{identifier}"
            current_count = self.redis_client.zcount(key, window_start, "+inf")
            
            if current_count >= limit:
                # Rate limit exceeded
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": window_start + self.time_window,
                    "limit": limit
                }
            
            # Add current request to Redis
            self.redis_client.zadd(key, {str(time.time()): time.time()})
            self.redis_client.expire(key, self.time_window)
            
            return {
                "allowed": True,
                "remaining": limit - current_count - 1,
                "reset_time": window_start + self.time_window,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"Redis rate limiting failed: {e}")
            # Fallback to memory-based rate limiting
            return self._check_memory_rate_limit(identifier, limit, window_start)
    
    def _check_memory_rate_limit(self, identifier: str, limit: int, window_start: float) -> Dict[str, Any]:
        """Check rate limit using in-memory storage."""
        current_time = time.time()
        
        if identifier not in self.memory_store:
            self.memory_store[identifier] = []
        
        # Clean old entries
        self.memory_store[identifier] = [
            timestamp for timestamp in self.memory_store[identifier]
            if timestamp > window_start
        ]
        
        current_count = len(self.memory_store[identifier])
        
        if current_count >= limit:
            # Rate limit exceeded
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": window_start + self.time_window,
                "limit": limit
            }
        
        # Add current request
        self.memory_store[identifier].append(current_time)
        
        return {
            "allowed": True,
            "remaining": limit - current_count - 1,
            "reset_time": window_start + self.time_window,
            "limit": limit
        }

def create_rate_limit_middleware(rate_limiter: RateLimiter):
    """
    Create FastAPI middleware for rate limiting.
    
    Args:
        rate_limiter: RateLimiter instance
        
    Returns:
        FastAPI middleware function
    """
    async def rate_limit_middleware(request: Request, call_next):
        """Rate limiting middleware function."""
        try:
            # Get user identifier
            identifier = rate_limiter.get_user_identifier(request)
            
            # Get rate limit for endpoint
            limit = rate_limiter.get_limit_for_endpoint(request.url.path)
            
            # Check if user is admin
            is_admin = rate_limiter.is_admin_user(request)
            
            # Check rate limit
            rate_limit_result = rate_limiter.check_rate_limit(identifier, limit, is_admin)
            
            if not rate_limit_result["allowed"]:
                # Rate limit exceeded
                try:
                    # Handle both seconds and milliseconds timestamps
                    reset_timestamp = rate_limit_result["reset_time"]
                    if reset_timestamp > 1e12:  # Likely milliseconds
                        timestamp_seconds = reset_timestamp / 1000.0
                    else:
                        timestamp_seconds = reset_timestamp
                    
                    if 946684800 <= timestamp_seconds <= 4102444800:
                        reset_time = datetime.fromtimestamp(timestamp_seconds)
                    else:
                        reset_time = datetime.utcnow() + timedelta(seconds=60)  # Default 1 minute
                except (ValueError, OverflowError, OSError):
                    reset_time = datetime.utcnow() + timedelta(seconds=60)  # Default 1 minute
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": "Too many requests. Please try again later.",
                        "reset_time": reset_time.isoformat(),
                        "limit": rate_limit_result["limit"]
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_limit_result["limit"]),
                        "X-RateLimit-Remaining": str(rate_limit_result["remaining"]),
                        "X-RateLimit-Reset": str(int(rate_limit_result["reset_time"]))
                    }
                )
            
            # Add rate limit headers to response
            response = await call_next(request)
            
            response.headers["X-RateLimit-Limit"] = str(rate_limit_result["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_result["remaining"])
            response.headers["X-RateLimit-Reset"] = str(int(rate_limit_result["reset_time"]))
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Continue without rate limiting if there's an error
            return await call_next(request)
    
    return rate_limit_middleware

def create_rate_limit_dependency(rate_limiter: RateLimiter, endpoint_limit: Optional[int] = None):
    """
    Create a dependency for rate limiting specific endpoints.
    
    Args:
        rate_limiter: RateLimiter instance
        endpoint_limit: Optional custom limit for this endpoint
        
    Returns:
        FastAPI dependency function
    """
    async def rate_limit_dependency(request: Request):
        """Rate limiting dependency function."""
        identifier = rate_limiter.get_user_identifier(request)
        limit = endpoint_limit or rate_limiter.get_limit_for_endpoint(request.url.path)
        is_admin = rate_limiter.is_admin_user(request)
        
        rate_limit_result = rate_limiter.check_rate_limit(identifier, limit, is_admin)
        
        if not rate_limit_result["allowed"]:
            try:
                # Handle both seconds and milliseconds timestamps
                reset_timestamp = rate_limit_result["reset_time"]
                if reset_timestamp > 1e12:  # Likely milliseconds
                    timestamp_seconds = reset_timestamp / 1000.0
                else:
                    timestamp_seconds = reset_timestamp
                
                if 946684800 <= timestamp_seconds <= 4102444800:
                    reset_time = datetime.fromtimestamp(timestamp_seconds)
                else:
                    reset_time = datetime.utcnow() + timedelta(seconds=60)  # Default 1 minute
            except (ValueError, OverflowError, OSError):
                reset_time = datetime.utcnow() + timedelta(seconds=60)  # Default 1 minute
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "reset_time": reset_time.isoformat(),
                    "limit": rate_limit_result["limit"]
                }
            )
        
        return rate_limit_result
    
    return rate_limit_dependency

# Example usage:
# from fastapi import FastAPI
# from .middleware.rate_limiter import RateLimiter, create_rate_limit_middleware
# 
# app = FastAPI()
# rate_limiter = RateLimiter()
# app.middleware("http")(create_rate_limit_middleware(rate_limiter)) 