#!/usr/bin/env python3
print("Hello from Railway!")
print("Python is working!")

import os
print(f"PORT: {os.getenv('PORT', 'Not set')}")
print(f"Environment variables: {list(os.environ.keys())}")

try:
    import fastapi
    print("FastAPI imported successfully!")
except ImportError as e:
    print(f"FastAPI import failed: {e}")

try:
    import uvicorn
    print("Uvicorn imported successfully!")
except ImportError as e:
    print(f"Uvicorn import failed: {e}")

print("Test completed!") 