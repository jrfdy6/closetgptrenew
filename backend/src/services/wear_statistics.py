"""Read-only weekly wear counts shared by dashboard and outfit statistics.

Calendar weeks begin Monday in the saved profile's IANA timezone. Historical
wear events remain authoritative after an outfit is removed or a wear is undone.
"""
from collections.abc import Mapping
from datetime import date, datetime, time, timedelta, timezone
import math
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


UTC = timezone.utc
_NUMERIC = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z")
_DATE_ONLY = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


def _zone(value, fallback="UTC"):
    if isinstance(value, str):
        try:
            return ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return ZoneInfo(fallback)


def _profile_zone(user):
    location = user.get("location_data") if isinstance(user, Mapping) else None
    return _zone(location.get("timezone") if isinstance(location, Mapping) else None)


def _now(now):
    instant = now if now is not None else datetime.now(UTC)
    if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("Wear statistics clock must be timezone aware")
    return instant.astimezone(UTC)


def week_bounds(user, now=None):
    """Return [Monday midnight, next Monday midnight) in UTC and its IANA zone."""
    zone = _profile_zone(user)
    local_today = _now(now).astimezone(zone).date()
    monday = local_today - timedelta(days=local_today.weekday())
    # Construct both local midnights, rather than adding 168 hours in UTC: the
    # week containing a daylight-saving change can be 167 or 169 hours long.
    start = datetime.combine(monday, time.min, zone).astimezone(UTC)
    end = datetime.combine(monday + timedelta(days=7), time.min, zone).astimezone(UTC)
    return start, end, zone.key


def parse_wear_timestamp(value, *, date_timezone="UTC"):
    """Parse persisted timestamp formats without credentials or host-local time.

    Date-only values represent a local calendar date. Legacy naive datetimes
    retain the old reader's UTC interpretation. Invalid values return None.
    """
    try:
        if isinstance(value, datetime):
            return value.replace(tzinfo=value.tzinfo or UTC).astimezone(UTC)
        if isinstance(value, date):
            return datetime.combine(value, time.min, _zone(date_timezone)).astimezone(UTC)
        if type(value) in (int, float):
            if not math.isfinite(value):
                return None
            seconds = value / 1000 if abs(value) >= 1e12 else value
            return datetime.fromtimestamp(seconds, UTC)
        if isinstance(value, str):
            cleaned = value.strip()
            if _DATE_ONLY.fullmatch(cleaned):
                return datetime.combine(date.fromisoformat(cleaned), time.min, _zone(date_timezone)).astimezone(UTC)
            if _NUMERIC.fullmatch(cleaned):
                return parse_wear_timestamp(float(cleaned), date_timezone=date_timezone)
            parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
            return parsed.replace(tzinfo=parsed.tzinfo or UTC).astimezone(UTC)
        if isinstance(value, Mapping):
            seconds = value.get("seconds", value.get("_seconds"))
            nanos = value.get("nanoseconds", value.get("_nanoseconds", 0))
            if type(seconds) in (int, float) and type(nanos) in (int, float):
                if math.isfinite(seconds) and math.isfinite(nanos) and 0 <= nanos < 1e9:
                    return datetime.fromtimestamp(seconds + nanos / 1e9, UTC)
            return None
        timestamp = getattr(value, "timestamp", None)
        if callable(timestamp):
            seconds = timestamp()
            if type(seconds) in (int, float) and math.isfinite(seconds):
                return datetime.fromtimestamp(seconds, UTC)
    except (ValueError, TypeError, OverflowError, OSError):
        return None
    return None


def _owned(value, user_id):
    if not isinstance(value, Mapping):
        return False
    owners = [value[key] for key in ("user_id", "userId") if value.get(key) is not None]
    return bool(owners) and all(owner == user_id for owner in owners)


def _owned_records(db, collection, user_id):
    from google.cloud.firestore_v1.base_query import FieldFilter

    seen = set()
    for field in ("user_id", "userId"):
        query = db.collection(collection).where(filter=FieldFilter(field, "==", user_id))
        for snapshot in query.stream():
            if snapshot.id in seen:
                continue
            seen.add(snapshot.id)
            record = snapshot.to_dict()
            if _owned(record, user_id):
                yield record


def _history_timestamp(event, profile_timezone):
    managed = event.get("wear_operation_version") is not None or "wear_date" in event
    event_timezone = _zone(event.get("timezone"), profile_timezone).key
    if managed:
        # Never replace an invalid managed wear instant with its later logging
        # time: doing so could move a backdated wear into the current week.
        if event.get("date_worn") is not None:
            return parse_wear_timestamp(event["date_worn"], date_timezone=event_timezone)
        return parse_wear_timestamp(event.get("wear_date"), date_timezone=event_timezone)
    for field in ("date_worn", "date", "createdAt", "created_at"):
        parsed = parse_wear_timestamp(event.get(field), date_timezone=event_timezone)
        if parsed is not None:
            return parsed
    return None


def weekly_wear_summary(db, uid, now=None):
    """Count owned events; fall back to active outfits only with no history.

    Database errors propagate to the caller instead of turning an unavailable
    count into zero. The reader performs no writes and does not query an outfit
    for an existing history event, preserving wear snapshots after deletion.
    """
    instant = _now(now)
    user_doc = db.collection("users").document(uid).get()
    user = user_doc.to_dict() if user_doc.exists else {}
    start, end, zone = week_bounds(user, instant)

    def in_week(worn_at):
        return worn_at is not None and start <= worn_at < end and worn_at <= instant

    count, history_count = 0, 0
    for event in _owned_records(db, "outfit_history", uid):
        history_count += 1
        if not event.get("undone") and in_week(_history_timestamp(event, zone)):
            count += 1

    source = "outfit_history_individual_events"
    if history_count == 0:
        source = "lastWorn_fallback"
        for outfit in _owned_records(db, "outfits", uid):
            if any(outfit.get(field) for field in ("deleted", "isDeleted", "deletedAt", "deleted_at")):
                continue
            if in_week(parse_wear_timestamp(outfit.get("lastWorn"), date_timezone=zone)):
                count += 1

    return {
        "success": True,
        "user_id": uid,
        "outfits_worn_this_week": count,
        "source": source,
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "timezone": zone,
        "calculated_at": instant.isoformat(),
    }
