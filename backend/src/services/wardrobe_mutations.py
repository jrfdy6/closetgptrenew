"""Transactional wardrobe edits and standalone wear, fenced against account clearing."""
from datetime import datetime, timezone
import hashlib
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from fastapi import HTTPException
from firebase_admin import firestore
from .app_data_privacy import require_app_data_writable, AppDataDeletionError


def _owned(item, uid):
    owners = [item[key] for key in ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId') if item.get(key) is not None]
    return bool(owners) and all(value == uid for value in owners)


def mutate_wardrobe(db, uid, item_id, operation, patch=None, *, expected_epoch=None, idempotency_key=None, now=None):
    if not isinstance(item_id, str) or not item_id or '/' in item_id:
        raise HTTPException(404, 'Wardrobe item not found')
    if operation not in ('edit', 'delete', 'wear'):
        raise ValueError('Unknown wardrobe operation')
    instant = now or datetime.now(timezone.utc)
    timestamp = int(instant.timestamp())
    ref = db.collection('wardrobe').document(item_id)
    user_ref = db.collection('users').document(uid)
    receipt_id = hashlib.sha256(f'{uid}:{item_id}'.encode()).hexdigest()
    deletion_ref = db.collection('wardrobe_deletion_receipts').document(receipt_id)
    asset_owner_ref = db.collection('wardrobe_asset_owners').document(item_id)

    operation_epoch = [expected_epoch]

    @firestore.transactional
    def mutate(txn):
        try:
            epoch = require_app_data_writable(db, uid, expected_epoch=operation_epoch[0], transaction=txn)
            operation_epoch[0] = epoch
        except AppDataDeletionError as error:
            raise HTTPException(error.status_code, error.detail) from None
        profile_doc = user_ref.get(transaction=txn)
        profile = profile_doc.to_dict() if profile_doc.exists else {}
        snapshot = ref.get(transaction=txn)
        item = snapshot.to_dict() if snapshot.exists else {}
        if operation == 'delete':
            asset_owner_snapshot = asset_owner_ref.get(transaction=txn)
            asset_owner = asset_owner_snapshot.to_dict() if asset_owner_snapshot.exists else {}
            if asset_owner and asset_owner.get('user_id') != uid:
                raise HTTPException(409, 'This item identity needs review')
            deleted_snapshot = deletion_ref.get(transaction=txn)
            deleted = deleted_snapshot.to_dict() if deleted_snapshot.exists else {}
            if not item and deleted.get('user_id') == uid:
                return {'deleted': True, 'already_deleted': True}
        if not item:
            raise HTTPException(404, 'Wardrobe item not found')
        if not _owned(item, uid):
            raise HTTPException(403, 'Not authorized to update this item')
        if operation != 'delete' and any(item.get(key) for key in ('deleted', 'isDeleted', 'deletedAt', 'deleted_at')):
            raise HTTPException(404, 'Wardrobe item not found')
        if operation == 'edit':
            if patch:
                txn.update(ref, {**patch, 'updatedAt': timestamp})
            return item
        if operation == 'delete':
            if not asset_owner:
                txn.set(asset_owner_ref, {'user_id': uid, 'first_seen': timestamp})
            txn.set(deletion_ref, {'user_id': uid, 'item_id': item_id, 'app_data_epoch': epoch, 'deleted_at': timestamp})
            txn.delete(ref)
            if profile_doc.exists:
                txn.update(user_ref, {'wardrobeItemCount': max(0, int(profile.get('wardrobeItemCount', 0)) - 1)})
            return {'deleted': True, 'already_deleted': False}
        zone_name = (profile.get('location_data') or {}).get('timezone', 'UTC')
        try:
            zone = ZoneInfo(zone_name)
        except (ZoneInfoNotFoundError, TypeError, ValueError):
            zone = ZoneInfo('UTC')
        day = instant.astimezone(zone).date().isoformat()
        key = idempotency_key or f'day:{day}'
        if not isinstance(key, str) or not 1 <= len(key) <= 200:
            raise HTTPException(422, 'Invalid wear request key')
        operation_id = hashlib.sha256(f'{uid}:{epoch}:{item_id}:{key}'.encode()).hexdigest()
        receipt_ref = db.collection('wardrobe_wear_receipts').document(operation_id)
        prior_doc = receipt_ref.get(transaction=txn)
        if prior_doc.exists:
            return prior_doc.to_dict()['result']
        previous = max(0, int(item.get('wearCount', 0)))
        result = {'itemId': item_id, 'previousWearCount': previous, 'newWearCount': previous + 1, 'lastWorn': timestamp}
        txn.update(ref, {'wearCount': previous + 1, 'lastWorn': timestamp, 'updatedAt': timestamp, 'wear_baseline_last_worn': timestamp})
        txn.set(receipt_ref, {'user_id': uid, 'item_id': item_id, 'app_data_epoch': epoch, 'result': result, 'created_at': timestamp})
        return result

    return mutate(db.transaction())
