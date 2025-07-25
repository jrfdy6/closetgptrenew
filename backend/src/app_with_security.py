#!/usr/bin/env python3
"""
FastAPI App with Integrated Security

This module provides a FastAPI application with all security components integrated:
- Rate limiting middleware
- Image sanitization for uploads
- Field-level encryption for sensitive data
- Authentication middleware
- Security headers
"""

from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth as firebase_auth
import logging
import os
from typing import Dict, Any, Optional
import tempfile

# Import security components
from middleware.rate_limiter import RateLimiter, create_rate_limit_middleware
from utils.image_sanitizer import ImageSanitizer, sanitize_uploaded_image
from utils.encryption import get_encryptor, encrypt_sensitive_data, decrypt_sensitive_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    firebase_admin.initialize_app()

# Initialize security components
rate_limiter = RateLimiter()
image_sanitizer = ImageSanitizer()
encryptor = get_encryptor()

# Security scheme
security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="Wardrobe System API",
    description="Secure wardrobe management system with AI-powered outfit generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.middleware("http")(create_rate_limit_middleware(rate_limiter))

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify Firebase ID token and return user data."""
    try:
        token = credentials.credentials
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "security": {
            "rate_limiting": "enabled",
            "image_sanitization": "enabled",
            "encryption": "enabled",
            "authentication": "required"
        }
    }

# Secure upload endpoint with image sanitization
@app.post("/upload/secure")
async def secure_upload(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload and sanitize an image securely."""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Only image files are allowed"
            )
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Sanitize the uploaded image
            sanitization_result = sanitize_uploaded_image(file, temp_dir)
            
            # Encrypt the file path for storage
            user_id = current_user["uid"]
            encrypted_path = encrypt_sensitive_data({
                "file_path": sanitization_result["output_path"],
                "original_filename": file.filename
            }, user_id)
            
            return {
                "message": "File uploaded and sanitized successfully",
                "file_id": sanitization_result["file_hash"],
                "sanitized_size": sanitization_result["sanitized_size"],
                "security_features": sanitization_result["security_features"],
                "encrypted_metadata": encrypted_path
            }
            
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Upload failed"
        )

# Secure profile update with encryption
@app.put("/profile/secure")
async def update_profile_secure(
    profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile with encrypted sensitive data."""
    try:
        user_id = current_user["uid"]
        
        # Encrypt sensitive fields
        encrypted_profile = encrypt_sensitive_data(profile_data, user_id)
        
        # Here you would save to Firestore
        # For demo purposes, we'll just return the encrypted data
        return {
            "message": "Profile updated securely",
            "encrypted_fields": len([f for f in encrypted_profile.values() 
                                   if isinstance(f, dict) and f.get('encrypted')]),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Profile update failed"
        )

# Secure profile retrieval with decryption
@app.get("/profile/secure")
async def get_profile_secure(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve user profile with decrypted sensitive data."""
    try:
        user_id = current_user["uid"]
        
        # Here you would fetch from Firestore
        # For demo purposes, we'll create sample encrypted data
        sample_encrypted_data = {
            "email": encryptor.encrypt_field("user@example.com", "email", user_id),
            "profile_image_url": encryptor.encrypt_field("https://example.com/profile.jpg", "profile_image_url", user_id),
            "wardrobe_items": ["item1", "item2"]  # Not encrypted
        }
        
        # Decrypt sensitive fields
        decrypted_profile = decrypt_sensitive_data(sample_encrypted_data, user_id)
        
        return {
            "profile": decrypted_profile,
            "user_id": user_id,
            "security": "decrypted"
        }
        
    except Exception as e:
        logger.error(f"Profile retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Profile retrieval failed"
        )

# Rate limit test endpoint
@app.get("/test/rate-limit")
async def test_rate_limit(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Test endpoint to demonstrate rate limiting."""
    return {
        "message": "Rate limiting is working",
        "user_id": current_user["uid"],
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Security status endpoint
@app.get("/security/status")
async def security_status():
    """Get security configuration status."""
    return {
        "rate_limiting": {
            "enabled": True,
            "limits": rate_limiter.default_limits
        },
        "image_sanitization": {
            "enabled": True,
            "allowed_formats": image_sanitizer.ALLOWED_EXTENSIONS,
            "max_size": f"{image_sanitizer.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        },
        "encryption": {
            "enabled": True,
            "algorithm": "AES-256-GCM",
            "encrypted_fields": list(encryptor.encrypted_fields)
        },
        "authentication": {
            "required": True,
            "provider": "Firebase Auth"
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with security headers."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions securely."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
        headers={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Run the app with security features
    uvicorn.run(
        "app_with_security:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info"
    ) 