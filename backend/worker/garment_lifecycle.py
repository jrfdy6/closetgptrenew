"""Durable garment jobs; wardrobe fields are a projection, never retry authority.

Transactions only read/write Firestore. Image/storage work runs after claim and
may publish only with the current attempt, live lease, owner and edit fence.
Unlike paid flatlays, a garment failure has no ambiguous provider charge.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from uuid import uuid4

from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

try:
    from .app_data_privacy import require_app_data_writable, AppDataDeletionError
except ImportError:
    from app_data_privacy import require_app_data_writable, AppDataDeletionError


def _writable_epoch(db, txn, uid, expected=None):
    if not uid:
        return None
    try:
        return require_app_data_writable(db, uid, expected_epoch=expected, transaction=txn)
    except AppDataDeletionError:
        return None


JOBS_COLLECTION = "garment_processing_jobs"
MAX_ATTEMPTS = 3
LEASE_SECONDS = 360
RETRY_BACKOFF_SECONDS = (30, 120)
IDENTIFIER = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9_.-]{0,127}\Z")


class GarmentRetryError(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


ERRORS = {
    "processing_failed": "We couldn't finish preparing this photo. Your original photo is still available.",
    "worker_timeout": "Photo preparation took too long. Your original photo is still available.",
    "worker_crashed": "Photo preparation stopped unexpectedly. Your original photo is still available.",
    "invalid_image": "We couldn't read this photo. Try another photo of this item.",
    "invalid_identifier": "This older item cannot be prepared. Add it again with its original photo.",
    "invalid_result": "We couldn't save the prepared photo. Your original photo is still available.",
    "source_changed": "This item's photo changed during preparation.",
    "item_changed": "This item changed during photo preparation.",
    "garment_unavailable": "This item is no longer available for photo preparation.",
    "retry_exhausted": "Photo preparation couldn't finish after three attempts. You can retry this item or use its original photo.",
}


def _now():
    return int(datetime.now(timezone.utc).timestamp())


def _owner(item):
    owners = [item[key] for key in ("user_id", "userId", "firebase_uid", "uid", "ownerId") if item.get(key) is not None]
    return owners[0] if (owners and isinstance(owners[0], str) and owners[0] and owners[0].strip() == owners[0]
                         and "/" not in owners[0] and len(owners[0]) <= 128 and all(owner == owners[0] for owner in owners)) else None


def _source_url(item):
    value = item.get("imageUrl") or item.get("image_url")
    return value if isinstance(value, str) and value.strip() else None


def _available(item):
    return bool(item and _owner(item) and _source_url(item) and not any(
        item.get(key) for key in ("deleted", "isDeleted", "deletedAt", "deleted_at")))


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _source(item):
    # Metadata edits fence a result without buying another automatic retry budget.
    return _hash({"owner": _owner(item), "image": _source_url(item)})


def garment_source_fingerprint(item):
    """Bind image identity to owner; safe for original-reference admission."""
    return _source(item)


def _revision(item):
    # A client need not remember to bump updatedAt for its edit to be protected.
    # The only exclusions are this worker's progress/original publication fields.
    return _hash({key: value for key, value in item.items()
                  if not key.startswith("processing_") and key not in {
                      "originalStoragePath", "originalUrl"}})


def _count(value):
    try:
        return min(MAX_ATTEMPTS, max(0, int(value or 0)))
    except (ValueError, TypeError, OverflowError):
        return MAX_ATTEMPTS


def _error(code):
    return code if code in ERRORS else "processing_failed"


def _projection(job, now):
    status = job["status"]
    code = job.get("error_code")
    return {
        "processing_status": status,
        "processing_attempt_id": job.get("attempt_id"),
        "processing_attempt_count": job.get("attempt_count", 0),
        "processing_retry_count": job.get("attempt_count", 0),
        "processing_error": ERRORS.get(code),
        "processing_last_error": ERRORS.get(code),
        "processing_error_code": code,
        "processing_retryable": status == "failed" and code not in {"invalid_identifier", "invalid_image"},
        "processing_retry_action": ("replace_item" if code == "invalid_identifier" else
                                    "replace_photo" if code == "invalid_image" else "retry_item") if status == "failed" else None,
        "processing_next_attempt_at": job.get("next_attempt_at"),
        "processing_expires_at": job.get("lease_expires_at"),
        "processing_updated_at": now,
    }


def _end_attempt(job, now, code=None):
    history = [dict(entry) for entry in job.get("attempts", [])]
    if history and history[-1].get("attempt_id") == job.get("attempt_id"):
        history[-1].update(ended_at=now, status="failed" if code else "done", error_code=code)
    return history


def _failed(job, now, code):
    count = _count(job.get("attempt_count"))
    terminal = count >= MAX_ATTEMPTS or code in {"invalid_image", "invalid_identifier"}
    failed = {**job, "status": "failed" if terminal else "pending",
              "error_code": _error(code), "finished_at": now,
              "next_attempt_at": None if terminal else now + RETRY_BACKOFF_SECONDS[max(count - 1, 0)],
              "attempts": _end_attempt(job, now, _error(code))}
    failed.pop("lease_expires_at", None)
    return failed


def _fence_error(job, item):
    if not _available(item) or _owner(item) != job.get("user_id"):
        return "garment_unavailable"
    if _source(item) != job.get("source_fingerprint"):
        return "source_changed"
    if _revision(item) != job.get("source_revision"):
        return "item_changed"
    return None


def _clear_source_assets():
    """Clear only derived pixels from an earlier image, preserving the new source."""
    return {**{key: None for key in (
        "originalStoragePath", "originalUrl", "backgroundRemovedStoragePath", "backgroundRemovedUrl",
        "background_removed_url", "processedStoragePath", "processedUrl", "processed_url",
        "thumbnailStoragePath", "thumbnailUrl", "thumbnail_url", "original_size", "processed_size",
    )}, "backgroundRemoved": False, "background_removed": False}


def _drop_original(job):
    cleared = dict(job)
    for key in ("original", "original_attempt_id", "original_source_fingerprint"):
        cleared.pop(key, None)
    return cleared


def _preserved_original(job, item):
    """Retain a proven original across retries of precisely the same owned photo."""
    original = job.get("original")
    attempt_id = job.get("original_attempt_id")
    if (job.get("user_id") == _owner(item) and job.get("original_source_fingerprint") == _source(item)
            and isinstance(original, dict)
            and _asset(original, job.get("garment_id"), attempt_id, "originalStoragePath", "originalUrl", "original")):
        return {"original": dict(original), "original_attempt_id": attempt_id,
                "original_source_fingerprint": job["original_source_fingerprint"]}
    return {}


def _invalidate(txn, job_ref, job, item, now, code, garment_ref=None):
    """Retire a stale result; only project queue state for the same current owner."""
    stale = _failed(job, now, code)
    if _owner(item) != job.get("user_id") or _source(item) != job.get("source_fingerprint"):
        stale = _drop_original(stale)
    if code == "garment_unavailable":
        stale.update(status="cancelled", next_attempt_at=None)
    elif code == "source_changed":
        # An actual replacement photo is a new generation on the next claim,
        # including when the old image had exhausted its own attempt budget.
        stale.update(status="pending", next_attempt_at=now)
    txn.set(job_ref, stale)
    if garment_ref is not None and _available(item) and _owner(item) == job.get("user_id"):
        # No old result/image/metadata fields are written. Requeueing the current
        # document prevents a stale 'processing' projection stranding new work.
        assets = _clear_source_assets() if code == "source_changed" else {}
        txn.update(garment_ref, {**assets, **_projection(stale, now)})
    return stale


def _fresh_job(garment_id, item, now, *, count=0, manual_retry_count=0):
    return {
        "schema_version": 1, "garment_id": garment_id, "user_id": _owner(item),
        "generation_id": uuid4().hex, "source_fingerprint": _source(item),
        "source_revision": _revision(item), "source_url": _source_url(item),
        "status": "pending", "attempt_count": count, "attempt_id": None,
        "attempts": [], "created_at": now, "next_attempt_at": now,
        "manual_retry_count": manual_retry_count,
    }


def claim_garment(db, garment_id, worker_id, *, now=None):
    """Reserve a unique attempt and a 360s lease before any expensive work.

    Returns job + item snapshot or None. Legacy attempts are conservatively
    adopted once. Changing a public pending/count field cannot reset a job.
    """
    now = _now() if now is None else now
    if not isinstance(garment_id, str) or not garment_id or "/" in garment_id:
        return None
    garment_ref = db.collection("wardrobe").document(garment_id)
    job_ref = db.collection(JOBS_COLLECTION).document(garment_id)
    attempt_id = uuid4().hex

    @firestore.transactional
    def claim(txn):
        garment_doc = garment_ref.get(transaction=txn)
        job_doc = job_ref.get(transaction=txn)
        item = garment_doc.to_dict() or {} if garment_doc.exists else {}
        job = job_doc.to_dict() or {} if job_doc.exists else {}
        epoch = _writable_epoch(db, txn, job.get("user_id") or _owner(item), job.get("app_data_epoch", 0) if job else None)
        if epoch is None:
            return None
        source_asset_reset = {}
        if not IDENTIFIER.fullmatch(garment_id):
            if _available(item) and (not job or job.get("user_id") == _owner(item)):
                failed = job or _fresh_job(garment_id, item, now)
                failed = {**failed, "status": "failed", "error_code": "invalid_identifier", "next_attempt_at": None}
                failed.pop("lease_expires_at", None)
                txn.set(job_ref, failed)
                txn.update(garment_ref, _projection(failed, now))
            return None
        if not _available(item):
            if job.get("status") in ("pending", "processing"):
                _invalidate(txn, job_ref, job, item, now, "garment_unavailable", garment_ref)
            elif item and item.get("processing_status") == "pending" and not any(item.get(key) for key in ("deleted", "isDeleted", "deletedAt", "deleted_at")):
                # Invalid legacy pending records cannot stay at the head forever.
                # No image work is attempted and no user content is overwritten.
                if _owner(item) and (not job or job.get("user_id") == _owner(item)):
                    failed = job or _fresh_job(garment_id, item, now)
                    failed = {**failed}
                    failed.pop("lease_expires_at", None)
                    failed.update(status="failed", attempt_id=attempt_id, error_code="invalid_image", next_attempt_at=None)
                    txn.set(job_ref, failed)
                    txn.update(garment_ref, _projection(failed, now))
                elif not job:
                    txn.update(garment_ref, {"processing_status": "failed", "processing_error_code": "garment_unavailable",
                               "processing_error": ERRORS["garment_unavailable"], "processing_retryable": False,
                               "processing_retry_action": "replace_item", "processing_updated_at": now})
            return None
        if job and job.get("user_id") != _owner(item):
            # A client-side owner change cannot inherit a private original or job.
            cancelled = {**_drop_original(job), "status": "cancelled", "next_attempt_at": None,
                         "error_code": "garment_unavailable"}
            cancelled.pop("lease_expires_at", None)
            txn.set(job_ref, cancelled)
            return None
        if not job:
            if item.get("processing_status") != "pending":
                return None
            job = _fresh_job(garment_id, item, now, count=_count(item.get("processing_retry_count")))
        elif job.get("source_fingerprint") != _source(item):
            source_asset_reset = _clear_source_assets()
            # The edit fence describes the committed item after our own cleanup,
            # so publishing the new original does not invalidate this attempt.
            item = {**item, **source_asset_reset}
            job = _fresh_job(garment_id, item, now, manual_retry_count=job.get("manual_retry_count", 0))
        elif job.get("status") == "processing":
            code = _fence_error(job, item)
            if code:
                _invalidate(txn, job_ref, job, item, now, code, garment_ref)
            elif job.get("lease_expires_at", 0) <= now:
                failed = _failed(job, now, "worker_timeout")
                txn.set(job_ref, failed)
                txn.update(garment_ref, _projection(failed, now))
            elif item.get("processing_status") != "processing":
                txn.update(garment_ref, _projection(job, now))
            return None
        if job.get("status") in ("done", "failed", "cancelled"):
            # Repair a spoofed pending projection; authoritative terminal budget wins.
            if job["status"] != "cancelled" and item.get("processing_status") != job["status"]:
                txn.update(garment_ref, _projection(job, now))
            return None
        count = _count(job.get("attempt_count"))
        if count >= MAX_ATTEMPTS:
            job = {**job, "status": "failed", "error_code": "retry_exhausted", "next_attempt_at": None,
                   "attempt_id": job.get("attempt_id") or attempt_id}
            job.pop("lease_expires_at", None)
            txn.set(job_ref, job)
            txn.update(garment_ref, _projection(job, now))
            return None
        if job.get("next_attempt_at", 0) > now:
            return None
        claimed = {**job, "app_data_epoch": epoch, "attempt_id": attempt_id, "attempt_count": count + 1,
                   "worker_id": worker_id, "status": "processing", "claimed_at": now,
                   "expires_at": now + LEASE_SECONDS, "lease_expires_at": now + LEASE_SECONDS,
                   "next_attempt_at": None, "source_revision": _revision(item), "error_code": None,
                   "attempts": [*job.get("attempts", []), {"attempt_id": attempt_id, "worker_id": worker_id,
                               "claimed_at": now, "expires_at": now + LEASE_SECONDS, "status": "processing"}]}
        txn.set(job_ref, claimed)
        txn.update(garment_ref, {**source_asset_reset, **_projection(claimed, now)})
        return {**claimed, "item": item}

    return claim(db.transaction())


def _read_attempt(db, txn, job_ref, garment_ref, attempt_id, now):
    job_doc = job_ref.get(transaction=txn)
    garment_doc = garment_ref.get(transaction=txn)
    job = job_doc.to_dict() or {} if job_doc.exists else {}
    item = garment_doc.to_dict() or {} if garment_doc.exists else {}
    if job.get("status") != "processing" or job.get("attempt_id") != attempt_id:
        return None, None
    if _writable_epoch(db, txn, job.get("user_id"), job.get("app_data_epoch", 0)) is None:
        return None, None
    code = _fence_error(job, item)
    if code:
        _invalidate(txn, job_ref, job, item, now, code, garment_ref)
        return None, None
    if job.get("lease_expires_at", 0) <= now:
        failed = _failed(job, now, "worker_timeout")
        txn.set(job_ref, failed)
        txn.update(garment_ref, _projection(failed, now))
        return None, None
    return job, item


def _asset(payload, garment_id, attempt_id, path_key, url_key, filename):
    return (isinstance(garment_id, str) and IDENTIFIER.fullmatch(garment_id)
            and isinstance(attempt_id, str) and IDENTIFIER.fullmatch(attempt_id)
            and payload.get(path_key) == f"items/{garment_id}/attempts/{attempt_id}/{filename}.png"
            and isinstance(payload.get(url_key), str) and payload[url_key].startswith("https://"))


def publish_original(db, garment_id, attempt_id, original, *, now=None):
    """Publish only this attempt's preserved original; never replace imageUrl."""
    now = _now() if now is None else now
    if not isinstance(original, dict) or not _asset(original, garment_id, attempt_id, "originalStoragePath", "originalUrl", "original"):
        return False
    job_ref = db.collection(JOBS_COLLECTION).document(garment_id)
    garment_ref = db.collection("wardrobe").document(garment_id)

    @firestore.transactional
    def publish(txn):
        job, _ = _read_attempt(db, txn, job_ref, garment_ref, attempt_id, now)
        if job is None:
            return False
        fields = {key: original[key] for key in ("originalStoragePath", "originalUrl")}
        txn.update(garment_ref, fields)
        txn.set(job_ref, {**job, "original": fields, "original_attempt_id": attempt_id,
                          "original_source_fingerprint": job["source_fingerprint"]})
        return True

    return publish(db.transaction())


