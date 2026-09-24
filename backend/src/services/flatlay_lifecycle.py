"""Transactional flat-lay lifecycle, shared verbatim with the isolated worker root.

The private flat_lay_requests collection is authoritative. Browser-writable outfit
fields are only a realtime projection, never proof of consent or credit payment.
No provider call runs inside a transaction (Firestore may retry its callback).
"""
from datetime import datetime, timezone
from uuid import uuid4
import re
import math
from firebase_admin import firestore

REQUESTS_COLLECTION = "flat_lay_requests"
WEEK_SECONDS = 7 * 24 * 60 * 60
TIER_LIMITS = {"tier1": 1, "tier2": 7, "tier3": 30}
PENDING_TIMEOUT_SECONDS = 15 * 60
PROCESSING_TIMEOUT_SECONDS = 10 * 60
LEGACY_ERROR = "This earlier preview needs review before another request. No new credit was used."


class FlatlayRequestError(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


try:
    from .app_data_privacy import require_app_data_writable, app_data_write_allowed, AppDataDeletionError
except ImportError:
    from app_data_privacy import require_app_data_writable, app_data_write_allowed, AppDataDeletionError


def _request_writable(db, txn, request):
    try:
        require_app_data_writable(db, request.get("user_id"), expected_epoch=request.get("app_data_epoch", 0), transaction=txn)
        return True
    except AppDataDeletionError:
        return False


def _now():
    return int(datetime.now(timezone.utc).timestamp())


def _owner_matches(data, user_id):
    owners = [data[key] for key in ("user_id", "userId", "firebase_uid", "uid", "ownerId") if data.get(key) is not None]
    return bool(user_id and owners) and all(owner == user_id for owner in owners)


def _status(data):
    metadata = data.get("metadata") or {}
    return data.get("flat_lay_status") or data.get("flatLayStatus") or metadata.get("flat_lay_status") or metadata.get("flatLayStatus")


def _projection(status, request_id, now, *, url=None, error=None, retryable=False,
                error_code=None, credit_status=None):
    values = {
        "flat_lay_status": status, "flatLayStatus": status,
        "flat_lay_url": url, "flatLayUrl": url,
        "flat_lay_error": error, "flatLayError": error,
        "flat_lay_request_id": request_id,
        "flat_lay_retryable": retryable,
        "flat_lay_request_allowed": retryable,
        "flat_lay_error_code": error_code,
        "flat_lay_credit_status": credit_status,
        "flat_lay_requested": status != "awaiting_consent", "flatLayRequested": status != "awaiting_consent",
        "flat_lay_updated_at": now,
    }
    return {**values, **{f"metadata.{key}": value for key, value in values.items()}}


def _response(outfit_id, request):
    return {
        "success": True, "id": outfit_id, "outfit_id": outfit_id,
        "flat_lay_status": request["status"], "flat_lay_url": request.get("url"),
        "flat_lay_error": request.get("error"), "request_id": request.get("request_id"),
        "retryable": bool(request.get("retryable")),
        "request_allowed": bool(request.get("retryable")),
        "error_code": request.get("error_code"),
        "credit_status": request.get("credit_status"),
    }


def _quota(data, now):
    subscription = data.get("subscription") or {}
    limit = TIER_LIMITS.get(subscription.get("role") or subscription.get("tier"), 1)
    quota = data.get("quotas") or {}
    try:
        remaining = max(0, int(quota.get("flatlaysRemaining", 0)))
    except (TypeError, ValueError):
        remaining = 0
    try:
        start = int(quota["lastRefillAt"])
    except (KeyError, TypeError, ValueError):
        start = None
    if start is None or now - start >= WEEK_SECONDS:
        return limit, now
    # Preserve the current period anchor: each use must not postpone the refill.
    return remaining, start


def _item_ids(items):
    result = []
    if not isinstance(items, list) or not items:
        raise FlatlayRequestError(422, "Add wardrobe items before requesting a preview.")
    for item in items:
        item_id = (item.get("id") or item.get("itemId") or item.get("item_id")) if isinstance(item, dict) else item
        if not isinstance(item_id, str) or not item_id or "/" in item_id:
            raise FlatlayRequestError(422, "Each preview item must reference a saved wardrobe item.")
        if item_id not in result:
            result.append(item_id)
    return result


def _same_item_set(request, outfit):
    """Compare actual unique garment IDs; order/name/style changes do not invalidate."""
    try:
        return set(_item_ids(request.get("items"))) == set(_item_ids(outfit.get("items")))
    except FlatlayRequestError:
        return False


def _source_fingerprint(garment):
    try:
        from .garment_lifecycle import garment_source_fingerprint
    except ImportError:
        from garment_lifecycle import garment_source_fingerprint
    return garment_source_fingerprint(garment)


def _available_garment(garment, user_id):
    return bool(garment and _owner_matches(garment, user_id) and not any(
        garment.get(key) for key in ("deleted", "isDeleted", "deletedAt", "deleted_at")))


def _has_source_identity(request):
    """Older private requests need review, never inferred source provenance."""
    items = request.get("items")
    if not isinstance(items, list) or not items:
        return False
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            return False
        garment_id = item.get("id")
        fingerprint = item.get("referenceSourceFingerprint")
        if (not isinstance(garment_id, str) or not garment_id or "/" in garment_id
                or garment_id in seen or not isinstance(fingerprint, str)
                or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None):
            return False
        seen.add(garment_id)
    return True


def _same_owned_sources(db, txn, request):
    """Read current garment identity before any transaction writes.

    Only the private reservation's source fingerprints prove which photos were
    authorized. Pre-fingerprint requests cannot prove freshness, even when a
    captured URL or a mutable legacy original path still looks the same. This
    helper never infers a debit, refunds, or starts provider work.
    """
    if not _has_source_identity(request):
        return False
    for item in request["items"]:
        garment_id = item["id"]
        garment_doc = db.collection("wardrobe").document(garment_id).get(transaction=txn)
        garment = (garment_doc.to_dict() or {}) if garment_doc.exists else {}
        if (not _available_garment(garment, request.get("user_id"))
                or item["referenceSourceFingerprint"] != _source_fingerprint(garment)):
            return False
    return True


def _reserved_reference(garment_id, garment, job, user_id, request_id):
    """Snapshot a proven original or owned raw input, independent of cutout work."""
    try:
        from .original_source import owned_upload_source, request_original_path
    except ImportError:
        from original_source import owned_upload_source, request_original_path
    fingerprint = _source_fingerprint(garment)
    reference = {"referenceSourceFingerprint": fingerprint}
    if job is not None:
        if job.get("user_id") != user_id:
            raise FlatlayRequestError(422, "One or more original item photos are unavailable.")
        original = job.get("original")
        attempt_id = job.get("original_attempt_id")
        if (isinstance(original, dict)
                and job.get("source_fingerprint") == fingerprint
                and job.get("original_source_fingerprint") == fingerprint
                and isinstance(attempt_id, str)
                and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", attempt_id)
                and original.get("originalStoragePath") == f"items/{garment_id}/attempts/{attempt_id}/original.png"):
            return {**reference, "originalStoragePath": original["originalStoragePath"]}
    # Never fetch arbitrary/client-controlled URLs here or in the image worker.
    # The helper admits only this user's upload prefix in the configured bucket.
    descriptor = owned_upload_source(garment.get("imageUrl") or garment.get("image_url"), user_id)
    if descriptor:
        try:
            path = request_original_path(garment_id, request_id)
        except (ValueError, TypeError):
            raise FlatlayRequestError(422, "One or more original item photos are unavailable.")
        return {**reference, "originalPreparation": descriptor, "originalStoragePath": path}
    if job is None:
        return {**reference, "originalStoragePath": f"items/{garment_id}/original.png"}
    raise FlatlayRequestError(422, "The original item photo is unavailable. Please replace this item's photo and try again.")


def reserve_request(db, outfit_id, user_id, *, now=None, request_id=None):
    """Reserve one credit and queue one explicit request in the same commit."""
    now = _now() if now is None else now
    request_id = request_id or uuid4().hex
    captured_epoch = [None]
    outfit_ref = db.collection("outfits").document(outfit_id)
    ledger_ref = db.collection(REQUESTS_COLLECTION).document(outfit_id)
    user_ref = db.collection("users").document(user_id)

    @firestore.transactional
    def reserve(txn):
        outfit_doc = outfit_ref.get(transaction=txn)
        if not outfit_doc.exists:
            raise FlatlayRequestError(404, "Outfit not found")
        outfit = outfit_doc.to_dict() or {}
        if not _owner_matches(outfit, user_id):
            raise FlatlayRequestError(403, "Access denied")
        if not _available_garment(outfit, user_id):
            raise FlatlayRequestError(404, "Outfit not found")
        try:
            epoch = require_app_data_writable(db, user_id, expected_epoch=captured_epoch[0], transaction=txn)
            if captured_epoch[0] is None:
                captured_epoch[0] = epoch
        except AppDataDeletionError as error:
            raise FlatlayRequestError(error.status_code, error.detail) from error
        ledger_doc = ledger_ref.get(transaction=txn)
        previous = (ledger_doc.to_dict() or {}) if ledger_doc.exists else {}
        if previous:
            if previous.get("user_id") != user_id or previous.get("outfit_id") != outfit_id:
                raise FlatlayRequestError(409, "This preview needs review before another request.")
            if previous.get("error_code") in ("provider_outcome_unknown", "worker_outcome_unknown"):
                # An older/inconsistent retryable flag cannot resolve an unknown
                # paid attempt. The same hold applies to the read projection.
                raise FlatlayRequestError(409, previous.get("error") or "This preview needs review before another request.")
            if previous.get("status") == "done" and not _has_source_identity(previous):
                raise FlatlayRequestError(409, LEGACY_ERROR)
            same_items = (_same_item_set(previous, outfit)
                          and _same_owned_sources(db, txn, previous))
            if previous.get("status") in ("pending", "processing"):
                # An edit cannot start another paid attempt while the existing
                # request may be in flight. Claim/finish will settle its credit.
                if not same_items:
                    return _response(outfit_id, {**previous, "url": None,
                        "error": "This outfit changed. Its earlier preview request is being settled.",
                        "error_code": "outfit_changed", "retryable": False})
                return _response(outfit_id, previous)
            if previous.get("status") == "done" and same_items:
                return _response(outfit_id, previous)
            changed_completed = previous.get("status") == "done" and not same_items
            retryable_failure = (previous.get("status") == "failed" and previous.get("retryable") is True
                                 and previous.get("credit_status") == "refunded")
            if not (changed_completed or retryable_failure):
                raise FlatlayRequestError(409, previous.get("error") or "This preview needs review before another request.")
            # A completed preview already consumed its own credit. Changed items
            # or unproven/currently different photos require this explicit new
            # request and a new credit; never auto-run.

        else:
            metadata = outfit.get("metadata") or {}
            legacy_url = outfit.get("flat_lay_url") or outfit.get("flatLayUrl") or metadata.get("flat_lay_url") or metadata.get("flatLayUrl")
            legacy_request = any(
                (outfit.get(key) or metadata.get(key)) in ("pending", "processing", "queued", "failed", "done")
                for key in ("flat_lay_status", "flatLayStatus"))
            if legacy_url or legacy_request:
                # No ledger means no provable debit. Never guess a refund/recharge.
                txn.update(outfit_ref, _projection("failed", None, now, error=LEGACY_ERROR,
                                                  error_code="legacy_request_needs_review"))
                return _response(outfit_id, {"status": "failed", "error": LEGACY_ERROR,
                                           "error_code": "legacy_request_needs_review"})
        user_doc = user_ref.get(transaction=txn)
        if not user_doc.exists:
            raise FlatlayRequestError(404, "User not found")
        remaining, period_start = _quota(user_doc.to_dict() or {}, now)
        if remaining <= 0:
            raise FlatlayRequestError(403, "No flat lay credits remaining.")
        # Snapshot authoritative wardrobe assets. A fabricated outfit item cannot
        # make the worker read another user's garment or a client-supplied URL.
        items = []
        asset_fields = ("name", "type", "category", "color", "material", "metadata",
                        "dominantColors", "dominant_colors", "imageUrl", "image_url",
                        "backgroundRemovedUrl", "background_removed_url")
        for item_id in _item_ids(outfit.get("items")):
            garment_doc = db.collection("wardrobe").document(item_id).get(transaction=txn)
            garment = (garment_doc.to_dict() or {}) if garment_doc.exists else {}
            if not _available_garment(garment, user_id):
                raise FlatlayRequestError(422, "One or more outfit items are no longer in your wardrobe.")
            job_doc = db.collection("garment_processing_jobs").document(item_id).get(transaction=txn)
            job = (job_doc.to_dict() or {}) if job_doc.exists else None
            reference = _reserved_reference(item_id, garment, job, user_id, request_id)
            items.append({"id": item_id, **{key: garment[key] for key in asset_fields if key in garment}, **reference})
        request = {
            "request_id": request_id, "outfit_id": outfit_id, "user_id": user_id, "app_data_epoch": epoch,
            "status": "pending", "credit_status": "reserved", "quota_period_start": period_start,
            "requested_at": now, "queued_at": now, "expires_at": now + PENDING_TIMEOUT_SECONDS,
            "items": items, "outfit_context": {key: outfit.get(key) for key in ("name", "style", "occasion", "mood")},
            "retryable": False, "error": None, "url": None,
        }
        txn.update(user_ref, {"quotas.flatlaysRemaining": remaining - 1, "quotas.lastRefillAt": period_start})
        txn.set(ledger_ref, request)
        txn.update(outfit_ref, _projection("pending", request_id, now, credit_status="reserved"))
        return _response(outfit_id, request)

    return reserve(db.transaction())


def claim_request(db, outfit_id, *, now=None, allow_claim=True):
    """Exactly one worker can move the private request from pending to processing."""
    now = _now() if now is None else now
    ledger_ref = db.collection(REQUESTS_COLLECTION).document(outfit_id)
    outfit_ref = db.collection("outfits").document(outfit_id)

    @firestore.transactional
    def claim(txn):
        ledger_doc = ledger_ref.get(transaction=txn)
        outfit_doc = outfit_ref.get(transaction=txn)
        outfit = (outfit_doc.to_dict() or {}) if outfit_doc.exists else {}
        if not ledger_doc.exists:
            return None
        request = ledger_doc.to_dict() or {}
        if request.get("outfit_id") != outfit_id:
            # A misplaced private record is not authority for this outfit, its
            # projection, or a credit settlement. Leave it untouched for review.
            return None
        writable = _request_writable(db, txn, request)
        available_outfit = outfit_doc.exists and _available_garment(outfit, request.get("user_id"))
        if not writable or not available_outfit:
            # Coordinator settles a pending reservation without provider work.
            return {**request, "preflight_error": "app_data_deleted" if not writable else "outfit_unavailable"} if request.get("status") == "pending" and request.get("credit_status") == "reserved" else None
        if request.get("status") != "pending" or request.get("credit_status") != "reserved":
            legacy_completed = request.get("status") == "done" and not _has_source_identity(request)
            changed_completed = (request.get("status") == "done"
                                 and (not _same_item_set(request, outfit)
                                      or not _same_owned_sources(db, txn, request)))
            # An old browser may overwrite its own projection with pending. The
            # private ledger wins, and reconciliation lets the legacy scan advance.
            if (request.get("status") in ("processing", "done", "failed")
                    and outfit_doc.exists and _owner_matches(outfit, request.get("user_id"))
                    and (_status(outfit) != request["status"]
                         or outfit.get("flat_lay_request_id") != request.get("request_id")
                         or changed_completed)):
                txn.update(outfit_ref, _projection(
                    "failed" if legacy_completed else "awaiting_consent" if changed_completed else request["status"],
                    request.get("request_id"), now,
                    url=None if changed_completed else request.get("url"),
                    error=LEGACY_ERROR if legacy_completed else None if changed_completed else request.get("error"),
                    retryable=False if legacy_completed else True if changed_completed else bool(request.get("retryable")),
                    error_code="legacy_request_needs_review" if legacy_completed else None if changed_completed else request.get("error_code"),
                    credit_status=request.get("credit_status"),
                ))
            return None
        if not allow_claim:
            return None
        claimed = {**request, "status": "processing", "started_at": now, "queued_at": None,
                   "expires_at": now + PROCESSING_TIMEOUT_SECONDS}
        # Hand invalid/expired jobs to the normal settlement path without ever
        # calling the provider. This keeps the refund and terminal state atomic.
        if not outfit_doc.exists or not _owner_matches(outfit, request.get("user_id")):
            claimed["preflight_error"] = "outfit_unavailable"
        elif not _has_source_identity(request):
            claimed["preflight_error"] = "legacy_request_needs_review"
        elif not _same_item_set(request, outfit) or not _same_owned_sources(db, txn, request):
            claimed["preflight_error"] = "outfit_changed"
        elif request.get("expires_at", 0) <= now:
            claimed["preflight_error"] = "queue_timeout"
        txn.update(ledger_ref, {key: claimed[key] for key in ("status", "started_at", "queued_at", "expires_at")})
        if outfit_doc.exists and _owner_matches(outfit, request.get("user_id")):
            txn.update(outfit_ref, _projection("processing", request["request_id"], now, credit_status="reserved"))
        return claimed

    return claim(db.transaction())



def _preparation_reports(request, reports):
    """Validate exact preparation proof for precisely the snapshotted raw inputs."""
    try:
        from .original_source import DEFAULT_BUCKET_NAME, is_owned_upload_path, request_original_path
    except ImportError:
        from original_source import DEFAULT_BUCKET_NAME, is_owned_upload_path, request_original_path
    if not isinstance(reports, list):
        return None
    expected = {}
    for item in request.get("items") or []:
        if not isinstance(item, dict):
            return None
        if "originalPreparation" in item:
            descriptor = item["originalPreparation"]
            if (not isinstance(descriptor, dict) or set(descriptor) != {"bucket", "sourceStoragePath"}
                    or descriptor.get("bucket") != DEFAULT_BUCKET_NAME
                    or not is_owned_upload_path(descriptor.get("sourceStoragePath"), request.get("user_id"))):
                return None
            expected[item.get("id")] = item
    if len(reports) != len(expected):
        return None
    accepted = []
    seen = set()
    for report in reports:
        if not isinstance(report, dict) or set(report) != {"id", "sourceStoragePath", "sourceGeneration", "originalStoragePath", "sha256"}:
            return None
        garment_id = report.get("id")
        if not isinstance(garment_id, str) or garment_id not in expected or garment_id in seen:
            return None
        item = expected[garment_id]
        try:
            path = request_original_path(garment_id, request["request_id"])
        except (ValueError, TypeError, KeyError):
            return None
        if (report.get("originalStoragePath") != path or item.get("originalStoragePath") != path
                or report.get("sourceStoragePath") != item["originalPreparation"]["sourceStoragePath"]
                or not isinstance(report.get("sourceGeneration"), str)
                or re.fullmatch(r"[0-9]+", report["sourceGeneration"]) is None
                or not isinstance(report.get("sha256"), str)
                or re.fullmatch(r"[0-9a-f]{64}", report["sha256"]) is None):
            return None
        seen.add(garment_id)
        accepted.append(dict(report))
    return accepted


def admit_provider_request(db, outfit_id, request_id, prepared_originals, *, now=None):
    """Fence the one paid provider call after originals are prepared, before I/O.

    This transaction never settles credits. False prevents stale/duplicate work;
    the coordinator uses the existing settlement path. A committed admission is
    deliberately ambiguous if the process dies before learning provider outcome.
    """
    now = _now() if now is None else now
    ledger_ref = db.collection(REQUESTS_COLLECTION).document(outfit_id)
    outfit_ref = db.collection("outfits").document(outfit_id)

    @firestore.transactional
    def admit(txn):
        ledger_doc = ledger_ref.get(transaction=txn)
        outfit_doc = outfit_ref.get(transaction=txn)
        request = (ledger_doc.to_dict() or {}) if ledger_doc.exists else {}
        outfit = (outfit_doc.to_dict() or {}) if outfit_doc.exists else {}
        expires_at = request.get("expires_at")
        if (request.get("outfit_id") != outfit_id
                or request.get("request_id") != request_id or request.get("status") != "processing"
                or request.get("credit_status") != "reserved"
                or request.get("provider_admitted_at") is not None
                or not isinstance(expires_at, (int, float)) or isinstance(expires_at, bool)
                or not math.isfinite(expires_at) or expires_at <= now
                or not _available_garment(outfit, request.get("user_id")) or not _same_item_set(request, outfit)):
            return False
        if not _request_writable(db, txn, request):
            return False
        reports = _preparation_reports(request, prepared_originals)
        if reports is None:
            return False
        if not _same_owned_sources(db, txn, request):
            return False
        txn.update(ledger_ref, {"prepared_originals": reports, "provider_admitted_at": now})
        return True

    return admit(db.transaction())


def finish_request(db, outfit_id, request_id, *, url=None, error=None,
                   error_code=None, retryable=True, now=None, expired_only=False):
    """Settle once, matching the private reservation; late workers cannot overwrite.

    A failed output returns the product credit, regardless of whether a provider
    may have charged us. It does not claim the provider request was unbilled.
    """
    now = _now() if now is None else now
    ledger_ref = db.collection(REQUESTS_COLLECTION).document(outfit_id)
    outfit_ref = db.collection("outfits").document(outfit_id)

    @firestore.transactional
    def finish(txn):
        ledger_doc = ledger_ref.get(transaction=txn)
        request = (ledger_doc.to_dict() or {}) if ledger_doc.exists else {}
        if (request.get("outfit_id") != outfit_id
                or request.get("request_id") != request_id or request.get("status") not in ("pending", "processing")
                or request.get("credit_status") != "reserved"):
            return False
        if expired_only and request.get("expires_at", now + 1) > now:
            return False
        if error_code == "request_changed" and request.get("provider_admitted_at") is not None:
            # A duplicate admission rejection is not proof the first provider
            # call stopped. Leave its reservation to the real result or expiry;
            # never refund it and enable another paid request in the meantime.
            return False
        outfit_doc = outfit_ref.get(transaction=txn)
        outfit = (outfit_doc.to_dict() or {}) if outfit_doc.exists else {}
        user_ref = db.collection("users").document(request["user_id"])
        user_doc = user_ref.get(transaction=txn)
        user = user_doc.to_dict() or {} if user_doc.exists else {}
        writable = user_doc.exists and app_data_write_allowed(user, request.get("app_data_epoch", 0))
        result_url, result_error, result_code, can_offer_retry = url, error, error_code, retryable
        if not writable:
            result_url, result_error, result_code, can_offer_retry = None, "App data was cleared.", "app_data_deleted", False
        owned_outfit = outfit_doc.exists and _owner_matches(outfit, request["user_id"])
        same_items = (owned_outfit and _available_garment(outfit, request["user_id"])
                      and _same_item_set(request, outfit) and _same_owned_sources(db, txn, request))
        if not same_items:
            # The provider may have completed an obsolete composition. Never
            # attach it to the edited outfit. Its product credit is still settled
            # exactly once; this makes no claim about the provider's own billing.
            if result_url:
                can_offer_retry = True  # confirmed output, so no ambiguous attempt remains
            result_url = None
            if writable and error_code not in ("provider_outcome_unknown", "worker_outcome_unknown"):
                result_error = "This outfit changed before its preview was ready. Request a new preview for the updated items."
                result_code = "outfit_changed" if owned_outfit else "outfit_unavailable"
                if not _has_source_identity(request):
                    result_error, result_code = LEGACY_ERROR, "legacy_request_needs_review"
                    can_offer_retry = False
        credit_status = "consumed" if result_url else "refund_needs_review"
        if not result_url and user_doc.exists:
            user = user_doc.to_dict() or {}
            remaining, period_start = _quota(user, now)
            # A reservation from a prior weekly window is already replaced by
            # the fresh allowance. Do not add an extra credit to the new period.
            if period_start == request.get("quota_period_start"):
                remaining += 1
            txn.update(user_ref, {"quotas.flatlaysRemaining": remaining, "quotas.lastRefillAt": period_start})
            credit_status = "refunded"
        can_retry = (not result_url and can_offer_retry and credit_status == "refunded"
                     and result_code not in ("provider_outcome_unknown", "worker_outcome_unknown"))
        status = "done" if result_url else "failed"
        changes = {"status": status, "url": result_url, "error": result_error, "error_code": result_code,
                   "credit_status": credit_status, "retryable": bool(can_retry),
                   "finished_at": now, "queued_at": None, "expires_at": None}
        txn.update(ledger_ref, changes)
        if owned_outfit and writable and _available_garment(outfit, request["user_id"]):
            txn.update(outfit_ref, _projection(status, request_id, now, url=result_url, error=result_error,
                                              retryable=can_retry, error_code=result_code,
                                              credit_status=credit_status))
        return True

    return finish(db.transaction())
