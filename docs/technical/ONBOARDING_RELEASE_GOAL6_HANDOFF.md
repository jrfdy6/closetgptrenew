# Goal 6 — integrated onboarding release

Status: controlled rollout of accepted source
`801b6679062e0ad1df6c0f5e085ddeac5c4d8724` is **partially live**. Protected
Firestore rules and the matching Railway API are deployed and verified. Worker
compatibility is **not accepted**: garment jobs preserve originals but fail during
later preparation. The worker was stopped to preserve remaining automatic
attempts; flatlay admission remains paused. Frontend production, full signed-in
workflows, provider-image/settlement and physical-device gates remain open.

## Candidate and scope

Branch `codex/onboarding-integrated-release` preserves all five accepted commits:

| Goal | Accepted commit |
| --- | --- |
| Durable onboarding state | `bf16ab125e7b7b51ae62e4cc3fdc7cfe1eb49f8f` |
| Image worker durability | `d8bbaccd22a9aa2636acba06da253551d8a6879a` |
| Capsule onboarding experience | `e47733446e32147d51dfb66a49ab0cbee5cd940e` |
| Recommendation fidelity | `fd148750a91cf226249a47f6b0a949562267bd31` |
| Saved outfit experience | `b0f7dfb3d5a56c5aa3ff43f7c24b52735d90f768` |

The full quiz, ten unique usable garments and category coverage, incremental
saves/resume, explicit flatlay creation, original photographs, existing hosted
providers and credit settlement remain intact. Stripe/prices, mixed PR #3,
Jev, new models, imports/reminders and a new multiple-required-item selector
remain excluded. Do not reset credits, delete historical outfits or transfer
the owner's photographs to the test account.

## Privileged boundary migration

The candidate moves profile, onboarding, quiz, garment and image privileged work
to Railway. Vercel contains thin fixed-origin proxies and the browser Firebase
client, with no Firebase Admin package/runtime or service-account credentials.
Do not provision Vercel Admin keys to make the release work. The canonical
operator playbook was updated first; the production architecture describes the
same candidate boundary.

Migrated Railway endpoints verify bearer tokens with revocation checks, deny
disabled/anonymous users and mismatched UID assertions in headers/query/body,
and preserve account authority, private job state and quiz/wear receipts.
The active direct `/api/auth/profile` GET/PUT clients use the same protected
profile contract. Profile transactions execute outside the request event loop.
Fresh profile edits cannot establish quiz completion through `stylePreferences`
or `preferences.style`: the transaction permits these edits only with completion
or legacy evidence in the stored profile before applying the update. Name-only
signup and completed/legacy profile edits remain supported.

Proxy destinations come from trusted configuration and fixed application paths,
not request headers or URLs. Proxies forward bearer authorization and required
body/content type, reject redirects and non-JSON responses, and return private,
no-store JSON. The default upstream request deadline is 50 seconds. Multipart
`/api/image/upload` preserves file/field semantics with a 45-second upstream
deadline. Timeouts can leave writes committed; confirm by retry/readback.

Unused frontend endpoints return `410`: `/api/profile/save`,
`/api/user/style-profile`, `/api/update-style-profile`, `/api/upload-photo`,
`/api/delete-photo`, `/api/migrate`, `/api/image/upload-direct`, `/api/analyze`
and `/api/admin/fix-onboarding-status`. Active callers use supported paths;
retirement does not authorize restoring permissive identity or migration scans.

Raw image-URL admission retains its previous policy. The worker checks
`original_source` at use time; no new general URL-admission or external-fetch
safety guarantee is claimed by this migration.

## Narrow integrated fix

The worker's oldest-only flatlay query could repeatedly launch an unclaimable
private ledger and starve later valid requests. The selector now advances using
a Firestore document snapshot, reads at most one candidate per idle dispatch,
and wraps after exhausting the queue. The transaction remains the sole claim
authority. Held ledgers and credits are not modified to force progress.

Regressions cover tied queue times, thirty held rows before a valid row,
deleted/dequeued cursor records, an earlier arrival, wraparound, and an actual
declined ledger claim followed by a valid claim. The coordinator/process suites
retain their standard-library-only CI contract.

## Verification before cloud changes

These checks cover the integrated migration, including the profile completion
guard and exact onboarding parity fixes. Source freeze, independent acceptance
and Linux CI remain distinct release gates.

