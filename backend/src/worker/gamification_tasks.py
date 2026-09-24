"""Idempotent maintenance tasks; invoked by the lightweight durable runner.

Dates are UTC for scheduling; user activity dates use the stored local timezone.
Historical feedback is never retroactively rewarded.
"""
import asyncio
from datetime import datetime, timedelta, timezone, date
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from ..services.reward_ledger import read, key_for, reward_patch
from ..services.app_data_privacy import app_data_write_allowed
from ..services.wear_rewards import reward_timezone
from ..custom_types.gamification import CHALLENGE_CATALOG
from zoneinfo import ZoneInfo


def rating_block_receipt(days):
    """Each consecutive run yields a bonus at7,14,... distinct dates."""
    ordered = sorted(set(days))
    blocks, start, previous, length = [], None, None, 0
    for value in ordered:
        current = date.fromisoformat(value)
        if previous is None or current != previous + timedelta(days=1):
            start, length = value, 0
        length += 1
        if length % 7 == 0:
            blocks.append((start, length // 7))
        previous = current
    return blocks


def award_rating_block(db, uid, block, expected_epoch):
    reference = db.collection("reward_ledger").document(key_for(uid, "rating-streak", *block))
    user_ref = db.collection("users").document(uid)
    @firestore.transactional
    def commit(transaction):
        user = read(user_ref, transaction)
        receipt = read(reference, transaction)
        if receipt or not user or not app_data_write_allowed(user, expected_epoch):
            return False
        patch, result = reward_patch(user, xp=20, timestamp=int(datetime.now(timezone.utc).timestamp() * 1000))
        transaction.update(user_ref, patch)
        transaction.set(reference, {"user_id": uid, "kind": "rating_streak", "block": list(block), "result": result, "app_data_epoch": expected_epoch})
        return True
    return commit(db.transaction())


async def reconcile_user(db, uid, activation_ms, expected_epoch=None):
    from ..services.cpw_service import cpw_service
    from ..services.gws_service import gws_service
    from ..services.ai_fit_score_service import ai_fit_score_service
    from ..services.challenge_service import challenge_service
    user_doc = db.collection("users").document(uid).get()
    user = user_doc.to_dict() if user_doc.exists else None
    if not user or not app_data_write_allowed(user, expected_epoch):
        return
    epoch = user.get("app_data_epoch", 0)
    # These existing services update derived caches; no reward replay.
    await cpw_service.recalculate_all_cpw_for_user(uid)
    await gws_service.calculate_gws(uid)
    score = await ai_fit_score_service.calculate_ai_fit_score(uid)
    await challenge_service.expire_old_challenges(uid)
    zone = ZoneInfo(reward_timezone(user, "UTC"))
    days = []
    # Immutable creation time, not rating edits. Unknown/legacy timestamps are
    # skipped; activation is a durable deployment marker, not process start.
    for snapshot in db.collection("outfit_feedback").where(filter=FieldFilter("user_id", "==", uid)).stream():
        record = snapshot.to_dict()
        created = record.get("created_at")
        if hasattr(created, "timestamp"):
            instant = created
        elif isinstance(created, (float, int)):
            instant = datetime.fromtimestamp(created / 1000 if created >= 1e12 else created, timezone.utc)
        elif isinstance(created, str):
            try:
                instant = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if instant.tzinfo is None:
                    instant = instant.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        else:
            continue
        if instant.timestamp() * 1000 >= activation_ms:
            days.append(instant.astimezone(zone).date().isoformat())
    for block in rating_block_receipt(days):
        award_rating_block(db, uid, block, epoch)
    @firestore.transactional
    def cache(transaction):
        ref = db.collection("users").document(uid)
        latest = read(ref, transaction)
        if latest and app_data_write_allowed(latest, epoch):
            transaction.update(ref, {"ai_fit_score": score})
    cache(db.transaction())


def weekly_challenge_generation_task(db, week):
    rotation = ["color_harmony", "forgotten_gems_weekly", "30_wears_challenge", "color_harmony"]
    featured = rotation[int(week.split("-W")[1]) % len(rotation)]
    batch = db.batch()
    for cid, definition in CHALLENGE_CATALOG.items():
        batch.set(db.collection("challenges").document(cid), {**definition.dict(), "featured": cid == featured, "week": week}, merge=True)
    batch.commit()
    return featured


def due_runs(now):
    daily = now.replace(hour=4, minute=0, second=0, microsecond=0)
    if now < daily:
        daily -= timedelta(days=1)
    weekly = now.replace(hour=4, minute=15, second=0, microsecond=0) - timedelta(days=now.weekday())
    if now < weekly:
        weekly -= timedelta(days=7)
    year, week, _ = weekly.isocalendar()
    return [("daily-" + daily.date().isoformat(), "daily"), (f"weekly-{year}-W{week:02d}", "weekly")]


def run_maintenance_page(db, worker_id, now=None):
    """At most100 users per page, durable cursor, one lease per run."""
    now = now or datetime.now(timezone.utc)
    timestamp = int(now.timestamp() * 1000)
    activation_ref = db.collection("gamification_jobs").document("activation-v2")
    @firestore.transactional
    def activate(transaction):
        value = read(activation_ref, transaction)
        if not value:
            value = {"activated_at": timestamp}
            transaction.set(activation_ref, value)
        return value["activated_at"]
    activation = activate(db.transaction())
    for job_id, kind in due_runs(now):
        reference = db.collection("gamification_jobs").document(job_id)
        @firestore.transactional
        def claim(transaction):
            existing = read(reference, transaction) or {}
            if existing.get("status") == "complete" or existing.get("lease_until", 0) > timestamp:
                return None
            value = {**existing, "kind": kind, "lease_owner": worker_id, "lease_until": timestamp + 600_000, "fence": existing.get("fence", 0) + 1, "status": "running"}
            transaction.set(reference, value)
            return value
        job = claim(db.transaction())
        if not job:
            continue
        cursor, complete = job.get("cursor"), True
        if kind == "weekly":
            weekly_challenge_generation_task(db, job_id.removeprefix("weekly-"))
        else:
            query = db.collection("users").order_by("__name__").limit(100)
            if cursor:
                query = query.start_after({"__name__": db.collection("users").document(cursor)})
            users = list(query.stream())
            for user in users:
                user_data = user.to_dict()
                job_ref = db.collection("gamification_user_jobs").document(key_for(job_id, user.id))
                @firestore.transactional
                def enqueue(transaction):
                    if read(job_ref, transaction):
                        return
                    latest = read(db.collection("users").document(user.id), transaction)
                    if latest and app_data_write_allowed(latest, user_data.get("app_data_epoch", 0)):
                        transaction.set(job_ref, {"user_id": user.id, "app_data_epoch": user_data.get("app_data_epoch", 0), "activation_ms": activation, "status": "pending", "available_at": timestamp, "lease_until": 0, "attempts": 0})
                enqueue(db.transaction())
            cursor = users[-1].id if users else cursor
            complete = len(users) < 100
        @firestore.transactional
        def finish(transaction):
            existing = read(reference, transaction)
            if existing and existing.get("fence") == job["fence"] and existing.get("lease_owner") == worker_id:
                transaction.update(reference, {"cursor": cursor, "status": "complete" if complete else "pending", "lease_until": 0})
        finish(db.transaction())
        return True
    return False


def process_reconciliation_jobs(db, worker_id, limit=2):
    now = int(datetime.now(timezone.utc).timestamp()*1000)
    query = db.collection("gamification_user_jobs").where(filter=FieldFilter("status", "in", ["pending", "running"])).where(filter=FieldFilter("available_at", "<=", now)).order_by("available_at").limit(limit)
    for snapshot in query.stream():
        reference = snapshot.reference
        @firestore.transactional
        def claim(transaction):
            job = read(reference, transaction)
            if not job or job.get("status") == "complete" or job.get("lease_until", 0) > now:
                return None
            value = {**job, "status": "running", "lease_until": now+600000, "lease_owner": worker_id, "fence": int(job.get("fence", 0))+1}
            transaction.update(reference, value)
            return value
        job = claim(db.transaction())
        if not job:
            continue
        success = True
        try:
            asyncio.run(reconcile_user(db, job["user_id"], job["activation_ms"], job.get("app_data_epoch", 0)))
        except Exception:
            import logging
            logging.getLogger(__name__).exception("User reconciliation remains retryable")
            success = False
        @firestore.transactional
        def finish(transaction):
            current = read(reference, transaction)
            if current and current.get("fence") == job["fence"] and current.get("lease_owner") == worker_id:
                transaction.update(reference, {"status": "complete" if success else "pending", "lease_until": 0, "attempts": job.get("attempts", 0)+int(not success), "available_at": now+(0 if success else 3600000), "last_error": None if success else "reconciliation_failed"})
        finish(db.transaction())


def maintenance_pass(db, worker_id):
    process_reconciliation_jobs(db, worker_id, limit=2)
    return run_maintenance_page(db, worker_id)
