"""Verified profile endpoint for the same-origin frontend proxy."""
import json
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from src.auth.verified_identity import verified_identity, reject_identity_overrides
from src.services.user_profile import InvalidProfile, persist_profile

router = APIRouter()


def profile_database():
    from src.config.firebase import db
    if db is None:
        raise HTTPException(status_code=503, detail="Profile access is temporarily unavailable. Please retry.")
    return db


def _response(profile, start):
    return JSONResponse(jsonable_encoder({**profile, "_source": "firestore",
                                         "_duration": f"{round((time.monotonic() - start) * 1000)}ms"}),
                        headers={"Cache-Control": "private, no-store"})


@router.get("/profile")
def get_profile(request: Request, claims: dict = Depends(verified_identity)):
    start = time.monotonic()
    reject_identity_overrides(claims, dict(request.query_params))
    try:
        return _response(persist_profile(profile_database(), claims), start)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Profile access is temporarily unavailable. Please retry.") from None


async def save_profile_response(request: Request, claims: dict, *, wardrobe_aliases=False):
    """Shared POST/legacy PUT boundary; parsing failures cannot mask DB outages."""
    start = time.monotonic()
    reject_identity_overrides(claims, dict(request.query_params))
    try:
        raw = await request.body()
        if len(raw) > 256_000:
            raise InvalidProfile("Profile update is too large")
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise InvalidProfile("Invalid profile update")
    except (InvalidProfile, json.JSONDecodeError, UnicodeError):
        raise HTTPException(status_code=422, detail="Invalid profile update") from None
    reject_identity_overrides(claims, body)
    try:
        profile = await run_in_threadpool(lambda: persist_profile(profile_database(), claims, body))
        if wardrobe_aliases:
            count = profile.get("wardrobeItemCount", 0)
            profile = {**profile, "wardrobeCount": count, "wardrobe_count": count}
        return _response(profile, start)
    except HTTPException:
        raise
    except InvalidProfile:
        raise HTTPException(status_code=422, detail="Invalid profile update") from None
    except Exception:
        raise HTTPException(status_code=503, detail="Your profile was not confirmed saved. Please retry.") from None


@router.post("/profile")
async def save_profile(request: Request, claims: dict = Depends(verified_identity)):
    return await save_profile_response(request, claims)