| Check | Latest recorded result | Release follow-up |
| --- | --- | --- |
| Full frontend | 720 tests in 57 suites passed | Includes runtime Admin-boundary guards |
| Full backend | 534 tests: 533 passed, one macOS-specific skip | Includes completion-guard, transaction and route-registration regressions |
| Executed TypeScript parity oracles | 189 quiz cases and 241 onboarding cases match | Frozen-source mapping, submission hashes, state, classification and timestamp behavior |
| Coordinator/process standard-library-only run | 29 tests: 28 passed, one macOS-specific skip | Linux CI on the final candidate remains required |
| Firestore rules emulator | 263 checks passed against the exact source hash below | Recheck if rules change |
| Parent independent real local Firestore emulator service checks | Frozen-source 25/25 passed, including completion guards and concurrent drafts | Transaction contention can return retryable exhaustion; retries converge without a dual winner |
| Production build | Passed with public Firebase client configuration and no server Firebase credentials | All 134 compiled server-route traces exclude Firebase Admin |
| Typecheck | 115 existing diagnostics; baseline 124 at `3ed2ecc4`; zero new diagnostic positions or changed-file errors | Repository-wide typecheck remains failing; the existing build skips type/lint gates |
| Accepted source and CI | `801b6679062e0ad1df6c0f5e085ddeac5c4d8724`; Linux runs `35798351924` and `35798348416` passed | A subsequent diagnostic candidate needs separate acceptance |
| Authenticated deployed/provider-image/physical-device checks | **Pending** | Local and viewport tests do not replace these gates |

The parent independently verified all 14 canonical public-health/private-debug
checks before release on September 22, 2026, and read-only verification confirmed
all three canonical backend URL environment variables. Reading the Firebase
Rules release and source succeeded. Synthetic `projects.test` was denied to the
current service account (HTTP 403); no IAM change, alternate credential, rules
deployment or app-document operation was used to bypass it. Current signed-in
operator Firebase-console sign-in has since been verified read-only; actual
publication and source-hash proof are now recorded below. Full deployed client
workflow evidence remains a release gate.

The rules emulator checks cover owner/foreign/anonymous policy, server-owned
profile authority, private job/receipt collections, managed wear immutability
and legacy behavior. They are local evidence, distinct from the independent
service-level emulator checks and from authenticated deployed-rule evidence.

## Observed controlled rollout — September 22–23, 2026

- Rules: `projects/closetgptrenew/rulesets/7bcef845-f06e-4825-af58-b248f21164a3`,
  published `2026-09-22T23:48:31.140678Z`. Official REST source SHA matches the
  accepted `eafa27b…f9811ca` exactly. Five console rules simulations passed;
  these are synthetic checks, not actual app-document writes.
- API: deployment `12c21fda-3559-48f3-a07c-102089bff6e3`, accepted source `801b6679`,
  one running instance `2798efdd-46dc-439b-94ad-eb0ae8e29501`. All 16 health and
  missing-bearer/private-route checks passed. A signed-in profile name save and
  reload passed, and the original name was restored. This tested the live
  compatibility path, not the new preview proxy. Two same-day bodyless Wear UI
  submissions left the exact outfit and all three garments at wear count one;
  readback found one matching managed history, one day receipt and one retry-key
  receipt (12/12 checks). This closes the API-first legacy wear compatibility gate,
  not the new-preview proxy or provider-image gates.
- Worker: deployment `777045cd-8f01-4f64-ab2f-bf2a18e75362`, same accepted source,
  one instance `09cf0f47-3e0f-465c-bb43-232c959b27ca`, started its coordinator at
  `00:03:32 UTC`. Claims and finite automatic retries progressed, but no successful
  garment completion was observed. Eight observed failed attempts took 48–91
  seconds and recorded `processing_failed`; all four inspected jobs had protected
  originals. No model/network/inference root cause is inferred from that coarse
  code. Official `railway down` exited successfully; by `00:14:21 UTC` the worker
  had no active instances, and its exact deployment was `REMOVED`. Logs recorded
  the container stop signal at `00:14:11 UTC` and `Worker stopped` at `00:14:14 UTC`.
  OS-level child reaping is not independently proven by these observations.
