"""
Security utilities and middleware for ClosetGPT.
Provides authentication, authorization, input validation, and security checks.
"""

import re
import hashlib
import secrets
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel, validator
import logging

from .config import get_settings
from .logging import get_logger

logger = get_logger("security")
settings = get_settings()

# Security token scheme
security = HTTPBearer()

class SecurityConfig:
    """Security configuration and utilities."""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]')
    
    # Input validation patterns
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
    PHONE_REGEX = re.compile(r'^\+?1?\d{9,15}$')
    
    # File upload restrictions
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 15  # minutes

class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email or not isinstance(email, str):
            return False
        return bool(SecurityConfig.EMAIL_REGEX.match(email))
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if not password or len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters"
        
        if not SecurityConfig.PASSWORD_REGEX.match(password):
            return False, "Password must contain uppercase, lowercase, number, and special character"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        if not username or not isinstance(username, str):
            return False
        return bool(SecurityConfig.USERNAME_REGEX.match(username))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        if not phone or not isinstance(phone, str):
            return False
        return bool(SecurityConfig.PHONE_REGEX.match(phone))
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        if not input_str:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
        sanitized = input_str
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Limit length
        return sanitized[:1000]
    
    @staticmethod
    def validate_file_upload(filename: str, file_size: int, content_type: str) -> tuple[bool, str]:
        """Validate file upload."""
        # Check file size
        if file_size > SecurityConfig.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum of {SecurityConfig.MAX_FILE_SIZE} bytes"
        
        # Check file extension
        if '.' not in filename:
            return False, "Invalid file format"
        
        extension = filename.lower().split('.')[-1]
        if f'.{extension}' not in SecurityConfig.ALLOWED_EXTENSIONS:
            return False, f"File type .{extension} not allowed"
        
        # Check content type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if content_type not in allowed_types:
            return False, f"Content type {content_type} not allowed"
        
        return True, "File upload is valid"

class AuthenticationManager:
    """Authentication and authorization management."""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate secure random token."""
        return secrets.token_urlsafe(length)

# Global authentication manager
auth_manager = AuthenticationManager()

# Convenience functions for backward compatibility
def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return auth_manager.verify_password(password, hashed)

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return auth_manager.hash_password(password)

class RateLimiter:
    """Simple in-memory rate limiter (use Redis in production)."""
    
    def __init__(self):
        self.attempts = {}
        self.lockouts = {}
    
    def is_rate_limited(self, identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """Check if identifier is rate limited."""
        now = datetime.utcnow()
        
        # Check if locked out
        if identifier in self.lockouts:
            lockout_until = self.lockouts[identifier]
            if now < lockout_until:
                return True
            else:
                del self.lockouts[identifier]
                if identifier in self.attempts:
                    del self.attempts[identifier]
        
        # Check attempts
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        # Remove old attempts outside window
        window_start = now - timedelta(minutes=window_minutes)
        self.attempts[identifier] = [
            attempt for attempt in self.attempts[identifier] 
            if attempt > window_start
        ]
        
        # Check if over limit
        if len(self.attempts[identifier]) >= max_attempts:
            self.lockouts[identifier] = now + timedelta(minutes=window_minutes)
            return True
        
        return False
    
    def record_attempt(self, identifier: str):
        """Record an attempt for rate limiting."""
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        self.attempts[identifier].append(datetime.utcnow())

# Global rate limiter
rate_limiter = RateLimiter()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = (payload.get("sub") if payload else None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "payload": payload}

async def require_authentication(request: Request) -> dict:
    """Require authentication for protected endpoints."""
    # Check for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if rate_limiter.is_rate_limited(f"auth_{client_ip}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts"
        )
    
    # Get authorization header
    auth_header = request.(headers.get("Authorization") if headers else None)
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    payload = auth_manager.verify_token(token)
    
    if payload is None:
        rate_limiter.record_attempt(f"auth_{client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = (payload.get("sub") if payload else None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "payload": payload}

class SecurityMiddleware:
    """Security middleware for additional protection."""
    
    @staticmethod
    async def validate_request(request: Request):
        """Validate incoming request for security issues."""
        # Check request size
        content_length = request.(headers.get("content-length") if headers else None)
        if content_length and int(content_length) > SecurityConfig.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request too large"
            )
        
        # Check for suspicious headers
        suspicious_headers = [
            "x-forwarded-for", "x-real-ip", "x-forwarded-proto",
            "x-forwarded-host", "x-forwarded-port"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                logger.warning(f"Suspicious header detected: {header}", extra={
                    "extra_fields": {
                        "client_ip": request.client.host,
                        "user_agent": request.(headers.get("user-agent") if headers else None),
                        "suspicious_header": header
                    }
                })
        
        # Rate limiting for sensitive endpoints
        sensitive_paths = ["/api/auth/login", "/api/auth/register", "/api/upload"]
        if any(path in request.url.path for path in sensitive_paths):
            client_ip = request.client.host if request.client else "unknown"
            if rate_limiter.is_rate_limited(f"api_{client_ip}", max_attempts=10):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )

def validate_production_security():
    """Validate security settings for production."""
    if settings.ENVIRONMENT == "production":
        # Check for weak secret key
        if len(settings.SECRET_KEY) < 32:
            logger.warning("Secret key is too short for production")
        
        # Check CORS settings
        if settings.ALLOWED_ORIGINS == ["*"]:
            logger.warning("CORS allows all origins in production")
        
        # Check rate limiting
        if settings.RATE_LIMIT_REQUESTS_PER_MINUTE > 100:
            logger.warning("Rate limit is very high for production")
        
        # Check token expiration
        if settings.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
            logger.warning("Access token expiration is very long for production")

# Initialize security validation
validate_production_security() 