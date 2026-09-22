"""Owned outfit edits with canonical garments and transactional preview invalidation."""
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from firebase_admin import firestore
from .flatlay_lifecycle import _owner_matches, _projection

EDITABLE = frozenset(('name', 'occasion', 'style', 'mood', 'description', 'notes', 'items', 'isFavorite'))


def _document_id(value):
    if not isinstance(value, str) or not value or '/' in value or len(value) > 250:
        raise HTTPException(422, 'Invalid outfit or garment ID')
    return value


def _garments(db, txn, items, uid):
    if not isinstance(items, list) or not 1 <= len(items) <= 10:
        raise HTTPException(422, 'Select between one and ten wardrobe items')
    result, seen = [], set()
    for item in items:
        key = _document_id((item.get('id') or item.get('itemId')) if isinstance(item, dict) else item)
        if key in seen:
            raise HTTPException(422, 'Select each wardrobe item only once')
        seen.add(key)
        snapshot = db.collection('wardrobe').document(key).get(transaction=txn)
        data = snapshot.to_dict() if snapshot.exists else None
        if not data or not _owner_matches(data, uid):
            raise HTTPException(422, 'One or more items are no longer in your wardrobe')
        result.append({**data, 'id': key})
    return result


def save_owned_outfit(db, uid, data, *, outfit_id=None, create=False):
    unknown = set(data) - EDITABLE
    if unknown:
        raise HTTPException(422, 'Unsupported outfit fields: ' + ', '.join(sorted(unknown)))
    for key, value in data.items():
        if key == 'items':
            continue
        if key == 'isFavorite':
            if not isinstance(value, bool):
                raise HTTPException(422, 'Favorite must be a boolean')
        elif value is not None and not isinstance(value, str):
            raise HTTPException(422, 'Invalid outfit field: ' + key)
    key = _document_id(outfit_id or f'outfit_{uuid4().hex}')
    ref = db.collection('outfits').document(key)
    now = datetime.now(timezone.utc)

    @firestore.transactional
    def save(txn):
        snapshot = ref.get(transaction=txn)
        existing = snapshot.to_dict() or {} if snapshot.exists else {}
        if snapshot.exists and not _owner_matches(existing, uid):
            raise HTTPException(403, 'Access denied')
        if create and snapshot.exists:
            return {**existing, 'id': key}
        if not create and not snapshot.exists:
            raise HTTPException(404, 'Outfit not found')
        patch = dict(data)
        if 'items' in patch:
            patch['items'] = _garments(db, txn, patch['items'], uid)
        elif create:
            raise HTTPException(422, 'Select wardrobe items')
        patch['updatedAt'] = now.isoformat()
        changed = ('items' in patch and
                   {x.get('id') if isinstance(x, dict) else x for x in existing.get('items', [])} !=
                   {x['id'] for x in patch['items']})
        if create:
            record = {**patch, 'id': key, 'user_id': uid, 'userId': uid,
                      'createdAt': now.isoformat(), 'wearCount': 0, 'isFavorite': False,
                      'metadata': {'creation_type': 'manual', 'item_count': len(patch['items'])}}
            # Nested maps, not dotted names, on create.
            for path, value in _projection('awaiting_consent', None, int(now.timestamp()), retryable=True).items():
                if path.startswith('metadata.'):
                    record['metadata'][path.split('.', 1)[1]] = value
                else:
                    record[path] = value
            txn.set(ref, record)
            return record
        if changed:
            request_snapshot = db.collection('flat_lay_requests').document(key).get(transaction=txn)
            request = request_snapshot.to_dict() or {} if request_snapshot.exists else {}
            if request.get('status') in ('pending', 'processing'):
                patch.update(_projection(request['status'], request.get('request_id'), int(now.timestamp()),
                    error='This outfit changed. Its earlier preview request is being settled.',
                    error_code='outfit_changed', credit_status=request.get('credit_status')))
            else:
                patch.update(_projection('awaiting_consent', None, int(now.timestamp()), retryable=True))
            patch['metadata.item_count'] = len(patch['items'])
        txn.update(ref, patch)
        result = {**existing, 'metadata': dict(existing.get('metadata') or {})}
        for path, value in patch.items():
            if path.startswith('metadata.'):
                result['metadata'][path.split('.', 1)[1]] = value
            else:
                result[path] = value
        return {**result, 'id': key}

    return save(db.transaction())


def delete_owned_outfit(db, uid, outfit_id):
    ref = db.collection('outfits').document(_document_id(outfit_id))

    @firestore.transactional
    def remove(txn):
        snapshot = ref.get(transaction=txn)
        if not snapshot.exists:
            return
        if not _owner_matches(snapshot.to_dict() or {}, uid):
            raise HTTPException(403, 'Access denied')
        request_snapshot = db.collection('flat_lay_requests').document(outfit_id).get(transaction=txn)
        request = request_snapshot.to_dict() or {} if request_snapshot.exists else {}
        if request.get('status') in ('pending', 'processing'):
            raise HTTPException(409, 'Wait for this preview request to finish before deleting the outfit')
        # Keep private credit history, even when its public outfit is removed.
        txn.delete(ref)

    remove(db.transaction())
