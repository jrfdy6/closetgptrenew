"""Owned outfit edits and recoverable soft deletion; financial settlement stays in the ledger."""
from datetime import datetime, timezone
import hashlib
import json
from fastapi import HTTPException
from firebase_admin import firestore
from .flatlay_lifecycle import _owner_matches, _projection, finish_request
from .outfit_creation_admission import resolve_owned_items, _item_id, is_deleted

EDITABLE = frozenset(('name', 'description', 'notes', 'occasion', 'style', 'mood', 'season', 'items', 'isFavorite'))


def _writable(db, uid, txn, expected_epoch=None):
    from .app_data_privacy import require_app_data_writable, AppDataDeletionError
    try:
        return require_app_data_writable(db, uid, expected_epoch=expected_epoch, transaction=txn)
    except AppDataDeletionError as error:
        raise HTTPException(error.status_code, error.detail) from None


def edit_owned_outfit(db, outfit_id, user_id, data):
    if not _item_id(outfit_id) or not isinstance(data, dict):
        raise HTTPException(422, 'Invalid outfit update.')
    if set(data) - EDITABLE:
        raise HTTPException(422, 'Only outfit details and selected pieces can be edited.')
    for key, value in data.items():
        if key == 'items':
            continue
        valid = isinstance(value, bool) if key == 'isFavorite' else (
            (isinstance(value, str) or value is None) or
            key == 'season' and isinstance(value, list) and all(isinstance(entry, str) for entry in value))
        if not valid:
            raise HTTPException(422, 'Invalid outfit field: ' + key)
    now = datetime.now(timezone.utc)
    ref = db.collection('outfits').document(outfit_id)
    operation_epoch = None

    @firestore.transactional
    def edit(txn):
        nonlocal operation_epoch
        operation_epoch = _writable(db, user_id, txn, operation_epoch)
        snapshot = ref.get(transaction=txn)
        existing = snapshot.to_dict() if snapshot.exists else {}
        if not existing or not _owner_matches(existing, user_id) or is_deleted(existing):
            raise HTTPException(404, 'Outfit not found.')
        patch = {**data, 'updatedAt': now.isoformat()}
        if 'items' in patch:
            patch['items'] = resolve_owned_items(db, txn, user_id, patch['items'])
            changed = {_item_id(item) for item in existing.get('items', [])} != {item['id'] for item in patch['items']}
            if changed:
                ledger_doc = db.collection('flat_lay_requests').document(outfit_id).get(transaction=txn)
                ledger = ledger_doc.to_dict() if ledger_doc.exists else {}
                active = ledger.get('status') in ('pending', 'processing') and ledger.get('user_id') == user_id
                patch.update(_projection(ledger['status'] if active else 'awaiting_consent',
                    ledger.get('request_id') if active else None, int(now.timestamp()),
                    error='This outfit changed. Its earlier preview request is still being resolved.' if active else None,
                    error_code='outfit_changed' if active else None, retryable=not active,
                    credit_status=ledger.get('credit_status') if active else None))
                patch['metadata.item_count'] = len(patch['items'])
        txn.update(ref, patch)
        return {'success': True, 'id': outfit_id, 'outfit_id': outfit_id, 'updatedAt': patch['updatedAt']}

    return edit(db.transaction())


