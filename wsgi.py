#!/usr/bin/env python3
print("=== wsgi.py is being executed ===")

# Import from backend directory
import sys
import os
sys.path.append('backend')

from app import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting wsgi app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 