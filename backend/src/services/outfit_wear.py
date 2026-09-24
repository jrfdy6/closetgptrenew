"""Atomic wear events, base rewards and retry receipts.

Physical date and recording-day engagement are separate. Challenges project
from a durable outbox; retries cannot repeat counts, TVE or earned rewards.
"""
import hashlib
import json
import re
from datetime import datetime, timezone, date, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from firebase_admin import firestore

from .app_data_privacy import require_app_data_writable, AppDataDeletionError
from .reward_ledger import WriteEpochFence
from .wear_rewards import calculate_wear_reward, reward_timezone, tve_delta

from ..utils.outfit_admission import has_complete_combination, owns_garment, usable_garment


JOBS_COLLECTION = "wear_projection_jobs"
REWARDS_COLLECTION = "reward_ledger"

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
    history = _read(db.collection("outfit_history").document(response["event_id"]), transaction) or {}
    current_garment_counts = {}
    for item_id in response.get("garment_wear_counts", {}):
        garment = _read(db.collection("wardrobe").document(item_id), transaction)
        if garment and owns_garment(garment, user_id):
            current_garment_counts[item_id] = _count(garment.get("wearCount"))
    return {
        **response, "already_recorded": True, "undone": bool(history.get("undone")), "event_revision": history.get("event_revision", 1), "projection_status": history.get("projection_status", "pending"), "rewards": {**response.get("rewards", {}), "xp_awarded": 0, "tokens_awarded": 0, "level_up": False},
        "event_wear_count": response["wear_count"],
        "event_garment_wear_counts": response["garment_wear_counts"],
        "wear_count": _count(outfit.get("wearCount")),
        "garment_wear_counts": current_garment_counts,
        "last_worn": _timestamp_ms(outfit["lastWorn"]) if outfit.get("lastWorn") else None,
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


def mark_outfit_worn(db, outfit_id, user_id, idempotency_key, timezone_name="UTC", *, now=None, wear_date=None, metadata=None, source="saved_outfit", suggestion_id=None):
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
    today = instant.astimezone(local_timezone).date()
    requested_date = wear_date
    try:
        calendar_date = date.fromisoformat(wear_date) if wear_date is not None else today
        if calendar_date > today:
            raise ValueError()
    except (ValueError, TypeError):
        raise OutfitWearError(422, "Wear date must be a valid past or present YYYY-MM-DD date") from None
    wear_date = calendar_date.isoformat()
    worn_timestamp = int(datetime.combine(calendar_date, time(12), local_timezone).timestamp() * 1000) if requested_date and calendar_date != today else int(instant.timestamp() * 1000)
    metadata = validate_history_metadata(metadata or {})
    timestamp = int(instant.timestamp() * 1000)
    key_ref = db.collection(RECEIPTS_COLLECTION).document("key-" + _digest(user_id, idempotency_key))
    day_identity = _digest(user_id, outfit_id, wear_date)
    day_ref = db.collection(RECEIPTS_COLLECTION).document("day-" + day_identity)
    history_id = "wear-v1-" + day_identity
    history_ref = db.collection("outfit_history").document(history_id)
    outfit_ref = db.collection("outfits").document(outfit_id)
    user_ref = db.collection("users").document(user_id)
    reward_ref = db.collection(REWARDS_COLLECTION).document(history_id)
    suggestion_ref = db.collection("daily_outfit_suggestions").document(suggestion_id) if suggestion_id else None

    epoch_fence = WriteEpochFence(db, user_id)
    @firestore.transactional
    def record(transaction):
        try:
            epoch = epoch_fence.check(transaction)
        except AppDataDeletionError as exc:
            raise OutfitWearError(exc.status_code, exc.detail) from None
        # Read every required document before queueing even the first write.
        key_receipt = _read(key_ref, transaction)
        outfit = _read(outfit_ref, transaction)
        suggestion = _read(suggestion_ref, transaction) if suggestion_ref else None
        if suggestion_ref:
            if not suggestion or suggestion.get("user_id") != user_id:
                raise OutfitWearError(404, "Suggestion not found")
            if not outfit:
                outfit = {**suggestion.get("outfit_data", {}), "user_id": user_id, "wearCount": 0}
        if not outfit or not owns_garment(outfit, user_id) or any(
            outfit.get(key) for key in ("deleted", "isDeleted", "deletedAt", "deleted_at")
        ):
            raise OutfitWearError(404, "Outfit not found")
        if key_receipt:
            return _acknowledge(key_receipt, user_id, outfit_id, outfit, db, transaction)
        day_receipt = _read(day_ref, transaction)
        history_existing = _read(history_ref, transaction)
        reactivating = bool(day_receipt and history_existing and history_existing.get("undone"))
        if day_receipt and not reactivating:
            result = _acknowledge(day_receipt, user_id, outfit_id, outfit, db, transaction)
            transaction.set(key_ref, day_receipt)
            return result

        # A history row cannot substitute for the server-owned receipt.
        if history_existing is not None and not reactivating:
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

        user = _read(user_ref, transaction)
        if user is None:
            raise OutfitWearError(409, "Your profile must be saved before logging an outfit")
        reward_zone = reward_timezone(user, timezone_name)
        engagement_day = instant.astimezone(ZoneInfo(reward_zone)).date().isoformat()
        daily_ref = db.collection("wear_engagement_days").document(_digest(user_id, engagement_day))
        daily = _read(daily_ref, transaction) or {}
        existing_reward = _read(reward_ref, transaction)
        user_patch, rewards = calculate_wear_reward(user, engagement_day, daily, timestamp) if not existing_reward and not reactivating else ({}, (existing_reward or {}).get("rewards", {}))
        wardrobe_for_tve = []
        if not reactivating and any(g.get("value_per_wear") is None for _, g in garments):
            from google.cloud.firestore_v1 import FieldFilter
            wardrobe_for_tve = [snapshot.to_dict() for snapshot in db.collection("wardrobe").where(filter=FieldFilter("userId", "==", user_id)).stream(transaction=transaction)]
        deltas = (history_existing or {}).get("tve_deltas", {}) if reactivating else {g["id"]: tve_delta(g, user, wardrobe_for_tve) for _, g in garments}
        revision = int((history_existing or {}).get("event_revision", 0)) + 1
        outfit_count = _count(outfit.get("wearCount")) + 1
        garment_counts = {garment["id"]: _count(garment.get("wearCount")) + 1 for _, garment in garments}
        result = {
            "success": True, "outfit_id": outfit_id, "event_id": history_id,
            "history_id": history_id, "wear_date": wear_date, "timezone": timezone_name,
            "date_worn": worn_timestamp, "last_worn": max(worn_timestamp, _timestamp_ms(outfit["lastWorn"]) if outfit.get("lastWorn") else 0), "wear_count": outfit_count,
            "garment_wear_counts": garment_counts, "already_recorded": False,
            "event_wear_count": outfit_count, "event_garment_wear_counts": garment_counts,
            "last_wear_date": wear_date if not outfit.get("lastWorn") or worn_timestamp >= _timestamp_ms(outfit["lastWorn"]) else outfit.get("lastWearDate"), "last_wear_timezone": timezone_name if not outfit.get("lastWorn") or worn_timestamp >= _timestamp_ms(outfit["lastWorn"]) else outfit.get("lastWearTimezone"),
            "rewards": rewards if not reactivating else {**rewards, "xp_awarded": 0, "tokens_awarded": 0, "level_up": False}, "projection_status": "pending", "event_revision": revision, "undone": False,
        }
        receipt = {"schema_version": 2, "user_id": user_id, "outfit_id": outfit_id, "response": result}
        history = {
            "wear_operation_version": 2, "app_data_epoch": epoch, "garment_counts_before": {g["id"]: _count(g.get("wearCount")) for _, g in garments}, "garment_counts_after": garment_counts, "event_revision": revision, "undone": False, "projection_status": "pending", "source": source, "suggestion_id": suggestion_id, "item_ids": item_ids, "tve_deltas": deltas, "recorded_at": timestamp, "engagement_day": engagement_day, "reward_timezone": reward_zone, "user_id": user_id, "outfit_id": outfit_id,
            "outfit_name": outfit.get("name") or "Saved outfit", "style": outfit.get("style", ""), "base_rewards": rewards, "outfit_image": outfit.get("imageUrl") or "",
            "date_worn": worn_timestamp, "wear_date": wear_date, "timezone": timezone_name,
            "occasion": outfit.get("occasion") or "", "mood": outfit.get("mood") or "",
            "weather": outfit.get("weather") if isinstance(outfit.get("weather"), dict) else {},
            "notes": "", "tags": [], "created_at": (history_existing or {}).get("created_at", timestamp), "updated_at": timestamp,
            "items": [{key: garment.get(key, "") for key in ("id", "name", "type", "color", "brand", "imageUrl", "pattern", "texture", "material", "season", "isFavorite", "estimated_cost", "wearCount", "lastWorn")}
                      for _, garment in garments],
        }
        history.update(metadata)
        outfit_patch = {"wearCount": outfit_count, "lastWorn": result["last_worn"], "updatedAt": timestamp, "lastWearDate": result["last_wear_date"], "lastWearTimezone": result["last_wear_timezone"], "wear_baseline_last_worn": outfit.get("wear_baseline_last_worn", outfit.get("lastWorn"))}
        if suggestion_ref:
            transaction.update(suggestion_ref, {"is_worn": True, "worn_at": worn_timestamp, "wear_event_id": history_id, "updated_at": timestamp})
        if suggestion_ref and not _valid_id(outfit.get("id")) and outfit_id.startswith("suggestion-"):
            transaction.set(outfit_ref, {**outfit, **outfit_patch, "id": outfit_id, "source": "daily_suggestion"})
        else:
            transaction.update(outfit_ref, outfit_patch)
        if user_patch:
            transaction.update(user_ref, user_patch)
            transaction.set(daily_ref, {"user_id": user_id, "day": engagement_day, "timezone": reward_zone, "rewarded": True})
            transaction.set(reward_ref, {"user_id": user_id, "event_id": history_id, "kind": "wear", "rewards": rewards, "created_at": timestamp})
        for reference, garment in garments:
            transaction.update(reference, {
                "wearCount": garment_counts[garment["id"]], "lastWorn": max(worn_timestamp, _timestamp_ms(garment["lastWorn"]) if garment.get("lastWorn") else 0), "updatedAt": timestamp,
                "value_per_wear": garment.get("value_per_wear", deltas.get(garment["id"], 0)), "wear_baseline_last_worn": garment.get("wear_baseline_last_worn", garment.get("lastWorn")), "current_tve": round(float(garment.get("current_tve", 0)) + deltas.get(garment["id"], 0), 6),
            })
        transaction.set(history_ref, history)
        transaction.set(db.collection(JOBS_COLLECTION).document(history_id + ":" + str(revision)), {"event_id": history_id, "user_id": user_id, "app_data_epoch": epoch, "revision": revision, "status": "pending", "attempts": 0, "available_at": timestamp, "created_at": timestamp, "cursor": None})
        transaction.set(day_ref, receipt)
        transaction.set(key_ref, receipt)
        return result

    return record(db.transaction())


def validate_history_metadata(updates):
    allowed = {"occasion", "mood", "weather", "notes", "tags"}
    result = {}
    for key, value in updates.items():
        if key not in allowed:
            continue
        if key in {"occasion", "mood", "notes"} and (not isinstance(value, str) or len(value) > (4000 if key == "notes" else 200)):
            raise OutfitWearError(422, "Invalid history metadata")
        if key == "weather" and (not isinstance(value, dict) or len(json.dumps(value)) > 4000):
            raise OutfitWearError(422, "Invalid weather metadata")
        if key == "tags" and (not isinstance(value, list) or len(value) > 30 or any(not isinstance(t, str) or len(t) > 100 for t in value)):
            raise OutfitWearError(422, "Invalid history tags")
        result[key] = value
    return result


def update_wear_metadata(db, user_id, event_id, updates):
    patch = validate_history_metadata(updates)
    reference = db.collection("outfit_history").document(event_id)
    epoch_fence = WriteEpochFence(db, user_id)
    @firestore.transactional
    def update(transaction):
        try:
            epoch_fence.check(transaction)
        except AppDataDeletionError as exc:
            raise OutfitWearError(exc.status_code, exc.detail) from None
        event = _read(reference, transaction)
        if not event or event.get("user_id") != user_id or event.get("undone"):
            raise OutfitWearError(404, "History entry not found")
        transaction.update(reference, {**patch, "updated_at": int(datetime.now(timezone.utc).timestamp() * 1000)})
        return {"success": True, "event_id": event_id}
    return update(db.transaction())


def _previous_worn(db, transaction, user_id, event_id, *, item_id=None, outfit_id=None, baseline=None):
    from google.cloud.firestore_v1 import FieldFilter
    query = db.collection("outfit_history").where(filter=FieldFilter("user_id", "==", user_id))
    if not item_id:
        query = query.where(filter=FieldFilter("outfit_id", "==", outfit_id))
    # Read active managed events in newest-first pages; tombstones do not count.
    query = query.order_by("date_worn", direction="DESCENDING")
    latest = _timestamp_ms(baseline) if baseline else 0
    for snapshot in query.stream(transaction=transaction):
        event = snapshot.to_dict()
        ids = event.get("item_ids") or [item.get("id") if isinstance(item, dict) else item for item in event.get("items", [])]
        if item_id and item_id not in ids:
            continue
        event_time = _timestamp_ms(event["date_worn"])
        if snapshot.id == event_id or event.get("undone"):
            if event_time == latest:
                latest = 0
            continue
        latest = max(latest, event_time)
        break
    return latest or None


def undo_wear(db, user_id, event_id, *, now=None):
    """Keep earned rewards; reverse physical contributions exactly once."""
    reference = db.collection("outfit_history").document(event_id)
    timestamp = int((now or datetime.now(timezone.utc)).timestamp() * 1000)
    epoch_fence = WriteEpochFence(db, user_id)
    @firestore.transactional
    def undo(transaction):
        try:
            epoch = epoch_fence.check(transaction)
        except AppDataDeletionError as exc:
            raise OutfitWearError(exc.status_code, exc.detail) from None
        event = _read(reference, transaction)
        if not event or event.get("user_id") != user_id:
            raise OutfitWearError(404, "History entry not found")
        if event.get("undone"):
            return {"success": True, "already_recorded": True, "undone": True, "event_id": event_id, "outfit_id": event.get("outfit_id")}
        if not event.get("wear_operation_version"):
            # Legacy rows carry no contribution receipt. Preserve legacy semantics;
            # never guess historical XP, TVE or counter deltas.
            transaction.update(reference, {"undone": True, "updated_at": timestamp})
            return {"success": True, "undone": True, "event_id": event_id, "outfit_id": event.get("outfit_id")}
        outfit_ref = db.collection("outfits").document(event["outfit_id"])
        outfit = _read(outfit_ref, transaction)
        previous_outfit = _previous_worn(db, transaction, user_id, event_id, outfit_id=event["outfit_id"], baseline=(outfit or {}).get("wear_baseline_last_worn"))
        garments = []
        for item in event.get("items", []):
            garment_ref = db.collection("wardrobe").document(item["id"])
            garment = _read(garment_ref, transaction)
            if garment and owns_garment(garment, user_id):
                previous = _previous_worn(db, transaction, user_id, event_id, item_id=item["id"], baseline=garment.get("wear_baseline_last_worn"))
                garments.append((garment_ref, garment, previous))
        suggestion_ref = db.collection("daily_outfit_suggestions").document(event["suggestion_id"]) if event.get("suggestion_id") else None
        suggestion = _read(suggestion_ref, transaction) if suggestion_ref else None
        revision = int(event.get("event_revision", 1)) + 1
        if outfit and owns_garment(outfit, user_id):
            zone = ZoneInfo(event.get("timezone") or "UTC")
            transaction.update(outfit_ref, {"wearCount": max(0, _count(outfit.get("wearCount")) - 1), "lastWorn": previous_outfit, "lastWearDate": datetime.fromtimestamp(previous_outfit / 1000, zone).date().isoformat() if previous_outfit else None, "lastWearTimezone": str(zone), "updatedAt": timestamp})
        for garment_ref, garment, previous in garments:
            transaction.update(garment_ref, {"wearCount": max(0, _count(garment.get("wearCount")) - 1), "lastWorn": previous, "current_tve": max(0, round(float(garment.get("current_tve", 0)) - event.get("tve_deltas", {}).get(garment_ref.id, 0), 6)), "updatedAt": timestamp})
        if suggestion and suggestion.get("wear_event_id") == event_id:
            transaction.update(suggestion_ref, {"is_worn": False, "updated_at": timestamp})
        transaction.update(reference, {"undone": True, "event_revision": revision, "projection_status": "pending", "updated_at": timestamp})
        transaction.set(db.collection(JOBS_COLLECTION).document(event_id + ":" + str(revision)), {"event_id": event_id, "user_id": user_id, "app_data_epoch": epoch, "revision": revision, "status": "pending", "attempts": 0, "available_at": timestamp, "created_at": timestamp, "cursor": None})
        return {"success": True, "undone": True, "event_id": event_id, "outfit_id": event.get("outfit_id"), "event_revision": revision, "projection_status": "pending", "rewards_retained": True}
    return undo(db.transaction())
