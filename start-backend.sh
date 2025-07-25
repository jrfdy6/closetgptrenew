#!/bin/bash

# Navigate to the backend directory
cd "$(dirname "$0")/backend"

# Activate the virtual environment
source .venv311/bin/activate

# Check if python is available
if command -v python &> /dev/null; then
    echo "Starting backend server with 'python'..."
    python run.py
elif command -v python3 &> /dev/null; then
    echo "Starting backend server with 'python3'..."
    python3 run.py
else
    echo "Error: Neither 'python' nor 'python3' found in PATH"
    echo "Please ensure Python is installed and available"
    exit 1
fi 