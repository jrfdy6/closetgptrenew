"""Settle a committed rating and its one-time XP in one recoverable transaction."""
from datetime import datetime, timezone
from firebase_admin import firestore
from .reward_ledger import WriteEpochFence, key_for, read, reward_patch
from .app_data_privacy import JOBS


def _preserved_by_analytics_clears(db, uid, row_epoch, epoch, user, transaction):
    """Only fresh work may adopt feedback explicitly retained by analytics clears."""
    if (not isinstance(row_epoch, int) or isinstance(row_epoch, bool) or
            not 0 < epoch - row_epoch <= 100):
        return False
    state = user.get('app_data_deletion') or {}
    job_id = state.get('job_id')
    if not job_id or state.get('status') != 'complete':
        return False
    latest = read(db.collection(JOBS).document(job_id), transaction) or {}
    def valid(job):
        return job.get('user_id') == uid and job.get('status') == 'complete' and job.get('scope') == 'analytics'
    if not valid(latest) or latest.get('epoch') != epoch:
        return False
    if row_epoch + 1 == epoch:
        return True
    from google.cloud.firestore_v1.base_query import FieldFilter
    jobs = db.collection(JOBS).where(filter=FieldFilter('user_id', '==', uid)).limit(100)
    preserved = {doc.to_dict().get('epoch') for doc in jobs.stream(transaction=transaction) if valid(doc.to_dict())}
    return set(range(row_epoch + 1, epoch + 1)).issubset(preserved)


def settle_feedback_reward(db, uid, feedback_id, *, expected_epoch):
    feedback_ref = db.collection('outfit_feedback').document(feedback_id)
    user_ref = db.collection('users').document(uid)
    operation_id = 'outfit-rating-' + feedback_id
    receipt_ref = db.collection('reward_ledger').document(key_for(uid, operation_id))
    fence = WriteEpochFence(db, uid, expected_epoch)
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

    @firestore.transactional
    def settle(transaction):
        epoch = fence.check(transaction)
        feedback = read(feedback_ref, transaction)
        user = read(user_ref, transaction)
        prior = read(receipt_ref, transaction)
        if (not feedback or feedback.get('user_id') != uid or
                feedback.get('reward_operation_id') != operation_id):
            return {'success': False, 'xp_awarded': 0}
        if (feedback.get('app_data_epoch', 0) != epoch and not
                _preserved_by_analytics_clears(db, uid, feedback.get('app_data_epoch', 0), epoch, user, transaction)):
            return {'success': False, 'xp_awarded': 0}
        if prior:
            result = {**prior.get('result', {}), 'success': True, 'already_awarded': True,
                      'xp_awarded': 0, 'level_up': False}
        elif feedback.get('reward_pending') is True:
            patch, result = reward_patch(user, xp=5, timestamp=timestamp)
            transaction.update(user_ref, patch)
            transaction.set(receipt_ref, {'user_id': uid, 'operation_id': operation_id,
                'result': result, 'created_at': timestamp, 'app_data_epoch': epoch,
                'metadata': {'reason': 'outfit_rated', 'outfit_id': feedback.get('outfit_id')}})
        else:
            return {'success': False, 'xp_awarded': 0}
        transaction.update(feedback_ref, {'reward_pending': False, 'reward_settled_at': timestamp, 'app_data_epoch': epoch})
        return result

    return settle(db.transaction())
