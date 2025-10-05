#!/usr/bin/env python3
"""
Setup script for local test environment.
This creates a minimal local environment to test the personalization demo.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_local_test_env():
    """Create a local test environment with minimal dependencies."""
    print("🔧 Setting up local test environment...")
    
    # Create virtual environment
    venv_path = Path("local_test_env")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Get the activation script path
    if sys.platform == "win32":
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_path = venv_path / "Scripts" / "pip"
    else:
        activate_script = venv_path / "bin" / "activate"
        pip_path = venv_path / "bin" / "pip"
    
    # Install minimal dependencies for testing
    print("📦 Installing minimal dependencies...")
    
    minimal_deps = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        "httpx==0.25.2",
        "python-dotenv==1.0.0"
    ]
    
    for dep in minimal_deps:
        try:
            print(f"   Installing {dep}...")
            subprocess.run([str(pip_path), "install", dep], check=True, capture_output=True)
            print(f"   ✅ {dep} installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {dep}: {e}")
    
    print("✅ Local test environment setup complete!")
    print(f"📝 To activate: source {activate_script}")
    print(f"🐍 Python path: {venv_path / 'bin' / 'python' if sys.platform != 'win32' else venv_path / 'Scripts' / 'python.exe'}")

if __name__ == "__main__":
    create_local_test_env()
