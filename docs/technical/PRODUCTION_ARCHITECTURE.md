# Easy Outfit Production Architecture

Canonical operator playbook:

- [docs/technical/EASYOUTFIT_OPERATOR_PLAYBOOK.md](/Users/neo/Desktop/closetgptrenew/docs/technical/EASYOUTFIT_OPERATOR_PLAYBOOK.md:1)

## Current Production Topology

- **Repo:** `closetgptrenew` (EasyOutfit) is separate from `aiclone`
- **Frontend:** Vercel project `closetgpt-frontend`
- **Backend API:** Railway service `closetgptrenew`
- **Background worker:** Railway service `background-processor`
- **OpenAI SDK gateway:** Railway service `closetgptrenewopenaisdk`

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

## Backend Deployment Truth

- The live deploy branch is `main`.
- The remote `production` branch is stale historical state and is not the live EasyOutfit deploy branch.
- The live backend service is `closetgptrenew`.
- The separate Railway service `closetgptrenew-backend` is currently stopped and should not be treated as production.
- The separate Railway service `closetgpt-backend` is also legacy/non-production for EasyOutfit.
- The canonical backend deploy command is:

```bash
railway up --project 97ed14e7-f7a6-4f86-b919-94f133ed478e --environment production --service closetgptrenew
```

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
- Use `backend/deploy_backend.sh` or the explicit `railway up ... --service closetgptrenew` command for backend deploys.
- If any local Railway link points at `aiclone-backend`, `closetgpt-backend`, or `closetgptrenew-backend`, treat that as deploy drift.

## Verification Checklist

After any production-facing change, verify:

```bash
curl https://closetgptrenew-production.up.railway.app/health
curl https://closetgptrenew-production.up.railway.app/health/simple
curl https://closetgptrenew-production.up.railway.app/api/health
```

And confirm these internal routes return `404` in production:

```bash
curl -I https://closetgptrenew-production.up.railway.app/debug/routes
curl -I https://closetgptrenew-production.up.railway.app/api/test-inline
curl -I https://closetgptrenew-production.up.railway.app/api/test-simple/health
```
