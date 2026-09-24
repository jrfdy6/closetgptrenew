# App data clearing and privacy controls

Clear app data is an authenticated, asynchronous operation. It does not delete the Firebase Auth account or cancel a subscription. `DELETE /api/privacy-data?data_type=all` returns HTTP 202 with a job ID and `completed: false`; `GET /api/privacy-data/status` reports the current owner's job. Repeating the same request while pending returns that job. Repeating it after a failed pass resumes its existing cursor and epoch. A failed job remains fenced until retry.

The clear removes wardrobe records, owned original/processed photos and flatlays, saved outfits and history, quiz/persona/profile content, derived preferences and analytics, and per-user processing jobs. It resets onboarding. It preserves authentication identity, subscription/billing and flatlay credit entitlements, privacy choices, and minimal financial/anti-duplication receipts. Shared avatar assets whose ownership cannot be established are retained; the user's reference is removed. Automatic retention periods are unsupported and non-null retention settings receive HTTP 422.

## Durable state and writer contract

- `users/{uid}.app_data_epoch` is a non-negative integer, initially zero. An accepted clear increments it in the same transaction that creates `app_data_deletion_jobs/{job_id}` and marks the user pending.
- User deletion states `pending`, `running`, and `failed` deny app-data writes. Completion allows new writes under the new epoch.
- `require_app_data_writable(db, uid, expected_epoch=..., transaction=...)` reads the account inside the writer's transaction. Long operations capture the epoch before work, and transaction retries retain the originally captured epoch. A missing account fails closed.
- Garment, flatlay, Codex, RAG and learning jobs preserve their starting epoch. Final publications re-check it. A late flatlay result is not published; the existing financial settlement transaction refunds its product credit at most once.
- `wardrobe_asset_owners/{item_id}` reserves a garment's globally named storage prefix for its verified owner. This minimal private receipt survives deletion and prevents another account from reusing a deleted garment ID and sharing its image prefix.

The deletion worker processes bounded pages with a persisted collection plan, owner/cursor paging for retained ledgers, a lease token and transactional checks before every database mutation. It records storage prefixes before removing their database owner records. Storage cleanup waits 600 seconds from acceptance for existing image workers to drain; object deletion uses generation preconditions. Worker subprocess deadlines must not exceed that bound. An old lease cannot complete or fail a replacement lease's job.

Run the existing dedicated worker (`python -m src.worker.gamification_runner` from `backend/`) to poll `process_deletion_jobs(db, bucket, limit=2, max_records=100)`. The image worker's `app_data_privacy.py`, `garment_lifecycle.py` and `flatlay_lifecycle.py` are exact mirrors of the API modules. Do not deploy only one side of this contract.

## Optional processing

`share_analytics` defaults false. Optional telemetry writes require it plus `allow_data_collection`. Learned preference reads/writes additionally follow `allow_personalization`, including fresh checks before cached/derived values are used. A denied telemetry write cannot trigger downstream favorite learning. Explicit user actions and billing receipts are not optional analytics. No unsupported retention schedule is silently accepted.

## Verification

Credential-free tests cover real route handlers and transactional fakes for revoked/malformed authentication; queue/final-publication fences; clear completion, interruption and resume; old lease/epoch rejection; credit refund idempotency; bounded receipt pages; storage generation matching; foreign-owner preservation; and deletion of orphaned nested records. Dedicated emulator evidence is kept outside this repository. Client Firestore rules allow owned reads and narrowly bounded bootstrap/name compatibility only; product mutations and private ledgers are server-owned.
