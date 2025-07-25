#!/bin/bash

# ClosetGPT Development Server Starter
echo "🚀 Starting ClosetGPT Development Environment..."

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Backend
echo "📡 Starting Backend (FastAPI) on http://127.0.0.1:3001"
cd backend
source ../.venv/bin/activate
python -m uvicorn src.app:app --host 127.0.0.1 --port 3001 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Frontend
echo "🌐 Starting Frontend (Next.js) on http://localhost:3000"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are starting..."
echo "📡 Backend: http://127.0.0.1:3001"
echo "🌐 Frontend: http://localhost:3000"
echo "📊 Health Check: http://127.0.0.1:3001/health"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait 