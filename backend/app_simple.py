#!/usr/bin/env python3
print("=== app_simple.py is being executed ===")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

# Create the app
app = FastAPI(
    title="ClosetGPT API - Simple",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0"
)

# Configure CORS
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://localhost:3000,https://closetgpt-clean.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Add production URLs
allowed_origins.extend([
    "https://closetgpt-clean.vercel.app",
    "https://closetgpt-clean-git-main-jrfdy6.vercel.app",
    "https://closetgpt-clean-jrfdy6.vercel.app",
    "https://closetgpt-frontend.vercel.app",
    "https://closetgpt-frontend-git-main-jrfdy6.vercel.app",
    "https://closetgpt-frontend-jrfdy6.vercel.app"
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0",
            "message": "Simple production app working"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health/simple")
async def simple_health_check():
    """Simple health check for Railway"""
    return {
        "status": "healthy",
        "message": "Simple production app is working",
        "port": "8080"
    }

@app.get("/")
async def root():
    return {"message": "ClosetGPT API - Simple production app is working"}

@app.get("/api/health")
async def api_health():
    return {
        "status": "ok", 
        "api": "working", 
        "features": ["basic_api", "health_checks", "cors"],
        "message": "Simple production API is working"
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "Test endpoint working",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    print(f"Starting simple production server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 