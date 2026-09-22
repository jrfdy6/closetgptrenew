"""Create the server-owned account authority once, under the debit transaction lock."""
from datetime import datetime, timezone

from firebase_admin import firestore

from .subscription_utils import quotas_defaults, subscription_defaults


def ensure_user_account(db, user_id, *, email=None, name=None, now=None):
    """Return an existing account unchanged or atomically create free defaults.

    Call only with UID and identity values from a verified Firebase token. Never
    reconstruct credits on sign-in: incomplete historical records go to review.
    """
    if not isinstance(user_id, str) or not user_id or "/" in user_id:
        raise ValueError("A verified user ID is required")
    now = now or datetime.now(timezone.utc)
    if isinstance(now, (int, float)):
        now = datetime.fromtimestamp(now, timezone.utc)
    user_ref = db.collection("users").document(user_id)

    @firestore.transactional
    def initialize(transaction):
        snapshot = user_ref.get(transaction=transaction)
        if snapshot.exists:
            return snapshot.to_dict() or {}
        user = {
            "email": email, "name": name or email, "firebase_uid": user_id,
            "created_at": now, "updated_at": now,
            "subscription": subscription_defaults(now=now),
            "quotas": quotas_defaults(now=now),
        }
        transaction.set(user_ref, user)
        return user

    return initialize(db.transaction())
