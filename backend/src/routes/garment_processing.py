"""Authenticated, attempt-fenced retries of failed garment image processing.

This route deliberately does not use the legacy auth helper, which accepts a
test token. The verified Firebase UID is the only ownership authority here.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from ..auth.verified_identity import verified_identity


logger = logging.getLogger(__name__)
router = APIRouter(tags=["garment-processing"])


class GarmentRetryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # The exact failed attempt is also the idempotency key. Clients may not
    # reset attempt counts or submit a new processing status themselves.
    expected_attempt_id: str = Field(min_length=1, max_length=256, strict=True)


@router.post("/{item_id}/retry-processing")
def retry_garment_processing(
    item_id: str,
    body: GarmentRetryRequest,
    claims: dict = Depends(verified_identity),
):
    user_id = claims['uid']
    if not item_id.strip() or item_id in {".", ".."} or "/" in item_id:
        raise HTTPException(status_code=422, detail="Invalid garment identifier")
    if not body.expected_attempt_id.strip():
        raise HTTPException(status_code=422, detail="A failed processing attempt is required")

    # Import storage and lifecycle only after real authentication. No image
    # inference modules or provider calls are part of this request.
    from ..config.firebase import db
    from ..services.garment_lifecycle import GarmentRetryError, retry_garment

    if db is None:
        raise HTTPException(status_code=503, detail="Garment processing is temporarily unavailable")
    try:
        return retry_garment(db, item_id, user_id, body.expected_attempt_id)
    except GarmentRetryError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from None
    except Exception:
        logger.warning("Garment retry could not be persisted")
        raise HTTPException(status_code=503, detail="Garment retry could not be saved. Please try again.") from None
