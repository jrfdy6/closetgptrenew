"""Atomic creation for upload records, with ownership-safe idempotent retries."""

from datetime import datetime, timezone
from uuid import uuid4

from firebase_admin import firestore

OWNER_FIELDS = ("userId", "user_id", "firebase_uid", "uid", "ownerId")


class WardrobeOwnershipConflict(Exception):
    """A caller-supplied identifier already belongs to a different account."""


class WardrobeInputError(ValueError):
    """Known input validation, distinct from Firestore transaction failures."""


def create_owned_wardrobe_item(db, user_id: str, item_data: dict, *, now=None) -> dict:
    if not isinstance(user_id, str) or not user_id.strip():
        raise WardrobeInputError("A verified account is required")
    for field in ("name", "type", "color"):
        if field not in item_data:
            raise WardrobeInputError(f"Missing required field: {field}")
    item_id = item_data.get("id")
    if item_id is None:
        item_id = str(uuid4())
    if (not isinstance(item_id, str) or not item_id.strip() or "/" in item_id
            or item_id in (".", "..") or len(item_id.encode("utf-8")) > 1500):
        raise WardrobeInputError("Invalid wardrobe item ID")

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
    # The verified UID is stored once. Legacy aliases remain readable on
    # existing records but cannot introduce a second owner on a new upload.
    for alias in OWNER_FIELDS[1:]:
        garment.pop(alias, None)
    reference = db.collection("wardrobe").document(item_id)

    @firestore.transactional
    def persist(transaction):
        snapshot = reference.get(transaction=transaction)
        if snapshot.exists:
            existing = snapshot.to_dict() or {}
            owners = [existing[key] for key in OWNER_FIELDS if existing.get(key) is not None]
            if not owners or any(not isinstance(owner, str) or owner != user_id for owner in owners):
                raise WardrobeOwnershipConflict("This item ID is already in use")
            # An upload retry must not reset completed image work, wear history,
            # or edits. Return the original persisted garment without writing.
            return {**existing, "id": item_id, "userId": user_id}
        transaction.create(reference, garment)
        return garment

    return persist(db.transaction())
