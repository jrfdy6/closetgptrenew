"""Strict identity dependency for owned saved-result operations."""
import logging

from fastapi import Header, HTTPException
from firebase_admin import auth

logger = logging.getLogger(__name__)


def verified_user_id(authorization: str | None = Header(default=None)) -> str:
    parts = (authorization or "").split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or parts[1].lower() == "test":
        raise HTTPException(status_code=401, detail="A valid sign-in is required")
    try:
        claims = auth.verify_id_token(parts[1], check_revoked=True)
    except (auth.InvalidIdTokenError, auth.RevokedIdTokenError, auth.UserDisabledError, ValueError):
        raise HTTPException(status_code=401, detail="A valid sign-in is required") from None
    except Exception:
        logger.warning("Saved outfit sign-in verification is unavailable")
        raise HTTPException(status_code=503, detail="Sign-in verification is temporarily unavailable") from None
    user_id = claims.get("uid") if isinstance(claims, dict) else None
    if not isinstance(user_id, str) or not user_id.strip():
        raise HTTPException(status_code=401, detail="A valid sign-in is required")
    return user_id