- The historical expired Neo flatlay request settled through normal worker
  expiry as `legacy_request_needs_review`; its reserved credit was refunded once
  (remaining credits 0 to 1, unchanged refill period). No manual credit write,
  request retry or provider image call was performed. No provider-start field
  was present; that does not prove historical provider billing.
- Vercel preview `dpl_2gsS5zGiCygBJWY1wvjwWHYQndy2` is ready at accepted `801b6679`.
  Authenticated preview checks remain pending. Production still uses
  `dpl_6jcTmawjEhem86s3ZtaKbMmNsLYn`; no frontend promotion has occurred.

The API admission variable was originally present with value `false` and is now
configured `true` on the running accepted API. Restore that exact prior state
only at the deliberate readiness gate. Before `main` is integrated, use
`--skip-deploys` for the variable change, followed by explicit reviewed-commit
deployment: a normal variable update can automatically rebuild the older linked
`main`. Runtime SSH flag inspection was unavailable because no SSH keys were
configured; none were created. Authenticated paused-handler proof remains open.

The failed initial CLI-upload API candidate did not replace the running API:
its monorepo archive omitted required files. The official `serviceInstanceDeploy`
API with explicit `commitSha` and `latestCommit: false` successfully deployed the
accepted Git source. Use this controlled path rather than unverified archives.

## Worker diagnostic run and remaining evidence gap

Accepted diagnostic source `4581d43cae2b9cff726cd1219dd8b681bf1b36ff` was deployed
for one bounded worker-only run after independent review and two successful Linux
CI runs (`35801948799`, `35801945634`). API source, rules and admission pause were
unchanged.

The contained failure needs more precise evidence than the public
`processing_failed` code. The narrow candidate forwards at most two finite
stage/category entries from the alpha and fallback inference processes through
the existing result manifests to coordinator operational logs. An optional HTTP
error status is constrained to integer 400–599. Every receiving boundary reapplies
the allowlist. No exception messages, URLs, object IDs, credentials, traceback
contents or frame locals are serialized. Diagnostics do not enter garment/job
lifecycle records or user-facing errors.

Diagnostic extraction and inference sidecar persistence are best effort. A broken
exception property or optional diagnostic file cannot turn successful inference
into a failure or obscure the original safe failure envelope. Existing models,
providers, leases, deadlines, automatic attempt budgets and public statuses are
unchanged. This candidate diagnoses the blocker; it does not claim to fix the
underlying image-preparation failure.

The focused diagnostic/process suites ran 55 tests: 54 passed and one expected
macOS skip. The full backend ran 542 tests: 541 passed and one expected macOS skip.
Independent review resolved the diagnostic-accessor fault and found no remaining
blocking issue. Real nested subprocess tests verify both inference causes cross
the manifest boundaries while original preservation and retry behavior remain
unchanged. Frontend, rules and API source are unchanged from accepted `801b6679`.
Deployment `00ccfc8d-2ac4-42c3-84a3-df69d5b8b810` ran one instance
`c04fd293-198e-45e4-9c09-6d5b84f5874a`. A naturally eligible second attempt began
at `00:29:20 UTC` and failed at `00:30:41 UTC` with both `alpha_process` and
`fallback_process` classified `process_crashed`. No Python failure manifest was
returned. That category included any nonzero integer exit and did not establish
a signal, native failure or OOM cause.

The coordinator started the next naturally eligible garment in the same tick
before the observer stopped the service. `Worker stopped` was recorded at
`00:30:50 UTC`; the stop command exited zero and no active instances remained.
The second job had no terminal event before shutdown; its existing durable lease
was retained for normal recovery. No manual garment or paid-request retry occurred.

Official 60-second metrics for this run sampled 0.306–1.861 GB memory against an
8 GB limit, and CPU up to 1.117 against an 8 limit. Sparse samples are not peak
measurements or OOM counters; they do not justify changing resources, models or
deadlines. The exact diagnostic build resolved rembg 2.0.85, onnxruntime 1.30.0,
NumPy 2.5.3, PyMatting 1.1.16, Pillow 12.3.0, SciPy 1.18.1 and scikit-image 0.26.0.
The selected native wheels target CPython 3.12 on Linux x86_64; this records the
active Nixpacks build, not the inactive worker Dockerfile or API dependency pins.
Next evidence is finite exit/signal classification from the supervisor,
best-effort last-stage markers, and optional bounded cgroup-v2 `oom`/`oom_kill`
counter deltas. Only a fixed, capped file read and two nonnegative integer deltas
are permitted; unavailable/malformed/reset counters are omitted. The deltas
describe container-level events during inference, not proof that this child was
killed by OOM. Any further worker run requires a fresh source/test review; keep
API admission paused.

