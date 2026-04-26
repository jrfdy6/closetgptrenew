# Easy Outfit App

A modern AI-powered wardrobe management and outfit generation system with a clean, production-ready architecture.

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
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
   Use Python 3.11 for local backend work. The current dependency set does not install cleanly on Python 3.10 or 3.12.

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

## 🔧 Production Deployment

### Backend Deployment
- **Railway:** Use `deploy_to_railway.sh`
- **Render:** Use `render.yaml`
- **Docker:** Use the provided Dockerfile

### Frontend Deployment
- **Vercel:** Use `vercel.json`
- **Netlify:** Configure build settings
- **Docker:** Build and deploy container

## 🧪 Testing

The project has been cleaned to exclude comprehensive outfit generation tests while maintaining essential functionality. All test files have been removed to keep the codebase production-ready.

## 🔒 Security

- Firebase credentials are managed through environment variables
- All Firebase access goes through the backend
- No direct Firebase initialization from the frontend

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. # Updated Sat Aug  9 20:29:53 EDT 2025
# Force deployment Mon Sep 15 01:43:27 EDT 2025
# Force deployment - Tue Sep 16 05:47:04 EDT 2025
# Force deployment Tue Oct 28 18:09:09 EDT 2025
