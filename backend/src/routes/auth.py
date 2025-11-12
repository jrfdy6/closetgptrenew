"""
Authentication routes for Easy Outfit App.
Handles user registration, login, and profile management.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
import jwt
import logging
import firebase_admin
from firebase_admin import auth as firebase_auth, firestore
import asyncio
import signal
from contextlib import asynccontextmanager
import concurrent.futures

from ..core.security import verify_password, get_password_hash
from ..core.logging import get_logger
from ..config.firebase import db
from ..models.analytics_event import AnalyticsEvent
from ..services.analytics_service import log_analytics_event
from ..services.subscription_utils import (
    DEFAULT_SUBSCRIPTION_TIER,
    subscription_defaults,
)

# HTTP Bearer scheme for token extraction
security = HTTPBearer()

# JWT configuration (keeping for backward compatibility)
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logger = get_logger("auth")
# db is imported from config.firebase

router = APIRouter(tags=["authentication"])

@asynccontextmanager
async def timeout_context(timeout_seconds: float):
    """Context manager for timeout handling."""
    try:
        yield
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification timed out"
        )

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from Firebase ID token."""
    try:
        logger.info("🔍 DEBUG: ===== STARTING AUTHENTICATION PROCESS =====")
        token = credentials.credentials
        logger.info(f"🔍 DEBUG: Received token length: {len(token)}")
        logger.info(f"🔍 DEBUG: Received token starts with: {token[:20]}...")
        
        logger.info("🔍 DEBUG: About to start Firebase token verification...")
        
        # Try with default settings first with timeout
        try:
            logger.info("🔍 DEBUG: Creating ThreadPoolExecutor...")
            
            # Use a timeout for the Firebase verification
            with concurrent.futures.ThreadPoolExecutor() as executor:
                logger.info("🔍 DEBUG: Submitting Firebase verification task...")
                future = executor.submit(firebase_auth.verify_id_token, token)
                logger.info("🔍 DEBUG: Waiting for Firebase verification result...")
                try:
                    decoded_token = future.result(timeout=30.0)  # Increased timeout to 30 seconds
                    logger.info("🔍 DEBUG: Firebase verification completed successfully!")
                    logger.info(f"🔍 DEBUG: Decoded token keys: {list(decoded_token.keys())}")
                except concurrent.futures.TimeoutError:
                    logger.error("🔍 DEBUG: Firebase token verification timed out after 30 seconds")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token verification timed out"
                    )
            
            logger.info("🔍 DEBUG: Extracting user_id from decoded token...")
            user_id: str = (decoded_token.get("uid") if decoded_token else None)
            logger.info(f"🔍 DEBUG: Token verification successful, user_id: {user_id}")
            
            if user_id is None:
                logger.error("🔍 DEBUG: No user_id found in decoded token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: no user ID found"
                )
            
            logger.info("🔍 DEBUG: Authentication completed successfully!")
            logger.info("🔍 DEBUG: ===== AUTHENTICATION PROCESS COMPLETED =====")
            return user_id
        except Exception as e:
            logger.error(f"🔍 DEBUG: Firebase token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )
    except firebase_auth.ExpiredIdTokenError:
        logger.error("🔍 DEBUG: Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except firebase_auth.RevokedIdTokenError:
        logger.error("🔍 DEBUG: Token has been revoked")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    except firebase_auth.InvalidIdTokenError:
        logger.error("🔍 DEBUG: Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"🔍 DEBUG: Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Keep the old JWT function for backward compatibility
def get_current_user_id_jwt(token: str = Depends(security)) -> str:
    """Get current user ID from JWT token (legacy)."""
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = (payload.get("sub") if payload else None)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def create_access_token(data: dict):
    """Create JWT access token (legacy)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    name: str
    email: str
    avatar_url: Optional[str] = None

@router.post("/verify-token")
async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify a Firebase ID token and return user information."""
    try:
        token = credentials.credentials
        decoded_token = firebase_auth.verify_id_token(token)
        
        user_id = (decoded_token.get("uid") if decoded_token else None)
        email = (decoded_token.get("email") if decoded_token else None)
        name = (decoded_token.get("name", email) if decoded_token else email)
        
        user_doc_ref = db.collection('users').document(user_id)
        user_doc = user_doc_ref.get()
        now_utc = datetime.now(timezone.utc)

        if not user_doc.exists:
            subscription_payload = subscription_defaults(
                tier=DEFAULT_SUBSCRIPTION_TIER,
                now=now_utc,
            )
            subscription_payload["last_updated"] = firestore.SERVER_TIMESTAMP

            user_doc_data = {
                'email': email,
                'name': name,
                'created_at': now_utc,
                'updated_at': now_utc,
                'firebase_uid': user_id,
                'subscription': subscription_payload,
            }
            user_doc_ref.set(user_doc_data)
        else:
            user_data = user_doc.to_dict() or {}
            subscription = user_data.get('subscription') or {}
            subscription_updates = {}

            if not subscription.get('tier'):
                subscription_updates['subscription.tier'] = DEFAULT_SUBSCRIPTION_TIER
            if 'openai_flatlays_used' not in subscription:
                subscription_updates['subscription.openai_flatlays_used'] = 0
            if 'flatlay_week_start' not in subscription:
                subscription_updates['subscription.flatlay_week_start'] = subscription_defaults(
                    tier=subscription.get('tier') or DEFAULT_SUBSCRIPTION_TIER,
                    now=now_utc,
                )['flatlay_week_start']

            if subscription_updates:
                subscription_updates['subscription.last_updated'] = firestore.SERVER_TIMESTAMP
                user_doc_ref.update(subscription_updates)
        
        return {
            "user_id": user_id,
            "email": email,
            "name": name,
            "verified": True
        }
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/register", status_code=201)
async def register_user(user_data: UserCreate):
    """Register a new user (legacy JWT-based)."""
    try:
        # Check if user already exists
        users_ref = db.collection('users')
        existing_user = users_ref.where('email', '==', user_data.email).limit(1).stream()
        
        if list(existing_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user document
        user_doc = {
            'email': user_data.email,
            'name': user_data.name,
            'password_hash': get_password_hash(user_data.password),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        doc_ref = users_ref.add(user_doc)[1]
        user_id = doc_ref.id
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": user_id})
        
        # Log analytics event
        analytics_event = AnalyticsEvent(
            user_id=user_id,
            event_type="user_registered",
            metadata={
                "email": user_data.email,
                "name": user_data.name,
                "method": "email"
            }
        )
        log_analytics_event(analytics_event)
        
        logger.info(f"User registered successfully: {user_data.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": user_data.email,
            "name": user_data.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login")
async def login_user(user_data: UserLogin):
    """Login user and return JWT token (legacy)."""
    try:
        # Find user by email
        users_ref = db.collection('users')
        user_query = users_ref.where('email', '==', user_data.email).limit(1).stream()
        user_docs = list(user_query)
        
        if not user_docs:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_doc = user_docs[0]
        user_data_firestore = user_doc.to_dict()
        
        # Verify password
        if not verify_password(user_data.password, user_data_firestore['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_id = user_doc.id
        
        # Generate JWT token
        access_token = create_access_token(data={"sub": user_id})
        
        # Log analytics event
        analytics_event = AnalyticsEvent(
            user_id=user_id,
            event_type="user_login",
            metadata={
                "email": user_data.email,
                "method": "email"
            }
        )
        log_analytics_event(analytics_event)
        
        logger.info(f"User logged in successfully: {user_data.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": user_data_firestore['email'],
            "name": user_data_firestore['name']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/profile")
async def get_user_profile(current_user_id: str = Depends(get_current_user_id)):
    """Get current user's profile."""
    try:
        user_doc = db.collection('users').document(current_user_id).get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user_data = user_doc.to_dict()
        
        # Return the full user profile data instead of just basic fields
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfile,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update current user's profile."""
    try:
        user_ref = db.collection('users').document(current_user_id)
        
        # Convert Pydantic model to dict and exclude id field
        update_data = profile_data.model_dump(exclude={'id'})
        update_data['updatedAt'] = int(datetime.utcnow().timestamp() * 1000)  # Convert to milliseconds
        
        user_ref.set(update_data, merge=True)  # Use merge=True to preserve existing fields
        
        # Log analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="profile_updated",
            metadata={
                "name": profile_data.name,
                "email": profile_data.email
            }
        )
        log_analytics_event(analytics_event)
        
        logger.info(f"User profile updated successfully: {current_user_id}")
        
        # Return the updated profile data
        return update_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        ) 