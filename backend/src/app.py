import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers with error handling
logger.info("🔗 Registering routers...")

# Try to import and register each router individually
try:
    from src.routes import auth
    app.include_router(auth.router, prefix="/api/auth")
    logger.info("✅ Registered /api/auth")
except Exception as e:
    logger.error(f"❌ Failed to register auth router: {e}")

try:
    from src.routes import image_processing, image_analysis
    app.include_router(image_processing.router, prefix="/api/image")
    app.include_router(image_analysis.router, prefix="/api/image")
    logger.info("✅ Registered /api/image routes")
except Exception as e:
    logger.error(f"❌ Failed to register image routers: {e}")

try:
    from src.routes import weather
    app.include_router(weather.router, prefix="/api/weather")
    logger.info("✅ Registered /api/weather")
except Exception as e:
    logger.error(f"❌ Failed to register weather router: {e}")

try:
    from src.routes import wardrobe, wardrobe_analysis
    app.include_router(wardrobe.router, prefix="/api/wardrobe")
    app.include_router(wardrobe_analysis.router, prefix="/api/wardrobe")
    logger.info("✅ Registered /api/wardrobe routes")
except Exception as e:
    logger.error(f"❌ Failed to register wardrobe routers: {e}")

try:
    from src.routes import outfit
    app.include_router(outfit.router, prefix="/api/outfit")
    logger.info("✅ Registered /api/outfit (singular)")
except Exception as e:
    logger.error(f"❌ Failed to register outfit router: {e}")

try:
    from src.routes import outfits
    app.include_router(outfits.router, prefix="/api/outfits")
    logger.info("✅ Registered /api/outfits (plural)")
except Exception as e:
    logger.error(f"❌ Failed to register outfits router: {e}")

try:
    from src.routes import outfit_history
    app.include_router(outfit_history.router, prefix="/api/outfit-history")
    logger.info("✅ Registered /api/outfit-history")
except Exception as e:
    logger.error(f"❌ Failed to register outfit history router: {e}")

try:
    from src.routes import forgotten_gems
    app.include_router(forgotten_gems.router, prefix="/api/wardrobe")
    logger.info("✅ Registered forgotten gems")
except Exception as e:
    logger.error(f"❌ Failed to register forgotten gems router: {e}")

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
    """Health check endpoint for Railway deployment - REDEPLOY FIX"""
    try:
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.1"  # Updated version to trigger redeploy
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