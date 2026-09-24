"""Verified privacy controls and resumable application-data deletion."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, field_validator
from firebase_admin import firestore

from ..auth.verified_user import verified_user_id
from ..config.firebase import db
from ..services.app_data_privacy import (
    AppDataDeletionError, request_app_data_deletion, read_deletion_status,
)

router = APIRouter(tags=['data-privacy'])


class PrivacySettings(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    share_analytics: bool = False
    share_style_data: bool = False
    allow_data_collection: bool = True
    allow_personalization: bool = True
    data_retention_days: Optional[int] = None

    @field_validator('data_retention_days')
    @classmethod
    def supported_retention(cls, value):
        if value is not None:
            raise ValueError('Automatic retention periods are not supported. Use Clear app data instead.')
        return value


def _settings(user):
    privacy = user.get('privacy') or {}
    return {**{key: privacy.get(key, default) for key, default in {
        'share_analytics': False, 'share_style_data': False,
        'allow_data_collection': True, 'allow_personalization': True}.items()},
        'data_retention_days': None, 'automatic_retention_supported': False,
        'last_updated': privacy.get('last_updated')}


@router.get('/privacy-settings')
async def get_privacy_settings(user_id: str = Depends(verified_user_id)):
    user = db.collection('users').document(user_id).get()
    if not user.exists:
        raise HTTPException(404, 'Account not found')
    return _settings(user.to_dict() or {})


@router.post('/privacy-settings')
async def update_privacy_settings(settings: PrivacySettings, user_id: str = Depends(verified_user_id)):
    ref = db.collection('users').document(user_id)
    values = {**settings.model_dump(), 'last_updated': datetime.now(timezone.utc).isoformat()}
    @firestore.transactional
    def save(txn):
        if not ref.get(transaction=txn).exists:
            raise HTTPException(404, 'Account not found')
        # Privacy choices remain editable during erasure and are preserved at completion.
        txn.update(ref, {'privacy': values})
    save(db.transaction())
    return {'success': True, 'message': 'Privacy settings saved.', 'settings': values}


@router.delete('/privacy-data', status_code=202)
async def delete_user_data(data_type: Optional[str] = Query(None), user_id: str = Depends(verified_user_id)):
    try:
        return request_app_data_deletion(db, user_id, data_type or 'all')
    except AppDataDeletionError as error:
        raise HTTPException(error.status_code, error.detail) from error


@router.get('/privacy-data/status')
async def deletion_status(user_id: str = Depends(verified_user_id)):
    try:
        return read_deletion_status(db, user_id)
    except AppDataDeletionError as error:
        raise HTTPException(error.status_code, error.detail) from error


@router.get('/privacy-summary')
async def get_privacy_summary(user_id: str = Depends(verified_user_id)):
    from google.cloud.firestore_v1.base_query import FieldFilter
    user = db.collection('users').document(user_id).get()
    if not user.exists:
        raise HTTPException(404, 'Account not found')
    summary = {}
    for key, collection, owner in [('outfits', 'outfits', 'user_id'),
                                    ('wardrobe_items', 'wardrobe', 'userId'),
                                    ('analytics_entries', 'analytics_events', 'user_id')]:
        summary[key] = sum(1 for _ in db.collection(collection).where(filter=FieldFilter(owner, '==', user_id)).stream())
    settings = _settings(user.to_dict() or {})
    return {'data_summary': {**summary, 'total': sum(summary.values())}, 'privacy_settings': settings,
            'data_retention': None, 'automatic_retention_supported': False,
            'last_updated': settings['last_updated'], 'deletion': read_deletion_status(db, user_id)}
