# EasyOutfit Operator Playbook

This is the canonical operator playbook for EasyOutfit.

Use it for:

- deploy truth
- environment truth
- Codex bridge truth
- admin Codex cohort truth
- verification after production-facing changes

If OpenClaw workspace docs and the product repo disagree, this file wins for EasyOutfit runtime and deployment truth.

## Current release and privileged boundary — September 24, 2026

The onboarding and connected-app release is deployed on `main` at
`cfe6cdd425e93eee624d3ac7c9b4c4e3236aa8b3` (PRs 10 and 11). The prior Goal 6
hold and paused-worker notes are historical; the API and image worker are running,
and `EASYOUTFIT_FLATLAY_REQUESTS_PAUSED=false`. The subsequent deep gamification
audit is being implemented on `codex/gamification-launch-polish`; do not describe
that candidate as deployed until its exact artifacts and acceptance are recorded.
See [the 59-challenge baseline audit](../gamification-launch-audit-2026-09-24.md)
and [launch verification](GAMIFICATION_LAUNCH_VERIFICATION.md).

- Vercel production: `dpl_6eppYsKS4oEhhkUUCZbCcbQw6mBG`, exact `cfe6cdd4`.
- Railway API: `bc01e86d-4a9f-40f7-8ce9-8329a9ae7a8a`, exact `cfe6cdd4`.
- Railway rewards/privacy worker: `82d06727-ddf2-4680-9d55-96151dc21f53`, exact `cfe6cdd4`.
- Railway image worker: `b599b94b-67ee-4a62-be57-4b34bfd4733c`, `31e1fe8a`;
  its worker subtree is byte-identical to `cfe6cdd4`.
- Protected Firestore rules: `6ac4e643-cf21-4042-be05-1d75bcd53561`, SHA-256
  `1ddc121a3bac204aff875a10ab2606bd84863e5fe4c9199946ab33d4a87d3dea`.
  All 26 production indexes were READY. The complete index manifest is
  `backend/firestore.indexes.json`; the empty frontend manifest must not replace it.

Vercel serves the frontend, public Firebase client configuration and thin fixed-origin
API proxies. It contains no Firebase Admin runtime and needs no Admin private keys.
Railway owns privileged profile, quiz, onboarding, wardrobe, outfit, reward and image
writes. Verified bearer identity, revocation checks, ownership checks, protected
server fields, durable receipts, private jobs and app-data epoch fences remain mandatory.
The canonical rules source is `frontend/firestore.rules`; do not deploy the divergent
backend rules copy or bundle unrelated Storage-rule changes with a rules release.

Existing customer pages, the complete questionnaire, ten unique usable garments
with outfit category coverage, and authoritative legacy completion remain the product
contract. Stripe and additional paid image/provider experiments are excluded from
this release. Native phone camera/share tests were waived, not passed. Calendar and
fault simulations do not establish weeks of natural production observation.

Before a production change, independently review the frozen source, test evidence,
production-config build, TypeScript baseline comparison, rules/index needs and recovery
plan. Deploy the matching API and dedicated worker, then verify the matching frontend
and canonical domains. Record exact source/artifact IDs. Do not restore older source,
weaker rules, Vercel Admin keys or obsolete deployment holds as a fallback.

For containment, the flatlay admission flag affects new API requests only; stopping
image dispatch requires stopping its worker. A gamification-only change does not need
a paid-image pause or image-worker replacement when their source and interfaces are
unchanged. Preserve reward receipts and privacy markers during any recovery.

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
- Image worker: Railway service `background-processor`
- Rewards/privacy worker: Railway service `gamification-worker`, `python -m src.worker.gamification_runner`
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
