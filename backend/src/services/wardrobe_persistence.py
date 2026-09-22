"""Atomic creation for upload records, with ownership-safe idempotent retries."""

from datetime import datetime, timezone
from uuid import uuid4

from firebase_admin import firestore


class WardrobeOwnershipConflict(Exception):
    """A caller-supplied identifier already belongs to a different account."""


def create_owned_wardrobe_item(db, user_id: str, item_data: dict, *, now=None) -> dict:
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("A verified account is required")
    for field in ("name", "type", "color"):
        if field not in item_data:
            raise ValueError(f"Missing required field: {field}")
    item_id = item_data.get("id")
    if item_id is None:
        item_id = str(uuid4())
    if (not isinstance(item_id, str) or not item_id.strip() or "/" in item_id
            or item_id in (".", "..") or len(item_id.encode("utf-8")) > 1500):
        raise ValueError("Invalid wardrobe item ID")

    timestamp = now or datetime.now(timezone.utc).isoformat()
    garment = {
        **item_data,
        "id": item_id,
        "userId": user_id,
        "createdAt": item_data.get("createdAt") or timestamp,
        "updatedAt": timestamp,
        "backgroundRemovedUrl": None,
        "processing_status": "pending",
    }
    # A caller cannot plant a second, conflicting ownership field.
    garment.pop("user_id", None)
    reference = db.collection("wardrobe").document(item_id)

    @firestore.transactional
    def persist(transaction):
        snapshot = reference.get(transaction=transaction)
        if snapshot.exists:
            existing = snapshot.to_dict() or {}
            owners = [existing.get(key) for key in ("userId", "user_id") if existing.get(key)]
            if not owners or any(owner != user_id for owner in owners):
                raise WardrobeOwnershipConflict("This item ID is already in use")
            # An upload retry must not reset completed image work, wear history,
            # or edits. Return the original persisted garment without writing.
            return {**existing, "id": item_id, "userId": user_id}
        transaction.create(reference, garment)
        return garment

    return persist(db.transaction())
