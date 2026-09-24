import logging
from fastapi import Request, HTTPException
import firebase_admin
from firebase_admin import auth as firebase_auth

logger = logging.getLogger(__name__)

def get_bearer_token_from_request(request: Request) -> str | None:
    """Extract bearer token from Authorization header."""
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]

def extract_uid_from_request(request: Request) -> str:
    """Use the same revoked-token and identity policy as every verified route."""
    from ..auth.verified_user import verify_bearer_claims
    return verify_bearer_claims(request.headers.get('authorization'))['uid']