def record_outfit_rating(db, user_id, outfit_id, data, *, now=None):
    """Persist one editable rating and its immutable first-submission timestamp.

    The deterministic document also identifies its single reward. Retry/edit
    submissions cannot manufacture another feedback event for challenges.
    """
    if not _item_id(outfit_id) or not isinstance(data, dict):
        raise HTTPException(422, 'Invalid outfit rating.')
    if set(data) - {'rating', 'isLiked', 'isDisliked', 'feedback'}:
        raise HTTPException(422, 'Invalid outfit rating field.')
    rating = data.get('rating')
    if rating is not None and (isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5):
        raise HTTPException(422, 'Choose a rating from 1 to 5.')
    if any(value is not None and not isinstance(value, bool) for value in (data.get('isLiked'), data.get('isDisliked'))):
        raise HTTPException(422, 'Invalid like or dislike value.')
    if data.get('isLiked') and data.get('isDisliked'):
        raise HTTPException(422, 'An outfit cannot be liked and disliked together.')
    feedback = data.get('feedback')
    if feedback is not None and (not isinstance(feedback, str) or len(feedback) > 2000):
        raise HTTPException(422, 'Feedback must contain at most 2000 characters.')
    timestamp = (now or datetime.now(timezone.utc)).isoformat()
    feedback_id = hashlib.sha256(json.dumps([user_id, outfit_id], separators=(',', ':')).encode()).hexdigest()
    outfit_ref = db.collection('outfits').document(outfit_id)
    feedback_ref = db.collection('outfit_feedback').document(feedback_id)
    operation_epoch = None

    @firestore.transactional
    def record(txn):
        nonlocal operation_epoch
        epoch = _writable(db, user_id, txn, operation_epoch)
        operation_epoch = epoch
        snapshot = outfit_ref.get(transaction=txn)
        outfit = snapshot.to_dict() if snapshot.exists else {}
        if not outfit or not _owner_matches(outfit, user_id) or is_deleted(outfit):
            raise HTTPException(404, 'Outfit not found.')
        prior_snapshot = feedback_ref.get(transaction=txn)
        prior = prior_snapshot.to_dict() if prior_snapshot.exists else {}
        if prior and (prior.get('user_id') != user_id or prior.get('outfit_id') != outfit_id):
            raise HTTPException(409, 'This feedback record needs review.')
        if not prior and rating is None and not data.get('isLiked') and not data.get('isDisliked') and not (feedback or '').strip():
            raise HTTPException(422, 'Add a rating, reaction, or feedback before submitting.')
        fields = {key: value for key, value in data.items() if value is not None}
        state = {**{key: prior[key] for key in ('rating', 'isLiked', 'isDisliked', 'feedback') if key in prior}, **fields}
        changed = not prior or any(prior.get(key) != value for key, value in state.items())
        if changed:
            patch = {key if key != 'feedback' else 'userFeedback': value for key, value in fields.items()}
            patch['updatedAt'] = timestamp
            txn.update(outfit_ref, patch)
            txn.set(feedback_ref, {**prior, **state, 'user_id': user_id, 'outfit_id': outfit_id,
                'created_at': prior.get('created_at') if prior else timestamp, 'updated_at': timestamp,
                'app_data_epoch': epoch, 'source': 'outfit_rating',
                'feedback_type': 'like' if state.get('isLiked') else 'dislike' if state.get('isDisliked') else 'rating'})
            outfit.update(patch)
        return {'outfit': {**outfit, 'id': outfit_id}, 'feedback_id': feedback_id,
                'created': not bool(prior), 'changed': changed, 'app_data_epoch': epoch,
                'reward_operation_id': 'outfit-rating-' + feedback_id}

    return record(db.transaction())


def delete_owned_outfit(db, outfit_id, user_id):
    if not _item_id(outfit_id):
        raise HTTPException(404, 'Outfit not found.')
    ref = db.collection('outfits').document(outfit_id)
    operation_epoch = None

    @firestore.transactional
    def remove(txn):
        nonlocal operation_epoch
        operation_epoch = _writable(db, user_id, txn, operation_epoch)
        snapshot = ref.get(transaction=txn)
        existing = snapshot.to_dict() if snapshot.exists else {}
        if not existing or not _owner_matches(existing, user_id):
            raise HTTPException(404, 'Outfit not found.')
        ledger_doc = db.collection('flat_lay_requests').document(outfit_id).get(transaction=txn)
        ledger = ledger_doc.to_dict() if ledger_doc.exists else {}
        if not is_deleted(existing):
            txn.update(ref, {'deleted': True, 'deletedAt': datetime.now(timezone.utc).isoformat()})
        return ledger

    ledger = remove(db.transaction())
    # Retrying DELETE retries settlement after a transient error; the normal
    # ledger transaction fences duplicate or late worker results and refunds.
    if (ledger.get('user_id') == user_id and ledger.get('outfit_id') == outfit_id
            and ledger.get('status') in ('pending', 'processing') and ledger.get('request_id')):
        finish_request(db, outfit_id, ledger['request_id'], error='This outfit was deleted.',
                       error_code='outfit_deleted', retryable=False)
    return {'success': True, 'id': outfit_id, 'outfit_id': outfit_id, 'deleted': True}