def finish_garment(db, garment_id, attempt_id, *, result=None, error_code=None, now=None):
    """Atomically finish the fenced attempt; false means stale or unavailable."""
    now = _now() if now is None else now
    job_ref = db.collection(JOBS_COLLECTION).document(garment_id)
    garment_ref = db.collection("wardrobe").document(garment_id)
    if error_code is None:
        if not isinstance(result, dict) or not all(_asset(result, garment_id, attempt_id, path, url, filename) for path, url, filename in (
            ("backgroundRemovedStoragePath", "backgroundRemovedUrl", "nobg"),
            ("processedStoragePath", "processedUrl", "processed"),
            ("thumbnailStoragePath", "thumbnailUrl", "thumbnail"),
        )):
            error_code = "invalid_result"

    @firestore.transactional
    def finish(txn):
        job, _ = _read_attempt(db, txn, job_ref, garment_ref, attempt_id, now)
        if job is None:
            return False
        if error_code is not None:
            finished = _failed(job, now, error_code)
            fields = _projection(finished, now)
        else:
            # Explicit allowlist: result cannot alter names, category, owner or source.
            derived = {key: result[key] for key in (
                "backgroundRemovedStoragePath", "backgroundRemovedUrl", "processedStoragePath", "processedUrl",
                "thumbnailStoragePath", "thumbnailUrl", "processing_mode", "processing_time", "original_size", "processed_size",
            ) if key in result}
            finished = {**job, "status": "done", "error_code": None, "finished_at": now,
                        "next_attempt_at": None, "result": derived, "attempts": _end_attempt(job, now)}
            finished.pop("lease_expires_at", None)
            fields = {**derived, "backgroundRemoved": True, **_projection(finished, now)}
        txn.set(job_ref, finished)
        txn.update(garment_ref, fields)
        return True

    return finish(db.transaction())


