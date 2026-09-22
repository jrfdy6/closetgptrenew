"""Transactional flat-lay lifecycle, shared verbatim with the isolated worker root.

The private flat_lay_requests collection is authoritative. Outfit flat-lay
fields are a server-owned projection, never proof of consent or credit payment.
No provider call runs inside a transaction (Firestore may retry its callback).
"""
from datetime import datetime, timezone
from uuid import uuid4
from firebase_admin import firestore

try:  # API package and isolated Railway worker root.
    from .subscription_utils import current_quota, QuotaNeedsReview, WEEKLY_ALLOWANCE_SECONDS
except ImportError:
    from subscription_utils import current_quota, QuotaNeedsReview, WEEKLY_ALLOWANCE_SECONDS

REQUESTS_COLLECTION = "flat_lay_requests"
WEEK_SECONDS = WEEKLY_ALLOWANCE_SECONDS
PENDING_TIMEOUT_SECONDS = 15 * 60
PROCESSING_TIMEOUT_SECONDS = 10 * 60
LEGACY_ERROR = "This earlier preview needs review before another request. No new credit was used."


class FlatlayRequestError(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _now():
    return int(datetime.now(timezone.utc).timestamp())


def _owner_matches(data, user_id):
    owners = [data[key] for key in ("user_id", "userId") if data.get(key)]
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
    try:
        return current_quota(data, now)
    except QuotaNeedsReview as error:
        raise FlatlayRequestError(409, "Your flat lay credits need account review. No credit was used.") from error


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


def reserve_request(db, outfit_id, user_id, *, now=None, request_id=None):
    """Reserve one credit and queue one explicit request in the same commit."""
    now = _now() if now is None else now
    request_id = request_id or uuid4().hex
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
        ledger_doc = ledger_ref.get(transaction=txn)
        previous = (ledger_doc.to_dict() or {}) if ledger_doc.exists else {}
        if previous:
            if previous.get("user_id") != user_id:
                raise FlatlayRequestError(409, "This preview needs review before another request.")
            same_items = _same_item_set(previous, outfit)
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
            # require this explicit new request and a new credit; never auto-run.

        else:
            legacy_status = _status(outfit)
            legacy_url = outfit.get("flat_lay_url") or outfit.get("flatLayUrl") or (outfit.get("metadata") or {}).get("flat_lay_url") or (outfit.get("metadata") or {}).get("flatLayUrl")
            if legacy_status == "done" and legacy_url:
                return _response(outfit_id, {"status": "done", "url": legacy_url})
            if legacy_status in ("pending", "processing", "failed", "done"):
                # No ledger means no provable debit. Never guess a refund/recharge.
                txn.update(outfit_ref, _projection("failed", None, now, error=LEGACY_ERROR,
                                                  error_code="legacy_request_needs_review"))
                return _response(outfit_id, {"status": "failed", "error": LEGACY_ERROR,
                                           "error_code": "legacy_request_needs_review"})
        user_doc = user_ref.get(transaction=txn)
        if not user_doc.exists:
            raise FlatlayRequestError(404, "User not found")
        quota = _quota(user_doc.to_dict() or {}, now)
        remaining, period_start = quota["flatlaysRemaining"], quota["lastRefillAt"]
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
            if not garment or not _owner_matches(garment, user_id):
                raise FlatlayRequestError(422, "One or more outfit items are no longer in your wardrobe.")
            items.append({"id": item_id, **{key: garment[key] for key in asset_fields if key in garment}})
        request = {
            "request_id": request_id, "outfit_id": outfit_id, "user_id": user_id,
            "status": "pending", "credit_status": "reserved", "quota_period_start": period_start,
            "requested_at": now, "queued_at": now, "expires_at": now + PENDING_TIMEOUT_SECONDS,
            "items": items, "outfit_context": {key: outfit.get(key) for key in ("name", "style", "occasion", "mood")},
            "retryable": False, "error": None, "url": None,
        }
        quota["flatlaysRemaining"] = remaining - 1
        txn.update(user_ref, {"quotas": quota})
        txn.set(ledger_ref, request)
        txn.update(outfit_ref, _projection("pending", request_id, now, credit_status="reserved"))
        return _response(outfit_id, request)

    return reserve(db.transaction())


def claim_request(db, outfit_id, *, now=None):
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
            if _status(outfit) in ("pending", "processing"):
                txn.update(outfit_ref, _projection("failed", None, now, error=LEGACY_ERROR,
                                                  error_code="legacy_request_needs_review"))
            return None
        request = ledger_doc.to_dict() or {}
        if request.get("status") != "pending" or request.get("credit_status") != "reserved":
            # An old browser may overwrite its own projection with pending. The
            # private ledger wins, and reconciliation lets the legacy scan advance.
            if (request.get("status") in ("processing", "done", "failed")
                    and outfit_doc.exists and _owner_matches(outfit, request.get("user_id"))
                    and (_status(outfit) != request["status"]
                         or outfit.get("flat_lay_request_id") != request.get("request_id")
                         or (request["status"] == "done" and not _same_item_set(request, outfit)))):
                changed_completed = request["status"] == "done" and not _same_item_set(request, outfit)
                txn.update(outfit_ref, _projection(
                    "awaiting_consent" if changed_completed else request["status"], request.get("request_id"), now,
                    url=None if changed_completed else request.get("url"),
                    error=None if changed_completed else request.get("error"),
                    retryable=True if changed_completed else bool(request.get("retryable")),
                    error_code=None if changed_completed else request.get("error_code"),
                    credit_status=request.get("credit_status"),
                ))
            return None
        claimed = {**request, "status": "processing", "started_at": now, "queued_at": None,
                   "expires_at": now + PROCESSING_TIMEOUT_SECONDS}
        # Hand invalid/expired jobs to the normal settlement path without ever
        # calling the provider. This keeps the refund and terminal state atomic.
        if not outfit_doc.exists or not _owner_matches(outfit, request.get("user_id")):
            claimed["preflight_error"] = "outfit_unavailable"
        elif not _same_item_set(request, outfit):
            claimed["preflight_error"] = "outfit_changed"
        elif request.get("expires_at", 0) <= now:
            claimed["preflight_error"] = "queue_timeout"
        txn.update(ledger_ref, {key: claimed[key] for key in ("status", "started_at", "queued_at", "expires_at")})
        if outfit_doc.exists and _owner_matches(outfit, request.get("user_id")):
            txn.update(outfit_ref, _projection("processing", request["request_id"], now, credit_status="reserved"))
        return claimed

    return claim(db.transaction())


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
        if (request.get("request_id") != request_id or request.get("status") not in ("pending", "processing")
                or request.get("credit_status") != "reserved"):
            return False
        if expired_only and request.get("expires_at", now + 1) > now:
            return False
        outfit_doc = outfit_ref.get(transaction=txn)
        outfit = (outfit_doc.to_dict() or {}) if outfit_doc.exists else {}
        result_url, result_error, result_code, can_offer_retry = url, error, error_code, retryable
        owned_outfit = outfit_doc.exists and _owner_matches(outfit, request["user_id"])
        same_items = owned_outfit and _same_item_set(request, outfit)
        if not same_items:
            # The provider may have completed an obsolete composition. Never
            # attach it to the edited outfit. Its product credit is still settled
            # exactly once; this makes no claim about the provider's own billing.
            if result_url:
                can_offer_retry = True  # confirmed output, so no ambiguous attempt remains
            result_url = None
            if error_code not in ("provider_outcome_unknown", "worker_outcome_unknown"):
                result_error = "This outfit changed before its preview was ready. Request a new preview for the updated items."
                result_code = "outfit_changed" if owned_outfit else "outfit_unavailable"
        user_ref = db.collection("users").document(request["user_id"])
        user_doc = user_ref.get(transaction=txn) if not result_url else None
        credit_status = "consumed" if result_url else "refund_needs_review"
        if not result_url and user_doc.exists:
            user = user_doc.to_dict() or {}
            try:
                quota = current_quota(user, now)
            except QuotaNeedsReview:
                # The debit is proven, but corrupt/missing quota state cannot be
                # safely reconstructed. Complete the job with an explicit review
                # status; do not guess a refund or offer another paid attempt.
                quota = None
            if quota is not None:
                # Prior-period reservations are replaced by the new allowance.
                # A downgrade within the same period still refunds its debit.
                if quota["lastRefillAt"] == request.get("quota_period_start"):
                    refunded = quota["flatlaysRemaining"] + 1
                    if refunded > 30 or (refunded > quota["highestAllowanceGranted"]
                                         and not quota.get("highestAllowanceInferred")):
                        quota = None  # Recorded grant and outstanding debit disagree.
                    else:
                        quota["flatlaysRemaining"] = refunded
                        # A proven legacy debit is additional evidence about its
                        # unrecorded grant. Keep that inference visible to audit.
                        quota["highestAllowanceGranted"] = max(quota["highestAllowanceGranted"], refunded)
                if quota is not None:
                    txn.update(user_ref, {"quotas": quota})
                    credit_status = "refunded"
        can_retry = not result_url and can_offer_retry and credit_status == "refunded"
        status = "done" if result_url else "failed"
        changes = {"status": status, "url": result_url, "error": result_error, "error_code": result_code,
                   "credit_status": credit_status, "retryable": bool(can_retry),
                   "finished_at": now, "queued_at": None, "expires_at": None}
        txn.update(ledger_ref, changes)
        if owned_outfit:
            txn.update(outfit_ref, _projection(status, request_id, now, url=result_url, error=result_error,
                                              retryable=can_retry, error_code=result_code,
                                              credit_status=credit_status))
        return True

    return finish(db.transaction())
