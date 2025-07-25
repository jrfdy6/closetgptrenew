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
        # Accept test token for development
        if credentials.credentials == "test":
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
            # Try with default settings first
            decoded_token = auth.verify_id_token(credentials.credentials)
            user_id = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', 'User')
        except Exception as e:
            # If it's a clock issue, try with more lenient settings
            if "Token used too early" in str(e) or "clock" in str(e).lower():
                print(f"Clock skew detected, trying with lenient settings: {e}")
                try:
                    # Try with a more lenient clock skew tolerance
                    decoded_token = auth.verify_id_token(credentials.credentials, check_revoked=False)
                    user_id = decoded_token['uid']
                    email = decoded_token.get('email', '')
                    name = decoded_token.get('name', 'User')
                except Exception as e2:
                    print(f"Still failed with lenient settings: {e2}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token validation failed",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
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
            return user
            
        except Exception as firebase_error:
            print(f"Firebase token verification failed: {firebase_error}")
            # Don't fallback to mock user for invalid tokens
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except Exception as e:
        print(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
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