"""
Custom exceptions and error handling for ClosetGPT.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from .logging import get_logger, ErrorTracker

logger = get_logger("exceptions")
error_tracker = ErrorTracker(logger)

class ClosetGPTException(Exception):
    """Base exception for ClosetGPT application."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
        
        # Track error
        error_tracker.track_error(
            self.error_code,
            self.message,
            **self.details
        )

class AuthenticationError(ClosetGPTException):
    """Authentication and authorization errors."""
    
    def __init__(self, message: str = "Authentication failed", details: Dict[str, Any] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)

class AuthorizationError(ClosetGPTException):
    """Authorization errors."""
    
    def __init__(self, message: str = "Access denied", details: Dict[str, Any] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", details)

class ValidationError(ClosetGPTException):
    """Data validation errors."""
    
    def __init__(self, message: str = "Validation failed", field: str = None, details: Dict[str, Any] = None):
        if field:
            details = details or {}
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)

class DatabaseError(ClosetGPTException):
    """Database operation errors."""
    
    def __init__(self, message: str = "Database operation failed", operation: str = None, details: Dict[str, Any] = None):
        if operation:
            details = details or {}
            details["operation"] = operation
        super().__init__(message, "DATABASE_ERROR", details)

class AIProcessingError(ClosetGPTException):
    """AI/ML processing errors."""
    
    def __init__(self, message: str = "AI processing failed", model: str = None, details: Dict[str, Any] = None):
        if model:
            details = details or {}
            details["model"] = model
        super().__init__(message, "AI_PROCESSING_ERROR", details)

class ImageProcessingError(ClosetGPTException):
    """Image processing errors."""
    
    def __init__(self, message: str = "Image processing failed", operation: str = None, details: Dict[str, Any] = None):
        if operation:
            details = details or {}
            details["operation"] = operation
        super().__init__(message, "IMAGE_PROCESSING_ERROR", details)

class OutfitGenerationError(ClosetGPTException):
    """Outfit generation errors."""
    
    def __init__(self, message: str = "Outfit generation failed", context: str = None, details: Dict[str, Any] = None):
        if context:
            details = details or {}
            details["context"] = context
        super().__init__(message, "OUTFIT_GENERATION_ERROR", details)

class ExternalServiceError(ClosetGPTException):
    """External service integration errors."""
    
    def __init__(self, message: str = "External service error", service: str = None, details: Dict[str, Any] = None):
        if service:
            details = details or {}
            details["service"] = service
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)

class RateLimitError(ClosetGPTException):
    """Rate limiting errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", limit: int = None, details: Dict[str, Any] = None):
        if limit:
            details = details or {}
            details["limit"] = limit
        super().__init__(message, "RATE_LIMIT_ERROR", details)

class ResourceNotFoundError(ClosetGPTException):
    """Resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", resource_type: str = None, resource_id: str = None, details: Dict[str, Any] = None):
        if resource_type or resource_id:
            details = details or {}
            if resource_type:
                details["resource_type"] = resource_type
            if resource_id:
                details["resource_id"] = resource_id
        super().__init__(message, "RESOURCE_NOT_FOUND", details)

class ConfigurationError(ClosetGPTException):
    """Configuration errors."""
    
    def __init__(self, message: str = "Configuration error", config_key: str = None, details: Dict[str, Any] = None):
        if config_key:
            details = details or {}
            details["config_key"] = config_key
        super().__init__(message, "CONFIGURATION_ERROR", details)

# Exception to HTTP status code mapping
EXCEPTION_STATUS_MAPPING = {
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    AIProcessingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ImageProcessingError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    OutfitGenerationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
    ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}

def handle_closetgpt_exception(exc: ClosetGPTException) -> HTTPException:
    """Convert ClosetGPT exceptions to HTTP exceptions."""
    status_code = EXCEPTION_STATUS_MAPPING.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )

def create_validation_error(field: str, message: str, value: Any = None) -> ValidationError:
    """Create a validation error with field information."""
    details = {"field": field}
    if value is not None:
        details["value"] = str(value)
    
    return ValidationError(
        message=f"Validation error in field '{field}': {message}",
        field=field,
        details=details
    )

def create_not_found_error(resource_type: str, resource_id: str) -> ResourceNotFoundError:
    """Create a resource not found error."""
    return ResourceNotFoundError(
        message=f"{resource_type} with id '{resource_id}' not found",
        resource_type=resource_type,
        resource_id=resource_id
    )

def create_ai_error(message: str, model: str = None, context: str = None) -> AIProcessingError:
    """Create an AI processing error."""
    details = {}
    if context:
        details["context"] = context
    
    return AIProcessingError(
        message=message,
        model=model,
        details=details
    )

def create_database_error(message: str, operation: str = None, collection: str = None) -> DatabaseError:
    """Create a database error."""
    details = {}
    if collection:
        details["collection"] = collection
    
    return DatabaseError(
        message=message,
        operation=operation,
        details=details
    )

# Global exception handlers
def setup_exception_handlers(app):
    """Setup global exception handlers for the FastAPI app."""
    
    @app.exception_handler(ClosetGPTException)
    async def closetgpt_exception_handler(request, exc: ClosetGPTException):
        """Handle ClosetGPT exceptions."""
        http_exc = handle_closetgpt_exception(exc)
        
        logger.error(
            f"ClosetGPT exception handled: {exc.error_code}",
            extra={
                "extra_fields": {
                    "error_code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                    "status_code": http_exc.status_code,
                    "request_path": request.url.path,
                    "request_method": request.method
                }
            }
        )
        
        return http_exc
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle general exceptions."""
        error_tracker.track_error(
            "UNHANDLED_EXCEPTION",
            str(exc),
            exception_type=type(exc).__name__,
            request_path=request.url.path,
            request_method=request.method
        )
        
        logger.error(
            "Unhandled exception",
            extra={
                "extra_fields": {
                    "exception_type": type(exc).__name__,
                    "message": str(exc),
                    "request_path": request.url.path,
                    "request_method": request.method
                }
            },
            exc_info=True
        )
        
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        ) 