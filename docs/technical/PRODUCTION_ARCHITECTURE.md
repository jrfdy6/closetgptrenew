# Easy Outfit Production Architecture

Canonical operator playbook:

- [docs/technical/EASYOUTFIT_OPERATOR_PLAYBOOK.md](/Users/neo/Desktop/closetgptrenew/docs/technical/EASYOUTFIT_OPERATOR_PLAYBOOK.md:1)

## Current Production Topology

- **Repo:** `closetgptrenew` (EasyOutfit) is separate from `aiclone`
- **Frontend:** Vercel project `closetgpt-frontend`
- **Backend API:** Railway service `closetgptrenew`
- **Background worker:** Railway service `background-processor`
- **OpenAI SDK gateway:** Railway service `closetgptrenewopenaisdk`

## Goal 6 Privileged Boundary — Rollout in Progress

The accepted source is `801b6679062e0ad1df6c0f5e085ddeac5c4d8724`. Protected
Firestore rules and the Railway API are live. Worker acceptance is held because
garment preparation fails after originals are preserved; the frontend production
release is also held. The operator playbook remains the authority for sequencing;
the Goal 6 handoff records actual deployment IDs and remaining gates.

| Surface | Candidate responsibility |
| --- | --- |
| Vercel | Frontend, browser Firebase client and thin fixed-origin proxies; no Firebase Admin package/runtime or service-account credentials |
| Railway API | Verified bearer identity and privileged profile, onboarding, quiz, garment and image writes |
| Railway worker | Durable garment/flatlay processing, lease recovery and publication of versioned assets |
| Firestore rules | Owner access constrained by server-owned profile fields, private job/receipt state and managed wear-history protection |

Migrated Railway endpoints check revocation, reject disabled and anonymous
accounts, and reject mismatched user-ID assertions in headers, query parameters
and bodies. Profile updates allow editable fields while preserving subscription,
quotas, quiz receipts and other server authority. The active legacy
`/api/auth/profile` GET/PUT routes share this contract. Fresh profile edits cannot
manufacture quiz completion through style preference aliases; these edits require
pre-update stored completion or legacy evidence. Synchronous profile transactions
execute outside the request event loop.

The frontend proxy selects its destination from trusted configuration and a fixed
route path. It forwards bearer authorization and the required body/content type,
not cookies, forwarded-host values or UID/role assertions. It refuses redirects
and non-JSON upstream responses and returns private, no-store JSON. Its default
upstream deadline is 50 seconds; multipart `/api/image/upload` retains file/field
semantics and uses 45 seconds. Retry/readback must resolve uncertain writes after
a timeout. Unused legacy Admin/Clerk/migration/upload-direct routes return `410`.

Raw image-URL admission remains under the previous policy; the worker's
`original_source` validation occurs at use time. This migration is not evidence
of a new general URL-admission or external-fetch guarantee.

## Canonical Production URLs

- **Frontend:** `https://closetgpt-frontend.vercel.app`
- **Primary domain:** `https://easyoutfitapp.com`
- **Backend API:** `https://closetgptrenew-production.up.railway.app`
- **Backend health:** `https://closetgptrenew-production.up.railway.app/health`

## Frontend Environment Variables

Set these in the Vercel project environment, not in `vercel.json`:

```bash
NEXT_PUBLIC_API_URL=https://closetgptrenew-production.up.railway.app
NEXT_PUBLIC_BACKEND_URL=https://closetgptrenew-production.up.railway.app
BACKEND_URL=https://closetgptrenew-production.up.railway.app
```

The active frontend code path is env-driven. Do not reintroduce hardcoded Railway production URLs in route handlers or client services.

The parent verified all three canonical URL values read-only during candidate
preparation. Do not add Firebase Admin credentials to Vercel. Privileged Firebase
credentials remain in the intended Railway services; frontend public Firebase
client configuration is a separate concern.

## Backend Deployment Truth

- The live deploy branch is `main`.
- The remote `production` branch is stale historical state and is not the live EasyOutfit deploy branch.
- The live backend service is `closetgptrenew`.
- The separate Railway service `closetgptrenew-backend` is currently stopped and should not be treated as production.
- The separate Railway service `closetgpt-backend` is also legacy/non-production for EasyOutfit.
- For this controlled rollout, deploy the accepted Git commit through the official
  `serviceInstanceDeploy` API with explicit `commitSha`, canonical service/environment
  IDs and `latestCommit: false`. The linked branch remains `main` until integration.