def recover_expired_garments(db, *, now=None, limit=20):
    """Reconcile expired leases independently from garment subprocess execution.

    Only active jobs have lease_expires_at; the inequality needs its ordinary
    single-field index, not a status+time composite index.
    """
    now = _now() if now is None else now
    counts = {"examined": 0, "recovered": 0, "failed": 0, "cancelled": 0}
    candidates = db.collection(JOBS_COLLECTION).where(filter=FieldFilter("lease_expires_at", "<=", now)).limit(max(1, min(int(limit), 100)))
    for candidate in candidates.stream(timeout=10, retry=None):
        counts["examined"] += 1
        job_ref = db.collection(JOBS_COLLECTION).document(candidate.id)
        garment_ref = db.collection("wardrobe").document(candidate.id)

        @firestore.transactional
        def recover(txn):
            job_doc = job_ref.get(transaction=txn)
            garment_doc = garment_ref.get(transaction=txn)
            job = job_doc.to_dict() or {} if job_doc.exists else {}
            item = garment_doc.to_dict() or {} if garment_doc.exists else {}
            if job.get("status") != "processing" or job.get("lease_expires_at", now + 1) > now:
                return None
            if _writable_epoch(db, txn, job.get("user_id"), job.get("app_data_epoch", 0)) is None:
                return None
            code = _fence_error(job, item)
            if code:
                stale = _invalidate(txn, job_ref, job, item, now, code, garment_ref)
                return stale["status"] if stale["status"] in ("cancelled", "failed") else "recovered"
            failed = _failed(job, now, "worker_timeout")
            txn.set(job_ref, failed)
            txn.update(garment_ref, _projection(failed, now))
            return "failed" if failed["status"] == "failed" else "recovered"

        outcome = recover(db.transaction())
        if outcome:
            counts[outcome] += 1
    return counts


