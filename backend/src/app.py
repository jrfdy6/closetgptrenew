import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from src.routes import (
    auth,
    image_processing,
    image_analysis,
    weather,
    wardrobe,
    wardrobe_analysis,
    outfit,
    outfits,
    outfit_history
    # forgotten_gems  # Temporarily disabled due to import issues
)

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="ClosetGPT Backend")

# CORS middleware - More robust configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:3000",
        "https://localhost:3000",
        
        # Production domains
        "https://closetgpt-clean.vercel.app",
        "https://closetgpt-frontend.vercel.app",
        
        # Vercel preview deployments (wildcard patterns)
        "https://closetgpt-frontend-*.vercel.app",
        "https://closetgptrenew-*.vercel.app",
        
        # Specific current domains (for immediate compatibility)
        "https://closetgpt-frontend-pmw4txto2-johnnie-fields-projects.vercel.app",
        "https://closetgpt-frontend-hqqi05dd5-johnnie-fields-projects.vercel.app",
        "https://closetgpt-frontend-jccojct6k-johnnie-fields-projects.vercel.app",
        "https://closetgpt-frontend-q2w0wliue-johnnie-fields-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers with proper prefixes
logger.info("🔗 Registering routers...")
app.include_router(auth.router, prefix="/api/auth")
logger.info("✅ Registered /api/auth")
app.include_router(image_processing.router, prefix="/api/image")
app.include_router(image_analysis.router, prefix="/api/image")
app.include_router(weather.router, prefix="/api/weather")
app.include_router(wardrobe.router, prefix="/api/wardrobe")
app.include_router(wardrobe_analysis.router, prefix="/api/wardrobe")
app.include_router(outfit.router, prefix="/api/outfit")
logger.info("✅ Registered /api/outfit (singular)")
app.include_router(outfits.router, prefix="/api/outfits")  # ✅ Fix for GET /api/outfits
logger.info("✅ Registered /api/outfits (plural) - THIS SHOULD HANDLE /api/outfits?limit=20")
app.include_router(outfit_history.router, prefix="/api/outfit-history")  # ✅ Add missing outfit history routes
# app.include_router(forgotten_gems.router, prefix="/api/wardrobe")  # ✅ Temporarily disabled

# Startup logging
logger.info("=== Starting FastAPI application ===")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python path: {os.sys.path}")
logger.info(f"__file__ location: {__file__}")

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete. All routers mounted successfully.")

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "API running", "message": "ClosetGPT API is running with clean router mounting"}

# ---------------- HEALTH CHECKS ----------------
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
        "message": "Full app is working",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "working", "features": ["gpt4_vision", "wardrobe", "outfits", "weather", "analytics"]}

# ---------------- TEST ENDPOINTS ----------------
@app.post("/api/test-upload")
async def test_upload():
    """Test endpoint to verify routing is working"""
    return {"message": "Test upload endpoint is working", "status": "success"}

@app.get("/api/test-inline")
async def test_inline():
    """Inline test route to verify FastAPI routing is working"""
    return {"message": "Inline test route is working", "status": "success"}

@app.post("/api/image/upload-inline")
async def upload_image_inline():
    """Inline test route to verify FastAPI routing is working"""
    return {"message": "Inline upload route is working", "status": "success"}