- Do not use an unverified CLI archive: the first `railway up` attempt omitted
  required files because of monorepo context and ignore rules; it failed before
  replacing the running API. Explicit Git-source deployment resolved that failure.

## Backend Safety Defaults

- Internal frontend demo/debug routes are blocked in production unless `ENABLE_INTERNAL_DEBUG_PAGES=true`.
- Internal backend debug/test/admin routes are blocked in production unless `ENABLE_INTERNAL_DEBUG_ROUTES=true`.
- The backend detects deployed Railway environments via Railway-injected environment variables and returns `404` for internal routes by default.

## Local Development Truth

- Canonical backend venv: `.venv311`
- Canonical frontend local backend env: `NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_BACKEND_URL`
- Do not rely on `backend/venv` or `backend/local_test_env`; those are stale.

## Operational Notes

- Vercel production currently deploys from `main`.
- Under the current root-link policy, repo root and `backend/` should both link to Railway service `closetgptrenew`.
- `backend/worker/` should link to Railway service `background-processor`.
- During the controlled rollout, use explicit accepted-commit deployment. If changing
  admission variables before `main` is integrated, use `--skip-deploys` and then
  deploy that accepted commit; automatic variable deployment can restore older code.
- If any local Railway link points at `aiclone-backend`, `closetgpt-backend`, or `closetgptrenew-backend`, treat that as deploy drift.

## Candidate Release and Recovery Gates

Independent parent acceptance of the final source, tests, build/typecheck, rules
and recovery procedure precedes production actions. Refresh the original artifact
inventory, hold flatlay admission and worker dispatch, apply the exact protected
`frontend/firestore.rules`, deploy/verify the matching API, replace the worker
deliberately from `backend/worker`, then verify and release the frontend. A preview
build must not be assumed to acquire Production variables when promoted. Avoid
intermediate Git-triggered deployments and record actual source/deployment IDs.

The current rules source hash is
`eafa27b3270d6906835309c68a10b13b71822852d8a35f8b501e36da9f9811ca`.
Deploy Firestore rules only; the backend rules copy's unrelated nested wardrobe
grant, Storage rules and indexes are outside this release.

Goal 5's archived source is historical evidence, not a compatible complete
rollback now that privileged ownership has moved. Contain incidents by pausing
API flatlay admission and stopping worker dispatch, and prepare a reviewed forward
repair that retains the Railway Admin boundary, protected rules, versioned
readers and private receipts/ledgers. Do not restore old Vercel Admin keys, old
writers or permissive rules as a shortcut.

Base `801b6679` verification records frontend 720 tests/57 suites passed, backend 533
passed/one macOS skip out of 534, rules 263 passed, and a production frontend
build with public client configuration only and no Firebase Admin credentials.
All 134 compiled server-route traces exclude Admin. Typecheck retains 115
existing diagnostics (124 at the previous candidate), with no new diagnostic
positions or changed-file diagnostics; the existing build skips type/lint gates.
Quiz and onboarding oracles match 189 and 241 executed TypeScript cases.
The parent's frozen-source local service-emulator checks passed 25/25, and both
Linux CI runs on accepted `801b6679` passed. The live API health/auth-denial and
signed-in profile compatibility checks passed. Full authenticated frontend,
provider-image and physical-device gates remain pending. See the Goal 6 handoff
for accepted source, exact deployed artifact IDs, later diagnostic checks and worker
containment evidence.

Worker diagnostic source `763220d8` ran once and was stopped after both removal
modes exited by SIGKILL with overlapping container OOM-kill counter increments.
The local compatibility candidate explicitly restores U2NET, the historical
rembg 2.0.50/2.0.67 default, while pinning the inspected rembg 2.0.85 library.
Each existing isolated inference child constructs and passes its own session;
no model/session is initialized in the coordinator. This replaces 2.0.85's
implicit BRIA selection without changing the hosted flatlay provider/model or
readiness, retry and credit contracts. Image-quality and capacity acceptance
remain separate gates; see the Goal 6 handoff for evidence and platform limits.
All ten approved public fixtures completed locally with originals preserved;
visual review still found internal background remnants and thin-lace loss.
Those cutouts must not be represented as the final polished outfit image.
