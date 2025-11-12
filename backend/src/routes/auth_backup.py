"""
Authentication routes for Easy Outfit App.
Handles user registration, login, and profile management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
import logging

from ..core.security import verify_password, get_password_hash
from ..core.logging import get_logger
from ..data.database import get_firestore_client
from ..models.analytics_event import AnalyticsEvent
from ..services.analytics_service import log_analytics_event

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logger = get_logger("auth")
db = get_firestore_client()

router = APIRouter(prefix="/auth", tags=["authentication"])

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """Get current user ID from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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

@router.post("/register", status_code=201)
async def register_user(user_data: UserCreate):
    """Register a new user."""
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
    """Login user and return JWT token."""
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
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        
        return UserProfile(
            name=user_data['name'],
            email=user_data['email'],
            avatar_url=(user_data.get('avatar_url') if user_data else None)
        )
        
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
        
        update_data = {
            'name': profile_data.name,
            'avatar_url': profile_data.avatar_url,
            'updated_at': datetime.utcnow()
        }
        
        user_ref.update(update_data)
        
        # Log analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user_id,
            event_type="profile_updated",
            metadata={
                "updated_fields": list(update_data.keys())
            }
        )
        log_analytics_event(analytics_event)
        
        logger.info(f"User profile updated: {current_user_id}")
        
        return {"message": "Profile updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

def create_access_token(data: dict):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt 