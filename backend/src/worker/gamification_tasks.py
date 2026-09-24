"""Idempotent maintenance tasks; invoked by the lightweight durable runner.

Dates are UTC for scheduling; user activity dates use the stored local timezone.
Historical feedback is never retroactively rewarded.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone, date
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from ..services.reward_ledger import read, key_for, reward_patch
from ..services.app_data_privacy import app_data_write_allowed, AppDataDeletionError
from ..services.wear_rewards import reward_timezone
from ..custom_types.gamification import CHALLENGE_CATALOG
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)
LEASE_MS = 600_000
RETRY_MS = 3_600_000
MAX_ATTEMPTS = 5
RETENTION_MS = 14 * 24 * 3_600_000
PAGE_SIZE = 100


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


def feedback_creation_instant(record):
    """Legacy malformed dates must not poison an account's durable queue.

    Rating edits do not create new days: only the initial created_at is read.
    """
    created = record.get("created_at")
    try:
        if isinstance(created, datetime):
            instant = created
        elif isinstance(created, (float, int)) and not isinstance(created, bool):
            instant = datetime.fromtimestamp(created / 1000 if created >= 1e12 else created, timezone.utc)
        elif isinstance(created, str):
            instant = datetime.fromisoformat(created.replace("Z", "+00:00"))
        else:
            return None
        return instant.replace(tzinfo=timezone.utc) if instant.tzinfo is None else instant
    except (ValueError, OverflowError, OSError, TypeError):
        return None


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
    zone = ZoneInfo(reward_timezone(user, "UTC"))
    days = []
    # Immutable creation time, not rating edits. Unknown/legacy timestamps are
    # skipped; activation is a durable deployment marker, not process start.
    for snapshot in db.collection("outfit_feedback").where(filter=FieldFilter("user_id", "==", uid)).stream():
        record = snapshot.to_dict()
        if record.get("reward_pending") is True:
            from ..services.feedback_rewards import settle_feedback_reward
            settle_feedback_reward(db, uid, snapshot.id, expected_epoch=epoch)
        instant = feedback_creation_instant(record)
        if instant is None:
            continue
        if instant.timestamp() * 1000 >= activation_ms:
            days.append(instant.astimezone(zone).date().isoformat())
    for block in rating_block_receipt(days):
        award_rating_block(db, uid, block, epoch)
    # Reward repair runs before derived caches: a broken legacy item must not
    # strand an already-recorded eligible action. Receipts make retries safe.
    await challenge_service.check_cold_start_progress(uid, 0, expected_epoch=epoch)
    from ..services.addiction_service import addiction_service
    await addiction_service.check_and_update_role(uid, expected_epoch=epoch)
    from ..services.challenge_actions import reconcile_action_challenges
    reconcile_action_challenges(db, uid, expected_epoch=epoch)
    await challenge_service.expire_old_challenges(uid, expected_epoch=epoch)
    # These services only refresh derived caches. They share the captured epoch.
    await cpw_service.recalculate_all_cpw_for_user(uid, expected_epoch=epoch)
    await gws_service.calculate_gws(uid, expected_epoch=epoch)
    score = await ai_fit_score_service.calculate_ai_fit_score(uid, expected_epoch=epoch)
    @firestore.transactional
    def cache(transaction):
        ref = db.collection("users").document(uid)
        latest = read(ref, transaction)
        if latest and app_data_write_allowed(latest, epoch):
            transaction.update(ref, {"ai_fit_score": score})
    cache(db.transaction())


def weekly_challenge_generation_task(db, week, *, job_ref=None, job=None):
    rotation = ["color_harmony", "forgotten_gems_weekly", "30_wears_challenge", "color_harmony"]
    featured = rotation[int(week.split("-W")[1]) % len(rotation)]
    @firestore.transactional
    def publish(transaction):
        if job_ref is not None:
            current = read(job_ref, transaction)
            marker = read(db.collection("gamification_jobs").document("activation-v2"), transaction)
            if (not current or current.get("status") != "running"
                    or current.get("fence") != job["fence"]
                    or current.get("lease_owner") != job["lease_owner"]
                    or not marker or marker.get("latest_weekly_run") != "weekly-" + week):
                return False
        for cid, definition in CHALLENGE_CATALOG.items():
            transaction.set(db.collection("challenges").document(cid),
                            {**definition.dict(), "featured": cid == featured, "week": week}, merge=True)
        return True
    return featured if publish(db.transaction()) else None


def utc_now(now=None):
    """Scheduling is UTC regardless of the worker host or supplied local zone."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def due_runs(now):
    now = utc_now(now)
    daily = now.replace(hour=4, minute=0, second=0, microsecond=0)
    if now < daily:
        daily -= timedelta(days=1)
    weekly = now.replace(hour=4, minute=15, second=0, microsecond=0) - timedelta(days=now.weekday())
    if now < weekly:
        weekly -= timedelta(days=7)
    year, week, _ = weekly.isocalendar()
    return [("daily-" + daily.date().isoformat(), "daily"), (f"weekly-{year}-W{week:02d}", "weekly")]


