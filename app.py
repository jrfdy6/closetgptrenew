import logging
import sys
import os
from pathlib import Path

# Configure logging to see what's happening during startup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("=== Starting FastAPI application ===")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import importlib
import traceback

# Create the app first
app = FastAPI(
    title="ClosetGPT API",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0"
)
print("DEBUG: FastAPI app created - simplified version for Railway deployment")

# Configure CORS first
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://localhost:3000,https://closetgpt-clean.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Add production URLs
allowed_origins.extend([
    "https://closetgpt-clean.vercel.app",
    "https://closetgpt-frontend.vercel.app",
    "https://closetgptrenew.vercel.app",
    "https://closetgpt-frontend-ggn2bebjo-johnnie-fields-projects.vercel.app",
    "https://closetgpt-frontend-lqe5zyn9u-johnnie-fields-projects.vercel.app",
    "https://closetgptrenew-*.vercel.app",
    "https://closetgpt-frontend-*.vercel.app"
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://closetgpt(renew|frontend)-[a-z0-9-]*\.vercel\.app$|^https://closetgpt-frontend-[a-z0-9]+-[a-z0-9-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# ---------------- ROOT ENDPOINTS ----------------
@app.get("/")
def root():
    return {"status": "API running", "message": "ClosetGPT API is running with simplified deployment"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@app.get("/health/simple")
async def simple_health_check():
    """Simple health check for Railway"""
    return {
        "status": "healthy",
        "message": "Simplified app is working",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "working", "features": ["wardrobe", "outfits", "weather", "analytics"]}

# ---------------- WARDROBE ENDPOINTS ----------------
@app.get("/api/wardrobe/wardrobe-stats")
async def get_wardrobe_stats():
    """Get wardrobe statistics - simplified version"""
    try:
        # For now, return mock data until we can get the full system working
        return {
            "total_items": 0,
            "categories": {},
            "colors": {},
            "user_id": "mock-user",
            "message": "Simplified backend - returning mock data"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get wardrobe statistics: {str(e)}"
        )

@app.get("/api/wardrobe/trending-styles")
async def get_trending_styles():
    """Get trending styles - simplified version"""
    try:
        return {
            "trending_styles": [
                {"name": "Classic Denim", "popularity": 85, "category": "bottoms"},
                {"name": "Minimalist Basics", "popularity": 78, "category": "tops"},
                {"name": "Athleisure", "popularity": 72, "category": "activewear"}
            ],
            "total_trends": 3,
            "message": "Simplified backend - returning mock data"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trending styles: {str(e)}"
        )

# ---------------- OUTFIT HISTORY ENDPOINT ----------------
@app.get("/api/outfit-history/")
async def get_outfit_history():
    """Get outfit history - simplified version"""
    try:
        return {
            "outfitHistory": [],
            "message": "Simplified backend - returning empty data"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get outfit history: {str(e)}"
        )

# ---------------- STARTUP LOG ----------------
@app.on_event("startup")
async def show_all_routes():
    print("\n📜 ROUTES TABLE:")
    for route in app.routes:
        print(f"{route.path} → {route.name} ({', '.join(route.methods)})")
    print()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)