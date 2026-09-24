"""Leased, resumable challenge projection. Core wear succeeds independently.

A per-event revision receipt accompanies every challenge update in its same
transaction. Retrying after a worker crash is harmless. No provider calls.
"""
from datetime import datetime, timedelta, timezone, date
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from .app_data_privacy import app_data_write_allowed
from .reward_ledger import read, key_for, reward_patch, WriteEpochFence
from .wear_rewards import TOKEN_MULTIPLIERS
from ..custom_types.gamification import CHALLENGE_CATALOG

PAGE_SIZE = 50
LEASE_MS = 60_000


def milliseconds():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def claim(db, job_id, worker_id, now=None):
    now = now or milliseconds()
    ref = db.collection("wear_projection_jobs").document(job_id)
    @firestore.transactional
    def acquire(transaction):
        job = read(ref, transaction)
        if not job or job.get("status") in {"complete", "superseded"} or job.get("available_at", 0) > now or (job.get("lease_until", 0) > now and job.get("lease_owner") != worker_id):
            return None
        job = {**job, "lease_owner": worker_id, "lease_until": now + LEASE_MS, "fence": int(job.get("fence", 0)) + 1, "status": "processing"}
        transaction.update(ref, job)
        return job
    return acquire(db.transaction())


def finish_page(db, job_id, job, cursor, done=False, error=False):
    ref = db.collection("wear_projection_jobs").document(job_id)
    event_ref = db.collection("outfit_history").document(job["event_id"])
    @firestore.transactional
    def save(transaction):
        current = read(ref, transaction)
        event = read(event_ref, transaction)
        if not current or current.get("fence") != job["fence"] or current.get("lease_owner") != job["lease_owner"]:
            return False
        attempts = int(current.get("attempts", 0)) + int(error)
        delay = [5, 30, 120, 600][attempts - 1] if error and attempts <= 4 else 3600 if error else 0
        superseded = not event or event.get("event_revision", 1) != job["revision"] or event.get("app_data_epoch", 0) != job.get("app_data_epoch", 0)
        status = "superseded" if superseded else "pending" if error or not done else "complete"
        transaction.update(ref, {"status": status, "cursor": cursor, "attempts": attempts, "available_at": milliseconds() + delay * 1000, "lease_until": 0, "last_error": "projection_failed" if error else None})
        if event and status == "complete":
            transaction.update(event_ref, {"projection_status": "complete"})
        return True
    return save(db.transaction())


def _ms(value):
    if isinstance(value, (float, int)):
        return int(value)
    if hasattr(value, "timestamp"):
        return int(value.timestamp() * 1000)
    if isinstance(value, str):
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=timezone.utc).timestamp() * 1000)
    return 0