def retry_garment(db, garment_id, user_id, expected_attempt_id, *, now=None):
    """Start one explicitly owned, bounded retry run after a terminal failure.

    Caller must verify Firebase authentication and pass that UID. An expected
    attempt token prevents delayed/double clicks resetting newer work. A public
    pending write alone cannot invoke this action. Each run allows three attempts.
    """
    now = _now() if now is None else now
    if not isinstance(garment_id, str) or not IDENTIFIER.fullmatch(garment_id):
        raise GarmentRetryError(404, "Wardrobe item not found.")
    job_ref = db.collection(JOBS_COLLECTION).document(garment_id)
    garment_ref = db.collection("wardrobe").document(garment_id)

    @firestore.transactional
    def retry(txn):
        job_doc = job_ref.get(transaction=txn)
        garment_doc = garment_ref.get(transaction=txn)
        job = job_doc.to_dict() or {} if job_doc.exists else {}
        item = garment_doc.to_dict() or {} if garment_doc.exists else {}
        if not _available(item) or _owner(item) != user_id or (job and job.get("user_id") != user_id):
            raise GarmentRetryError(404, "Wardrobe item not found.")
        try:
            epoch = require_app_data_writable(db, user_id, expected_epoch=job.get("app_data_epoch", 0), transaction=txn)
        except AppDataDeletionError as error:
            raise GarmentRetryError(error.status_code, error.detail) from error
        if not expected_attempt_id:
            raise GarmentRetryError(409, "Reload this item before retrying photo preparation.")
        if job.get("retry_of_attempt_id") == expected_attempt_id and job.get("source_fingerprint") == _source(item):
            return {"success": True, "garment_id": garment_id, "status": job["status"],
                    "generation_id": job["generation_id"], "attempt_count": job["attempt_count"], "idempotent": True}
        if (job.get("status") != "failed" or job.get("attempt_id") != expected_attempt_id
                or job.get("source_fingerprint") != _source(item)):
            raise GarmentRetryError(409, "This photo is not awaiting a retry. Reload this item for its current status.")
        if job.get("error_code") == "invalid_image":
            raise GarmentRetryError(409, "We could not read this photo. Choose another photo of this item before retrying.")
        queued = _fresh_job(garment_id, item, now, manual_retry_count=job.get("manual_retry_count", 0) + 1)
        queued["app_data_epoch"] = epoch
        queued.update(_preserved_original(job, item))
        queued["retry_of_attempt_id"] = expected_attempt_id
        txn.set(job_ref, queued)
        txn.update(garment_ref, _projection(queued, now))
        return {"success": True, "garment_id": garment_id, "status": "pending",
                "generation_id": queued["generation_id"], "attempt_count": 0, "idempotent": False}

    return retry(db.transaction())
