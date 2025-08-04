#!/usr/bin/env python3
print("=== main.py is being executed ===")

# Import the app from app_full.py
from app_full import app

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    print(f"Starting main app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 