#!/usr/bin/env python3
print("=== debug_startup.py is being executed ===")

import os
import sys

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

try:
    print("Attempting to import FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully!")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    print("Attempting to import uvicorn...")
    import uvicorn
    print("✅ Uvicorn imported successfully!")
except ImportError as e:
    print(f"❌ Uvicorn import failed: {e}")

try:
    print("Attempting to import firebase_admin...")
    import firebase_admin
    print("✅ Firebase Admin imported successfully!")
except ImportError as e:
    print(f"❌ Firebase Admin import failed: {e}")

print("=== Environment variables ===")
env_vars = [
    "PORT", "FIREBASE_PROJECT_ID", "FIREBASE_CLIENT_EMAIL", 
    "FIREBASE_PRIVATE_KEY", "ENVIRONMENT"
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        if "PRIVATE_KEY" in var:
            print(f"{var}: {'*' * 20} (hidden)")
        else:
            print(f"{var}: {value}")
    else:
        print(f"{var}: Not set")

print("=== Debug startup completed ===") 