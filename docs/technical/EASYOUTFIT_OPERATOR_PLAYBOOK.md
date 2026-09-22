# EasyOutfit Operator Playbook

This is the canonical operator playbook for EasyOutfit.

Use it for:

- deploy truth
- environment truth
- Codex bridge truth
- admin Codex cohort truth
- verification after production-facing changes

If OpenClaw workspace docs and the product repo disagree, this file wins for EasyOutfit runtime and deployment truth.

## Goal 6 Candidate Boundary — Not Yet Live

The integrated Goal 6 candidate changes where privileged work runs. This section
describes the candidate contract, not an observed production rollout. No cloud
configuration, rules or deployment has been changed as part of this preparation.

- Vercel runs the frontend and thin API proxies. The candidate has no Firebase
  Admin runtime/package and needs no Firebase Admin credentials in Vercel. Do not
  add `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL` or `FIREBASE_PRIVATE_KEY` to
  Vercel to make these routes work. Browser Firebase configuration remains public
  client configuration and does not confer Admin access.
- Railway owns privileged profile, onboarding, quiz, garment and image writes.
  The migrated endpoints verify bearer tokens with revocation checks, reject
  disabled/anonymous users and conflicting identity headers/query/body fields,
  and preserve server-owned account fields, completion receipts and private job
  state. Fresh profile edits cannot establish quiz completion through style
  preference aliases; only previously completed or legacy profiles can edit those
  aliases. Direct legacy profile GET/PUT clients use the same protected contract.
- Proxies choose a fixed configured Railway origin and application path. They
  forward bearer identity and the required content type/body, never cookies or
  UID/role assertions, reject redirects and unexpected non-JSON responses, and
  return private, no-store responses. The upstream request deadline is 50 seconds
  by default; multipart photo upload preserves its fields/files and uses a
  45-second upstream deadline. A timeout is an uncertain outcome, not proof that
  a write failed; confirm through retry/readback.
- Unused legacy Admin/Clerk/migration routes return `410`. Do not restore them as
  a fallback. Supported uploads use `/api/image/upload`; supported profile edits
  use `/api/user/profile` or the retained Railway `/api/auth/profile` alias.
- Release `frontend/firestore.rules`, including protected user fields and private
  job/receipt collections. The additional nested wardrobe grant in the backend
  rules copy is outside this release. Deploying rules must not also deploy Storage
  rules or indexes.
- Raw image-URL admission retains its prior policy. The worker's
  `original_source` check is a check at use time; this candidate does not establish
  a new blanket admission or fetch-safety guarantee.

Parent review must independently accept the final candidate, tests, build,
typecheck, rules hash and recovery procedure before any production action.
Refresh the existing release inventory immediately before release. With flatlay
admission paused and worker dispatch stopped, apply the protected rules, deploy
and verify the matching API, then deliberately replace the worker from
`backend/worker` (`python main.py`, one replica). Verify an authenticated frontend
preview before deploying a build made with Production variables; confirm every
canonical domain. Keep intermediate Git-triggered deployments from publishing
mixed versions. Record exact source and platform artifact IDs after acceptance.

The Goal 5 source archive is now historical evidence only, not a compatible
complete fallback for this boundary change. Containment and forward repair must
retain Railway Admin ownership, protected rules, versioned asset readers, private
ledgers and receipts. `EASYOUTFIT_FLATLAY_REQUESTS_PAUSED=true` stops API admission
only; stop the worker deployment to stop dispatch. Do not blindly restore old
source, old rules or Vercel Admin keys. A rebuilt recovery candidate needs its own
review and verification.

Current local evidence: frontend 720 tests in 57 suites passed; backend 534 tests
ran with 533 passed and one macOS skip; Firestore rules 263 checks passed against
SHA-256 `eafa27b3270d6906835309c68a10b13b71822852d8a35f8b501e36da9f9811ca`.
The production frontend build passed with the existing public Firebase client
configuration and no server Firebase credentials; all 134 compiled server-route
traces exclude Firebase Admin. Typecheck still reports 115 existing diagnostics,
compared with 124 at the preceding candidate, with no new diagnostic positions
or diagnostics in changed files. Build configuration still skips type/lint gates;
a successful build is not a clean repository-wide typecheck. Frozen TypeScript
oracles verify 189 quiz cases and 241 onboarding cases. The parent's earlier
real local Firestore service checks passed 23/23 and require final-candidate
acceptance. Live authenticated/provider-image and physical-device checks remain
pending. The three canonical backend URL variables were verified read-only;
that does not constitute deployment. See
[the Goal 6 handoff](ONBOARDING_RELEASE_GOAL6_HANDOFF.md) for release gates and the
inventory to refresh. No final source SHA or CI pass is asserted here.

## Canonical Surfaces

- Product repo: `/Users/neo/Desktop/closetgptrenew`
- OpenClaw workspace lane: `/Users/neo/.openclaw/workspace/workspaces/easyoutfitapp`
- Canonical frontend production host: `https://closetgpt-frontend.vercel.app`
- Canonical frontend domains: `https://easyoutfitapp.com`, `https://closetgpt.app`
- Canonical backend production host: `https://closetgptrenew-production.up.railway.app`

## Repo and Branch Truth

