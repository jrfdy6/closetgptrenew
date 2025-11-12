#!/usr/bin/env python3
"""
Start the backend locally for development
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import openai
        import torch
        import clip
        import PIL
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements-full.txt")
        return False

def start_backend():
    """Start the backend server"""
    try:
        print("🚀 Starting Easy Outfit Backend...")
        print("📍 Server will be available at: http://localhost:8080")
        print("🔗 API docs will be available at: http://localhost:8080/docs")
        
        # Set environment variables
        os.environ.setdefault("PORT", "8080")
        os.environ.setdefault("ENVIRONMENT", "development")
        
        # Start the server
        subprocess.run([
            "python", "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8080",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    print("🔧 Easy Outfit Backend - Local Development")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start the backend
    start_backend()

if __name__ == "__main__":
    main() 