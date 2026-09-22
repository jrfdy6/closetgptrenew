"""Read-only, owned saved-result projection. A read never creates paid work."""
from copy import deepcopy
from firebase_admin import firestore
from .flatlay_lifecycle import _owner_matches, _same_item_set, _available_garment, _source_fingerprint, _has_source_identity


class SavedOutfitNotFound(Exception):
    pass


OUTFIT_FIELDS = (
    'name', 'style', 'occasion', 'mood', 'reasoning', 'description', 'notes',
    'weather', 'outfitAnalysis', 'createdAt', 'updatedAt', 'wearCount', 'lastWorn',
    'lastWearDate', 'lastWearTimezone', 'rating', 'isLiked', 'isDisliked', 'feedback',
    'baseItemId',
)
ITEM_FIELDS = ('name', 'type', 'category', 'color', 'imageUrl', 'image_url',
               'originalImageUrl', 'thumbnailUrl', 'backgroundRemovedUrl', 'reason')


def item_id(item):
    value = (item.get('id') or item.get('itemId') or item.get('item_id')) if isinstance(item, dict) else item
    return value if isinstance(value, str) and value and '/' not in value else None


def public_preview(outfit, ledger, garments, user_id, outfit_id):
    status, url, error, code, request_id, credit = 'awaiting_consent', None, None, None, None, None
    allowed = True
    metadata = outfit.get('metadata') if isinstance(outfit.get('metadata'), dict) else {}
    if ledger:
        allowed = False
        if ledger.get('user_id') != user_id or ledger.get('outfit_id') != outfit_id:
            status, error, code = 'failed', 'This preview needs review before another request.', 'preview_identity_unavailable'
        else:
            status = ledger.get('status') or 'failed'
            request_id, credit = ledger.get('request_id'), ledger.get('credit_status')
            error, code = ledger.get('error'), ledger.get('error_code')
            allowed = status == 'failed' and ledger.get('retryable') is True and credit == 'refunded'
            sources_known = _has_source_identity(ledger)
            same = _same_item_set(ledger, outfit) and sources_known and all(
                _available_garment(garments.get(item_id(item)), user_id)
                and item['referenceSourceFingerprint'] == _source_fingerprint(garments[item_id(item)])
                for item in ledger.get('items', []))
            if same:
                url = ledger.get('url') if status == 'done' else None
            elif status in ('pending', 'processing'):
                error = 'This outfit changed. Its earlier preview request is still being resolved.'
                code, allowed = 'outfit_changed', False
            elif status == 'done' and sources_known:
                status, allowed, code = 'awaiting_consent', True, 'outfit_changed'
                error = 'The pieces or their photos changed. Create a new flatlay for this version.'
            elif status == 'done':
                status, allowed, code = 'failed', False, 'preview_identity_unavailable'
                error = 'This earlier preview cannot be verified against the current photos. Your original pieces are still available.'
            if code in ('provider_outcome_unknown', 'worker_outcome_unknown'):
                allowed = False
    elif any(outfit.get(key) or metadata.get(key) for key in ('flat_lay_url', 'flatLayUrl')) or any(
        (outfit.get(key) or metadata.get(key)) in ('pending', 'processing', 'queued', 'failed', 'done')
        for key in ('flat_lay_status', 'flatLayStatus')):
        status, allowed, code = 'failed', False, 'legacy_request_needs_review'
        error = 'This earlier preview needs review before another request. Your original pieces are still available.'
    return {
        'flat_lay_status': status, 'flatLayStatus': status,
        'flat_lay_url': url, 'flatLayUrl': url,
        'flat_lay_error': error, 'flatLayError': error,
        'flat_lay_request_id': request_id,
        'flat_lay_request_allowed': allowed, 'flat_lay_retryable': allowed and status == 'failed',
        'flat_lay_error_code': code, 'flat_lay_credit_status': credit,
    }


def read_saved_outfit(db, outfit_id, user_id):
    if not outfit_id or '/' in outfit_id:
        raise SavedOutfitNotFound()

    @firestore.transactional
    def read(txn):
        snapshot = db.collection('outfits').document(outfit_id).get(transaction=txn)
        outfit = snapshot.to_dict() if snapshot.exists else None
        if not outfit or not _owner_matches(outfit, user_id) or any(
                outfit.get(field) for field in ('deleted', 'isDeleted', 'deletedAt', 'deleted_at')):
            raise SavedOutfitNotFound()
        ledger_doc = db.collection('flat_lay_requests').document(outfit_id).get(transaction=txn)
        ledger = ledger_doc.to_dict() if ledger_doc.exists else None
        garment_ids = {item_id(item) for item in outfit.get('items', [])}
        if ledger and ledger.get('user_id') == user_id:
            garment_ids.update(item_id(item) for item in ledger.get('items', []))
        garments = {}
        for garment_id in sorted(value for value in garment_ids if value):
            doc = db.collection('wardrobe').document(garment_id).get(transaction=txn)
            garments[garment_id] = doc.to_dict() if doc.exists else {}
        items = []
        for item in outfit.get('items', []):
            garment_id = item_id(item)
            if not garment_id:
                continue
            current = garments.get(garment_id, {})
            if _available_garment(current, user_id):
                # Original photo authority belongs to the current garment. Never
                # resurrect an obsolete snapshot URL after a photo was cleared.
                fallback = {key: value for key, value in item.items()
                            if key in ('name', 'type', 'category', 'color', 'reason')} if isinstance(item, dict) else {}
                source = {**fallback, **current}
                items.append({'id': garment_id, **{key: deepcopy(source[key]) for key in ITEM_FIELDS if key in source}})
            else:
                items.append({'id': garment_id, 'name': 'Unavailable piece', 'type': '', 'color': '', 'unavailable': True})
        preview = public_preview(outfit, ledger, garments, user_id, outfit_id)
        return {'id': outfit_id, 'user_id': user_id,
                **{key: deepcopy(outfit[key]) for key in OUTFIT_FIELDS if key in outfit},
                'isFavorite': bool(outfit.get('favorite', False)) if outfit.get('isFavorite') is None else outfit.get('isFavorite') is True,
                'feedback': outfit.get('userFeedback', outfit.get('feedback', '')),
                'items': items, 'items_available': bool(items) and len(items) == len(outfit.get('items', [])) and all(not item.get('unavailable') for item in items),
                **preview, 'metadata': dict(preview)}

    return read(db.transaction())