- EasyOutfit lives in the `closetgptrenew` repo.
- It is separate from the `aiclone` repo.
- The live deploy branch is `main`.
- The remote `production` branch is stale historical state and not a live deploy branch.

## Production Topology

- Frontend: Vercel project `closetgpt-frontend`
- Backend API: Railway service `closetgptrenew`
- Background worker: Railway service `background-processor`
- OpenAI SDK gateway: Railway service `closetgptrenewopenaisdk`

Legacy non-production Railway services:

- `closetgpt-backend`
- `closetgptrenew-backend`

Do not treat those legacy services as production targets.

## Local Railway Link Policy

Option 1 is intentional for EasyOutfit:

- repo root `closetgptrenew/` should link to Railway service `closetgptrenew`
- `backend/` should link to Railway service `closetgptrenew`
- `backend/worker/` should link to Railway service `background-processor`

If a local Railway link points at `aiclone-backend`, `closetgpt-backend`, or `closetgptrenew-backend`, treat that as drift.

## Canonical Local Development Paths

- Backend venv: `backend/.venv311`
- Backend env file: `backend/.env`
- Frontend env file: `frontend/.env.local`
- Local Codex bridge env file: `.env.easyoutfit_codex_bridge`

Do not rely on:

- `backend/venv`
- `backend/local_test_env`

Those are stale.

## Codex Runtime Truth

EasyOutfit currently has two AI lanes:

1. direct hosted AI runtime for main production image workflows
2. local Codex bridge for Firestore-backed EasyOutfit Codex jobs

The live Codex bridge components are:

- queue service: [backend/src/services/ai_runtime/codex_jobs.py](/Users/neo/Desktop/closetgptrenew/backend/src/services/ai_runtime/codex_jobs.py:1)
- queue API: [backend/src/routes/codex_jobs.py](/Users/neo/Desktop/closetgptrenew/backend/src/routes/codex_jobs.py:1)
- bridge runner: [scripts/local_codex_bridge_easyoutfit.py](/Users/neo/Desktop/closetgptrenew/scripts/local_codex_bridge_easyoutfit.py:1)
- launch wrapper: [scripts/run_local_codex_bridge_easyoutfit.sh](/Users/neo/Desktop/closetgptrenew/scripts/run_local_codex_bridge_easyoutfit.sh:1)
- launch-agent installer: [scripts/install_easyoutfit_codex_bridge_launch_agent.sh](/Users/neo/Desktop/closetgptrenew/scripts/install_easyoutfit_codex_bridge_launch_agent.sh:1)
- launch-agent label: `com.neo.easyoutfit_codex_bridge`

## Admin Codex Cohort Truth

Admin upload analysis can run through Codex in parallel with the direct OpenAI lane.

Current rule:

- verified admin cohort routes to Codex for upload analysis
- non-admin users stay on the direct hosted path

Current admin cohort truth is controlled by backend env vars:

- `EASYOUTFIT_CODEX_UPLOAD_ANALYSIS_ENABLED`
- `EASYOUTFIT_CODEX_ADMIN_EMAILS`
- `EASYOUTFIT_CODEX_COHORT_USER_IDS`
- `EASYOUTFIT_CODEX_UPLOAD_FAST_PATH_TIMEOUT_MS`
- `EASYOUTFIT_CODEX_UPLOAD_FAST_PATH_POLL_MS`

Current operator access truth for Codex jobs is controlled by:

- `EASYOUTFIT_LOCAL_CODEX_TOKEN`
- `EASYOUTFIT_CODEX_OPERATOR_USER_IDS`
- `EASYOUTFIT_CODEX_JOB_ACCESS`

## Upload Flow Truth

For admin uploads in the Codex cohort:

1. frontend uploads the image
2. backend queues an `upload_image_analysis` Codex job
3. backend waits briefly for the fast path
4. if Codex does not finish in time, the item is saved with `processing_status=codex_pending`
5. when Codex completes, the backend promotes the item to `processing_status=pending`
6. the normal worker pipeline continues from there

This means `codex_pending` is the intentional placeholder status for admin Codex uploads.

## Verification Commands

Use these after production-facing changes:

```bash
cd /Users/neo/Desktop/closetgptrenew
./scripts/verify_production.sh
```

Manual spot checks:

```bash
curl -I https://closetgpt-frontend.vercel.app/signin
curl -I https://closetgpt-frontend.vercel.app/debug-token
curl -I https://closetgpt-frontend.vercel.app/api/test-env
curl -I https://closetgptrenew-production.up.railway.app/health
curl -I https://closetgptrenew-production.up.railway.app/debug/routes
curl -I https://closetgptrenew-production.up.railway.app/api/test-inline
```

Expected behavior:

- public frontend routes return `200`
- internal frontend debug routes return `404`
- backend health routes return `200`
- internal backend debug/test/admin routes return `404`

## Sync Rule With OpenClaw

OpenClaw should not maintain a second source of deploy/runtime truth for EasyOutfit.

OpenClaw should:

- treat this file as the canonical EasyOutfit operator playbook
- keep workspace-lane docs focused on execution rhythm, standups, and delegated work
- point back to this file for repo, deploy, branch, Codex bridge, and production verification truth

If EasyOutfit runtime or deploy truth changes:

1. update this file first
2. update OpenClaw pointer docs second
3. update registry/status truth if the workspace state changed
