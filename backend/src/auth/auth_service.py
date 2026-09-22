"""Firebase authentication shared by public API routes.

Test callers override FastAPI dependencies; no literal token bypass exists.
"""
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..custom_types.profile import UserProfile

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def verified_identity(credentials):
    if not credentials or not credentials.credentials:
        raise HTTPException(401, "Authentication required", headers={"WWW-Authenticate": "Bearer"})
    from firebase_admin import auth
    try:
        token = auth.verify_id_token(credentials.credentials, check_revoked=True)
        if not token.get('uid'):
            raise ValueError('Missing identity')
        return token
    except Exception:
        raise HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    token = verified_identity(credentials)
    return UserProfile(id=token['uid'], name=token.get('name') or 'User',
                       email=token.get('email') or '', bodyType='', createdAt=0, updatedAt=0)


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return verified_identity(credentials)['uid']


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)) -> Optional[UserProfile]:
    if not credentials:
        return None
    return await get_current_user(credentials)
