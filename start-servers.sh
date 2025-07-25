#!/bin/bash

# ClosetGPT Development Server Starter
echo "🚀 Starting ClosetGPT Development Environment..."

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $1 is already in use. Please free up the port and try again."
        exit 1
    fi
}

# Check if ports are available
echo "🔍 Checking port availability..."
check_port 3000
check_port 3001
echo "✅ Ports are available"

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server
echo "📡 Starting Backend (FastAPI) on http://127.0.0.1:3001"
cd backend

# Activate virtual environment from root directory
echo "🐍 Activating Python virtual environment..."
source ../.venv/bin/activate

# Install/update requirements if needed
echo "📦 Installing/updating Python dependencies..."
pip install -r requirements-weather.txt
pip install -r requirements-test.txt

# Start backend in background using uvicorn module approach
echo "🚀 Starting backend server..."
python -m uvicorn src.app:app --host 127.0.0.1 --port 3001 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend health
echo "🔍 Testing backend health..."
if curl -s http://127.0.0.1:3001/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend may still be starting..."
fi

# Start frontend server
echo "🌐 Starting Frontend (Next.js) on http://localhost:3000"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Both servers are starting..."
echo "📡 Backend: http://127.0.0.1:3001"
echo "🌐 Frontend: http://localhost:3000"
echo "📊 Health Check: http://127.0.0.1:3001/health"
echo "📈 Metrics: http://127.0.0.1:3001/metrics"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Keep script running and wait for both processes
wait 