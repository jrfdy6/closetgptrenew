"""Explicit, default-deny access to internal operator endpoints."""
import os

from fastapi import HTTPException, Request, Response

from .verified_identity import IDENTITY_HEADERS, IDENTITY_KEYS
from .verified_user import verify_bearer_claims


def require_operator(request: Request, response: Response) -> dict:
    """Only verified UIDs explicitly configured by the operator may enter."""
    claims = verify_bearer_claims(request.headers.get("authorization"))
    allowed = {value.strip() for value in os.getenv("EASYOUTFIT_OPERATOR_USER_IDS", "").split(",") if value.strip()}
    if claims["uid"] not in allowed:
        raise HTTPException(status_code=403, detail="Operator access is required")
    # Legacy identity hints are never authority, even for allowlisted operators.
    if any(value != claims["uid"] for key in IDENTITY_HEADERS for value in request.headers.getlist(key)):
        raise HTTPException(status_code=403, detail="Conflicting account identity")
    if any(value != claims["uid"] for key in IDENTITY_KEYS for value in request.query_params.getlist(key)):
        raise HTTPException(status_code=403, detail="Conflicting account identity")
    response.headers["Cache-Control"] = "private, no-store"
    return claims


def require_internal_operator(request: Request, response: Response) -> dict:
    """Debug utilities remain hidden unless both gates are satisfied."""
    if os.getenv("ENABLE_INTERNAL_DEBUG_ROUTES", "").strip().lower() != "true":
        raise HTTPException(status_code=404, detail="Not found")
    try:
        return require_operator(request, response)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Not found") from None
