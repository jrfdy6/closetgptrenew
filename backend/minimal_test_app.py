#!/usr/bin/env python3
"""
Minimal test app to isolate Railway deployment issues.
This is the simplest possible FastAPI app to test Railway deployment.
"""

import os
from fastapi import FastAPI

# Create minimal FastAPI app
app = FastAPI(title="Minimal Test App", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "Minimal test app is working!",
        "status": "healthy",
        "port": os.getenv("PORT", "not set"),
        "environment": "production"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "Minimal health check passed",
        "port": os.getenv("PORT", "not set")
    }

@app.get("/test")
async def test():
    return {
        "message": "Test endpoint working",
        "all_good": True,
        "port": os.getenv("PORT", "not set")
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Starting minimal test app on port {port}")
    print(f"🔍 Environment PORT: {os.getenv('PORT')}")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"❌ Failed to start minimal app: {e}")
        raise