def run_maintenance_page(db, worker_id, now=None):
    """Resume one daily page across midnight; independently refresh the week.

    Missed daily periods coalesce to the latest period after any already-started
    page run finishes. Cache reconciliation does not need one run per missed day.
    The immutable activation marker is never advanced by restarts or catch-up.
    """
    now = utc_now(now)
    timestamp = int(now.timestamp() * 1000)
    daily_id, weekly_id = [job_id for job_id, _ in due_runs(now)]
    activation_ref = db.collection("gamification_jobs").document("activation-v2")
    @firestore.transactional
    def activate(transaction):
        value = read(activation_ref, transaction)
        if not value:
            value = {"activated_at": timestamp, "active_daily_run": daily_id}
            transaction.set(activation_ref, value)
        return value
    marker = activate(db.transaction())
    activation = marker["activated_at"]

    @firestore.transactional
    def select_daily(transaction):
        current = read(activation_ref, transaction)
        previous_id = current.get("active_daily_run", daily_id)
        previous = read(db.collection("gamification_jobs").document(previous_id), transaction)
        selected = daily_id if previous and previous.get("status") == "complete" else previous_id
        updates = {}
        if current.get("active_daily_run") != selected:
            updates["active_daily_run"] = selected
        if weekly_id > current.get("latest_weekly_run", ""):
            updates["latest_weekly_run"] = weekly_id
        if updates:
            transaction.update(activation_ref, updates)
        return selected
    selected_daily = select_daily(db.transaction())
    advanced = False
    # Weekly work cannot be held behind a multi-page daily scan.
    for job_id, kind in [(weekly_id, "weekly"), (selected_daily, "daily")]:
        reference = db.collection("gamification_jobs").document(job_id)
        @firestore.transactional
        def claim(transaction):
            existing = read(reference, transaction) or {}
            if existing.get("status") == "complete" or existing.get("lease_until", 0) > timestamp:
                return None
            value = {**existing, "kind": kind, "lease_owner": worker_id,
                     "lease_until": timestamp + LEASE_MS,
                     "fence": existing.get("fence", 0) + 1, "status": "running"}
            transaction.set(reference, value)
            return value
        job = claim(db.transaction())
        if not job:
            continue
        cursor, complete = job.get("cursor"), True
        if kind == "weekly":
            weekly_challenge_generation_task(db, job_id.removeprefix("weekly-"), job_ref=reference, job=job)
        else:
            query = db.collection("users").order_by("__name__").limit(PAGE_SIZE)
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
                        transaction.set(job_ref, {"user_id": user.id,
                            "app_data_epoch": user_data.get("app_data_epoch", 0),
                            "activation_ms": activation, "status": "pending",
                            "available_at": timestamp, "created_at": timestamp,
                            "run_id": job_id, "lease_until": 0, "attempts": 0})
                enqueue(db.transaction())
            cursor = users[-1].id if users else cursor
            complete = len(users) < PAGE_SIZE
        @firestore.transactional
        def finish(transaction):
            existing = read(reference, transaction)
            if existing and existing.get("fence") == job["fence"] and existing.get("lease_owner") == worker_id:
                transaction.update(reference, {"cursor": cursor,
                    "status": "complete" if complete else "pending", "lease_until": 0,
                    "updated_at": timestamp})
        finish(db.transaction())
        advanced = True
    return advanced


