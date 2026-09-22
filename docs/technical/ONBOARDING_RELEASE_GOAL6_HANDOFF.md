# Goal 6 — integrated onboarding release

Status: candidate preparation and verification in progress; this document does
not yet assert a production release or successful live-account/device checks.

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

- Final integrated backend: 436 tests, 435 passed and one macOS-specific skip.
- Standard-library-only coordinator/process run: 29 tests, 28 passed and one
  macOS-specific skip. Linux CI on the final candidate remains a release gate.
- Frontend is unchanged from accepted Goal 5: 691 tests in 51 suites and build
  passed there. The 124 existing TypeScript diagnostics remain recorded in that
  handoff; none were in changed Goal 5 files.
- Parent independently verified all 14 canonical public-health/private-debug
  checks before release on September 22, 2026.
- Reading the actual Firebase Rules release and source succeeded. Synthetic
  `projects.test` was denied by the current service account (HTTP 403); it did
  not deploy rules or access app documents. No IAM permissions were changed.
- All 178 local Firestore emulator checks passed against the exact frontend
  rules hash below: owner/foreign/anonymous CRUD, private collections including
  admin-claim and list denial, managed-history immutability and legacy behavior.
  Used cached Firestore emulator 1.19.8, JRE 21 and official rules-unit-testing on
  localhost with a demo project. The emulator was stopped after verification.
- Authenticated deployed-rule/cloud, physical-phone and provider-image proof
  are still pending. Local and viewport tests are not substitutes for them.

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
`a12dd16fb49562d4548c6c3f7b13ede62147772579a63479f807ab42ca1fbe75`.
A complete deployed-versus-candidate review found no live-only explicit allow/admin policy
removed. The backend copy additionally contains a pre-existing nested
`users/{uid}/wardrobe/{itemId}` allow absent from live and frontend rules; do not
activate that unrelated grant during this release. The frontend source keeps
the existing collection policy and adds private job/onboarding/receipt denial
and client immutability for managed wear history. Deploy only Firestore rules;
do not implicitly update Storage rules or indexes.

Vercel currently lacks the three server-only Admin variables. Explicit browser
credential-entry consent is pending for `FIREBASE_PROJECT_ID`,
`FIREBASE_CLIENT_EMAIL`, and `FIREBASE_PRIVATE_KEY` in Production and only the
release preview branch. If approved, import only those three values from the
intended existing credential source through a private mode-0600 temporary file.
Never import a complete backend environment or expose values in logs. No new
provider, pricing or unrelated preview-branch access is authorized by that step.

## Controlled release and recovery

1. Freeze a clean cumulative candidate, push one draft PR against `main`, and
   require its Linux process/queue checks. Do not merge the stacked PRs one by
   one: Git triggers must never publish intermediate runtime combinations.
2. Validate the chosen rules source and environment names. Record the exact
   candidate and original artifact IDs. Keep `main` untouched while deploying
   the candidate manually to canonical services through official interfaces.
3. Deploy and verify the exact `frontend/firestore.rules` source/hash recorded
   above before new API endpoints can create managed wear records. Record the
   resulting live ruleset ID and actual client allow/deny evidence. Deploy the
   matching API from the frozen source. Verify health, ownership,
   legacy bodyless-wear compatibility and new endpoint availability. Keep the
   worker stopped until the API/rules boundary is compatible.
4. Deliberately retire any old worker deployment before starting the candidate
   worker (`backend/worker`, `python main.py`, one replica). Verify new bounded
   recovery and independent garment/flatlay progress. Do not use the stale
   `backend/Dockerfile.worker` path.
5. Verify a configured authenticated preview, then deploy a frontend build made
   with Production environment values. Do not assume promoting a Preview build
   rebuilds it with Production variables. Verify all canonical domains.
6. Integrate only the final accepted cumulative candidate into `main` once
   services are compatible. Confirm Git source connections remain correct and
   subsequent deployments use the accepted tree. Record final artifact IDs.

The minimum compatible source recovery target is accepted Goal 5 commit
`b0f7dfb3d5a56c5aa3ff43f7c24b52735d90f768`, subject to the recorded review and
platform build/health checks. It contains the same versioned asset readers,
leases, protected request/source checks and atomic wear receipts; Goal 6's queue
fix has no schema migration. Its worker retains the queue-starvation defect,
so keep dispatch stopped if that incident is present and prefer a forward fix.

For containment, set `EASYOUTFIT_FLATLAY_REQUESTS_PAUSED=true` on the API,
deploy that setting, verify admission is paused, and stop the worker deployment;
the API flag alone does not stop queued work. Record its prior value/presence
and restore that exact state deliberately after recovery is verified.
For a source rollback, deploy the compatible Goal 5 API and frontend, then
start its worker only after health and ledger compatibility checks. Preserve
the new protected rules, receipts, job ledgers and immutable assets. Never
blindly restore the original API/worker or old rules after new writes exist.
SIGTERM on the new coordinator terminates and reaps its children while retaining
leases for normal recovery. Record any actual rollback artifacts when built;
an accepted source SHA is not an already-built recovery deployment.

An immutable source archive of that exact fallback commit was prepared as
`easyoutfit-goal6-goal5-rollback-source.tar.gz`, SHA-256
`5085bebe9134be5551d05e2dc5b8706a8f659ce068ec06c5434b6f0773649310`.
Its matching manifest records the full commit and archive digest. This is a
verified source recovery artifact, not a prebuilt image or live rollback pass.

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
