print("=== app_simple.py is being executed ===")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

app = FastAPI(
    title="ClosetGPT API - Simple",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0"
)
print("DEBUG: FastAPI app created")

# Configure CORS
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://localhost:3000,https://closetgpt-clean.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Add production URLs
allowed_origins.extend([
    "https://closetgpt-clean.vercel.app",
    "https://closetgpt-clean-git-main-jrfdy6.vercel.app",
    "https://closetgpt-clean-jrfdy6.vercel.app"
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
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health/simple")
async def simple_health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {
        "message": "ClosetGPT API is running",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/health")
async def api_health():
    """API health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Basic API endpoints for testing
@app.get("/api/test")
async def test_endpoint():
    return {"message": "API is working", "status": "success"}

@app.get("/api/wardrobe/test")
async def wardrobe_test():
    return {"message": "Wardrobe endpoint placeholder", "status": "success"}

@app.get("/api/outfits/test")
async def outfits_test():
    return {"message": "Outfits endpoint placeholder", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 