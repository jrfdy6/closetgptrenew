"""
Security test endpoints for verifying authentication, validation, and security features.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from ..core.security import (
    InputValidator, 
    auth_manager, 
    get_current_user, 
    require_authentication,
    SecurityConfig
)
from ..core.logging import get_logger

router = APIRouter()
logger = get_logger("security")

class ValidationTestRequest(BaseModel):
    """Test request for input validation."""
    email: str
    password: str
    username: str
    phone: Optional[str] = None
    text_input: str

class SecurityTestResponse(BaseModel):
    """Response for security tests."""
    success: bool
    message: str
    details: dict

@router.post("/test/validation", response_model=SecurityTestResponse)
async def test_input_validation(request: ValidationTestRequest):
    """Test input validation features."""
    results = {}
    
    # Test email validation
    email_valid = InputValidator.validate_email(request.email)
    results["email"] = {"valid": email_valid, "value": request.email}
    
    # Test password validation
    password_valid, password_message = InputValidator.validate_password(request.password)
    results["password"] = {"valid": password_valid, "message": password_message}
    
    # Test username validation
    username_valid = InputValidator.validate_username(request.username)
    results["username"] = {"valid": username_valid, "value": request.username}
    
    # Test phone validation (if provided)
    if request.phone:
        phone_valid = InputValidator.validate_phone(request.phone)
        results["phone"] = {"valid": phone_valid, "value": request.phone}
    
    # Test input sanitization
    sanitized_input = InputValidator.sanitize_input(request.text_input)
    results["sanitization"] = {
        "original": request.text_input,
        "sanitized": sanitized_input,
        "changed": request.text_input != sanitized_input
    }
    
    # Check overall validation
    all_valid = all([
        email_valid, 
        password_valid, 
        username_valid,
        not request.phone or results["phone"]["valid"]
    ])
    
    logger.info("Input validation test completed", extra={
        "extra_fields": {
            "all_valid": all_valid,
            "results": results
        }
    })
    
    return SecurityTestResponse(
        success=all_valid,
        message="Input validation test completed",
        details=results
    )

@(router.get("/test/authentication", response_model=SecurityTestResponse) if router else response_model=SecurityTestResponse)
async def test_authentication(user: dict = Depends(get_current_user)):
    """Test authentication middleware."""
    logger.info("Authentication test successful", extra={
        "extra_fields": {
            "user_id": user["user_id"],
            "payload": user["payload"]
        }
    })
    
    return SecurityTestResponse(
        success=True,
        message="Authentication successful",
        details={
            "user_id": user["user_id"],
            "authenticated": True,
            "token_valid": True
        }
    )

@router.post("/test/token", response_model=SecurityTestResponse)
async def test_token_generation():
    """Test JWT token generation and validation."""
    # Create test data
    test_data = {"sub": "test_user_123", "role": "user"}
    
    # Generate token
    token = auth_manager.create_access_token(test_data)
    
    # Verify token
    payload = auth_manager.verify_token(token)
    
    # Generate secure token
    secure_token = auth_manager.generate_secure_token()
    
    logger.info("Token generation test completed", extra={
        "extra_fields": {
            "token_generated": bool(token),
            "token_verified": bool(payload),
            "secure_token_generated": bool(secure_token)
        }
    })
    
    return SecurityTestResponse(
        success=bool(payload),
        message="Token generation and validation test completed",
        details={
            "token_generated": bool(token),
            "token_verified": bool(payload),
            "payload_matches": payload.get("sub") == test_data["sub"] if payload else False,
            "secure_token_length": len(secure_token)
        }
    )

@(router.get("/test/security-config", response_model=SecurityTestResponse) if router else response_model=SecurityTestResponse)
async def test_security_configuration():
    """Test security configuration."""
    config = {
        "min_password_length": SecurityConfig.MIN_PASSWORD_LENGTH,
        "allowed_extensions": list(SecurityConfig.ALLOWED_EXTENSIONS),
        "max_file_size": SecurityConfig.MAX_FILE_SIZE,
        "max_login_attempts": SecurityConfig.MAX_LOGIN_ATTEMPTS,
        "lockout_duration": SecurityConfig.LOCKOUT_DURATION
    }
    
    logger.info("Security configuration test completed", extra={
        "extra_fields": config
    })
    
    return SecurityTestResponse(
        success=True,
        message="Security configuration loaded successfully",
        details=config
    )

@router.post("/test/file-validation", response_model=SecurityTestResponse)
async def test_file_validation(filename: str, file_size: int, content_type: str):
    """Test file upload validation."""
    is_valid, message = InputValidator.validate_file_upload(filename, file_size, content_type)
    
    logger.info("File validation test completed", extra={
        "extra_fields": {
            "filename": filename,
            "file_size": file_size,
            "content_type": content_type,
            "is_valid": is_valid,
            "message": message
        }
    })
    
    return SecurityTestResponse(
        success=is_valid,
        message=message,
        details={
            "filename": filename,
            "file_size": file_size,
            "content_type": content_type,
            "validation_passed": is_valid
        }
    )

@(router.get("/test/protected", response_model=SecurityTestResponse) if router else response_model=SecurityTestResponse)
async def test_protected_endpoint(user: dict = Depends(require_authentication)):
    """Test protected endpoint with authentication."""
    logger.info("Protected endpoint accessed successfully", extra={
        "extra_fields": {
            "user_id": user["user_id"],
            "endpoint": "/api/security/test/protected"
        }
    })
    
    return SecurityTestResponse(
        success=True,
        message="Protected endpoint accessed successfully",
        details={
            "user_id": user["user_id"],
            "authenticated": True,
            "authorized": True
        }
    )

@(router.get("/test/rate-limit") if router else None)
async def test_rate_limiting():
    """Test rate limiting (this endpoint should be rate limited)."""
    from ..core.security import rate_limiter
    
    # Simulate rate limiting
    client_id = "test_client"
    is_limited = rate_limiter.is_rate_limited(client_id, max_attempts=3, window_minutes=1)
    
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Record attempt
    rate_limiter.record_attempt(client_id)
    
    logger.info("Rate limiting test completed", extra={
        "extra_fields": {
            "client_id": client_id,
            "is_limited": is_limited
        }
    })
    
    return SecurityTestResponse(
        success=not is_limited,
        message="Rate limiting test completed",
        details={
            "client_id": client_id,
            "rate_limited": is_limited,
            "attempts_recorded": True
        }
    ) 