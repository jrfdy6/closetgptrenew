# Railway Architecture

## Project

- **Railway project:** `closetgpt-backend`
- **Environment:** `production`
- **Project ID:** `97ed14e7-f7a6-4f86-b919-94f133ed478e`

## Services

### Live API

- **Service:** `closetgptrenew`
- **Public URL:** `https://closetgptrenew-production.up.railway.app`
- **Status:** production backend in active use by Vercel
- **Code path:** `backend/`

### Background Worker

- **Service:** `background-processor`
- **Role:** async/background wardrobe processing
- **Code path:** `backend/worker/`

### OpenAI SDK Gateway

- **Service:** `closetgptrenewopenaisdk`
- **Role:** OpenAI Apps / MCP-style gateway

### Legacy or Stopped Service

- **Service:** `closetgptrenew-backend`
- **Public URL:** `https://closetgptrenew-backend-production.up.railway.app`
- **Status:** stopped / not the production API Vercel uses
- **Rule:** do not deploy backend changes here unless you intentionally revive that service

## Deployment Commands

### Backend API

```bash
cd backend
railway up --project 97ed14e7-f7a6-4f86-b919-94f133ed478e --environment production --service closetgptrenew
```

### Background Worker

```bash
cd backend/worker
railway up --project 97ed14e7-f7a6-4f86-b919-94f133ed478e --environment production --service background-processor
```

## Linking Rules

- Link `backend/` to service `closetgptrenew`
- Link `backend/worker/` to service `background-processor`
- Do not trust the repo root Railway link for backend deployment work

## Environment Notes

- Railway injects `RAILWAY_PROJECT_ID`, `RAILWAY_PUBLIC_DOMAIN`, and `RAILWAY_STATIC_URL` into deployed services.
- The backend uses those variables to recognize deployed Railway environments and block internal debug/test/admin routes unless `ENABLE_INTERNAL_DEBUG_ROUTES=true`.

## Verification

The live API should answer:

```bash
curl https://closetgptrenew-production.up.railway.app/health
curl https://closetgptrenew-production.up.railway.app/health/simple
curl https://closetgptrenew-production.up.railway.app/api/health
```

And the following should be blocked in production:

```bash
curl -I https://closetgptrenew-production.up.railway.app/debug/routes
curl -I https://closetgptrenew-production.up.railway.app/api/test-inline
curl -I https://closetgptrenew-production.up.railway.app/api/monitoring/dashboard
```