def event_contribution(event, challenge, definition):
    """Return contribution keys. Distinct keys make diversity counts reversible."""
    if event.get("undone"):
        return []
    recorded = event.get("recorded_at", event.get("created_at", 0))
    if recorded < _ms(challenge.get("started_at")) or (challenge.get("expires_at") and recorded >= _ms(challenge["expires_at"])):
        return []
    rules = definition.rules
    items = event.get("items", [])
    ids = event.get("item_ids", [item["id"] for item in items])
    if definition.id == "annual_wardrobe_master":
        day = date.fromisoformat(event["wear_date"])
        return [(day - timedelta(days=day.weekday())).isoformat()]
    selected = set(challenge.get("items", []))
    if selected:
        return list(selected.intersection(ids))
    # Non-wear catalog challenges are processed by their own action.
    if any(key in rules for key in ("ratings_required", "ratings_days", "pulls_required", "rarity_required", "target_role", "token_balance_required", "target_level", "badges_required")) or definition.id in {"cold_start_quest", "wardrobe_builder", "wardrobe_curator"}:
        return []
    if rules.get("first_log_today") and not (event.get("base_rewards") or {}).get("is_first_log_today"):
        return []
    if "styles_required" in rules:
        return [event["style"]] if event.get("style") else []
    if "formality_levels_required" in rules:
        return [event["occasion"]] if event.get("occasion") else []
    if "contexts_required" in rules:
        return [event["occasion"] + ":" + str((event.get("weather") or {}).get("condition", ""))] if event.get("occasion") else []
    if any(key in rules for key in ("never_worn", "days_dormant_min", "favorite_only", "target_wears", "max_cpw")):
        matched = []
        for item in items:
            before = event.get("garment_counts_before", {}).get(item["id"], item.get("wearCount", 0) or 0)
            after = event.get("garment_counts_after", {}).get(item["id"], before + 1)
            if rules.get("never_worn") and before != 0:
                continue
            if rules.get("favorite_only") and not item.get("isFavorite"):
                continue
            if "days_dormant_min" in rules and (not item.get("lastWorn") or recorded - _ms(item["lastWorn"]) < rules["days_dormant_min"] * 86400000):
                continue
            if "target_wears" in rules and after < rules["target_wears"]:
                continue
            if "max_cpw" in rules and (not isinstance(item.get("estimated_cost"), (float, int)) or item["estimated_cost"] / max(after, 1) > rules["max_cpw"]):
                continue
            matched.append(item["id"])
        return matched
    patterns = {str(item.get("pattern") or "solid").lower() for item in items}
    if rules.get("pattern_mixing") and len(patterns - {"solid", "plain", "none"}) < 2:
        return []
    if rules.get("no_patterns") and not patterns.issubset({"solid", "plain", "none"}):
        return []
    if rules.get("texture_mixing") and len({str(item.get("texture") or item.get("material") or "").lower() for item in items} - {""}) < 2:
        return []
    if rules.get("seasonal") and not event.get("season"):
        return []
    if rules.get("themed") and not event.get("theme"):
        return []
    if rules.get("color_intensity") == "bold" and not any(str(item.get("color", "")).lower() in {"red", "orange", "yellow", "purple", "hot pink", "fuchsia", "lime", "turquoise"} for item in items):
        return []
    if "time_limit_hours" in rules and recorded - _ms(challenge.get("started_at")) > rules["time_limit_hours"] * 3600000:
        return []
    if "occasions_required" in rules:
        return [event["occasion"]] if event.get("occasion") else []
    if "moods_required" in rules:
        return [event["mood"]] if event.get("mood") else []
    if "weather_conditions_required" in rules:
        condition = (event.get("weather") or {}).get("condition")
        return [str(condition)] if condition else []
    if "categories_required" in rules:
        return list({item.get("type") for item in items if item.get("type")})
    if "unique_colors_required" in rules:
        return list({str(item.get("color")).lower() for item in items if item.get("color")})
    if rules.get("weekend_only") or "weekend_days" in rules:
        if date.fromisoformat(event["wear_date"]).weekday() < 5:
            return []
    if "days_required" in rules or "streak_days" in rules or "weekend_days" in rules:
        return [event["wear_date"]]
    if "color_rule" in rules:
        colors = {str(item.get("color", "")).lower() for item in items} - {""}
        rule = rules["color_rule"]
        if rule == "monochrome" and len(colors) != 1:
            return []
        if rule == "neutral" and not colors.issubset({"white", "black", "gray", "grey", "beige", "brown", "navy", "cream", "tan"}):
            return []
        if rule == "complementary" and not any(pair.issubset(colors) for pair in ({"red", "green"}, {"blue", "orange"}, {"yellow", "purple"})):
            return []
    # Only explicit outfit-count rules are counted generically: unknown item/
    # context rules must not award a challenge by guessing.
    if "outfits_required" in rules or rules.get("first_log_today"):
        return [event.get("outfit_id", "") if rules.get("unique_outfits") else event["event_id"]]
    return []


def _target(definition):
    rules = definition.rules
    for key in ("outfits_required", "items_required", "occasions_required", "weather_conditions_required", "moods_required", "categories_required", "unique_colors_required", "days_required", "streak_days", "weekend_days", "styles_required", "formality_levels_required", "contexts_required"):
        if key in rules:
            return int(rules[key])
    return 1


