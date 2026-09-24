"""Idempotent, atomic reward mutations shared by wear, challenges and feedback."""
import hashlib
import json
from datetime import datetime, timezone
from firebase_admin import firestore
from .app_data_privacy import require_app_data_writable
from .wear_rewards import level_for, TOKEN_MULTIPLIERS


def key_for(*parts):
    return hashlib.sha256(json.dumps(parts, separators=(",", ":")).encode()).hexdigest()


def read(reference, transaction):
    snapshot = reference.get(transaction=transaction)
    return snapshot.to_dict() if snapshot.exists else None


def reward_patch(user, *, xp=0, tokens=0, badge=None, timestamp=0):
    old_xp = int(user.get("xp", 0))
    new_xp = old_xp + xp
    patch = {"xp": new_xp, "level": level_for(new_xp), "updatedAt": timestamp}
    balance = user.get("style_tokens") or {}
    patch["style_tokens"] = {**balance, "balance": int(balance.get("balance", 0)) + tokens, "total_earned": int(balance.get("total_earned", 0)) + tokens, "total_spent": int(balance.get("total_spent", 0)), "updated_at": timestamp}
    badges = list(user.get("badges") or [])
    new_badge = bool(badge and badge not in badges)
    if new_badge:
        badges.append(badge)
    patch["badges"] = badges
    return patch, {"success": True, "xp_awarded": xp, "tokens_awarded": tokens, "new_xp": new_xp, "level": patch["level"], "new_level": patch["level"], "level_up": patch["level"] > level_for(old_xp), "new_balance": patch["style_tokens"]["balance"], "badge_unlocked": badge if new_badge else None}


def award(db, user_id, operation_id, *, xp=0, tokens=0, badge=None, apply_role_multiplier=False, metadata=None, expected_epoch=None):
    if isinstance(xp, bool) or isinstance(tokens, bool) or xp < 0 or tokens < 0:
        raise ValueError("Rewards must be nonnegative")
    user_ref = db.collection("users").document(user_id)
    receipt_ref = db.collection("reward_ledger").document(key_for(user_id, operation_id))
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    epoch_fence = WriteEpochFence(db, user_id, expected_epoch)
    @firestore.transactional
    def commit(transaction):
        epoch_fence.check(transaction)
        user = read(user_ref, transaction)
        receipt = read(receipt_ref, transaction)
        if not user:
            raise ValueError("User not found")
        if receipt:
            return {"success": True, "level": level_for(int(user.get("xp", 0))), "new_level": level_for(int(user.get("xp", 0))), **receipt.get("result", {}), "already_awarded": True, "xp_awarded": 0, "tokens_awarded": 0, "level_up": False, "badge_unlocked": None}
        actual_tokens = int(tokens * TOKEN_MULTIPLIERS.get((user.get("role") or {}).get("current_role", "starter"), 1)) if apply_role_multiplier else tokens
        patch, result = reward_patch(user, xp=xp, tokens=actual_tokens, badge=badge, timestamp=timestamp)
        transaction.update(user_ref, patch)
        transaction.set(receipt_ref, {"user_id": user_id, "operation_id": operation_id, "result": result, "metadata": metadata or {}, "created_at": timestamp})
        return result
    return commit(db.transaction())


def initialize_missing(db, user_id):
    reference = db.collection("users").document(user_id)
    defaults = {"xp": 0, "level": 1, "ai_fit_score": 0.0, "badges": [], "current_challenges": {}}
    epoch_fence = WriteEpochFence(db, user_id)
    @firestore.transactional
    def initialize(transaction):
        epoch_fence.check(transaction)
        user = read(reference, transaction)
        updates = {key: value for key, value in defaults.items() if key not in user}
        if updates:
            transaction.update(reference, updates)
        return updates
    return initialize(db.transaction())


class WriteEpochFence:
    """Bind a logical action to its first read across Firestore retries."""
    def __init__(self, db, user_id, expected_epoch=None):
        self.db, self.user_id, self.expected_epoch = db, user_id, expected_epoch

    def check(self, transaction):
        epoch = require_app_data_writable(self.db, self.user_id, expected_epoch=self.expected_epoch, transaction=transaction)
        if self.expected_epoch is None:
            self.expected_epoch = epoch
        return epoch
