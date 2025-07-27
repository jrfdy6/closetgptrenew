#!/usr/bin/env python3
print("=== main.py is being executed ===")

import os
import sys

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

try:
    from fastapi import FastAPI
    import uvicorn
    from datetime import datetime
    
    app = FastAPI()
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "message": "Main app working"
        }
    
    @app.get("/")
    async def root():
        return {"message": "Main API working"}
    
    if __name__ == "__main__":
        port = int(os.getenv("PORT", 8000))
        print(f"Starting main app on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
        
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 