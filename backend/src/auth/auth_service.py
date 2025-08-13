from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from firebase_admin import auth
from ..custom_types.profile import UserProfile

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """
    Authenticate user using Firebase JWT token.
    """
    try:
        print(f"🔍 DEBUG: Auth service called with credentials: {credentials.credentials[:20]}...")
        
        # Accept test token for development
        if credentials.credentials == "test":
            print("🔍 DEBUG: Using test token")
            mock_user = UserProfile(
                id="dANqjiI0CKgaitxzYtw1bhtvQrG3",  # Original default user ID
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
            return mock_user
        
        # Verify Firebase JWT token
        try:
            print("🔍 DEBUG: Attempting Firebase token verification...")
            # Try with default settings first
            decoded_token = auth.verify_id_token(credentials.credentials)
            user_id = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', 'User')
            print(f"🔍 DEBUG: Token verified successfully for user: {user_id}")
        except Exception as e:
            print(f"🔍 DEBUG: Firebase token verification failed: {e}")
            # If it's a clock issue, try with more lenient settings
            if "Token used too early" in str(e) or "clock" in str(e).lower():
                print(f"🔍 DEBUG: Clock skew detected, trying with lenient settings: {e}")
                try:
                    # Try with a more lenient clock skew tolerance
                    decoded_token = auth.verify_id_token(credentials.credentials, check_revoked=False)
                    user_id = decoded_token['uid']
                    email = decoded_token.get('email', '')
                    name = decoded_token.get('name', 'User')
                    print(f"🔍 DEBUG: Token verified with lenient settings for user: {user_id}")
                except Exception as e2:
                    print(f"🔍 DEBUG: Still failed with lenient settings: {e2}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token validation failed",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                print(f"🔍 DEBUG: Non-clock related token error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
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
            print(f"🔍 DEBUG: User profile created successfully for: {user_id}")
            return user
            
        except Exception as firebase_error:
            print(f"🔍 DEBUG: Firebase token verification failed: {firebase_error}")
            # Don't fallback to mock user for invalid tokens
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except Exception as e:
        print(f"🔍 DEBUG: Authentication error: {e}")
        print(f"🔍 DEBUG: Error type: {type(e)}")
        import traceback
        print(f"🔍 DEBUG: Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication service error: {str(e)}"
        )

# Alternative function that doesn't require authentication for testing
async def get_current_user_optional() -> Optional[UserProfile]:
    """
    Optional authentication function for testing endpoints without auth.
    """
    try:
        mock_user = UserProfile(
            id="dANqjiI0CKgaitxzYtw1bhtvQrG3",  # Original default user ID
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
        return mock_user
    except Exception as e:
        print(f"Error creating mock user: {e}")
        return None 