# Dependable image processing — Goal 2 handoff

This change prevents a slow or crashed background-removal job from occupying the
worker indefinitely. It builds on Goal 1 commit
`bf16ab125e7b7b51ae62e4cc3fdc7cfe1eb49f8f`; the draft PR is stacked on
`codex/onboarding-durable-progress`. It implements the image-processing portion
of the approved onboarding plan. Onboarding UI, recommendation changes, result
presentation and deployment remain later goals.

## Execution and recovery

The coordinator runs one garment subprocess and one flatlay subprocess. It
imports no rembg, NumPy or ONNX runtime and performs no image inference. Each
tick separately handles flatlay expiry, garment lease recovery, result polling,
dispatch and legacy projection repair. A failed database operation in one phase
does not skip the remaining phases. Query streams have bounded timeouts; cloud
transactions may still delay a tick, so local process deadlines are enforced
independently of polling.

Garment jobs have a persisted attempt and a 360-second lease before launch. Each
photo receives at most three automatic attempts per run, with 30/120-second
backoff. An alpha inference subprocess has a 240-second budget; an invalid or
failed alpha output can use one 60-second fallback subprocess. The remaining
whole-job deadline limits both. An independent watchdog terminates and reaps
the job and registered descendant groups even while the coordinator is blocked
on database I/O. The Linux supervisor adopts and reaps orphan descendants.
There is no in-process inference fallback.

An expired lease cannot publish a result before the recovery sweep. Recovery
consumes the already-recorded attempt, requeues eligible work, and stops after
the retry budget. Deleted items and owner conflicts retire private pending jobs
instead of filling the due queue forever. Legacy pending items are adopted
through a paginated scan; `codex_pending` analysis placeholders are not adopted.
Public status/count edits cannot reset the private retry budget.

The flatlay subprocess continues to claim the existing private request ledger.
Its timeout remains 600 seconds. Coordinator expiry and the existing settlement
transactions remain authoritative; a killed child or unknown provider outcome
does not trigger an automatic provider retry or a guessed credit adjustment.

## Images and authority

`garment_processing_jobs/{itemId}` is server-owned and explicitly denied to
clients in both tracked Firestore rules files. It records schema version,
owner/source identity, metadata revision, generation, attempt history, lease,
next-attempt time, original provenance and result disposition. The wardrobe
document receives only a public processing projection and allowlisted assets.

The job normalizes and uploads the original before background removal. All
assets use immutable `items/<id>/attempts/<attempt>/...` objects with a creation
precondition. Publication transactions require the current attempt, live lease,
owner, source and edit revision. A stale process cannot replace an object or
publish into a newer item state. Metadata edits invalidate its result without
granting a new automatic retry budget.

A valid published original remains available across later failures and explicit
retries of the same photo. Its publishing attempt is stored separately from the
latest processing attempt. Replacing the source photo clears old original,
cutout, processed and thumbnail fields; the new attempt's revision is calculated
after that cleanup. Same-photo metadata changes preserve existing valid assets.
Unreferenced immutable attempt objects are retained; this change does not delete
historical assets or add a cleanup job.

Flatlay reservation prefers the exact original path from a protected job, checks
its owned garment/source identity and uses the attempt that actually published
it. Later processing cannot change a reserved reference. When a selected item's
cutout has not started, the reservation can instead snapshot its owned raw upload
object under `wardrobe/<verified-user-id>/<leaf>` in the configured bucket. Only
the exact supported Google Storage/Firebase URL formats can resolve to that
object; arbitrary URLs, other buckets, foreign users and path escapes are denied.

The flatlay child reads that raw object through the Storage SDK with byte limits,
finite timeouts and a generation precondition. It normalizes the original without
inference, then writes a private immutable
`items/<id>/flatlay-requests/<request-id>/original.png`. This allows selected later
items to reach the provider while an unrelated earlier cutout is still stalled.
These copies do not alter the garment queue or its original provenance. All
prepared references remain subject to aggregate byte/pixel limits. Before the
provider call, a transaction rechecks the live reserved request, outfit/item
ownership and source fingerprints, records source generations and PNG digests,
and admits that request only once. Preparation failures use the existing atomic
credit settlement; no provider attempt is made with partial or stale references.
Reservation fixes the source URL/path, not its storage generation. The generation
is captured when preparation reads the object. The digest records preparation
provenance; it is not a second digest comparison after reference loading. The
reference loader reads the immutable request output with its own generation
precondition.

Client storage-path fields are never authority. The fixed legacy
`items/<id>/original.png` path remains compatible only when no private garment job
exists and no eligible owned raw source is present. Missing/invalid protected
references without a safe preparation path fail admission before reservation.
The existing original-image validation and storage generation checks remain.

## Failure and retry contract for Goal 3

