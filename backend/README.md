# Easy Outfit Backend

This is the backend API for Easy Outfit, providing AI-powered clothing analysis and outfit recommendations.

## Features

- **Image Analysis**: Analyze clothing items using GPT-4 Vision and CLIP
- **Style Detection**: Identify clothing types, colors, and styles
- **Recommendations**: Generate outfit suggestions based on user preferences
- **Weather Integration**: Consider weather conditions for outfit recommendations

## Quick Start

1. **Create a Python 3.11 virtual environment**:
   ```bash
   python3.11 -m venv .venv311
   source .venv311/bin/activate
   ```
   Use `.venv311` as the canonical local backend environment. The older `venv` and `local_test_env` directories in this repo are stale.

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**:
   ```bash
   cp env.example .env
   # Fill in Firebase and API credentials
   ```
   Leave `ENABLE_INTERNAL_DEBUG_ROUTES=false` unless you intentionally need internal backend debug routes exposed in a non-local environment.

4. **Run locally**:
   ```bash
   python run.py
   ```
   The backend listens on port `8080`.

5. **Deploy to Railway**:
   ```bash
   railway up --project 97ed14e7-f7a6-4f86-b919-94f133ed478e --environment production --service closetgptrenew
   ```
   The live API service is `closetgptrenew`. The separate `closetgptrenew-backend` service in Railway is currently stopped and is not the production backend Vercel uses.
   Under the current option-1 policy, the repo root and `backend/` should both link to `closetgptrenew`.

6. **Deploy the background worker**:
   ```bash
   cd worker
   railway up --project 97ed14e7-f7a6-4f86-b919-94f133ed478e --environment production --service background-processor
   ```

## API Endpoints

- `GET /health` - Health check
- `POST /api/analyze-image` - Analyze clothing image
- `POST /api/outfits` - Generate outfit recommendations

## Environment Variables

- `OPENAI_API_KEY` - OpenAI API key for the hosted EasyOutfit AI runtime
- `EASYOUTFIT_OPENAI_TIMEOUT_SECONDS` - default request timeout for hosted AI calls
- `EASYOUTFIT_OPENAI_VISION_MODEL` - sync clothing-analysis model override
- `EASYOUTFIT_OPENAI_EMBEDDING_MODEL` - embedding model override
- `EASYOUTFIT_OPENAI_IMAGE_EDIT_MODEL` - worker flat-lay image-edit model override
- `EASYOUTFIT_OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS` - worker image-edit timeout override
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `FIREBASE_STORAGE_BUCKET` - Firebase Storage bucket name
- `PORT` - Server port (default: 8080)

## AI Runtime Notes

- The current production backend still uses direct OpenAI-hosted inference for sync image analysis and worker-driven flat-lay enhancement.
- The planned migration toward the `aiclone` Codex-runner model is documented in [docs/technical/EASYOUTFIT_CODEX_MIGRATION_PLAN.md](/Users/neo/Desktop/closetgptrenew/docs/technical/EASYOUTFIT_CODEX_MIGRATION_PLAN.md:1).
- The intended first step is to centralize AI calls behind a runtime layer before introducing any EasyOutfit-local Codex job queue.
- The first EasyOutfit-local Codex queue path is now `POST /api/codex-jobs` with Firestore-backed state and the bridge script at [scripts/local_codex_bridge_easyoutfit.py](/Users/neo/Desktop/closetgptrenew/scripts/local_codex_bridge_easyoutfit.py:1).
- Bridge claim/complete/fail endpoints require `EASYOUTFIT_LOCAL_CODEX_TOKEN`.
- User-facing Codex job endpoints are operator-only by default. Set `EASYOUTFIT_CODEX_OPERATOR_USER_IDS` or `EASYOUTFIT_CODEX_JOB_ACCESS=authenticated` if you intentionally want broader access.
- Admin upload analysis can now run through the same local Codex lane by setting `EASYOUTFIT_CODEX_UPLOAD_ANALYSIS_ENABLED=true` and putting the verified admin cohort in `EASYOUTFIT_CODEX_ADMIN_EMAILS` and/or `EASYOUTFIT_CODEX_COHORT_USER_IDS`.
- Admin upload items save as `processing_status=codex_pending` until Codex finishes; once the job completes, the backend promotes them to the normal worker queue with `processing_status=pending`.

## Local Codex Bridge

Minimal setup for the first EasyOutfit Codex job lane:

```bash
export EASYOUTFIT_LOCAL_CODEX_TOKEN=replace_with_long_random_token
export EASYOUTFIT_CODEX_API_BASE_URL=http://localhost:8080/api/codex-jobs
export EASYOUTFIT_CODEX_OPERATOR_USER_IDS=your_firebase_uid
python3 scripts/local_codex_bridge_easyoutfit.py
```

The first supported job kind is `wardrobe_metadata_audit`.

To keep the bridge always on for admin upload analysis:

```bash
chmod +x scripts/run_local_codex_bridge_easyoutfit.sh scripts/install_easyoutfit_codex_bridge_launch_agent.sh
./scripts/install_easyoutfit_codex_bridge_launch_agent.sh
```

The launch agent reads local secrets from `.env.easyoutfit_codex_bridge`, which should define `EASYOUTFIT_LOCAL_CODEX_TOKEN`.

## Deployment

The backend is configured to deploy to Railway with the correct app entry point.
- Production internal/test/debug routes are blocked by default unless `ENABLE_INTERNAL_DEBUG_ROUTES=true` is set.
- EasyOutfit deploys from `main`. The remote `production` branch is stale historical state and should not be treated as the live deploy source.
# Clean deployment
# Railway deployment trigger - Tue Aug 12 06:47:16 EDT 2025
# Force deployment Mon Sep  8 06:28:18 EDT 2025
# Trigger Railway deployment
# Trigger Railway deployment
# Simple debug endpoint added
