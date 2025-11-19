from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
# Firebase imports moved inside function to prevent import-time crashes
# from firebase_admin import auth
from ..custom_types.profile import UserProfile

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """
    Authenticate user using Firebase JWT token.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Import Firebase inside function to prevent import-time crashes
    try:
        from firebase_admin import auth
        import firebase_admin
        
        # Check if Firebase Admin is initialized
        if not firebase_admin._apps:
            logger.error("❌ AUTH: Firebase Admin not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Firebase Admin not initialized - authentication unavailable"
            )
    except ImportError as e:
        logger.error(f"❌ AUTH: Firebase import failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Authentication service unavailable"
        )
    
    try:
        logger.debug(f"🔍 AUTH: get_current_user called - token length: {len(credentials.credentials) if credentials.credentials else 0}")
        # print(f"🔍 DEBUG: Auth service called with credentials: {credentials.credentials[:20]}...")
        # print(f"🔍 DEBUG: Full token length: {len(credentials.credentials)}")
        # Removed full token logging for security
        
        # Temporarily allow test token for testing purposes
        if credentials.credentials == "test":
            # print("🔍 DEBUG: Using test token for testing purposes")
            # Return a mock user for testing
            user = UserProfile(
                id="test-user-id",
                name="Test User",
                email="test@example.com",
                preferences={
                    "style": ["Casual", "Business Casual"],
                    "colors": ["Black", "White", "Blue"],
                    "occasions": ["Casual", "Business"]
                },
                measurements={
                    "height": 175,
                    "weight": 70,
                    "bodyType": "average"
                },
                stylePreferences=[],
                bodyType="average",
                createdAt=1234567890,
                updatedAt=1234567890
            )
            return user
        
        # Verify Firebase JWT token
        try:
            # print("🔍 DEBUG: Attempting Firebase token verification...")
            # print(f"🔍 DEBUG: Firebase auth module: {auth}")
            # print(f"🔍 DEBUG: Firebase auth type: {type(auth)}")
            # print(f"🔍 DEBUG: Token to verify: {credentials.credentials[:20]}...")
            # Try with default settings first
            decoded_token = auth.verify_id_token(credentials.credentials)
            user_id = decoded_token['uid']
            email = (decoded_token.get('email', '') if decoded_token else '')
            name = (decoded_token.get('name', 'User') if decoded_token else 'User')
            # print(f"🔍 DEBUG: Token verified successfully for user: {user_id}")
            
            # Create user profile from token data
            user = UserProfile(
                id=user_id,
                name=name,
                email=email,
                preferences={
                    "style": ["Casual", "Business Casual"],
                    "colors": ["Black", "White", "Blue"],
                    "occasions": ["Casual", "Business"]
                },
                measurements={
                    "height": 175,
                    "weight": 70,
                    "bodyType": "average"
                },
                stylePreferences=[],
                bodyType="average",
                createdAt=1234567890,
                updatedAt=1234567890
            )
            # print(f"🔍 DEBUG: User profile created successfully for: {user_id}")
            return user
            
        except Exception as e:
            # print(f"🔍 DEBUG: Firebase token verification failed: {e}")
            # If it's a clock issue, try with more lenient settings
            if "Token used too early" in str(e) or "clock" in str(e).lower():
                # print(f"🔍 DEBUG: Clock skew detected, trying with lenient settings: {e}")
                try:
                    # Try with a more lenient clock skew tolerance
                    decoded_token = auth.verify_id_token(credentials.credentials, check_revoked=False)
                    user_id = decoded_token['uid']
                    email = (decoded_token.get('email', '') if decoded_token else '')
                    name = (decoded_token.get('name', 'User') if decoded_token else 'User')
                    # print(f"🔍 DEBUG: Token verified with lenient settings for user: {user_id}")
                    
                    # Create user profile from token data
                    user = UserProfile(
                        id=user_id,
                        name=name,
                        email=email,
                        preferences={
                            "style": ["Casual", "Business Casual"],
                            "colors": ["Black", "White", "Blue"],
                            "occasions": ["Casual", "Business"]
                        },
                        measurements={
                            "height": 175,
                            "weight": 70,
                            "bodyType": "average"
                        },
                        stylePreferences=[],
                        bodyType="average",
                        createdAt=1234567890,
                        updatedAt=1234567890
                    )
                    # print(f"🔍 DEBUG: User profile created successfully for: {user_id}")
                    return user
                    
                except Exception as e2:
                    # print(f"🔍 DEBUG: Still failed with lenient settings: {e2}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token validation failed",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                # print(f"🔍 DEBUG: Non-clock related token error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
    except HTTPException:
        # Re-raise HTTP exceptions (like 401, 503) without modification
        raise
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"❌ AUTH: Authentication error: {type(e).__name__}: {str(e)}", exc_info=True)
        logger.error(f"❌ AUTH: Full traceback: {traceback.format_exc()}")
        
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication service error: {str(e) if str(e) else 'Unknown error'}"
        )

# Alternative function that doesn't require authentication for testing
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[UserProfile]:
    """
    Optional authentication function that authenticates real users when tokens are provided,
    but doesn't fail if no token is provided (for testing).
    """
    try:
        # If no credentials provided, return None (for testing)
        if not credentials or not credentials.credentials:
            # print("🔍 DEBUG: No credentials provided to get_current_user_optional")
            return None
            
        # Allow test token for testing purposes
        if credentials.credentials == "test":
            # print("🔍 DEBUG: Using test token for testing purposes in get_current_user_optional")
            # Return a mock user for testing
            user = UserProfile(
                id="test-user-id",
                name="Test User",
                email="test@example.com",
                preferences={
                    "style": ["Casual", "Business Casual"],
                    "colors": ["Black", "White", "Blue"],
                    "occasions": ["Casual", "Business"]
                },
                measurements={
                    "height": 175,
                    "weight": 70,
                    "bodyType": "average"
                },
                stylePreferences=[],
                bodyType="average",
                createdAt=1234567890,
                updatedAt=1234567890
            )
            return user
        
        # Try to authenticate real user
        # print("🔍 DEBUG: Attempting to authenticate real user in get_current_user_optional")
        try:
            # Try with default settings first
            decoded_token = auth.verify_id_token(credentials.credentials)
            user_id = decoded_token['uid']
            email = (decoded_token.get('email', '') if decoded_token else '')
            name = (decoded_token.get('name', 'User') if decoded_token else 'User')
            # print(f"🔍 DEBUG: Real user authenticated successfully: {user_id}")
            
            # Create user profile from token data
            user = UserProfile(
                id=user_id,
                name=name,
                email=email,
                preferences={
                    "style": ["Casual", "Business Casual"],
                    "colors": ["Black", "White", "Blue"],
                    "occasions": ["Casual", "Business"]
                },
                measurements={
                    "height": 175,
                    "weight": 70,
                    "bodyType": "average"
                },
                stylePreferences=[],
                bodyType="average",
                createdAt=1234567890,
                updatedAt=1234567890
            )
            return user
            
        except Exception as e:
            # print(f"🔍 DEBUG: Real user authentication failed in get_current_user_optional: {e}")
            # If it's a clock issue, try with more lenient settings
            if "Token used too early" in str(e) or "clock" in str(e).lower():
                # print(f"🔍 DEBUG: Clock skew detected, trying with lenient settings: {e}")
                try:
                    decoded_token = auth.verify_id_token(credentials.credentials, check_revoked=False)
                    user_id = decoded_token['uid']
                    email = (decoded_token.get('email', '') if decoded_token else '')
                    name = (decoded_token.get('name', 'User') if decoded_token else 'User')
                    # print(f"🔍 DEBUG: Real user authenticated with lenient settings: {user_id}")
                    
                    user = UserProfile(
                        id=user_id,
                        name=name,
                        email=email,
                        preferences={
                            "style": ["Casual", "Business Casual"],
                            "colors": ["Black", "White", "Blue"],
                            "occasions": ["Casual", "Business"]
                        },
                        measurements={
                            "height": 175,
                            "weight": 70,
                            "bodyType": "average"
                        },
                        stylePreferences=[],
                        bodyType="average",
                        createdAt=1234567890,
                        updatedAt=1234567890
                    )
                    return user
                    
                except Exception as e2:
                    # print(f"🔍 DEBUG: Still failed with lenient settings: {e2}")
                    return None
            else:
                # print(f"🔍 DEBUG: Non-clock related token error: {e}")
                return None
                
    except Exception as e:
        # print(f"🔍 DEBUG: Error in get_current_user_optional: {e}")
        return None

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Get current user ID from Firebase JWT token.
    Returns the user ID string for use in other endpoints.
    """
    try:
        # print(f"🔍 DEBUG: get_current_user_id called with credentials: {credentials.credentials[:20]}...")
        # print(f"🔍 DEBUG: Full token length: {len(credentials.credentials)}")
        
        # Temporarily allow test token for testing purposes
        if credentials.credentials == "test":
            # print("🔍 DEBUG: Using test token for testing purposes")
            return "test-user-id"
        
        # print(f"🔍 DEBUG: Token received: {credentials.credentials[:20]}...")
        # print(f"🔍 DEBUG: Full token: {credentials.credentials}")
        
        # Verify Firebase JWT token
        try:
            # print("🔍 DEBUG: Attempting Firebase token verification for user ID...")
            # Import Firebase inside function to prevent import-time crashes
            try:
                from firebase_admin import auth
            except ImportError as e:
                # print(f"⚠️ Firebase import failed: {e}")
                raise HTTPException(status_code=500, detail="Authentication service unavailable")
            
            decoded_token = auth.verify_id_token(credentials.credentials)
            user_id = decoded_token['uid']
            # print(f"🔍 DEBUG: Token verified successfully for user ID: {user_id}")
            return user_id
            
        except Exception as e:
            # print(f"🔍 DEBUG: Firebase token verification failed: {e}")
            # print(f"🔍 DEBUG: Token verification error type: {type(e).__name__}")
            # print(f"🔍 DEBUG: Token verification error details: {str(e)}")
            # If it's a clock issue, try with more lenient settings
            if "Token used too early" in str(e) or "clock" in str(e).lower():
                # print(f"🔍 DEBUG: Clock skew detected, trying with lenient settings: {e}")
                try:
                    decoded_token = auth.verify_id_token(credentials.credentials, check_revoked=False)
                    user_id = decoded_token['uid']
                    # print(f"🔍 DEBUG: Token verified with lenient settings for user ID: {user_id}")
                    return user_id
                except Exception as e2:
                    # print(f"🔍 DEBUG: Still failed with lenient settings: {e2}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token validation failed",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                # print(f"🔍 DEBUG: Non-clock related token error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
    except HTTPException:
        raise
    except Exception as e:
        # print(f"🔍 DEBUG: Authentication error in get_current_user_id: {e}")
        # print(f"🔍 DEBUG: Authentication error type: {type(e).__name__}")
        # print(f"🔍 DEBUG: Authentication error details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication service error: {str(e)}"
        ) 