def process_reconciliation_jobs(db, worker_id, limit=2, now=None):
    timestamp = int(utc_now(now).timestamp() * 1000)
    query = db.collection("gamification_user_jobs").where(filter=FieldFilter("status", "in", ["pending", "running"])).where(filter=FieldFilter("available_at", "<=", timestamp)).order_by("available_at").limit(limit)
    processed = 0
    for snapshot in query.stream():
        reference = snapshot.reference
        @firestore.transactional
        def claim(transaction):
            job = read(reference, transaction)
            if not job or job.get("status") not in {"pending", "running"}:
                return None
            if job.get("lease_until", 0) > timestamp:
                # Repair pre-upgrade running rows so a lease cannot occupy the
                # oldest query slots until every later account is starved.
                if job.get("available_at", 0) < job["lease_until"]:
                    transaction.update(reference, {"available_at": job["lease_until"]})
                return None
            if job.get("available_at", 0) > timestamp:
                return None
            attempts = int(job.get("attempts", 0))
            if attempts >= MAX_ATTEMPTS:
                logger.error("Gamification user job exhausted retries; next daily run can recover the account")
                transaction.update(reference, {"status": "failed", "lease_until": 0,
                    "available_at": timestamp, "finished_at": timestamp,
                    "last_error": "reconciliation_attempts_exhausted"})
                return None
            value = {**job, "status": "running", "lease_until": timestamp + LEASE_MS,
                     "available_at": timestamp + LEASE_MS, "lease_owner": worker_id,
                     "fence": int(job.get("fence", 0)) + 1, "attempts": attempts + 1}
            transaction.update(reference, value)
            return value
        job = claim(db.transaction())
        if not job:
            continue
        outcome, error = "complete", None
        try:
            asyncio.run(reconcile_user(db, job["user_id"], job["activation_ms"], job.get("app_data_epoch", 0)))
        except Exception as exc:
            obsolete = False
            if isinstance(exc, AppDataDeletionError):
                try:
                    user_snapshot = db.collection("users").document(job["user_id"]).get()
                    obsolete = (not user_snapshot.exists or not app_data_write_allowed(
                        user_snapshot.to_dict(), job.get("app_data_epoch", 0)))
                except Exception:
                    # A failed read cannot prove an account was cleared.
                    pass
            if not obsolete:
                logger.exception("User reconciliation remains retryable")
                outcome = "failed" if job["attempts"] >= MAX_ATTEMPTS else "pending"
                error = "reconciliation_attempts_exhausted" if outcome == "failed" else "reconciliation_failed"
                if outcome == "failed":
                    logger.error("Gamification user job exhausted retries; next daily run can recover the account")
        @firestore.transactional
        def finish(transaction):
            current = read(reference, transaction)
            if current and current.get("fence") == job["fence"] and current.get("lease_owner") == worker_id:
                transaction.update(reference, {"status": outcome, "lease_until": 0,
                    "available_at": timestamp + (RETRY_MS if outcome == "pending" else 0),
                    "finished_at": timestamp if outcome != "pending" else None,
                    "last_error": error})
        finish(db.transaction())
        processed += 1
    return processed


def prune_reconciliation_jobs(db, now=None, limit=50):
    """Bound terminal cache-job growth; immutable reward receipts are untouched."""
    cutoff = int(utc_now(now).timestamp() * 1000) - RETENTION_MS
    query = db.collection("gamification_user_jobs").where(filter=FieldFilter("status", "in", ["complete", "failed"])).where(filter=FieldFilter("available_at", "<=", cutoff)).order_by("available_at").limit(limit)
    removed = 0
    for snapshot in query.stream():
        @firestore.transactional
        def remove(transaction):
            job = read(snapshot.reference, transaction)
            if job and job.get("status") in {"complete", "failed"} and job.get("available_at", cutoff + 1) <= cutoff:
                transaction.delete(snapshot.reference)
                return True
            return False
        removed += bool(remove(db.transaction()))
    return removed


def maintenance_pass(db, worker_id, now=None):
    # Keep scheduler, cache retries and retention independently recoverable.
    results = {}
    for name, action in (("schedule", lambda: run_maintenance_page(db, worker_id, now)),
                         ("reconcile", lambda: process_reconciliation_jobs(db, worker_id, limit=2, now=now)),
                         ("prune", lambda: prune_reconciliation_jobs(db, now))):
        try:
            results[name] = action()
        except Exception:
            logger.exception("Gamification maintenance component failed: %s", name)
            results[name] = False
    return results
