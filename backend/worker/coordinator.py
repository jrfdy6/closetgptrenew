"""Small, dependency-injected scheduler; image work never runs in its tick.

One garment slot and one flatlay slot are independent. Storage failures in one
lane do not prevent the other lane's polling or the expiry sweep. A terminated
paid child is never automatically replayed: the existing ledger expiry settles
its ambiguous outcome.
"""
from dataclasses import dataclass

try:
    from .garment_errors import garment_failure_code, safe_diagnostics
except ImportError:
    from garment_errors import garment_failure_code, safe_diagnostics


@dataclass
class GarmentRun:
    claim: dict
    process: object
    published_original: dict | None = None


class WorkerCoordinator:
    def __init__(self, *, expire_flatlays, recover_garments, garment_candidates,
                 claim_garment, start_garment, publish_original, finish_garment,
                 flatlay_candidates, start_flatlay, legacy_reconcile=None,
                 report=None):
        self.expire_flatlays = expire_flatlays
        self.recover_garments = recover_garments
        self.garment_candidates = garment_candidates
        self.claim_garment = claim_garment
        self.start_garment = start_garment
        self.publish_original = publish_original
        self.finish_garment = finish_garment
        self.flatlay_candidates = flatlay_candidates
        self.start_flatlay = start_flatlay
        self.legacy_reconcile = legacy_reconcile or (lambda: None)
        self.report = report or (lambda _event, _fields: None)
        self.garment = None
        self.flatlay = None

    def _safe(self, phase, action):
        try:
            action()
        except Exception as error:
            # Never emit URLs, credentials or exception payloads from providers.
            self.report("coordinator_error", {"phase": phase, "type": type(error).__name__})

    def tick(self):
        self._safe("flatlay_expiry", self.expire_flatlays)
        self._safe("garment_recovery", self.recover_garments)
        self._safe("garment_poll", self._poll_garment)
        self._safe("flatlay_poll", self._poll_flatlay)
        self._safe("garment_dispatch", self._dispatch_garment)
        self._safe("flatlay_dispatch", self._dispatch_flatlay)
        self._safe("legacy_projection", self.legacy_reconcile)

    def _publish_original(self, run, progress):
        original = {key: progress.get(key) for key in ("originalStoragePath", "originalUrl")}
        if not all(original.values()) or original == run.published_original:
            return True
        current = self.publish_original(run.claim["garment_id"], run.claim["attempt_id"], original)
        if current:
            run.published_original = original
        return current

    def _poll_garment(self):
        run = self.garment
        if run is None:
            return
        # Poll/reap before any cloud write. A storage outage must not defer local
        # process cleanup; the terminal summary remains cached until settlement.
        outcome = run.process.poll()
        progress = (outcome or {}).get("progress") or run.process.read_progress() or {}
        if not self._publish_original(run, progress):
            run.process.terminate("superseded")
            outcome = run.process.poll()
        if outcome is None:
            return
        # The progress file can land immediately before termination. Retain a
        # valid original even when background removal subsequently fails.
        self._publish_original(run, outcome.get("progress") or {})
        result = outcome.get("result")
        result = result if isinstance(result, dict) else {}
        valid_result = outcome["status"] == "succeeded" and all(
            result.get(key) for key in ("backgroundRemovedUrl", "thumbnailUrl",
                                       "backgroundRemovedStoragePath", "thumbnailStoragePath")
        )
        error_code = None if valid_result else (
            "worker_timeout" if outcome["status"] == "timed_out" else
            "item_changed" if outcome["status"] == "superseded" else
            "invalid_result" if outcome["status"] == "succeeded" else
            garment_failure_code(result["error_code"]) if "error_code" in result else
            garment_failure_code(result["error"]) if "error" in result else
            "worker_crashed"
        )
        accepted = self.finish_garment(run.claim["garment_id"], run.claim["attempt_id"],
                                       result=result if valid_result else None,
                                       error_code=error_code)
        fields = {"status": outcome["status"], "accepted": bool(accepted),
                  "attempt": run.claim["attempt_count"]}
        if not valid_result:
            fields["diagnostics"] = safe_diagnostics(result.get("diagnostics"))
        self.report("garment_finished", fields)
        run.process.close()
        self.garment = None

    def _poll_flatlay(self):
        if self.flatlay is None:
            return
        outcome = self.flatlay.poll()
        if outcome is None:
            return
        self.report("flatlay_child_finished", {"status": outcome["status"]})
        self.flatlay.close()
        self.flatlay = None

    def _dispatch_garment(self):
        if self.garment is not None:
            return
        for garment_id in self.garment_candidates():
            claim = self.claim_garment(garment_id)
            if claim is None:
                continue
            try:
                process = self.start_garment(claim)
            except Exception:
                self.finish_garment(garment_id, claim["attempt_id"], error_code="worker_start_failed")
                raise
            self.garment = GarmentRun(claim, process)
            self.report("garment_started", {"attempt": claim["attempt_count"]})
            break

    def _dispatch_flatlay(self):
        if self.flatlay is not None:
            return
        for outfit_id in self.flatlay_candidates():
            # Claiming and at-most-once provider processing happen in the child
            # through the existing private flatlay lifecycle transaction.
            self.flatlay = self.start_flatlay(outfit_id)
            self.report("flatlay_child_started", {})
            break

    def close(self):
        # Keep unfinished durable leases/requests intact; recovery/expiry is the
        # authority after shutdown, including an unknown paid-provider outcome.
        if self.garment is not None:
            self.garment.process.terminate("shutdown")
            self.garment.process.close()
            self.garment = None
        if self.flatlay is not None:
            self.flatlay.terminate("shutdown")
            self.flatlay.close()
            self.flatlay = None
