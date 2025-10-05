#!/bin/bash

# Quick start script for local personalization demo testing
# This script sets up and runs the local test environment

echo "🚀 Starting Local Personalization Demo Test Environment"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Check if we're in the backend directory
if [ ! -f "local_personalization_demo_server.py" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

echo "✅ Backend directory confirmed"

# Setup local test environment
echo "📦 Setting up local test environment..."
python3 setup_local_test_env.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to setup local test environment"
    exit 1
fi

echo "✅ Local test environment setup complete"

# Check if virtual environment exists
if [ ! -d "local_test_env" ]; then
    echo "❌ Virtual environment not created"
    exit 1
fi

# Activate virtual environment and install dependencies
echo "🔧 Activating virtual environment and installing dependencies..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source local_test_env/Scripts/activate
else
    # Unix-like systems
    source local_test_env/bin/activate
fi

# Install additional dependencies if needed
pip install httpx

echo "✅ Dependencies installed"

# Start the local server
echo "🚀 Starting local personalization demo server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 local_personalization_demo_server.py
