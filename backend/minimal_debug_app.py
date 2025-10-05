#!/usr/bin/env python3
"""
Minimal FastAPI app for debugging Railway deployment issues
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create minimal app
app = FastAPI(title="Minimal Debug App", version="1.0.0")

# Add basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    print("🔍 DEBUG: Root endpoint called")
    return {"message": "Minimal app is working!", "port": os.getenv("PORT", "unknown")}

@app.get("/health")
async def health():
    print("🔍 DEBUG: Health endpoint called")
    return {"status": "ok", "message": "Minimal health check"}

@app.get("/health/")
async def health_slash():
    return {"status": "ok", "message": "Minimal health check with slash"}

@app.get("/_health")
async def health_underscore():
    return {"status": "ok", "message": "Minimal health check with underscore"}

@app.get("/test")
async def test():
    return {"status": "ok", "message": "Minimal test endpoint"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Starting minimal app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