def project_instance(db, event_id, revision, instance_ref, lease=None):
    event_ref = db.collection("outfit_history").document(event_id)
    receipt_ref = db.collection("wear_projection_receipts").document(key_for(event_id, instance_ref.path))
    @firestore.transactional
    def apply(transaction):
        if lease:
            job_id, expected = lease
            current_job = read(db.collection("wear_projection_jobs").document(job_id), transaction)
            if not current_job or current_job.get("fence") != expected["fence"] or current_job.get("lease_owner") != expected["lease_owner"]:
                raise RuntimeError("Projection lease changed")
        event = read(event_ref, transaction)
        if event and lease and event.get("app_data_epoch", 0) != current_job.get("app_data_epoch", 0):
            return False
        instance = read(instance_ref, transaction)
        receipt = read(receipt_ref, transaction) or {}
        if not event or event.get("event_revision", 1) != revision or not instance or receipt.get("revision", 0) >= revision:
            return False
        uid = event["user_id"]
        if instance.get("user_id") != uid:
            return False
        definition = CHALLENGE_CATALOG.get(instance.get("challenge_id"))
        if not definition:
            return False
        user_ref = db.collection("users").document(uid)
        user = read(user_ref, transaction)
        completion_ref = db.collection("reward_ledger").document(key_for(uid, "challenge", instance_ref.path, str(instance.get("started_at"))))
        prior_completion = read(completion_ref, transaction)
        if not user or not app_data_write_allowed(user, event.get("app_data_epoch", 0)):
            return False
        if instance.get("status") in {"completed", "expired", "failed"}:
            transaction.set(receipt_ref, {"user_id": uid, "event_id": event_id, "revision": revision, "keys": []})
            return True
        event = {**event, "event_id": event_id}
        keys = event_contribution(event, instance, definition)
        old_keys = receipt.get("keys", [])
        counts = dict(instance.get("wear_contributions") or {})
        legacy_progress = instance.get("progress", 0)
        annual_baseline = legacy_progress.get("weeks_completed", 0) if isinstance(legacy_progress, dict) else 0
        if definition.id == "annual_wardrobe_master" and "wear_contributions" not in instance and isinstance(legacy_progress, dict) and legacy_progress.get("current_week_start"):
            old_week = str(legacy_progress["current_week_start"])[:10]
            counts[key_for(old_week)] = int(legacy_progress.get("current_week_outfits", 0))
        # Encoded keys cannot introduce nested field paths and are bounded by
        # challenge expiry/targets rather than number of raw outfit events.
        for key in old_keys:
            digest = key_for(key)
            counts[digest] = max(0, counts.get(digest, 0) - 1)
        for key in keys:
            digest = key_for(key)
            counts[digest] = counts.get(digest, 0) + 1
        counts = {key: count for key, count in counts.items() if count}
        annual = definition.id == "annual_wardrobe_master"
        progress = sum(count >= definition.rules.get("outfits_per_week", 5) for count in counts.values()) if annual else len(counts)
        baseline = int(instance.get("wear_progress_baseline", instance.get("progress", 0) if isinstance(instance.get("progress"), int) else annual_baseline))
        target = int(definition.rules.get("weeks_required", 52)) if annual else _target(definition)
        if definition.rules.get("consecutive") or "streak_days" in definition.rules:
            previous_dates = dict(instance.get("wear_day_values") or {})
            for value in keys:
                previous_dates[key_for(value)] = value
            dates = sorted(date.fromisoformat(value) for key, value in previous_dates.items() if counts.get(key, 0))
            longest, length, previous = 0, 0, None
            for current in dates:
                length = length + 1 if previous and current == previous + timedelta(days=1) else 1
                longest = max(longest, length)
                previous = current
            progress = longest
        else:
            previous_dates = instance.get("wear_day_values", {})
        completed = progress + baseline >= target
        from zoneinfo import ZoneInfo
        today = datetime.now(ZoneInfo(event.get("timezone") or "UTC")).date()
        this_week = (today - timedelta(days=today.weekday())).isoformat()
        patch = {"wear_day_values": previous_dates, "wear_contributions": counts, "wear_progress_baseline": baseline, "progress": {"weeks_completed": progress + baseline, "total_outfits": sum(counts.values()), "current_week_outfits": counts.get(key_for(this_week), 0), "current_week_start": this_week} if annual else progress + baseline, "target": target}
        if completed:
            patch.update({"status": "completed", "completed_at": datetime.now(timezone.utc)})
            if not prior_completion and baseline < target:
                reward = definition.rewards
                badge = (instance.get("metadata") or {}).get("badge_id", reward.get("badge"))
                tokens = int(reward.get("tokens", reward.get("xp", 0)) * TOKEN_MULTIPLIERS.get((user.get("role") or {}).get("current_role", "starter"), 1))
                user_patch, result = reward_patch(user, xp=reward.get("xp", 0), tokens=tokens, badge=badge, timestamp=milliseconds())
                transaction.update(user_ref, user_patch)
                transaction.set(completion_ref, {"user_id": uid, "kind": "challenge", "result": result, "event_id": event_id, "created_at": milliseconds()})
            completed_ref = db.collection("user_challenges").document(uid).collection("completed").document(key_for(instance_ref.path, str(instance.get("started_at"))))
            transaction.set(completed_ref, {**instance, **patch})
        transaction.update(instance_ref, patch)
        transaction.set(receipt_ref, {"user_id": uid, "event_id": event_id, "revision": revision, "keys": keys})
        return True
    return apply(db.transaction())


