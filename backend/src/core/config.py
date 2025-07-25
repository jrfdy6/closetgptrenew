"""
Configuration management for ClosetGPT.
Handles environment variables, validation, and production settings.
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from .logging import get_logger

logger = get_logger("config")

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    APP_NAME: str = "ClosetGPT"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8080, env="PORT")
    WORKERS: int = 1
    
    # Database settings
    FIREBASE_PROJECT_ID: str = "closetgptrenew"  # Default for development
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    FIREBASE_CLIENT_ID: Optional[str] = None
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = None
    
    # AI/ML settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch32"
    
    # Security settings
    SECRET_KEY: str = "dev-secret-key-change-in-production"  # Default for development
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS settings
    ALLOWED_ORIGINS: str = "*"
    ALLOWED_METHODS: str = "*"
    ALLOWED_HEADERS: str = "*"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"
    
    # Monitoring settings
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # External services
    WEATHER_API_KEY: Optional[str] = None
    WEATHER_BASE_URL: str = "http://api.weatherapi.com/v1"
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("DEBUG")
    def validate_debug(cls, v, values):
        if values.get("ENVIRONMENT") == "production" and v:
            logger.warning("Debug mode enabled in production environment")
        return v
    
    @validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v):
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",")]
    
    @validator("ALLOWED_METHODS")
    def parse_allowed_methods(cls, v):
        if v == "*":
            return ["*"]
        return [method.strip() for method in v.split(",")]
    
    @validator("ALLOWED_HEADERS")
    def parse_allowed_headers(cls, v):
        if v == "*":
            return ["*"]
        return [header.strip() for header in v.split(",")]
    
    @validator("ALLOWED_IMAGE_TYPES")
    def parse_allowed_image_types(cls, v):
        return [mime_type.strip() for mime_type in v.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings."""
    return settings

def validate_production_settings():
    """Validate critical settings for production deployment."""
    if settings.ENVIRONMENT == "production":
        required_settings = [
            "FIREBASE_PROJECT_ID",
            "SECRET_KEY",
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not getattr(settings, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            raise ValueError(f"Missing required settings for production: {missing_settings}")
        
        # Warn about optional but recommended settings
        recommended_settings = [
            "OPENAI_API_KEY",
            "WEATHER_API_KEY",
        ]
        
        missing_recommended = []
        for setting in recommended_settings:
            if not getattr(settings, setting):
                missing_recommended.append(setting)
        
        if missing_recommended:
            logger.warning(f"Missing recommended settings: {missing_recommended}")
        
        # Security checks
        if settings.DEBUG:
            logger.warning("Debug mode is enabled in production")
        
        if settings.ALLOWED_ORIGINS == ["*"]:
            logger.warning("CORS is configured to allow all origins in production")
        
        if settings.RATE_LIMIT_REQUESTS_PER_MINUTE > 100:
            logger.warning("Rate limit is set very high for production")

def get_firebase_config() -> Dict[str, Any]:
    """Get Firebase configuration dictionary."""
    return {
        "type": "service_account",
        "project_id": settings.FIREBASE_PROJECT_ID,
        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
        "private_key": settings.FIREBASE_PRIVATE_KEY,
        "client_email": settings.FIREBASE_CLIENT_EMAIL,
        "client_id": settings.FIREBASE_CLIENT_ID,
        "auth_uri": settings.FIREBASE_AUTH_URI,
        "token_uri": settings.FIREBASE_TOKEN_URI,
        "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
        "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
    }

def get_cors_config() -> Dict[str, Any]:
    """Get CORS configuration."""
    return {
        "allow_origins": settings.ALLOWED_ORIGINS,
        "allow_credentials": True,
        "allow_methods": settings.ALLOWED_METHODS,
        "allow_headers": settings.ALLOWED_HEADERS,
    }

def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    return {
        "log_level": settings.LOG_LEVEL,
        "log_file": settings.LOG_FILE,
        "enable_console": True,
        "enable_file": bool(settings.LOG_FILE),
    }

# Initialize settings validation
try:
    validate_production_settings()
    logger.info("Configuration validation completed", extra={
        "extra_fields": {
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION
        }
    })
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")
    raise 