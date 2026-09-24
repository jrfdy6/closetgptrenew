"""Owned profile persistence; editable fields never confer account authority."""
from copy import deepcopy
from datetime import datetime, timezone
import math

from firebase_admin import firestore
from src.services.onboarding_state import has_style_profile


class InvalidProfile(ValueError):
    pass


# Older profile screens send their whole readback. Ignore server-owned/unknown
# fields instead of copying them back, including billing, counters and receipts.
SCALAR_FIELDS = frozenset((
    "name", "gender", "bodyType", "skinTone", "fitPreference", "sizePreference",
    "budget", "height", "weight", "topSize", "bottomSize", "shoeSize", "dressSize",
    "chest", "waist", "inseam", "age", "formality", "heightFeetInches",
))
LIST_FIELDS = frozenset((
    "stylePreferences", "preferredBrands", "occasions", "preferredColors",
    "seasonalPreferences",
))
MAP_FIELDS = {
    "preferences": ("style", "colors", "occasions"),
    "measurements": (
        "height", "weight", "bodyType", "skinTone", "heightFeetInches", "topSize",
        "bottomSize", "shoeSize", "dressSize", "jeanWaist", "braSize", "inseam",
        "waist", "chest", "shoulderWidth", "waistWidth", "hipWidth", "armLength",
        "neckCircumference", "thighCircumference", "calfCircumference", "plusSize",
        "adaptiveNeeds", "mobilityConsiderations", "sensoryPreferences",
    ),
    "colorPalette": ("primary", "secondary", "accent", "neutral", "avoid"),
    "stylePersonality": ("classic", "modern", "creative", "minimal", "bold"),
    "materialPreferences": ("preferred", "avoid", "seasonal"),
    "fitPreferences": ("tops", "bottoms", "dresses"),
    "comfortLevel": ("tight", "loose", "structured", "relaxed"),
    "spending_ranges": ("tops", "pants", "shoes", "jackets", "dresses", "accessories",
                        "undergarments", "swimwear"),
}


def _safe_value(value, depth=0):
    if depth > 5:
        raise InvalidProfile("Profile value is too deeply nested")
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        if len(value) > 10000:
            raise InvalidProfile("Profile value is too long")
        return value
    if isinstance(value, (int, float)):
        if abs(value) > 1e15 or not math.isfinite(value):
            raise InvalidProfile("Invalid numeric profile value")
        return value
    if isinstance(value, list) and len(value) <= 100:
        return [_safe_value(item, depth + 1) for item in value]
    if isinstance(value, dict) and len(value) <= 100:
        return {key: _safe_value(item, depth + 1) for key, item in value.items()
                if key not in ("__proto__", "prototype", "constructor")}
    raise InvalidProfile("Invalid profile value")


def editable_updates(body):
    if not isinstance(body, dict) or len(body) > 200:
        raise InvalidProfile("Invalid profile update")
    result = {}
    for key in SCALAR_FIELDS & body.keys():
        value = body[key]
        if isinstance(value, (dict, list, bool)):
            raise InvalidProfile("Invalid profile field")
        if key in ("name", "gender") and value is not None and not isinstance(value, str):
            raise InvalidProfile("Invalid profile field")
        result[key] = _safe_value(value)
    for key in LIST_FIELDS & body.keys():
        value = body[key]
        if value is not None and (not isinstance(value, list) or any(not isinstance(item, str) for item in value)):
            raise InvalidProfile("Invalid profile preferences")
        result[key] = _safe_value(value)
    for key, allowed in MAP_FIELDS.items():
        if key not in body:
            continue
        value = body[key]
        if value is None:
            result[key] = None
            continue
        if not isinstance(value, dict):
            raise InvalidProfile("Invalid profile details")
        selected = {field: _safe_value(value[field]) for field in allowed if field in value}
        if key == "materialPreferences" and isinstance(selected.get("seasonal"), dict):
            selected["seasonal"] = {season: items for season, items in selected["seasonal"].items()
                                    if season in ("spring", "summer", "fall", "winter")}
        result[key] = selected
    return result


