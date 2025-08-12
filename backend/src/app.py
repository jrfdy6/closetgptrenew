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
import importlib
import traceback

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
    "https://closetgpt-frontend-ggn2bebjo-johnnie-fields-projects.vercel.app",  # Your specific Vercel domain
    "https://closetgpt-frontend-lqe5zyn9u-johnnie-fields-projects.vercel.app",  # Your current Vercel preview domain
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
    allow_origin_regex=r"^https://closetgpt(renew|frontend)-[a-z0-9-]*\.vercel\.app$|^https://closetgpt-frontend-[a-z0-9]+-[a-z0-9-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Add explicit OPTIONS handler for all routes to ensure CORS headers are sent
@app.options("/{full_path:path}")
async def options_handler(full_path: str, request: Request):
    """Explicit OPTIONS handler for all routes to ensure CORS headers are sent."""
    from fastapi.responses import Response
    
    # Get the origin from the request
    origin = request.headers.get("origin")
    
    # Check if origin is in allowed origins
    if origin in allowed_origins or any(re.match(pattern, origin) for pattern in [
        r"^https://closetgpt(renew|frontend)-[a-z0-9-]*\.vercel\.app$",
        r"^https://closetgpt-frontend-[a-z0-9]+-[a-z0-9-]+\.vercel\.app$"
    ]):
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    else:
        # Return a simple response for non-allowed origins
        return Response(status_code=200)

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

# Remove duplicate FastAPI app and CORS configuration

# ---------------- FIREBASE INITIALIZATION ----------------
@app.on_event("startup")
async def initialize_firebase():
    """Initialize Firebase on startup"""
    try:
        from firebase_admin import initialize_app, credentials
        from firebase_admin import firestore, storage
        
        # Initialize Firebase if not already initialized
        try:
            initialize_app()
            print("🔥 Firebase initialized successfully")
        except ValueError:
            print("🔥 Firebase already initialized")
            
        # Test database connection
        db = firestore.client()
        print("🔥 Firebase database connected")
        
        # Test storage connection (optional)
        try:
            bucket = storage.bucket()
            print("🔥 Firebase storage connected")
        except ValueError as e:
            print(f"⚠️ Firebase storage not configured: {e}")
            print("⚠️ Image upload functionality may not work without storage bucket")
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        traceback.print_exc()

# ---------------- ROUTER LOADER ----------------
ROUTERS = [
    ("src.routes.image_processing", ""),  # Router already has /api/image prefix
    ("src.routes.image_analysis", ""),   # Router already has /api/image prefix
    ("src.routes.weather", ""),          # Router already has /api/weather prefix
    ("src.routes.wardrobe", ""),         # Main wardrobe router with /api/wardrobe prefix
    ("src.routes.wardrobe_minimal", ""), # Router already has /api/wardrobe prefix - using simplified version
    ("src.routes.wardrobe_analysis", ""), # Router already has /api/wardrobe-analysis prefix
    ("src.routes.outfit", ""),           # Router already has /api/outfit prefix
    ("src.routes.outfits", "/api/outfits"),          # Router needs /api/outfits prefix
    ("src.routes.outfit_history", "/api"), # Router has no prefix, so add /api
    ("src.routes.test_debug", ""),       # Router already has /api/test prefix
]

def include_router_safe(module_name: str, prefix: str):
    try:
        print(f"🔄 Attempting to import {module_name}...")
        module = importlib.import_module(module_name)
        print(f"📦 Successfully imported {module_name}")
        
        router = getattr(module, "router", None)
        if router is None:
            print(f"❌ {module_name}: No `router` object found")
            return
            
        print(f"🔗 Found router in {module_name}, mounting at prefix {prefix}")
        app.include_router(router, prefix=prefix)
        print(f"✅ Mounted {module_name} at prefix {prefix}")
        
    except Exception as e:
        print(f"🔥 Failed to mount {module_name}")
        traceback.print_exc()

print("🚀 Starting router loading process...")
for mod, prefix in ROUTERS:
    include_router_safe(mod, prefix)
print("🏁 Router loading process complete!")

# ---------------- STARTUP LOG ----------------
@app.on_event("startup")
async def show_all_routes():
    print("\n📜 ROUTES TABLE:")
    for route in app.routes:
        print(f"{route.path} → {route.name} ({', '.join(route.methods)})")
    print()

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "API running", "message": "ClosetGPT API is running with bulletproof router loader"}

# ---------------- INLINE TEST ROUTES ----------------
@app.post("/api/image/upload-inline")
async def upload_image_inline():
    """Inline test route to verify FastAPI routing is working"""
    return {"message": "Inline upload route is working", "status": "success"}

@app.get("/api/test-inline")
async def test_inline():
    """Inline test route to verify FastAPI routing is working"""
    return {"message": "Inline test route is working", "status": "success"}

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

# Removed duplicate root route

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "working", "features": ["gpt4_vision", "wardrobe", "outfits", "weather", "analytics"]}

@app.post("/api/test-upload")
async def test_upload():
    """Test endpoint to verify routing is working"""
    return {"message": "Test upload endpoint is working", "status": "success"}