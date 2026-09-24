"""Shared server-side admission for every path that creates a saved outfit."""
from datetime import datetime, timezone
import os
from fastapi import HTTPException
from firebase_admin import firestore
from .onboarding_state import sources, record, has_style_profile, evaluate_capsule, has_complete_combination, owned_by
from .flatlay_lifecycle import _available_garment, _projection

DEFAULT_GRANDFATHER_CUTOFF = '2026-09-23T00:00:00Z'


def _epoch(value):
    try:
        if isinstance(value, datetime):
            return (value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value).timestamp()
        if type(value) in (int, float):
            return value / 1000 if value > 1e12 else value
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return (parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed).timestamp()
        if isinstance(value, dict) and type(value.get('seconds')) in (int, float):
            return value['seconds']
    except (ValueError, TypeError, OverflowError, OSError):
        pass
    return None


def _item_id(item):
    value = (item.get('id') or item.get('itemId') or item.get('item_id')) if isinstance(item, dict) else item
    return value if isinstance(value, str) and value and '/' not in value and len(value) <= 250 else None


def is_deleted(data):
    return any(data.get(key) for key in ('deleted', 'isDeleted', 'deletedAt', 'deleted_at'))


def _historical_completion(db, data, uid, transaction=None):
    cutoff = _epoch(os.environ.get('EASYOUTFIT_ONBOARDING_GRANDFATHER_CUTOFF', DEFAULT_GRANDFATHER_CUTOFF))
    if cutoff is None:
        return False  # Invalid rollout configuration must not broaden admission.
    garments = {item['id']: item for item in data['wardrobe']}
    for outfit in data['outfits']:
        # Firestore's immutable creation metadata, never the editable createdAt
        # payload, proves this saved document existed before rollout.
        snapshot = db.collection('outfits').document(outfit['id']).get(transaction=transaction)
        created = _epoch(getattr(snapshot, 'create_time', None))
        raw_items = outfit.get('items')
        if created is None or not 0 < created < cutoff or not owned_by(outfit, uid) or not isinstance(raw_items, list):
            continue
        ids = [_item_id(item) for item in raw_items]
        if not ids or None in ids or len(set(ids)) != len(ids):
            continue
        items = [garments.get(key, {}) for key in ids]
        if all(_available_garment(item, uid) for item in items) and has_complete_combination(items):
            return True
    return False


def require_outfit_creation_ready(db, user_id, *, transaction=None):
    """Use persisted protected completion, never flags in a creation request."""
    from .app_data_privacy import require_app_data_writable, AppDataDeletionError
    try:
        epoch = require_app_data_writable(db, user_id, transaction=transaction)
    except AppDataDeletionError as error:
        raise HTTPException(error.status_code, error.detail) from None
    data = sources(db, user_id, transaction)
    milestones = record(record(data['stored']).get('milestones'))
    profile_complete = has_style_profile(data['profile']) or bool(milestones.get('styleCompletedAt'))
    capsule = evaluate_capsule([item for item in data['wardrobe'] if _available_garment(item, user_id)])
    grandfathered = bool(milestones.get('capsuleCompletedAt') or milestones.get('firstOutfitId')) or _historical_completion(db, data, user_id, transaction)
    stage = 'first-look' if grandfathered or profile_complete and capsule['ready'] else 'style' if not profile_complete else 'capsule'
    admission = {'stage': stage, 'profile_complete': profile_complete, 'capsule': capsule,
                 'grandfathered': grandfathered, 'app_data_epoch': epoch}
    if not grandfathered and not (profile_complete and capsule['ready']):
        raise HTTPException(409, {'code': 'onboarding_required', 'resume': '/onboarding',
                                 'stage': stage, 'profile_complete': profile_complete, 'capsule': capsule})
    return admission


def resolve_owned_items(db, transaction, user_id, items):
    if not isinstance(items, list) or not 1 <= len(items) <= 10:
        raise HTTPException(422, 'Select between one and ten wardrobe items.')
    ids = [_item_id(item) for item in items]
    if None in ids or len(set(ids)) != len(ids):
        raise HTTPException(422, 'Select each saved wardrobe item only once.')
    result = []
    for identifier in ids:
        snapshot = db.collection('wardrobe').document(identifier).get(transaction=transaction)
        garment = snapshot.to_dict() if snapshot.exists else {}
        if not _available_garment(garment, user_id) or not any(
                isinstance(garment.get(field), str) and garment[field].strip()
                for field in ('imageUrl', 'image_url', 'originalImageUrl')):
            raise HTTPException(422, 'One or more pieces or their original photos are unavailable. Refresh your wardrobe.')
        result.append({**garment, 'id': identifier})
    return result


def persist_created_outfit(db, user_id, outfit_id, outfit, admission, *, require_complete=True):
    """Commit only if onboarding and deletion epoch still permit creation."""
    from .app_data_privacy import require_app_data_writable, AppDataDeletionError
    if not _item_id(outfit_id):
        raise HTTPException(422, 'Invalid outfit ID.')
    ref = db.collection('outfits').document(outfit_id)
    now = datetime.now(timezone.utc)

    @firestore.transactional
    def save(txn):
        try:
            require_app_data_writable(db, user_id, expected_epoch=admission['app_data_epoch'], transaction=txn)
        except AppDataDeletionError as error:
            raise HTTPException(error.status_code, error.detail) from None
        require_outfit_creation_ready(db, user_id, transaction=txn)
        existing = ref.get(transaction=txn)
        if existing.exists:
            data = existing.to_dict() or {}
            if not owned_by(data, user_id) or is_deleted(data):
                raise HTTPException(409, 'This outfit cannot be replaced. Refresh and retry.')
            return {**data, 'id': outfit_id}
        items = resolve_owned_items(db, txn, user_id, outfit.get('items'))
        if require_complete and not has_complete_combination(items):
            raise HTTPException(422, 'The outfit is no longer a complete combination. Please retry.')
        if outfit.get('baseItemId') and outfit['baseItemId'] not in {item['id'] for item in items}:
            raise HTTPException(422, 'The outfit is missing your required piece. Please retry.')
        result = {**outfit, 'id': outfit_id, 'user_id': user_id, 'userId': user_id,
                  'items': items, 'createdAt': now.isoformat(), 'updatedAt': now.isoformat(),
                  'wearCount': 0, 'isFavorite': False, 'app_data_epoch': admission['app_data_epoch']}
        result['metadata'] = {**record(result.get('metadata')), 'item_count': len(items)}
        for path, value in _projection('awaiting_consent', None, int(now.timestamp()), retryable=True).items():
            if path.startswith('metadata.'):
                result['metadata'][path.split('.', 1)[1]] = value
            else:
                result[path] = value
        txn.set(ref, result)
        return result

    return save(db.transaction())