def unix_seconds(value):
    if isinstance(value, datetime):
        return math.floor(value.replace(tzinfo=value.tzinfo or timezone.utc).timestamp())
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (float, int)):
        if not math.isfinite(value):
            return None
        return math.floor(value / 1000 if value > 1_000_000_000_000 else value)
    if isinstance(value, dict):
        return unix_seconds(value.get("seconds", value.get("_seconds")))
    if isinstance(value, str):
        try:
            return unix_seconds(float(value))
        except ValueError:
            try:
                return unix_seconds(datetime.fromisoformat(value.replace("Z", "+00:00")))
            except ValueError:
                return None
    return None


def normalize_profile(data, claims):
    result = deepcopy(data)
    uid = claims["uid"]
    result.update(userId=uid, user_id=uid, firebase_uid=uid,
                  email=data.get("email") or claims.get("email") or "",
                  name=data.get("name") or claims.get("name") or claims.get("email") or "")
    created = next((value for value in (unix_seconds(data.get("created_at")),
                                       unix_seconds(data.get("createdAt")),
                                       unix_seconds(claims.get("iat"))) if value is not None), None)
    updated = next((value for value in (unix_seconds(data.get("updated_at")),
                                       unix_seconds(data.get("updatedAt")), created) if value is not None), None)
    if created is not None:
        result["created_at"] = created
    if updated is not None:
        result["updated_at"] = updated
    return result


def _merge(existing, updates):
    result = deepcopy(existing)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def persist_profile(db, claims, body=None, *, now=None):
    """A transaction prevents an absent-profile read from replacing a quiz save."""
    updates = editable_updates(body) if body is not None else None
    now = now or datetime.now(timezone.utc)
    reference = db.collection("users").document(claims["uid"])
    expected_epoch = None

    @firestore.transactional
    def apply(transaction):
        nonlocal expected_epoch
        snapshot = reference.get(transaction=transaction)
        stored = (snapshot.to_dict() or {}) if snapshot.exists else {}
        if snapshot.exists and updates is None:
            return normalize_profile(stored, claims)
        from .app_data_privacy import app_data_write_allowed, data_epoch
        from fastapi import HTTPException
        if not app_data_write_allowed(stored, expected_epoch):
            raise HTTPException(409, 'Your app data is being cleared. Reload before saving.')
        # A retry must not replay a pre-clear form into the newly cleared
        # account after Firestore detects a conflict with the deletion commit.
        if expected_epoch is None:
            expected_epoch = data_epoch(stored)
        profile_updates = deepcopy(updates or {})
        # Both aliases count as legacy completion evidence. Only an already
        # completed stored profile may edit them; a new profile must use the
        # verified quiz submission path. Re-evaluate on every transaction retry.
        if not has_style_profile(stored):
            profile_updates.pop("stylePreferences", None)
            if isinstance(profile_updates.get("preferences"), dict):
                profile_updates["preferences"].pop("style", None)
        result = _merge(stored, profile_updates)
        # The legacy profile PUT queues this work; queue in the same transaction
        # so retries, partial updates and concurrent saves cannot lose the request.
        if updates is not None and "spending_ranges" in updates and result.get("spending_ranges") != stored.get("spending_ranges"):
            result.update(tveRecalcStatus="queued", tveRecalcRequestedAt=math.floor(now.timestamp()))
        # Identity/email and timestamps are server-owned even when echoed by UI.
        result.update(userId=claims["uid"], user_id=claims["uid"], firebase_uid=claims["uid"],
                      email=stored.get("email") or claims.get("email") or "",
                      name=result.get("name") or stored.get("name") or claims.get("name") or claims.get("email") or "",
                      created_at=stored.get("created_at") if stored.get("created_at") is not None
                      else stored.get("createdAt") if stored.get("createdAt") is not None else now,
                      updated_at=now, updatedAt=math.floor(now.timestamp() * 1000))
        transaction.set(reference, result)
        return normalize_profile(result, claims)

    return apply(db.transaction())