def project_milestones(db, event_id, revision, expected_epoch=None):
    event_ref = db.collection("outfit_history").document(event_id)
    @firestore.transactional
    def apply(transaction):
        event = read(event_ref, transaction)
        if not event or event.get("undone") or event.get("event_revision", 1) != revision or expected_epoch is not None and event.get("app_data_epoch", 0) != expected_epoch:
            return
        user_ref = db.collection("users").document(event["user_id"])
        user = read(user_ref, transaction)
        if not user or not app_data_write_allowed(user, event.get("app_data_epoch", 0)):
            return
        counts = []
        for item_id in event.get("item_ids", []):
            garment = read(db.collection("wardrobe").document(item_id), transaction)
            counts.append(int((garment or {}).get("wearCount", 0)))
        candidates = [(30, "sustainable_style_bronze", 100), (60, "sustainable_style_silver", 150), (100, "sustainable_style_gold", 250)]
        awards = []
        for threshold, badge, xp in candidates:
            ref = db.collection("reward_ledger").document(key_for(event["user_id"], "milestone", badge))
            receipt = read(ref, transaction)
            if any(event.get("garment_counts_before", {}).get(item_id, threshold) < threshold <= event.get("garment_counts_after", {}).get(item_id, 0) for item_id in event.get("item_ids", [])) and badge not in user.get("badges", []) and not receipt:
                awards.append((ref, badge, xp))
        for ref, badge, xp in awards:
            patch, result = reward_patch(user, xp=xp, badge=badge, timestamp=milliseconds())
            user = {**user, **patch}
            transaction.set(ref, {"user_id": event["user_id"], "event_id": event_id, "kind": "milestone", "result": result})
        if awards:
            transaction.update(user_ref, patch)
    return apply(db.transaction())


def process_page(db, job_id, worker_id):
    job = claim(db, job_id, worker_id)
    if not job:
        return False
    try:
        ensure_annual_challenge(db, job["user_id"], job["created_at"], job.get("app_data_epoch", 0))
        query = db.collection("user_challenges").document(job["user_id"]).collection("active").order_by("__name__").limit(PAGE_SIZE)
        if job.get("cursor"):
            query = query.start_after({"__name__": db.collection("user_challenges").document(job["user_id"]).collection("active").document(job["cursor"])})
        instances = list(query.stream())
        for instance in instances:
            project_instance(db, job["event_id"], job["revision"], instance.reference, lease=(job_id, job))
        done = len(instances) < PAGE_SIZE
        if done:
            project_milestones(db, job["event_id"], job["revision"], job.get("app_data_epoch", 0))
            refresh_wear_stats(db, job["event_id"], job["revision"], job.get("app_data_epoch", 0))
        finish_page(db, job_id, job, instances[-1].id if instances else job.get("cursor"), done=done)
        return True
    except Exception:
        finish_page(db, job_id, job, job.get("cursor"), error=True)
        raise


