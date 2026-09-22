"""Full style quiz writes belong to the verified Railway identity only."""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from ..auth.verified_identity import reject_identity_overrides, verified_identity
from ..services.quiz_profile import QuizSubmissionError, save_quiz_profile, validate_submission

logger = logging.getLogger(__name__)
router = APIRouter(tags=["style-quiz"])


def _response(body, status=200):
    return JSONResponse(body, status_code=status, headers={"Cache-Control": "private, no-store"})


@router.post("/submit")
async def submit_style_quiz(request: Request, identity: dict = Depends(verified_identity)):
    try:
        # JSON.parse in the accepted Next route interpreted every number as
        # binary64. Preserve that representation for cross-version receipts.
        def invalid_constant(_):
            raise ValueError("Invalid JSON number")
        submission = json.loads(await request.body(), parse_int=float, parse_float=float, parse_constant=invalid_constant)
    except (ValueError, UnicodeError):
        return _response({"success": False, "error": "Invalid quiz submission."}, 422)
    try:
        validate_submission(submission, identity)
        reject_identity_overrides(identity, submission)
        from ..config.firebase import db
        if db is None:
            raise RuntimeError("Profile persistence unavailable")
        return _response(await run_in_threadpool(save_quiz_profile, db, identity, submission))
    except QuizSubmissionError as error:
        return _response({"success": False, "code": error.code, "error": error.message}, error.status_code)
    except HTTPException:
        raise
    except Exception:
        logger.warning("Style profile could not be persisted")
        return _response({"success": False, "error": "Your style profile could not be saved. Your answers are still available to retry."}, 503)
