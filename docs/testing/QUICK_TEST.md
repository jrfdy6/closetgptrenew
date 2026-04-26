# Quick Test Guide

This is the current local smoke test for EasyOutfit. It replaces an older misplaced quick-test flow that referenced prospect and outreach endpoints from a different project.

## Start Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env  # first run only
python run.py
```

Expected local backend URL: `http://localhost:8080`

## Start Frontend

```bash
cd frontend
npm ci
cp env.example .env.local  # first run only
npm run dev
```

Expected local frontend URL: `http://localhost:3000`

## Smoke Tests

### 1. Backend health

```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/health
```

Expected:
- `/health` returns a JSON object with `status: "healthy"`
- `/api/health` returns a JSON object with `status: "ok"`

### 2. Frontend build

```bash
cd frontend
npm run build
```

Expected:
- Build completes successfully
- You may still see non-blocking Next.js `metadata.viewport` warnings on older pages

### 3. Sign-in and dashboard

1. Open `http://localhost:3000/signin`
2. Sign in with a real test account
3. Open `http://localhost:3000/dashboard`
4. Confirm the dashboard loads without proxy errors

Expected:
- Auth succeeds
- Dashboard renders
- No `401`, `404`, or backend proxy errors in the browser network tab

### 4. Wardrobe load and upload

1. Open `http://localhost:3000/wardrobe`
2. Confirm existing wardrobe items load
3. Upload a test clothing image through the batch uploader
4. Re-open the uploaded item and verify metadata appears

Expected:
- Wardrobe list loads
- Upload reaches success state
- Item detail modal shows core metadata like name, type, color, and tags

### 5. Outfit generation

1. Open `http://localhost:3000/outfits` or `http://localhost:3000/outfits/generate`
2. Generate an outfit
3. Submit feedback on the generated outfit

Expected:
- Outfit request completes
- Feedback request succeeds
- No proxy route silently hits the production backend because local env should now drive these routes

## Troubleshooting

- Backend install fails on Python 3.10 or 3.12:
  Use Python 3.11. The current backend dependency set is pinned around that runtime.
- Frontend loads but API requests behave like production:
  Check `frontend/.env.local` and confirm `NEXT_PUBLIC_BACKEND_URL`, `NEXT_PUBLIC_API_URL`, and `BACKEND_URL` point to `http://localhost:8080`.
- Build passes but logs are noisy:
  The current main warnings are mostly stale `metadata.viewport` exports on older pages.
- Local server cannot bind in a restricted environment:
  Use an in-process backend health check instead:

```bash
./backend/.venv/bin/python -c "import sys,json; from dotenv import load_dotenv; load_dotenv('backend/.env'); sys.path.insert(0,'backend'); from app import app; from fastapi.testclient import TestClient; r=TestClient(app).get('/health'); print(r.status_code); print(json.dumps(r.json()))"
```
