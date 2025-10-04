"""
Production Middleware for ClosetGPT
Provides request logging, performance monitoring, and error tracking.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from .logging import get_logger, RequestLogger, ErrorTracker, ErrorLoggingMiddleware
from .cache import cache_manager

# Break circular import by making monitoring imports optional
try:
    from ..routes.monitoring import increment_request_count, increment_error_count, increment_slow_request_count
    MONITORING_AVAILABLE = True
except ImportError:
    # If monitoring routes aren't available, use dummy functions
    def increment_request_count():
        pass
    def increment_error_count():
        pass
    def increment_slow_request_count():
        pass
    MONITORING_AVAILABLE = False

logger = get_logger("middleware")
request_logger = RequestLogger(logger)
error_tracker = ErrorTracker(logger)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger.info(f"LoggingMiddleware: Received {request.method} {request.url.path}")
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add user ID if available (from auth middleware)
        user_id = getattr(request.state, 'user_id', None)
        
        # Increment request count for monitoring (if available)
        if MONITORING_AVAILABLE:
            try:
                increment_request_count()
            except Exception as e:
                logger.warning(f"Failed to increment request count: {e}")
        
        # Log request start
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "extra_fields": {
                    "request_id": request_id,
                    "user_id": user_id,
                    "method": request.method,
                    "url": str(request.url),
                    "ip_address": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent") if headers else None),
                }
            }
        )
        
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log successful request
            try:
                await request_logger.log_request(request, response, duration)
            except Exception as e:
                logger.warning(f"Failed to log request: {e}")
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Increment error count for monitoring (if available)
            if MONITORING_AVAILABLE:
                try:
                    increment_error_count()
                except Exception as monitoring_error:
                    logger.warning(f"Failed to increment error count: {monitoring_error}")
            
            # Track error
            try:
                error_tracker.track_error(
                    "request_error",
                    str(e),
                    request_id=request_id,
                    user_id=user_id,
                    method=request.method,
                    url=str(request.url),
                    duration_seconds=duration
                )
            except Exception as tracking_error:
                logger.warning(f"Failed to track error: {tracking_error}")
            
            # Re-raise the exception
            raise

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring."""
    
    def __init__(self, app: ASGIApp, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log slow requests and increment counter
        if duration > self.slow_request_threshold:
            increment_slow_request_count()
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path}",
                extra={
                    "extra_fields": {
                        "request_id": getattr(request.state, 'request_id', None),
                        "user_id": getattr(request.state, 'user_id', None),
                        "method": request.method,
                        "url": str(request.url),
                        "duration_seconds": duration,
                        "threshold_seconds": self.slow_request_threshold
                    }
                }
            )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers and basic security checks."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware."""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Simple rate limiting (in production, use Redis or similar)
        current_time = time.time()
        minute_key = int(current_time / 60)
        
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {}
        
        if minute_key not in self.request_counts[client_ip]:
            self.request_counts[client_ip][minute_key] = 0
        
        self.request_counts[client_ip][minute_key] += 1
        
        # Check rate limit
        if self.request_counts[client_ip][minute_key] > self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                extra={
                    "extra_fields": {
                        "client_ip": client_ip,
                        "request_count": self.request_counts[client_ip][minute_key],
                        "limit": self.requests_per_minute,
                        "method": request.method,
                        "url": str(request.url)
                    }
                }
            )
            
            # Return rate limit response
            from fastapi import HTTPException
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - self.request_counts[client_ip][minute_key]
        )
        
        return response

class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for response caching."""
    
    def __init__(self, app: ASGIApp, cache_ttl: int = 300):
        super().__init__(app)
        self.cache_ttl = cache_ttl
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Skip caching for certain endpoints
        skip_cache_paths = [
            "/health", "/api/health", "/api/metrics", "/api/ready", 
            "/api/status", "/api/security"
        ]
        
        if any(path in request.url.path for path in skip_cache_paths):
            return await call_next(request)
        
        # Generate cache key
        cache_key = f"response:{request.method}:{request.url.path}:{hash(str(request.query_params))}"
        
        # Try to get from cache
        cached_response = (cache_manager.get("api", cache_key) if cache_manager else cache_key)
        if cached_response:
            logger.debug("Cache hit for response", extra={
                "extra_fields": {
                    "cache_key": cache_key,
                    "url": str(request.url)
                }
            })
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content=cached_response,
                headers={"X-Cache": "HIT"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            try:
                # Try to get response content
                if hasattr(response, 'body'):
                    content = response.body.decode() if response.body else None
                    if content:
                        cache_manager.set("api", cache_key, content, self.cache_ttl)
                        logger.debug("Cached response", extra={
                            "extra_fields": {
                                "cache_key": cache_key,
                                "url": str(request.url),
                                "ttl": self.cache_ttl
                            }
                        })
            except Exception as e:
                logger.warning(f"Failed to cache response: {e}")
        
        return response

class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware to handle health check requests efficiently."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip logging for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        # Process other requests normally
        return await call_next(request)

def setup_middleware(app: ASGIApp) -> None:
    """Setup only LoggingMiddleware for debugging."""
    # print("DEBUG: setup_middleware called - adding LoggingMiddleware")
    
    # RE-ENABLING LOGGING MIDDLEWARE NOW THAT STARTUP IS STABLE
    app.add_middleware(LoggingMiddleware)
    
    # app.add_middleware(CacheMiddleware, cache_ttl=300)
    # app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    # app.add_middleware(SecurityMiddleware)
    # app.add_middleware(PerformanceMiddleware, slow_request_threshold=1.0)
    # app.add_middleware(ErrorLoggingMiddleware)  # Add error logging middleware
    # app.add_middleware(HealthCheckMiddleware)
    
    # Make logging call safer to prevent silent failures
    try:
        logger.info("LoggingMiddleware re-enabled - startup issue resolved")
        # print("DEBUG: LoggingMiddleware logging call completed successfully")
    except Exception as e:
        # print(f"DEBUG: LoggingMiddleware logging call failed: {e}")
        # Continue anyway - don't let logging failure break the app
    
    # print("DEBUG: setup_middleware completed - LoggingMiddleware re-enabled") 