The public projection includes `processing_status`, `processing_attempt_id`,
`processing_attempt_count`, `processing_error_code`, sanitized error text,
`processing_retryable`, `processing_retry_action`, `processing_next_attempt_at`
and `processing_expires_at`. UI counts must continue to use saved usable originals
and categories, not completed cutouts. Do not restore public bulk status resets.

`POST /api/wardrobe/{itemId}/retry-processing` accepts only
`{"expected_attempt_id":"<terminal failed attempt>"}`. It verifies a Firebase ID
token with revocation checking and derives ownership from that identity. The
expected failure token makes a repeated request acknowledge the same replacement
run, even if it has already started or completed. A new failed run requires its
new failure token. Foreign/missing items return 404; stale or unavailable retry
state returns 409; verification/storage failures fail closed.

Temporary download, inference and storage failures use bounded retry; an
unreadable or unsupported source is terminal and asks for a replacement photo.
An unchanged invalid image cannot start another run through the retry endpoint.
Failure envelopes use a finite safe code mapping rather than exception text.
Coordinator events include `schema_version: 1`, phase/status and attempt number;
they omit photo URLs, answers, credentials and provider exception payloads.

## Verification

The final macOS backend run completed 312 tests: 311 passed and the Linux-only
orphan-reaping test was skipped. Python compilation and `git diff --check` passed.
The exact pushed revision's Linux workflow result is reported in the draft PR
checks and delivery handoff; Linux execution is required before Goal 2 delivery.

The backend suite covers transactional claim/lease/recovery, ownership and edit
fences, immutable asset paths, original retention, duplicate/manual retries,
protected flatlay snapshots and the existing settlement contracts. Real local
subprocess tests cover hangs, crashes, watchdog execution without coordinator
polling, nested process groups, cancellation races and subsequent job progress.
Retry endpoint tests exercise its actual route registration and HTTP boundary.
The failure-envelope integration suite carries child output through the real
coordinator into lifecycle projections using a transactional database double.
The stalled-cutout scenario holds a real garment subprocess open while the real
flatlay flow prepares later selected JPEGs, preserves decoded pixels, reaches a
fake provider once and consumes one reservation. No canonical originals or
cutouts exist for those selected items beforehand.

The authorized white-tee fixture was exercised through real original-image
normalization and an injected model failure. Its 2048 × 1536 RGBA pixels were
preserved exactly and original progress was emitted before the failure. Source
SHA-256: `77f7caa3b19fad9231f777a9d0623a1a4d3fe609a7456c63309f60e65e95c25f`.
This is original-preservation and failure-path evidence, not a successful rembg
run or a visual cutout-quality pass. No model was downloaded.

Reproducible backend command, using the existing Python 3.11 environment:

```sh
cd backend
python -m unittest discover -s tests -p 'test_*.py'
```

`.github/workflows/image-worker-process-tests.yml` runs the real subprocess and
coordinator suites on Ubuntu 24.04/Python 3.11. These two suites need only the
standard library, no credentials, production packages, image models or provider
calls. Lifecycle mirrors in `worker` and `src/services` are byte-parity checked
because Railway's worker service root is `backend/worker`.

No frontend application code changed in this goal. Goal 1's frontend build and
test results remain its baseline evidence; no new browser or mobile pass is
claimed. No live Firestore/emulator transaction, Storage write, Railway job,
provider request, billing operation, production deployment or memory/throughput
benchmark was performed. Test doubles do not replace those integration checks.

## Goal 6 release gates and rollback

Use the canonical [operator playbook](EASYOUTFIT_OPERATOR_PLAYBOOK.md). Confirm
Goal 1's Firebase Admin environment prerequisites separately. This change does
not provision credentials or alter provider/model/price configuration.

1. Verify and deploy the protected rules and compatible API, including the
   versioned-original reservation reader and owned retry endpoint. Verify ordinary
   single-field indexes for lease/due-time queries; no composite index or
   destructive migration is introduced.
2. Retire the previous worker deliberately before enabling this coordinator.
   The old worker does not respect the new private leases and writes mutable
   asset paths, so running both during an uncontrolled overlap is unsafe. Handle
   in-flight paid requests through their existing ledger/expiry policy.
3. Deploy the matching worker revision. Verify actual Linux watchdog/descendant
   cleanup, expired lease recovery, following garment and flatlay progress, and
   request/credit settlement against the intended environment.
4. Exercise the full authorized photo set and real phone uploads; inspect cutout
   and flatlay identity/color/silhouette against originals. Confirm an actual
   image is delivered before recording a visual pass. Check leave/return/retry,
   missing-source guidance and failure recovery in the later UI.

Record exact API/worker/frontend revisions, deployed rules and smoke evidence.
Rollbacks must preserve private jobs, original provenance, request ledgers and
attempt objects. Do not restore an API that reads only legacy originals after
versioned assets have been adopted. Stop dispatch as needed and retain compatible
readers while preparing a forward fix or explicitly validated rollback; the old
worker is not a safe blind fallback. No merge or deployment is part of Goal 2.
