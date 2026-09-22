"""Atomic wear-today events and private retry receipts.

Only the transaction writes: there are deliberately no external analytics, XP,
TVE or preference side effects that could run twice after a lost acknowledgment.
Existing history readers retain their numeric-millisecond date contract.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from firebase_admin import firestore

from ..utils.outfit_admission import has_complete_combination, owns_garment, usable_garment


RECEIPTS_COLLECTION = "outfit_wear_receipts"
IDENTIFIER = re.compile(r"[^/\x00-\x1f\x7f]{1,256}\Z")
KEY = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9_.:-]{0,127}\Z")


class OutfitWearError(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code, self.detail = status_code, detail


def _digest(*values):
    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()


def _valid_id(value):
    return isinstance(value, str) and value == value.strip() and value not in {".", ".."} and bool(IDENTIFIER.fullmatch(value))


def _read(reference, transaction):
    snapshot = reference.get(transaction=transaction)
    return snapshot.to_dict() if snapshot.exists else None


def _count(value):
    if value is None:
        return 0
    if isinstance(value, str) and value.isdecimal():
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise OutfitWearError(409, "Wear history needs to be refreshed before this outfit can be logged.")
    return value


def _timestamp_ms(value):
    if hasattr(value, "timestamp"):
        return int(value.timestamp() * 1000)
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return int(value.timestamp() * 1000)
        except ValueError:
            raise OutfitWearError(409, "Wear history needs to be refreshed.") from None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(value * 1000 if value < 1e12 else value)
    raise OutfitWearError(409, "Wear history needs to be refreshed.")


def _acknowledge(receipt, user_id, outfit_id, outfit, db, transaction):
    if receipt.get("user_id") != user_id or receipt.get("outfit_id") != outfit_id:
        raise OutfitWearError(409, "This wear request was already used for another outfit.")
    response = receipt.get("response")
    if not isinstance(response, dict) or not response.get("event_id"):
        raise OutfitWearError(409, "The saved wear receipt is unavailable. Please refresh.")
    # Keep the original event identity/date, but never roll visible counters
    # backward if another device recorded a later wear before this retry.
    current_garment_counts = {}
    for item_id in response.get("garment_wear_counts", {}):
        garment = _read(db.collection("wardrobe").document(item_id), transaction)
        if garment and owns_garment(garment, user_id):
            current_garment_counts[item_id] = _count(garment.get("wearCount"))
    return {
        **response, "already_recorded": True,
        "event_wear_count": response["wear_count"],
        "event_garment_wear_counts": response["garment_wear_counts"],
        "wear_count": _count(outfit.get("wearCount")),
        "garment_wear_counts": current_garment_counts,
        "last_worn": _timestamp_ms(outfit.get("lastWorn")),
        "last_wear_date": outfit.get("lastWearDate"),
        "last_wear_timezone": outfit.get("lastWearTimezone"),
    }


def mark_legacy_outfit_worn(db, outfit_id, user_id, *, now=None):
    """Keep the deployed empty-body caller safe during API-first rollout.

    Older clients provide neither a stable action ID nor a timezone. Bind their
    operation to owner+outfit+server UTC date, and use that same clock instant in
    the transaction. Same-day retries dedupe; a retry after UTC midnight is a new
    day's action. New clients must send an explicit key to recover the original
    event across dates and a timezone for their local calendar day.
    """
    instant = now or datetime.now(timezone.utc)
    date = instant.astimezone(timezone.utc).date().isoformat()
    key = "legacy-" + _digest(user_id, outfit_id, date)
    return mark_outfit_worn(db, outfit_id, user_id, key, "UTC", now=instant)


def mark_outfit_worn(db, outfit_id, user_id, idempotency_key, timezone_name="UTC", *, now=None):
    """Record one event per owner/outfit/local date, replaying keys across dates.

    The IANA timezone only selects the current calendar day; the client cannot
    backdate the timestamp. Receipt identity is user+key, so reusing a key for a
    different outfit is a conflict. A different key on the same day returns the
    original day receipt and cannot count another wear.
    """
    if not _valid_id(outfit_id) or not _valid_id(user_id):
        raise OutfitWearError(422, "Invalid outfit identifier")
    if not isinstance(idempotency_key, str) or not KEY.fullmatch(idempotency_key):
        raise OutfitWearError(422, "A valid wear request identifier is required")
    try:
        if not isinstance(timezone_name, str) or len(timezone_name) > 100:
            raise ValueError()
        local_timezone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        raise OutfitWearError(422, "A valid timezone is required") from None
    instant = now or datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("Wear clock must be timezone aware")
    wear_date = instant.astimezone(local_timezone).date().isoformat()
    timestamp = int(instant.timestamp() * 1000)
    key_ref = db.collection(RECEIPTS_COLLECTION).document("key-" + _digest(user_id, idempotency_key))
    day_identity = _digest(user_id, outfit_id, wear_date)
    day_ref = db.collection(RECEIPTS_COLLECTION).document("day-" + day_identity)
    history_id = "wear-v1-" + day_identity
    history_ref = db.collection("outfit_history").document(history_id)
    outfit_ref = db.collection("outfits").document(outfit_id)

    @firestore.transactional
    def record(transaction):
        # Read every required document before queueing even the first write.
        key_receipt = _read(key_ref, transaction)
        outfit = _read(outfit_ref, transaction)
        if not outfit or not owns_garment(outfit, user_id) or any(
            outfit.get(key) for key in ("deleted", "isDeleted", "deletedAt", "deleted_at")
        ):
            raise OutfitWearError(404, "Outfit not found")
        if key_receipt:
            return _acknowledge(key_receipt, user_id, outfit_id, outfit, db, transaction)
        day_receipt = _read(day_ref, transaction)
        if day_receipt:
            result = _acknowledge(day_receipt, user_id, outfit_id, outfit, db, transaction)
            transaction.set(key_ref, day_receipt)
            return result

        # A history row cannot substitute for the server-owned receipt.
        if _read(history_ref, transaction) is not None:
            raise OutfitWearError(409, "This wear history entry needs to be refreshed.")
        raw_items = outfit.get("items")
        if not isinstance(raw_items, list) or not 1 <= len(raw_items) <= 20:
            raise OutfitWearError(409, "This saved outfit has no complete set of garments to log.")
        item_ids = [item.get("id") if isinstance(item, dict) else item for item in raw_items]
        if any(not _valid_id(item_id) for item_id in item_ids) or len(set(item_ids)) != len(item_ids):
            raise OutfitWearError(409, "This saved outfit has invalid or repeated garments. Please refresh.")
        garments = []
        for item_id in item_ids:
            reference = db.collection("wardrobe").document(item_id)
            garment = _read(reference, transaction)
            if not garment or not owns_garment(garment, user_id) or not usable_garment(garment) or garment.get("deleted_at"):
                raise OutfitWearError(409, "Some garments in this outfit are no longer available. Please refresh.")
            garments.append((reference, {**garment, "id": item_id}))
        if not has_complete_combination([garment for _, garment in garments]):
            raise OutfitWearError(409, "This saved outfit is missing a top, bottom and shoes, or a one-piece and shoes.")

        outfit_count = _count(outfit.get("wearCount")) + 1
        garment_counts = {garment["id"]: _count(garment.get("wearCount")) + 1 for _, garment in garments}
        result = {
            "success": True, "outfit_id": outfit_id, "event_id": history_id,
            "history_id": history_id, "wear_date": wear_date, "timezone": timezone_name,
            "date_worn": timestamp, "last_worn": timestamp, "wear_count": outfit_count,
            "garment_wear_counts": garment_counts, "already_recorded": False,
            "event_wear_count": outfit_count, "event_garment_wear_counts": garment_counts,
            "last_wear_date": wear_date, "last_wear_timezone": timezone_name,
        }
        receipt = {"schema_version": 1, "user_id": user_id, "outfit_id": outfit_id, "response": result}
        history = {
            "wear_operation_version": 1, "user_id": user_id, "outfit_id": outfit_id,
            "outfit_name": outfit.get("name") or "Saved outfit", "outfit_image": outfit.get("imageUrl") or "",
            "date_worn": timestamp, "wear_date": wear_date, "timezone": timezone_name,
            "occasion": outfit.get("occasion") or "", "mood": outfit.get("mood") or "",
            "weather": outfit.get("weather") if isinstance(outfit.get("weather"), dict) else {},
            "notes": "", "tags": [], "created_at": timestamp, "updated_at": timestamp,
            "items": [{key: garment.get(key, "") for key in ("id", "name", "type", "color", "brand", "imageUrl")}
                      for _, garment in garments],
        }
        transaction.update(outfit_ref, {
            "wearCount": outfit_count, "lastWorn": timestamp, "updatedAt": timestamp,
            "lastWearDate": wear_date, "lastWearTimezone": timezone_name,
        })
        for reference, garment in garments:
            transaction.update(reference, {
                "wearCount": garment_counts[garment["id"]], "lastWorn": timestamp, "updatedAt": timestamp,
            })
        transaction.set(history_ref, history)
        transaction.set(day_ref, receipt)
        transaction.set(key_ref, receipt)
        return result

    return record(db.transaction())