## Exit/stage/cgroup diagnostic extension — not yet deployed

The follow-up candidate changes only worker diagnostic extraction and its tests.
It classifies the supervisor's retained return code into finite signal/nonzero
exit categories; exit 74 is a neutral category, not proof the registration barrier
caused the production failure. Best-effort progress markers identify the last
inference import/input/removal/output stage. The outer supervisor, coordinator,
lifecycle, model/provider settings, resources, retry budgets and deadlines remain
unchanged. Missing marker or counter evidence stays unknown rather than being
invented. Counter evidence is projected through the same finite schema before
operational logging and never enters user/job records.

Focused checks ran 64 tests: 63 passed and one expected macOS skip. Standard-library
checks ran 33: 32 passed and one expected macOS skip. Full backend checks ran 551:
550 passed and one expected macOS skip. Regressions include actual SIGKILL, exit 1,
the real missing-registration-barrier exit 74, native exits through the production
`--infer` path, malformed codes, optional marker-write failures and bounded cgroup
read/reset/overflow behavior. Generic tests isolate host cgroup availability.
No further worker deployment is authorized by these local checks alone; record
the frozen commit, exact CI and parent review before any bounded next run.

## Original production state

Refresh these values immediately before any mutation; they are a recovery
inventory, not a recommendation to restore unsafe legacy writers.

| Surface | Original observed artifact |
| --- | --- |
| API | Railway deployment `9b8e9d61-229f-4e25-8c9f-3659a8130d79`, successful/running, commit `ba62aed8aa573cbae1e16933fab5dae42afb130d` |
| Worker | Railway deployment `9c03de98-4f1c-4640-946d-394de485148e`, crashed/stopped, commit `5bb9ccff329d62c19fd0e684ed344d6dbe66c7b5` |
| Frontend | Vercel production deployment `dpl_6jcTmawjEhem86s3ZtaKbMmNsLYn`, commit `bb5f14bf`; refresh before mutation |
| Firestore | `projects/closetgptrenew/rulesets/4180bc45-e15b-4fb2-9dfe-669174ac2af1`, release `cloud.firestore`, updated 2025-10-25 |

Canonical targets are the ones in `EASYOUTFIT_OPERATOR_PLAYBOOK.md`:
Railway project `97ed14e7-f7a6-4f86-b919-94f133ed478e`, production environment
`240a7503-5fbc-49aa-9e9b-dc543c572dce`, API service
`43e4d1da-678f-4232-89ea-4394e404a372`, worker service
`cc65e747-accb-48a8-a4fd-fd3a3e30eaeb`; Vercel project
`prj_X8XE8UKf5R54oscVbNrXBdWgpMkB`, team
`team_OnDYjnYcXBXVSXCkAYZbToU6`.

## Rules and environment boundary

Use `frontend/firestore.rules` as the explicit release source, SHA-256
`eafa27b3270d6906835309c68a10b13b71822852d8a35f8b501e36da9f9811ca`.
The candidate intentionally constrains direct user-document writes to safe
bootstrap/name edits; full profile changes go through verified Railway APIs.
It also denies direct access to private jobs, onboarding state and receipts,
and protects managed wear history. The backend rules copy additionally contains
a pre-existing nested `users/{uid}/wardrobe/{itemId}` grant absent from live and
frontend rules; do not activate that unrelated grant. Refresh the complete
live-to-final-source rules diff before release. Deploy Firestore rules only,
without implicitly deploying Storage rules or indexes.

Vercel uses `BACKEND_URL`, `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_BACKEND_URL`
pointing to `https://closetgptrenew-production.up.railway.app`; the parent verified
all three read-only. No Vercel Admin credentials or `firebase-admin` package are
required. Keep privileged Firebase access in the intended Railway services.
Public browser Firebase configuration remains separate. The previous Vercel
Admin credential-entry proposal is withdrawn; do not import backend credentials
or restore old Admin handlers as a release or recovery step.

