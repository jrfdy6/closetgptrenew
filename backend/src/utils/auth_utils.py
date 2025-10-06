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
    """
    Verifies the Firebase ID token, returns uid. Raises HTTPException(401) on failure.
    Use this in endpoints that require user identity.
    """
    token = get_bearer_token_from_request(request)
    if not token:
        logger.warning("No Authorization header or malformed header in request")
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    # optional: block the debug/test token explicitly
    if token == "test":
        logger.warning("Test token present - refusing to use test token for real queries")
        raise HTTPException(status_code=401, detail="Test token not allowed for this endpoint")

    try:
        decoded = firebase_auth.verify_id_token(token)
        uid = decoded.get("uid") or decoded.get("user_id") or decoded.get("sub")
        # log only the uid (safe) for debugging
        logger.info("Authenticated request - uid=%s", uid)
        if not uid:
            logger.error("Token verified but uid not found in decoded token: %s", {k: v for k, v in decoded.items() if k == "uid"})
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return uid
    except firebase_auth.InvalidIdTokenError as e:
        logger.warning("Invalid ID token: %s", e)
        raise HTTPException(status_code=401, detail="Invalid ID token")
    except firebase_auth.ExpiredIdTokenError as e:
        logger.warning("Expired ID token: %s", e)
        raise HTTPException(status_code=401, detail="Expired ID token")
    except Exception as e:
        logger.exception("Unexpected error verifying token")
        raise HTTPException(status_code=401, detail="Failed to verify token")
