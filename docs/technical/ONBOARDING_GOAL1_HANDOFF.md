# Onboarding reliability — Goal 1 handoff

This change protects questionnaire and upload work before the later onboarding and result-presentation redesign. It retains the full questionnaire, the ten-piece capsule requirement, and the existing visual identity. It does not deploy, change billing, replace image providers, or implement the later goals.

## Behavior

- Full-questionnaire answers and position resume from an account-owned, versioned server draft, with a per-account session backup for unacknowledged edits. Serialized saves reject stale revisions; a lost acknowledgment can be retried without adding a revision. Explicitly loading a newer draft resolves a conflict.
- Guest work stays in browser storage. A new signup can transfer it into a draft; existing-account sign-in does not submit it as a profile. Replacing an existing quiz requires explicit retake. Signup names are saved in both Firebase Auth and the profile.
- Quiz submission verifies Firebase identity, requires every question in the selected variant, and acknowledges only committed profile writes. An identical retry recovers a lost response. Storage failures remain retryable errors.
- Batch upload modes acknowledge only real, owned saved records. Atomic backend creation rejects foreign IDs and returns an already-saved owned record unchanged on retry, preserving processing results, edits and wear history.
- Capsule readiness requires ten unique usable saved garments and either top/bottom/shoes or one-piece/shoes. Original photos remain usable when cutout processing fails. Repeated image identities do not inflate the usable count.
- The dashboard separates load errors from an empty closet, stops generation without a ready capsule, preserves the generation component across statistics refreshes, and makes at most one automatic account/day generation attempt across remounts. Manual retry remains available.
- Generated outputs are checked against authoritative owned garments before persistence. Empty, duplicate, foreign, incomplete or required-item-omitting outputs fail; a one-piece and shoes remains a valid two-item outfit. Save failures return errors.

## API and storage contract

`onboarding_states/{uid}` is private to the server; direct client reads and writes are denied in both tracked Firestore rules files. Existing user documents remain compatible.

- `GET /api/onboarding`: read-only full state, including profile evidence, current capsule readiness, stage, draft revision and milestones.
- `PATCH /api/onboarding`: `{expectedRevision, draft: {answers, currentQuestionId}}`. One-document transaction; returns only draft/revision/milestones. A conflicting edit returns 409 with the newer draft. An identical immediately retried write returns its existing acknowledgment.
- `POST /api/onboarding`: authenticated reconciliation without client counts or completion claims. Reads owned persisted sources in a transaction and promotes completion history without changing the draft revision. Only a completed profile plus a currently ready capsule can create a new capsule milestone. Repeated reconciliation is idempotent. Draft saves and milestone promotion preserve each other under transaction retries.

Responses are private/no-store. All three operations verify a real Firebase ID token with revocation checking. Missing configuration or storage failure produces an error rather than an empty successful state.

Stage hydration reconciles progress; successful questionnaire submission, upload completion and dashboard generation also refresh it. Recorded milestones survive later garment/outfit deletion. Current readiness remains separate and may become false after deletion.

Legacy compatibility uses persisted profile/persona/preferences and real complete outfit snapshots as historical evidence; quiz-only flags and empty outfit rows do not count as capsule completion. Legacy collections are client-writable under existing rules: this adapter is not proof that every old profile or outfit passed the new server validators. A historical row deleted before its first successful reconciliation cannot be reconstructed. No broad migration, historical cleanup or unrelated rules rewrite is included.

## Release prerequisites

Before releasing the frontend, provision Firebase Admin access for the intended Vercel production/preview environments using the existing helper:

- `FIREBASE_PROJECT_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_PRIVATE_KEY`

Read-only inspection of the canonical Vercel project on 2026-09-22 confirmed these names are absent and no shared variables are linked. Browser/public Firebase configuration is insufficient. No credential values were revealed or copied during implementation. Do not restore the former unverified fallback to work around missing credentials.

Deploy the protected Firestore rules and the matching Railway API changes before the frontend release, then verify the live authenticated journey. Existing default-deny rules already deny the new collection in this repository; the deployed rules must be checked rather than assumed. No new index or destructive data migration is required by this change.

## Validation and remaining verification

The implementation uses credential-free unit/component/API contract tests and a production compilation with placeholder public Firebase configuration. Shared category/coverage fixtures live at `backend/tests/fixtures/onboarding-readiness-fixtures.json` and are consumed by both test stacks.

Results on the final implementation: 427 frontend tests across 38 suites passed; 163 backend tests passed; production build passed. The shared fixture was then rechecked from its tracked location in both stacks. Full TypeScript check exits 2 with 139 diagnostics outside changed files and zero diagnostics in changed files.

Commands:

```sh
cd frontend
npm test -- --runInBand
npx tsc --noEmit --pretty false
npm run build
```

```sh
cd backend
python -m unittest discover -s tests -p 'test_*.py'
```

The existing Next configuration skips lint and TypeScript errors during builds. A successful build is not a clean repository type-check. Whole-repository type checking currently reports diagnostics outside the changed files; changed files are checked separately.

No live authenticated browser journey, real Firestore transaction/emulator run, mobile capture, live recommendation/provider call, background worker job or production deployment was performed in this goal. Test doubles exercise contention and ownership contracts; they do not replace integration verification. Those checks, credential provisioning, and production smoke testing remain release gates in Goal 6. Later goals retain responsibility for the upload workflow redesign, image-worker durability, recommendation quality, addressable results and polished flatlay presentation.