def process_pending(db, worker_id, limit=10):
    query = db.collection("wear_projection_jobs").where(filter=FieldFilter("status", "in", ["pending", "processing"])).where(filter=FieldFilter("available_at", "<=", milliseconds())).order_by("available_at").limit(limit)
    processed = 0
    for job in query.stream():
        try:
            processed += bool(process_page(db, job.id, worker_id))
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Wear projection failed for job %s", job.id)
    return processed


def ensure_annual_challenge(db, uid, event_time, expected_epoch=None):
    """One deterministic challenge per52-week account cycle, never retro-credit."""
    user_ref = db.collection("users").document(uid)
    epoch_fence = WriteEpochFence(db, uid, expected_epoch)
    @firestore.transactional
    def create(transaction):
        try:
            epoch_fence.check(transaction)
        except Exception as error:
            if hasattr(error, "status_code"):
                return None
            raise
        user = read(user_ref, transaction)
        if not user or not app_data_write_allowed(user, expected_epoch):
            return None
        signup_ms = _ms(user.get("createdAt") or user.get("created_at")) or event_time
        signup = datetime.fromtimestamp(signup_ms / 1000, timezone.utc)
        now = datetime.fromtimestamp(event_time / 1000, timezone.utc)
        cycle = max(1, (now - signup).days // 364 + 1)
        collection = db.collection("user_challenges").document(uid).collection("active")
        existing = list(collection.where(filter=FieldFilter("challenge_id", "==", "annual_wardrobe_master")).stream(transaction=transaction))
        for snapshot in existing:
            if snapshot.to_dict().get("cycle_number") == cycle:
                return snapshot.id
        ref = collection.document("annual_wardrobe_master-" + str(cycle))
        previous = read(ref, transaction)
        if previous:
            return ref.id
        start = signup + timedelta(weeks=52 * (cycle - 1))
        transaction.set(ref, {"challenge_id": "annual_wardrobe_master", "user_id": uid, "cycle_number": cycle, "started_at": start, "expires_at": start + timedelta(weeks=52), "progress": {"total_outfits": 0, "weeks_completed": 0, "current_week_outfits": 0}, "status": "in_progress", "metadata": {"badge_id": "annual_master_cycle_" + str(cycle)}, "app_data_epoch": user.get("app_data_epoch", 0)})
        return ref.id
    return create(db.transaction())


def refresh_wear_stats(db, event_id, revision, expected_epoch=None):
    """Dashboard cache is a projection of active physical events, never ++ forever."""
    event_ref = db.collection("outfit_history").document(event_id)
    @firestore.transactional
    def refresh(transaction):
        event = read(event_ref, transaction)
        if not event or event.get("event_revision", 1) != revision or expected_epoch is not None and event.get("app_data_epoch", 0) != expected_epoch:
            return False
        uid = event["user_id"]
        user = read(db.collection("users").document(uid), transaction)
        if not user or not app_data_write_allowed(user, event.get("app_data_epoch", 0)):
            return False
        from zoneinfo import ZoneInfo
        from .wear_rewards import reward_timezone
        zone = ZoneInfo(reward_timezone(user, event.get("timezone") or "UTC"))
        current = datetime.now(zone)
        start = (current - timedelta(days=current.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        query = db.collection("outfit_history").where(filter=FieldFilter("user_id", "==", uid)).where(filter=FieldFilter("date_worn", ">=", int(start.timestamp()*1000))).where(filter=FieldFilter("date_worn", "<", int((start+timedelta(days=7)).timestamp()*1000)))
        count = sum(not snap.to_dict().get("undone") for snap in query.stream(transaction=transaction))
        stats_ref = db.collection("user_stats").document(uid)
        stats = read(stats_ref, transaction) or {}
        transaction.set(stats_ref, {**stats, "user_id": uid, "worn_this_week": count, "wear_week_start": start.date().isoformat(), "wear_timezone": str(zone), "updated_at": milliseconds()})
        return True
    return refresh(db.transaction())
