"""Application-data privacy policy and durable, fenced deletion (worker mirrored).

Authentication, billing, credit balances and minimal anti-duplication receipts
survive clear-all. No Stripe or Auth deletion is performed here.
"""
from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4
import time

from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

JOBS = 'app_data_deletion_jobs'
BLOCKING = {'pending', 'running', 'failed'}
OWNER_KEYS = ('user_id', 'userId', 'requested_by', 'uid', 'ownerId', 'firebase_uid')
RETAIN_USER = {'email', 'firebase_uid', 'user_id', 'userId', 'uid', 'created_at', 'createdAt',
               'subscription', 'quotas', 'billing', 'stripeCustomerId', 'stripeSubscriptionId',
               'trial_used', 'privacy', 'app_data_epoch', 'app_data_deletion'}
APP_COLLECTIONS = ('wardrobe', 'outfits', 'outfit_history', 'daily_outfit_suggestions',
                   'analytics_events', 'item_analytics', 'item_favorite_scores', 'user_analytics',
                   'outfit_feedback', 'enhanced_outfit_feedback', 'outfit_likes', 'generation_traces',
                   'user_journeys', 'sessions', 'style_insights', 'user_learning_stats',
                   'user_preferences', 'user_style_profiles', 'user_stats', 'user_challenges',
                   'garment_processing_jobs', 'codex_jobs', 'ingest_jobs', 'knowledge_chunks',
                   'wear_projection_jobs', 'wear_projection_receipts', 'wardrobe_deletion_receipts', 'wardrobe_wear_receipts',
                   'gamification_user_jobs')
DIRECT_COLLECTIONS = {'user_preferences', 'user_style_profiles', 'user_stats', 'user_challenges',
                      'user_learning_stats', 'onboarding_states', 'profiles'}
RECEIPT_COLLECTIONS = ('outfit_wear_receipts', 'outfit_reward_receipts', 'reward_ledger',
                       'wear_engagement_days', 'gamification_rating_days')
RECEIPT_FIELDS = {'user_id', 'userId', 'operation_id', 'wear_id', 'outfit_id', 'date', 'date_worn',
                  'status', 'version', 'schema_version', 'created_at', 'applied_at', 'app_data_epoch',
                  'event_id', 'day', 'timezone', 'rewarded', 'rewards', 'result', 'revision'}


