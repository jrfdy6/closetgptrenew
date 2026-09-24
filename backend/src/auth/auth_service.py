"""Compatibility dependencies backed by the one strict Firebase verifier."""
from typing import Optional
from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .verified_user import verify_bearer_claims
from ..custom_types.profile import UserProfile

security = HTTPBearer(auto_error=False)


def _claims(credentials):
    authorization = f'{credentials.scheme} {credentials.credentials}' if credentials else None
    return verify_bearer_claims(authorization)


def _profile_database():
    from ..config.firebase import db
    if db is None:
        raise HTTPException(503, 'Profile service is unavailable')
    return db


def _profile(claims):
    """Hydrate only the verified account's profile; stored data is never identity."""
    try:
        snapshot = _profile_database().collection('users').document(claims['uid']).get()
        if not snapshot.exists:
            raise HTTPException(404, 'Account not found')
        data = snapshot.to_dict() or {}
        if any(data.get(key) not in (None, claims['uid']) for key in ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId')):
            raise HTTPException(409, 'Account identity needs review')
        payload = {key: value for key, value in data.items() if key in UserProfile.model_fields}
        payload.update(id=claims['uid'], email=claims.get('email') or '',
                       name=data.get('name') or claims.get('name') or 'User',
                       bodyType=data.get('bodyType') or (data.get('measurements') or {}).get('bodyType') or '',
                       createdAt=data.get('createdAt') or data.get('created_at') or 0,
                       updatedAt=data.get('updatedAt') or data.get('updated_at') or 0)
        return UserProfile(**payload)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, 'Profile service is unavailable') from None


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> UserProfile:
    return _profile(_claims(credentials))


async def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    return _claims(credentials)['uid']


async def get_current_user_optional(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[UserProfile]:
    # Optional means absent credentials, never invalid or revoked credentials.
    authorization = request.headers.get('authorization')
    if authorization is None:
        return None
    return _profile(verify_bearer_claims(authorization))
