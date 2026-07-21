# EasyOutfit

EasyOutfit is an AI-powered wardrobe assistant that turns a user's real closet,
style preferences, and context into practical outfit recommendations. It combines
a Next.js product experience with FastAPI services, Firebase, image analysis, and
background processing.

**Live product:** [easyoutfitapp.com](https://easyoutfitapp.com)
**Frontend:** [closetgpt-frontend.vercel.app](https://closetgpt-frontend.vercel.app)
**API health:** [closetgptrenew-production.up.railway.app/health](https://closetgptrenew-production.up.railway.app/health)

## What it demonstrates

- AI-assisted clothing-image analysis and wardrobe metadata extraction
- Schema-driven outfit generation using closet inventory, preferences, weather, occasion, and a required base item
- Layered validation plus explicit composition, layering, color, material, style, and wardrobe-intelligence scoring
- A full-stack product flow spanning authentication, Firestore, storage, APIs, and workers
- Feedback, wear history, liked outfits, and wardrobe analytics that improve ranking context over time
- A local Codex job lane for controlled wardrobe audits and admin upload analysis
- Production hardening that keeps internal debug and test routes unavailable by default

## Outfit intelligence

The active generation path is intentionally inspectable:

1. [`backend/src/custom_types/outfit.py`](backend/src/custom_types/outfit.py) defines the typed request and outfit contracts.
2. [`backend/src/routes/outfits/routes.py`](backend/src/routes/outfits/routes.py) assembles wardrobe, weather, profile, trend, and feedback context; applies occasion/category requirements; and orchestrates generation and persistence.
3. [`backend/src/routes/outfits/validation.py`](backend/src/routes/outfits/validation.py) handles combination constraints and validation feedback.
4. [`backend/src/routes/outfits/scoring.py`](backend/src/routes/outfits/scoring.py) scores composition, layering, color harmony, materials, style coherence, and wardrobe intelligence.

This hybrid design keeps model creativity inside deterministic product constraints: the app can explain why a combination was accepted, warn when a request cannot be satisfied by the current wardrobe, and learn from real wear and rating signals.

## 🏗️ Project Structure

```
closetgptrenew/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Core application modules
│   ├── src/                # Source code
│   ├── firebase/           # Firebase configuration
│   ├── app.py              # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── start_backend.py    # Backend startup script
├── frontend/               # Next.js frontend
│   ├── src/                # React components and pages
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── next.config.js      # Next.js configuration
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (Python 3.11):**
   ```bash
   python3.11 -m venv .venv311
   source .venv311/bin/activate  # On Windows: .venv311\Scripts\activate
   ```
   Use Python 3.11 and keep `.venv311` as the canonical local backend environment. The current dependency set does not install cleanly on Python 3.10 or 3.12.

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your Firebase credentials and API keys
   ```

5. **Start the backend server:**
   ```bash
   python run.py
   ```
   
   The backend will run on port 8080.

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm ci
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your configuration
   ```
   `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_BACKEND_URL` should both point at the backend base URL.
   Leave `ENABLE_INTERNAL_DEBUG_PAGES=false` unless you intentionally need internal demo or debug routes exposed in production.

4. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will run on port 3000.

## 🔧 Production and verification

- **Repo:** `closetgptrenew` is the EasyOutfit repo. It is separate from the `aiclone` repo.
- **Canonical operator playbook:** [docs/technical/EASYOUTFIT_OPERATOR_PLAYBOOK.md](docs/technical/EASYOUTFIT_OPERATOR_PLAYBOOK.md)
- **Live deploy branch:** `main`
- **Legacy branch:** `production` is stale historical state and is not the live deploy branch for EasyOutfit.
- **Railway root-link policy:** for this repo, option 1 is intentional.
  - repo root `closetgptrenew/` should link to Railway service `closetgptrenew`
  - `backend/` should link to Railway service `closetgptrenew`
  - `backend/worker/` should link to Railway service `background-processor`
- **Live Railway services:** `closetgptrenew`, `background-processor`, `closetgptrenewopenaisdk`
- **Legacy non-production Railway services:** `closetgpt-backend`, `closetgptrenew-backend`

If a local Railway link points anywhere else, treat it as drift and fix it before deploying.
If OpenClaw workspace docs disagree with EasyOutfit deploy/runtime truth, use the canonical operator playbook above and then update the OpenClaw pointer docs.

### Backend Deployment
- **Railway:** Follow the operator playbook, then use `backend/deploy_to_railway.sh`
- **Render:** `backend/render.yaml` is retained as an alternate configuration
- **Docker:** Use the backend Dockerfile

### Frontend Deployment
- **Vercel:** Use `frontend/vercel.json`

## 🧪 Testing

Run the frontend unit suite and production build:

```bash
cd frontend
npm test -- --runInBand
npm run build
```

Run the backend regression suite:

```bash
cd backend
./.venv311/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

Run the public production-surface checks from the repository root:

```bash
./scripts/verify_production.sh
```

## 🔒 Security

- Server-side Firebase Admin credentials and API keys are supplied through environment variables and are never committed
- Firebase client access supports authenticated product flows; privileged operations and AI calls stay behind server/API boundaries
- Internal demo, debug, diagnostics, and test routes return `404` in production unless explicitly enabled
- API handlers validate authentication and scope wardrobe/outfit access to the requesting user

## 🤖 AI Runtime

- EasyOutfit currently uses OpenAI directly for sync clothing-image analysis and worker-based flat-lay enhancement.
- The researched migration path toward the `aiclone` Codex-runner architecture is documented in [docs/technical/EASYOUTFIT_CODEX_MIGRATION_PLAN.md](docs/technical/EASYOUTFIT_CODEX_MIGRATION_PLAN.md).
- The recommended first move is to centralize AI boundaries inside the backend before migrating any workload onto a local Codex queue.
- Admin upload analysis can now run in a parallel Codex-only cohort. The backend queues those uploads into the Firestore-backed local Codex runner lane, saves placeholder items as `codex_pending`, and promotes them into the normal worker pipeline after Codex writes the final metadata.

## 📱 Features

- AI-powered outfit generation
- Wardrobe management
- Style analysis and recommendations
- Weather-aware outfit suggestions
- User authentication and profiles
- Analytics and insights

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Firebase Admin
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **AI:** OpenAI GPT, CLIP embeddings
- **Database:** Firebase Firestore
- **Storage:** Firebase Storage
- **Authentication:** Firebase Auth

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
