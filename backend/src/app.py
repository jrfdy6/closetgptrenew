import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    logger.info("Application startup complete. Basic app is running.")

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "API running", "message": "ClosetGPT API is running with basic functionality"}

# ---------------- HEALTH CHECKS ----------------
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment - REDEPLOY FIX"""
    try:
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.2"  # Updated version to trigger redeploy
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
        "message": "Basic app is working",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "working", "features": ["basic", "health", "ready"]}

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

# ---------------- MOCK ENDPOINTS FOR FRONTEND ----------------
@app.get("/api/wardrobe/")
async def mock_wardrobe():
    """Mock wardrobe endpoint to prevent frontend errors"""
    return {
        "success": True,
        "items": [],
        "count": 0,
        "user_id": "mock_user"
    }

@app.get("/api/auth/profile")
async def mock_profile():
    """Mock profile endpoint to prevent frontend errors"""
    return {
        "id": "mock_user",
        "name": "Mock User",
        "email": "mock@example.com",
        "gender": "male",
        "onboardingCompleted": True
    }

@app.post("/api/outfits/generate")
async def mock_outfit_generation():
    """Mock outfit generation endpoint"""
    return {
        "success": True,
        "outfit": {
            "id": "mock_outfit_1",
            "name": "Mock Outfit",
            "items": [
                {"id": "item1", "name": "Mock Shirt", "type": "shirt"},
                {"id": "item2", "name": "Mock Pants", "type": "pants"}
            ]
        }
    }