## Controlled release and recovery

1. Freeze the tested clean cumulative source and obtain independent parent
   acceptance of source, tests,
   final rules drift/hash, recovery plan and remaining live gates. Record the
   actual SHA and CI results; the accepted base is recorded above. Do not
   merge stacked PRs one by one or allow Git triggers to publish intermediate
   runtime combinations.
2. Refresh the original production inventory and canonical environment bindings.
   Use the intended signed-in operator console without bypassing the service
   account denial. Keep `main` untouched while validating the accepted
   candidate through controlled official deployment interfaces.
3. Pause new flatlay admission and keep worker dispatch stopped while establishing
   compatibility. Apply and verify the exact protected frontend Firestore rules
   before enabling writes that rely on them. Record the deployed ruleset ID and
   actual client allow/deny evidence. Deploy and verify the matching Railway API,
   including strict bearer identity, profile/quiz authority, upload ownership,
   private receipts and legacy bodyless-wear compatibility.
4. Deliberately retire any old worker deployment before starting the candidate
   worker (`backend/worker`, `python main.py`, one replica). Verify bounded
   recovery and independent garment/flatlay progress. Do not use the stale
   `backend/Dockerfile.worker` path. Resume admissions only after compatibility
   and dispatch are verified.
5. Verify the configured authenticated frontend preview, then release a frontend
   build made with Production environment values. A Preview promotion does not
   imply a rebuild with Production variables. Verify all canonical domains and
   retain the Railway-only privileged boundary.
6. Integrate only the final accepted cumulative candidate into `main` once the
   controlled rollout is compatible. Confirm Git source connections and record
   actual API/worker/frontend/rules artifacts, source SHA, live evidence and
   parent acceptance.

The accepted Goal 5 commit `b0f7dfb3d5a56c5aa3ff43f7c24b52735d90f768` is now
**historical evidence only, not a compatible complete fallback**. Its versioned
asset readers, leases and receipts were compatible with the earlier queue-only
candidate, but it predates the privileged-boundary migration and protected
profile rules. It also retains the queue-starvation defect. Do not deploy it
blindly or restore Vercel Admin keys to make its old writers work.

Contain incidents by setting `EASYOUTFIT_FLATLAY_REQUESTS_PAUSED=true` on the API,
applying that setting and verifying admission is paused, then stopping the worker
deployment. The API flag alone does not stop queued work. Record the prior flag
value/presence and restore that exact state only after deliberate verification.
The coordinator's SIGTERM handling terminates/reaps children and retains leases
for normal recovery.

Prepare and review a forward repair or a separately proven recovery candidate
that retains Railway Admin ownership, protected rules, versioned asset readers,
private job ledgers, receipts and immutable assets. Never blindly restore the
original API/worker/rules after new writes exist. Neither an old source SHA nor
a successful historical deployment is proof of a compatible recovery artifact.
Record actual recovery build/deployment IDs and health/contract evidence when
available; none is claimed here.

The immutable archive `easyoutfit-goal6-goal5-rollback-source.tar.gz`, SHA-256
`5085bebe9134be5551d05e2dc5b8706a8f659ce068ec06c5434b6f0773649310`, and its
matching full-commit manifest are retained as historical source evidence. The
archive name does not designate a supported full rollback, prebuilt image or
live recovery pass for the current candidate.

## Remaining live gates

Use only the explicitly authorized test account and public human-style garment
photos. It already contains ten garments and historical empty outfits; preserve
them and do not label its walkthrough a fresh zero-to-ten account test.

Required: authenticated save/readback and resume; category/coverage behavior;
configured, random and existing one-required-item generation; valid two-piece
one-piece/shoes combinations; saved owned detail without regeneration;
favorite/feedback persistence; one wear event on retry; explicit flatlay
queue/leave/return, authoritative settlement and delivered-image comparison;
physical-phone capture/HEIC and interrupted-network resume. A fresh-account
gate requires a separately authorized fresh identity if still needed.

Inspect the historical queued request through normal lifecycle handling.
Do not infer provider invocation, reset quotas or retry an ambiguous paid
request. Record real timing/cost only when observed. Final live evidence,
deployment IDs, limitations and parent acceptance must be appended before this
goal is marked complete.
