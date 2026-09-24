# Background image worker

The worker runs as Railway service `background-processor`, with `backend/worker`
as its root and `python main.py` as its start command. Follow the canonical
[operator playbook](../../docs/technical/EASYOUTFIT_OPERATOR_PLAYBOOK.md) for
production identity and deployment. No deployment is implied by this source.

## Execution

- A lightweight coordinator polls every five seconds. It supervises one garment
  process and one flatlay process independently; neither runs inference in the
  coordinator. Expiry and lease recovery run regardless of either job's progress.
- Garments use the private `garment_processing_jobs` collection. An attempt and
  360-second lease are committed before process launch. At most three automatic
  attempts run for one photo, with 30/120-second backoff between failures.
- Original preparation, storage and background removal run in a disposable job.
  Alpha inference has a separate 240-second process budget and fallback has 60
  seconds. An independent watchdog enforces the remaining whole-job budget even
  when database I/O blocks the coordinator. Termination covers descendant groups.
- The original is published before background removal. Original and cutout assets
  use immutable `items/<id>/attempts/<attempt>/...` objects; transaction fences
  prevent a stale process from publishing over a changed photo or newer attempt.
- Paid flatlays retain the private request ledger, original-reference inputs,
  explicit user request and existing credit settlement. A stopped or unconfirmed
  provider job is not automatically retried. Coordinator expiry settles its
  reservation under the existing ambiguity policy.
- A flatlay can prepare originals for its selected items before their cutouts run.
  It reads only snapshotted owned upload objects from the configured bucket,
  normalizes them without inference, and saves immutable request-specific PNGs.
  A transaction checks ownership/source changes and records preparation provenance
  before admitting the provider call. A stalled unrelated cutout cannot block it.

## Failure and retry

Saved originals remain usable if a cutout fails. Inspect the private attempt
record and public `processing_error_code`, `processing_attempt_count`,
`processing_attempt_id` and `processing_retryable` projection. Missing or invalid
photos receive a visible failure without expensive processing. Existing
`codex_pending` upload-analysis records are not adopted until promoted to pending.

A signed-in owner can explicitly retry one terminal failed garment using
`POST /api/wardrobe/{id}/retry-processing` with its `expected_attempt_id`. Duplicate
requests acknowledge the same run. This starts a new bounded run for that item;
changing a public retry count/status cannot reset the authoritative budget.
Do not use bulk status resets as a recovery mechanism.

## Configuration

Firebase access comes from platform-managed `FIREBASE_PROJECT_ID`,
`FIREBASE_CLIENT_EMAIL`, and `FIREBASE_PRIVATE_KEY` (plus existing optional account
fields). The existing storage bucket is unchanged. Only the flatlay child uses
`OPENAI_API_KEY`; garment and inference children do not receive it. Existing
`EASYOUTFIT_OPENAI_*` model/timeout/quality overrides remain unchanged. No new
provider, model, quota, billing or resource-size choice is introduced.

No timing, memory or throughput result is claimed from configuration alone.
Inspect actual runtime signals before diagnosing an infrastructure failure as OOM.

## Verification and release

See [Goal 2 handoff](../../docs/technical/IMAGE_WORKER_GOAL2_HANDOFF.md) for the
state contract, tests, release order, rollback constraints and live verification
that remains required. Worker modules are self-contained because the Railway
worker root cannot depend on `backend/src`. Mirrored lifecycle modules have
byte-parity tests.

Credential-free process checks, from `backend`:

```sh
python -m unittest discover -s tests -p 'test_process_supervisor.py' -v
python -m unittest discover -s tests -p 'test_worker_coordinator.py' -v
```
