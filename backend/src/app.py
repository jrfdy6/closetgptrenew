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
logger.info(f"__file__ location: {__file__}")

from fastapi import FastAPI, Request, Depends, HTTPException, status
import re
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

# Create the app first
app = FastAPI(
    title="ClosetGPT API",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0"
)
print("DEBUG: FastAPI app created - deployment test - CORS fix attempt")

# Configure CORS first
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://localhost:3000,https://closetgpt-clean.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Add production URLs
allowed_origins.extend([
    "https://closetgpt-clean.vercel.app",
    "https://closetgpt-frontend.vercel.app",
    "https://closetgptrenew.vercel.app",  # Add the current Vercel domain
    # Allow any Vercel preview deployment for this project
    "https://closetgptrenew-*.vercel.app",
    "https://closetgpt-frontend-*.vercel.app"
])

# Add Railway preview URLs if in development
if os.getenv("ENVIRONMENT") == "development":
    allowed_origins.extend([
        "http://localhost:3000",
        "https://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3001"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://closetgpt(renew|frontend)-[a-z0-9-]*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Add explicit OPTIONS handler for image upload to ensure CORS headers are sent
@app.options("/api/image/upload")
async def options_image_upload():
    """Explicit OPTIONS handler for image upload to ensure CORS headers are sent."""
    from fastapi.responses import Response
    response = Response(status_code=200)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Add inline test route to isolate the issue
@app.post("/api/image/upload-inline")
async def upload_image_inline():
    """Inline test route to verify FastAPI routing is working"""
    logger.info("Inline upload route called successfully")
    return {"message": "Inline upload route is working", "status": "success"}

@app.get("/api/test-inline")
async def test_inline():
    """Inline test route to verify FastAPI routing is working"""
    logger.info("Inline test route called successfully")
    return {"message": "Inline test route is working", "status": "success"}

# Try to import and setup core modules
try:
    from .core.logging import setup_logging
    setup_logging()
    print("DEBUG: Logging setup completed")
except Exception as e:
    print(f"DEBUG: Logging setup failed: {e}")
    # Continue without logging setup

try:
    from .core.middleware import setup_middleware
    setup_middleware(app)
    print("DEBUG: setup_middleware(app) completed")
except Exception as e:
    print(f"DEBUG: Middleware setup failed: {e}")
    # Continue without middleware setup

# Try to import Firebase config
try:
    from .config import firebase
    print("DEBUG: Firebase config imported successfully")
except Exception as e:
    print(f"DEBUG: Firebase config import failed: {e}")

# Import routes with error handling
def safe_import_router(module_name, router_name):
    """Safely import a router module."""
    try:
        logger.info(f"Attempting to import {module_name}.{router_name}")
        
        # Add routes directory to Python path for Railway deployment
        import sys
        import os
        routes_path = os.path.join(os.path.dirname(__file__), "routes")
        logger.info(f"Routes path: {routes_path}")
        logger.info(f"Routes path exists: {os.path.exists(routes_path)}")
        
        if routes_path not in sys.path:
            sys.path.insert(0, routes_path)
            logger.info(f"Added {routes_path} to Python path")
        
        logger.info(f"Current Python path: {sys.path}")
        
        # Now try to import the module
        logger.info(f"Importing module: {module_name}")
        module = __import__(module_name, fromlist=[router_name])
        logger.info(f"Successfully imported module: {module}")
        
        router = getattr(module, router_name)
        logger.info(f"Successfully got router: {router}")
        return router
    except Exception as e:
        logger.exception(f"Failed to import {module_name}.{router_name}: {e}")
        raise  # Re-raise to see the actual error

# Import and include routers with error handling
routers_to_include = [
    ("wardrobe", "router"),
    ("outfit", "router"),
    ("outfits", "router"),
    ("image_processing", "router"),
    ("image_analysis", "router"),
    ("weather", "router"),
    ("outfit_history", "router"),
    ("test_debug", "router"),
]

logger.info("=== Starting router inclusion process ===")

for module_name, router_name in routers_to_include:
    try:
        logger.info(f"Processing router: {module_name}.{router_name}")
        router = safe_import_router(module_name, router_name)
        
        if module_name == "wardrobe":
            logger.info(f"Including wardrobe router with prefix /api/wardrobe")
            app.include_router(router, prefix="/api/wardrobe", tags=["wardrobe"])
        elif module_name == "outfit":
            logger.info(f"Including outfit router with prefix /api/outfit")
            app.include_router(router, prefix="/api/outfit", tags=["outfit"])
        elif module_name == "outfits":
            logger.info(f"Including outfits router with prefix /api/outfits")
            app.include_router(router, prefix="/api/outfits", tags=["outfits"])
        elif module_name == "image_processing":
            logger.info(f"Including image_processing router with NO prefix (router already has /api/image)")
            app.include_router(router, tags=["images"])
        elif module_name == "image_analysis":
            logger.info(f"Including image_analysis router with no prefix")
            app.include_router(router)
        elif module_name == "weather":
            logger.info(f"Including weather router with no prefix")
            app.include_router(router)
        elif module_name == "outfit_history":
            logger.info(f"Including outfit_history router with prefix /api")
            app.include_router(router, prefix="/api", tags=["outfit-history"])
        elif module_name == "test_debug":
            logger.info(f"Including test_debug router with tags")
            app.include_router(router, tags=["test"])
        
        logger.info(f"✅ Successfully included {module_name} router")
    except Exception as e:
        logger.exception(f"❌ Failed to include {module_name} router: {e}")

logger.info("=== Router inclusion process completed ===")

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
        "port": "8080"
    }

@app.get("/")
async def root():
    return {"message": "ClosetGPT API - Full app is working"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "working", "features": ["gpt4_vision", "wardrobe", "outfits", "weather", "analytics"]}

@app.post("/api/test-upload")
async def test_upload():
    """Test endpoint to verify routing is working"""
    return {"message": "Test upload endpoint is working", "status": "success"}