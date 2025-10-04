"""
Structured logging configuration for ClosetGPT backend.
Provides JSON-formatted logging with error tracking and performance monitoring.
"""

import logging
import json
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

# Context variable to store request ID
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log errors and create analytics events."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("error_middleware")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        start_time = datetime.utcnow()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Log successful requests (optional, for debugging)
            if response.status_code >= 400:
                self.logger.warning(
                    f"HTTP {response.status_code} for {request.method} {request.url.path}",
                    extra={
                        "extra_fields": {
                            "request_id": request_id,
                            "method": request.method,
                            "path": request.url.path,
                            "status_code": response.status_code,
                            "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
                        }
                    }
                )
            
            return response
            
        except Exception as e:
            # Log error details
            error_id = str(uuid.uuid4())
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            error_details = {
                "error_id": error_id,
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": dict(request.headers),
                "duration_ms": duration_ms,
                "exception_type": type(e).__name__,
                "exception_message": str(e),
                "traceback": traceback.format_exc()
            }
            
            # Log error
            self.logger.error(
                f"Unhandled exception: {type(e).__name__}: {str(e)}",
                extra={"extra_fields": error_details},
                exc_info=True
            )
            
            # Try to log analytics event for error
            try:
                from ..models.analytics_event import AnalyticsEvent
                from ..services.analytics_service import log_analytics_event
                
                # Extract user ID from request if available
                user_id = None
                try:
                    # Try to get user ID from auth header or request state
                    auth_header = request.headers.get("authorization") if headers else None
                    if auth_header and auth_header.startswith("Bearer "):
                        token = auth_header.split(" ")[1]
                        # Decode JWT token to get user ID
                        import jwt
                        from ..routes.auth import SECRET_KEY, ALGORITHM
                        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                        user_id = (payload.get("sub") if payload else None)
                except:
                    pass
                
                analytics_event = AnalyticsEvent(
                    user_id=user_id,
                    event_type="application_error",
                    metadata={
                        "error_id": error_id,
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": 500,
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                        "duration_ms": duration_ms
                    }
                )
                log_analytics_event(analytics_event)
                
            except Exception as analytics_error:
                # Don't let analytics errors break the error handling
                self.logger.error(f"Failed to log analytics event: {analytics_error}")
            
            # Re-raise the exception
            raise

def setup_logging(level: str = "INFO") -> None:
    """Set up structured logging configuration."""
    
    # Create JSON formatter
    formatter = JSONFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler for errors
    try:
        file_handler = logging.FileHandler("logs/backend.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.ERROR)
        root_logger.addHandler(file_handler)
    except Exception:
        # Ignore file handler errors (e.g., logs directory doesn't exist)
        pass

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)

def log_performance(operation: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Log performance metrics."""
    logger = get_logger("performance")
    
    log_data = {
        "operation": operation,
        "duration_ms": duration_ms,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if metadata:
        log_data.update(metadata)
    
    logger.info(
        f"Performance: {operation} took {duration_ms:.2f}ms",
        extra={"extra_fields": log_data}
    )

def log_security_event(event_type: str, details: Dict[str, Any], user_id: Optional[str] = None) -> None:
    """Log security-related events."""
    logger = get_logger("security")
    
    log_data = {
        "event_type": event_type,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        **details
    }
    
    logger.warning(
        f"Security event: {event_type}",
        extra={"extra_fields": log_data}
    )

# Initialize logging on module import
setup_logging()

class ErrorTracker:
    """Error tracking and reporting utility."""
    def __init__(self, logger):
        self.logger = logger
        self.error_count = 0
        self.error_types = {}
    def track_error(self, error, context=None):
        import uuid
        error_id = str(uuid.uuid4())
        error_type = type(error).__name__
        self.error_count += 1
        self.error_types[error_type] = (self.error_types.get(error_type, 0) if self.error_types else 0) + 1
        error_data = {
            "error_id": error_id,
            "error_type": error_type,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "error_count": self.error_count
        }
        if context:
            error_data.update(context)
        self.logger.error(
            f"Error tracked: {error_type}: {str(error)}",
            extra={"extra_fields": error_data},
            exc_info=True
        )
        return error_id
    def get_error_stats(self):
        return {
            "total_errors": self.error_count,
            "error_types": self.error_types,
            "timestamp": datetime.utcnow().isoformat()
        }
    def reset_stats(self):
        self.error_count = 0
        self.error_types = {}

class RequestLogger:
    """Request logging utility."""
    def __init__(self, logger):
        self.logger = logger
    
    async def log_request(self, request, response, duration_ms):
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
            "user_agent": request.headers.get("user-agent", "") if headers else ""),
            "ip_address": request.client.host if request.client else None
        }
        self.logger.info(
            f"Request: {request.method} {request.url.path} - {response.status_code} ({duration_ms:.2f}ms)",
            extra={"extra_fields": log_data}
        )