class AppDataDeletionError(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code, self.detail = status_code, detail


def data_epoch(user):
    value = user.get('app_data_epoch', 0)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AppDataDeletionError(409, 'Account data state needs review')
    return value


def app_data_write_allowed(user_data, expected_epoch=None):
    if not isinstance(user_data, dict) or (expected_epoch is not None and (isinstance(expected_epoch, bool) or not isinstance(expected_epoch, int) or expected_epoch < 0)):
        return False
    try:
        epoch = data_epoch(user_data)
    except AppDataDeletionError:
        return False
    state = user_data.get('app_data_deletion') or {}
    return (isinstance(state, dict) and state.get('status') not in BLOCKING
            and (expected_epoch is None or expected_epoch == epoch))


def require_app_data_writable(db, user_id, expected_epoch=None, transaction=None):
    if not isinstance(user_id, str) or not user_id or user_id.strip() != user_id or '/' in user_id or len(user_id) > 128:
        raise AppDataDeletionError(404, 'Account not found')
    snapshot = db.collection('users').document(user_id).get(transaction=transaction)
    if not snapshot.exists:
        raise AppDataDeletionError(404, 'Account not found')
    user = snapshot.to_dict() or {}
    if not app_data_write_allowed(user, expected_epoch):
        raise AppDataDeletionError(409, 'Your app data is being cleared or has changed. Reload before saving.')
    return data_epoch(user)


def optional_processing_allowed(user, kind):
    if not app_data_write_allowed(user):
        return False
    privacy = user.get('privacy') or {}
    if not isinstance(privacy, dict) or privacy.get('allow_data_collection', True) is not True:
        return False
    if kind == 'telemetry':
        return privacy.get('share_analytics', False) is True
    if kind == 'shared_style':
        return privacy.get('share_style_data', False) is True
    return privacy.get('allow_personalization', True) is True


def optional_policy(db, user_id, kind):
    try:
        snapshot = db.collection('users').document(user_id).get()
        return snapshot.exists and optional_processing_allowed(snapshot.to_dict() or {}, kind)
    except Exception:
        return False


def write_optional_record(db, user_id, reference, payload, *, kind='telemetry', expected_epoch=None, merge=False):
    captured_epoch = [expected_epoch]
    @firestore.transactional
    def write(txn):
        snapshot = db.collection('users').document(user_id).get(transaction=txn)
        user = snapshot.to_dict() or {} if snapshot.exists else None
        if not user or not optional_processing_allowed(user, kind) or not app_data_write_allowed(user, captured_epoch[0]):
            return False
        if captured_epoch[0] is None:
            captured_epoch[0] = data_epoch(user)
        txn.set(reference, {**payload, 'app_data_epoch': data_epoch(user)}, merge=merge)
        return True
    return write(db.transaction())


def write_app_record(db, user_id, reference, payload, *, expected_epoch, merge=False):
    """Atomically fence a non-optional app record produced by background work."""
    @firestore.transactional
    def write(txn):
        epoch = require_app_data_writable(db, user_id, expected_epoch=expected_epoch, transaction=txn)
        txn.set(reference, {**payload, 'app_data_epoch': epoch}, merge=merge)
    write(db.transaction())


def _owned(record, uid):
    owners = [record[key] for key in OWNER_KEYS if record.get(key) is not None]
    return bool(owners) and all(owner == uid for owner in owners)


def _job_view(job, job_id):
    return {'success': True, 'job_id': job_id, 'status': job['status'],
            'scope': job['scope'], 'epoch': job['epoch'],
            'completed': job['status'] == 'complete', 'deleted': job.get('deleted', 0),
            'error': job.get('error'), 'retryable': job['status'] == 'failed',
            'retained': ['login', 'billing', 'credits', 'privacy settings', 'minimal financial and anti-duplication receipts']}


def request_app_data_deletion(db, uid, scope='all', *, now=None):
    if scope not in {'all', 'wardrobe', 'outfits', 'analytics'}:
        raise AppDataDeletionError(422, 'Choose all, wardrobe, outfits, or analytics')
    now = int(time.time()) if now is None else now
    user_ref = db.collection('users').document(uid)
    initial = user_ref.get()
    if not initial.exists:
        raise AppDataDeletionError(404, 'Account not found')
    captured_epoch = data_epoch(initial.to_dict() or {})
    job_id = uuid4().hex
    job_ref = db.collection(JOBS).document(job_id)

    @firestore.transactional
    def request(txn):
        snapshot = user_ref.get(transaction=txn)
        if not snapshot.exists:
            raise AppDataDeletionError(404, 'Account not found')
        user = snapshot.to_dict() or {}
        active = user.get('app_data_deletion') or {}
        if not isinstance(active, dict):
            raise AppDataDeletionError(409, 'Deletion state needs review')
        if active.get('status') in BLOCKING:
            current_ref = db.collection(JOBS).document(active['job_id'])
            current = current_ref.get(transaction=txn)
            if not current.exists:
                raise AppDataDeletionError(409, 'Deletion state needs review')
            job = current.to_dict()
            if job['scope'] != scope:
                raise AppDataDeletionError(409, 'Finish the existing data-clear request first')
            if job['status'] == 'failed':
                job = {**job, 'status': 'pending', 'error': None, 'lease_until': 0}
                txn.update(current_ref, {'status': 'pending', 'error': None, 'lease_until': 0})
                txn.update(user_ref, {'app_data_deletion.status': 'pending'})
            return _job_view(job, active['job_id'])
        if data_epoch(user) != captured_epoch:
            raise AppDataDeletionError(409, 'Account data changed; reload before clearing it again')
        epoch = captured_epoch + 1
        job = {'user_id': uid, 'scope': scope, 'epoch': epoch, 'status': 'pending',
               'schema_version': 1, 'collections': _collections(scope),
               'phase': 0, 'deleted': 0, 'created_at': now, 'updated_at': now,
               'lease_until': 0, 'drain_until': now, 'error': None}
        txn.create(job_ref, job)
        txn.update(user_ref, {'app_data_epoch': epoch,
                             'app_data_deletion': {'job_id': job_id, 'epoch': epoch, 'status': 'pending'}})
        return _job_view(job, job_id)
    return request(db.transaction())


def read_deletion_status(db, uid):
    user = db.collection('users').document(uid).get()
    state = (user.to_dict() or {}).get('app_data_deletion') or {} if user.exists else {}
    if not state.get('job_id'):
        return {'success': True, 'status': 'idle', 'completed': False}
    snapshot = db.collection(JOBS).document(state['job_id']).get()
    job = snapshot.to_dict() or {} if snapshot.exists else {}
    if job.get('user_id') != uid:
        raise AppDataDeletionError(409, 'Deletion state needs review')
    return _job_view(job, state['job_id'])


def _collections(scope):
    if scope == 'wardrobe':
        # Saved looks and derived learning contain the erased garment photos/data.
        return list(dict.fromkeys([*APP_COLLECTIONS, *sorted(DIRECT_COLLECTIONS), *RECEIPT_COLLECTIONS]))
    if scope == 'outfits':
        return ['outfits', 'outfit_history', 'daily_outfit_suggestions', 'outfit_likes',
                'outfit_feedback', 'enhanced_outfit_feedback', 'user_preferences', 'user_stats',
                *RECEIPT_COLLECTIONS]
    if scope == 'analytics':
        return ['analytics_events', 'item_analytics', 'item_favorite_scores', 'user_analytics',
                'generation_traces', 'user_journeys', 'sessions', 'style_insights', 'user_learning_stats']
    return list(dict.fromkeys([*APP_COLLECTIONS, *sorted(DIRECT_COLLECTIONS), *RECEIPT_COLLECTIONS]))


def _owned_documents(db, collection, uid, limit):
    found = {}
    if collection in DIRECT_COLLECTIONS:
        ref = db.collection(collection).document(uid)
        snapshot = ref.get()
        value = snapshot.to_dict() or {} if snapshot.exists else {}
        if any(value.get(key) is not None for key in OWNER_KEYS) and not _owned(value, uid):
            raise AppDataDeletionError(409, 'Conflicting record ownership needs review before deletion')
        if snapshot.exists or any(ref.collections()):
            found[snapshot.id] = snapshot
    for field in OWNER_KEYS:
        for doc in db.collection(collection).where(filter=FieldFilter(field, '==', uid)).limit(limit).stream():
            value = doc.to_dict() or {}
            if _owned(value, uid):
                found[doc.id] = doc
            else:
                raise AppDataDeletionError(409, 'Conflicting record ownership needs review before deletion')
    return list(found.values())[:limit]


def _asset_prefixes(collection, doc_id, uid, data=None):
    if collection == 'wardrobe_deletion_receipts':
        doc_id = (data or {}).get('item_id', '')
        collection = 'wardrobe'
    if not isinstance(doc_id, str) or not doc_id:
        raise AppDataDeletionError(409, 'Asset identity needs review')
    if '/' in doc_id or doc_id in {'.', '..'}:
        raise AppDataDeletionError(409, 'Asset identity needs review')
    if collection == 'wardrobe':
        return [f'items/{doc_id}/']
    if collection == 'outfits':
        return [f'flat_lays/outfit_{doc_id}/', f'flat_lays/outfit_{doc_id}.png']
    return []


def _retained_batch(db, collection, uid, field_index, cursor, limit):
    """Stable single-field pages also visit records missing a cleanup marker."""
    field = OWNER_KEYS[field_index]
    query = db.collection(collection).where(filter=FieldFilter(field, '==', uid)).order_by('__name__')
    if cursor:
        query = query.start_after({'__name__': db.collection(collection).document(cursor)})
    docs = list(query.limit(limit).stream())
    for doc in docs:
        if not _owned(doc.to_dict() or {}, uid):
            raise AppDataDeletionError(409, 'Conflicting record ownership needs review before deletion')
    return docs


def process_deletion_job(db, bucket, job_id, *, max_records=100, now=None):
    """Run one bounded, leased page. All database changes check the deletion fence.

    Storage objects are listed before a fresh lease check, then removed using
    generation preconditions. A stale pass cannot delete replacements. Workers
    have a maximum 600-second lifetime; storage cleanup waits for that drain.
    """
    clock = (lambda: int(time.time())) if now is None else (lambda: now)
    now = clock()
    max_records = max(1, min(int(max_records), 100))
    job_ref = db.collection(JOBS).document(job_id)
    token = uuid4().hex

    @firestore.transactional
    def claim(txn):
        snap = job_ref.get(transaction=txn)
        job = (snap.to_dict() or {}) if snap.exists else {}
        if job.get('status') not in {'pending', 'running'} or job.get('lease_until', 0) > now:
            return None
        user = db.collection('users').document(job['user_id']).get(transaction=txn)
        user = (user.to_dict() or {}) if user.exists else {}
        if data_epoch(user) != job['epoch'] or (user.get('app_data_deletion') or {}).get('job_id') != job_id:
            raise AppDataDeletionError(409, 'Deletion fence changed')
        txn.update(job_ref, {'status': 'running', 'lease_token': token, 'lease_until': now + 120})
        txn.update(db.collection('users').document(job['user_id']), {'app_data_deletion.status': 'running'})
        return {**job, 'status': 'running'}
    job = claim(db.transaction())
    if job is None:
        current = job_ref.get()
        return _job_view(current.to_dict(), job_id) if current.exists else None
    uid = job['user_id']
    user_ref = db.collection('users').document(uid)

    def guard(txn):
        current = job_ref.get(transaction=txn).to_dict() or {}
        user_doc = user_ref.get(transaction=txn)
        user = (user_doc.to_dict() or {}) if user_doc.exists else {}
        state = user.get('app_data_deletion') or {}
        if (current.get('lease_token') != token or current.get('lease_until', 0) <= clock()
                or current.get('status') != 'running' or data_epoch(user) != job['epoch']
                or state.get('job_id') != job_id or state.get('status') != 'running'):
            raise AppDataDeletionError(409, 'Deletion lease or account fence changed')
        return user

    @firestore.transactional
    def checkpoint(txn, changes, *, failed=False):
        guard(txn)
        txn.update(job_ref, {**changes, 'updated_at': clock(), 'lease_until': 0, 'lease_token': None})
        if failed:
            txn.update(user_ref, {'app_data_deletion.status': 'failed'})

    @firestore.transactional
    def guarded_delete(txn, ref):
        guard(txn)
        txn.delete(ref)

    @firestore.transactional
    def guarded_set(txn, ref, values):
        guard(txn)
        txn.set(ref, values)

    @firestore.transactional
    def renew(txn):
        guard(txn)
        txn.update(job_ref, {'lease_until': clock() + 120})

    def delete_tree(ref, remaining):
        count = 0
        for collection in ref.collections():
            for child in collection.limit(remaining - count).stream():
                count += delete_tree(child.reference, remaining - count)
                if count >= remaining:
                    return count
        guarded_delete(db.transaction(), ref)
        return count + 1

    def record_asset(prefix):
        ref = job_ref.collection('assets').document(sha256(prefix.encode()).hexdigest())
        @firestore.transactional
        def reserve(txn):
            guard(txn)
            owner_ref = None
            if prefix.startswith('items/'):
                item_id = prefix.split('/')[1]
                owner_ref = db.collection('wardrobe_asset_owners').document(item_id)
                owner = owner_ref.get(transaction=txn)
                current_item = db.collection('wardrobe').document(item_id).get(transaction=txn)
                if ((owner.exists and (owner.to_dict() or {}).get('user_id') != uid)
                        or (current_item.exists and not _owned(current_item.to_dict() or {}, uid))):
                    raise AppDataDeletionError(409, 'Photo ownership needs review')
            if owner_ref is not None and not owner.exists:
                txn.create(owner_ref, {'user_id': uid})
            txn.set(ref, {'prefix': prefix, 'exact': not prefix.endswith('/')})
        reserve(db.transaction())

    try:
        columns = job.get('collections') or _collections(job['scope'])
        phase = job['phase']
        if phase == 0:
            # Refund active preview reservations via the normal atomic settlement.
            # Analytics-only requests do not touch billing or preview records.
            field_index = job.get('financial_owner_index', 0)
            cursor = job.get('financial_cursor')
            docs = [] if job['scope'] == 'analytics' else _retained_batch(
                db, 'flat_lay_requests', uid, field_index, cursor, max_records)
            try:
                from .flatlay_lifecycle import finish_request
            except ImportError:
                from flatlay_lifecycle import finish_request
            for doc in docs:
                renew(db.transaction())
                value = doc.to_dict() or {}
                if value.get('status') in {'pending', 'processing'} and value.get('credit_status') == 'reserved':
                    finish_request(db, doc.id, value['request_id'], error='App data was cleared.',
                                   error_code='app_data_deleted', retryable=False, now=clock())
                @firestore.transactional
                def scrub(txn):
                    guard(txn)
                    latest = doc.reference.get(transaction=txn).to_dict() or {}
                    if latest.get('credit_status') == 'reserved':
                        raise AppDataDeletionError(409, 'A preview credit could not be settled')
                    retained = {'user_id', 'outfit_id', 'request_id', 'status', 'credit_status',
                                'quota_period_start', 'requested_at', 'finished_at', 'provider_admitted_at',
                                'app_data_epoch', 'error_code'}
                    txn.set(doc.reference, {**{key: val for key, val in latest.items() if key in retained},
                                            'data_cleared_epoch': job['epoch']})
                scrub(db.transaction())
            changes = {'financial_cursor': docs[-1].id} if docs else {'financial_owner_index': field_index + 1, 'financial_cursor': None}
            if job['scope'] == 'analytics' or (not docs and field_index + 1 >= len(OWNER_KEYS)):
                if job['scope'] in {'all', 'wardrobe'}:
                    for prefix in [f'wardrobe/{uid}/', f'flat_lays/{uid}/', f'users/{uid}/', f'photos/{uid}/']:
                        record_asset(prefix)
                changes = {'phase': 1, 'drain_until': max(job.get('created_at', now) + 600, job.get('drain_until', 0))}
        elif phase <= len(columns):
            collection = columns[phase - 1]
            retained = collection in RECEIPT_COLLECTIONS
            field_index = job.get('receipt_owner_index', 0)
            docs = (_retained_batch(db, collection, uid, field_index, job.get('receipt_cursor'), max_records)
                    if retained else _owned_documents(db, collection, uid, max_records))
            deleted = 0
            for doc in docs:
                renew(db.transaction())
                if retained:
                    # Receipt identifiers remain; application response/photo payloads do not.
                    value = doc.to_dict() or {}
                    values = {key: val for key, val in value.items() if key in RECEIPT_FIELDS}
                    values['data_cleared_epoch'] = job['epoch']
                    guarded_set(db.transaction(), doc.reference, values)
                    deleted += 1
                    continue
                for prefix in _asset_prefixes(collection, doc.id, uid, doc.to_dict()):
                    record_asset(prefix)
                deleted += delete_tree(doc.reference, max_records - deleted)
                if deleted >= max_records:
                    break
            changes = {'deleted': job.get('deleted', 0) + deleted}
            if retained:
                if docs:
                    changes['receipt_cursor'] = docs[-1].id
                elif field_index + 1 < len(OWNER_KEYS):
                    changes.update(receipt_owner_index=field_index + 1, receipt_cursor=None)
                else:
                    changes.update(phase=phase + 1, receipt_owner_index=0, receipt_cursor=None)
            elif not docs:
                changes['phase'] = phase + 1
        elif phase == len(columns) + 1:
            deleted = 0
            if job['scope'] in {'all', 'wardrobe'}:
                for collection in user_ref.collections():
                    # Keep only private financial receipts if a legacy account has them nested.
                    if collection.id in {'billing_receipts', 'payment_receipts', 'credit_receipts', 'invoices'}:
                        continue
                    for doc in collection.limit(max_records - deleted).stream():
                        renew(db.transaction())
                        deleted += delete_tree(doc.reference, max_records - deleted)
                        if deleted >= max_records:
                            break
                    if deleted >= max_records:
                        break
            changes = {'deleted': job.get('deleted', 0) + deleted}
            if deleted == 0:
                changes['phase'] = phase + 1
        elif phase == len(columns) + 2:
            changes = {}
            if clock() >= job.get('drain_until', 0):
                assets = list(job_ref.collection('assets').limit(1).stream())
                for asset in assets:
                    renew(db.transaction())
                    value = asset.to_dict() or {}
                    if bucket is None:
                        raise RuntimeError('Photo storage unavailable')
                    blobs = list(bucket.list_blobs(prefix=value['prefix'], max_results=max_records))
                    matching = [blob for blob in blobs if not value.get('exact') or blob.name == value['prefix']]
                    for blob in matching:
                        # Never apply an old list to a newly replaced storage object.
                        renew(db.transaction())
                        try:
                            blob.delete(if_generation_match=blob.generation)
                        except Exception as error:
                            if getattr(error, 'code', None) != 404:
                                raise
                    if not matching:
                        guarded_delete(db.transaction(), asset.reference)
                if not assets:
                    changes['phase'] = phase + 1
        else:
            @firestore.transactional
            def complete(txn):
                user = guard(txn)
                if job['scope'] in {'all', 'wardrobe'}:
                    clean = {key: value for key, value in user.items() if key in RETAIN_USER}
                    clean.update(wardrobeItemCount=0, onboardingCompleted=False, onboarding_completed=False)
                    clean['app_data_deletion'] = {'job_id': job_id, 'epoch': job['epoch'], 'status': 'complete'}
                    txn.set(user_ref, clean)
                else:
                    txn.update(user_ref, {'app_data_deletion.status': 'complete'})
                txn.update(job_ref, {'status': 'complete', 'completed_at': clock(), 'lease_until': 0, 'lease_token': None})
            complete(db.transaction())
            return _job_view(job_ref.get().to_dict(), job_id)
        checkpoint(db.transaction(), changes)
    except Exception as error:
        # A stale worker must never mark a newer deletion/completed account failed.
        try:
            checkpoint(db.transaction(), {'status': 'failed', 'error': 'Data clearing paused. Retry to continue.',
                                         'error_type': type(error).__name__}, failed=True)
        except AppDataDeletionError:
            pass
    return _job_view(job_ref.get().to_dict(), job_id)


def process_deletion_jobs(db, bucket, *, limit=2, max_records=100):
    counts = {'examined': 0, 'complete': 0, 'failed': 0}
    for status in ['pending', 'running']:
        for doc in db.collection(JOBS).where(filter=FieldFilter('status', '==', status)).limit(limit).stream():
            result = process_deletion_job(db, bucket, doc.id, max_records=max_records)
            counts['examined'] += 1
            if result and result['status'] in counts:
                counts[result['status']] += 1
    return counts
