"""Verified routes for durable, private onboarding progress."""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from ..auth.verified_identity import verified_identity, reject_identity_overrides
from ..services.onboarding_state import (DraftRevisionConflict, js_length, parse_draft,
    read_onboarding_state, reconcile_onboarding_state, save_onboarding_draft)

router = APIRouter(tags=['onboarding'])
logger = logging.getLogger(__name__)

def response(body, status=200):
    return JSONResponse(body, status_code=status, headers={'Cache-Control': 'private, no-store'})

def database():
    from ..config.firebase import db
    if db is None:
        raise HTTPException(status_code=503, detail='Your progress is temporarily unavailable. Please retry.')
    return db

async def body_or_error(request, *, optional=False):
    raw = await request.body()
    if optional and not raw:
        return {}
    try:
        if len(raw) > 512_000:
            raise ValueError()
        data = json.loads(raw)
        if not isinstance(data, dict) or js_length(json.dumps(data, ensure_ascii=False, separators=(',', ':'))) > 128_000:
            raise ValueError()
        return data
    except (ValueError, UnicodeError):
        raise HTTPException(status_code=422, detail='Invalid questionnaire draft.') from None

@router.get('')
def get_onboarding(identity=Depends(verified_identity)):
    try:
        return response({'success': True, 'state': read_onboarding_state(database(), identity['uid'])})
    except HTTPException:
        raise
    except Exception:
        logger.warning('Onboarding progress could not be read')
        return response({'success': False, 'error': 'Your progress could not be loaded. Please retry.'}, 503)

@router.post('')
async def reconcile_onboarding(request: Request, identity=Depends(verified_identity)):
    body = await body_or_error(request, optional=True)
    reject_identity_overrides(identity, body)
    try:
        state = await run_in_threadpool(lambda: reconcile_onboarding_state(database(), identity['uid']))
        return response({'success': True, 'state': state})
    except HTTPException:
        raise
    except Exception:
        logger.warning('Onboarding progress could not be reconciled')
        return response({'success': False, 'error': 'Your progress could not be confirmed. Please retry.'}, 503)

@router.patch('')
async def patch_onboarding(request: Request, identity=Depends(verified_identity)):
    body = await body_or_error(request)
    reject_identity_overrides(identity, body)
    draft, revision = parse_draft(body.get('draft')), body.get('expectedRevision')
    safe_revision = type(revision) in (int, float) and 0 <= revision <= 2**53 - 1 and (type(revision) is int or revision.is_integer())
    if draft is None or not safe_revision:
        return response({'success': False, 'error': 'Invalid questionnaire draft.'}, 422)
    try:
        state = await run_in_threadpool(lambda: save_onboarding_draft(database(), identity['uid'], int(revision), draft))
        return response({'success': True, 'state': state})
    except DraftRevisionConflict as error:
        return response({'success': False, 'code': 'revision_conflict', 'error': str(error), 'state': error.state}, 409)
    except HTTPException:
        raise
    except Exception:
        logger.warning('Onboarding draft could not be persisted')
        return response({'success': False, 'error': 'Your answers were not saved. Please retry.'}, 503)
