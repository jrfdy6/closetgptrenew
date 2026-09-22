"""Shared verified identity for privileged API operations moved from Vercel."""
from collections.abc import Mapping

from fastapi import HTTPException, Request

from .verified_user import verify_bearer_claims


IDENTITY_KEYS = ("userId", "user_id", "firebase_uid", "uid")
IDENTITY_HEADERS = ("x-user-id", "x-userid", "x-firebase-uid", "user-id", "userid", "user_id", "firebase_uid", "uid")


def reject_identity_overrides(claims: Mapping, value: Mapping | None) -> None:
    if isinstance(value, Mapping) and any(key in value and value[key] != claims["uid"] for key in IDENTITY_KEYS):
        raise HTTPException(status_code=403, detail="The record does not belong to the signed-in account")


def verified_identity(request: Request) -> dict:
    claims = verify_bearer_claims(request.headers.get("authorization"))
    # Matching legacy hints remain non-authoritative. A conflicting hint is an
    # error, never an alternate owner and never an authentication fallback.
    if any(value != claims["uid"] for key in IDENTITY_HEADERS for value in request.headers.getlist(key)):
        raise HTTPException(status_code=403, detail="The record does not belong to the signed-in account")
    if any(value != claims["uid"] for key in IDENTITY_KEYS for value in request.query_params.getlist(key)):
        raise HTTPException(status_code=403, detail="The record does not belong to the signed-in account")
    return claims
