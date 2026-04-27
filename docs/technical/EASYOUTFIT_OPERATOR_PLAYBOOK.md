# EasyOutfit Operator Playbook

This is the canonical operator playbook for EasyOutfit.

Use it for:

- deploy truth
- environment truth
- Codex bridge truth
- admin Codex cohort truth
- verification after production-facing changes

If OpenClaw workspace docs and the product repo disagree, this file wins for EasyOutfit runtime and deployment truth.

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
