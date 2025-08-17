print("🔍 DEBUG: File loading started - this should appear first!")
import logging
import sys
import os
from pathlib import Path

# Configure logging to see what's happening during startup
print("🔍 DEBUG: About to configure logging...")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print("🔍 DEBUG: Logging configured successfully")

logger.info("=== Starting FastAPI application ===")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")
logger.info(f"__file__ location: {__file__}")
print("🔍 DEBUG: About to import FastAPI...")

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
print("DEBUG: FastAPI app created - deployment test - CORS fix attempt - FORCING REDEPLOY - Router fixes deployed")
print("🔍 DEBUG: FastAPI app created successfully, about to configure CORS...")

# Configure CORS first
print("🔍 DEBUG: Starting CORS configuration...")
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://localhost:3000,https://closetgpt-clean.vercel.app")
print(f"🔍 DEBUG: ALLOWED_ORIGINS env var: {allowed_origins_str}")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
print(f"🔍 DEBUG: Parsed allowed_origins: {allowed_origins}")

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

print("🔍 DEBUG: About to add CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://closetgpt(renew|frontend)-[a-z0-9-]*\.vercel\.app$|^https://closetgpt-frontend-[a-z0-9]+-[a-z0-9-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)
print("🔍 DEBUG: CORS middleware added successfully")
print("🔍 DEBUG: About to add explicit OPTIONS handler...")

# Add explicit OPTIONS handler for all routes to ensure CORS headers are sent
print("🔍 DEBUG: About to define OPTIONS handler function...")
@app.options("/{full_path:path}")
async def options_handler(full_path: str, request: Request):
    """Explicit OPTIONS handler for all routes to ensure CORS headers are sent."""
    print("🔍 DEBUG: OPTIONS handler function defined successfully")
    from fastapi.responses import Response
    
    # Get the origin from the request
    origin = request.headers.get("origin")
    
    # Check if origin is in allowed origins
    if origin in allowed_origins or any(re.match(pattern, origin) for pattern in [
        r"^https://closetgpt(renew|frontend)-[a-z0-9-]*\.vercel\.app$",
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
print("🔍 DEBUG: OPTIONS handler function completed successfully")
print("🔍 DEBUG: About to start core modules import section...")

# Try to import and setup core modules
print("🔍 DEBUG: Starting core modules import section...")
try:
    print("🔍 DEBUG: About to import src.core.logging...")
    from src.core.logging import setup_logging
    print("🔍 DEBUG: src.core.logging imported successfully")
    print("🔍 DEBUG: About to call setup_logging()...")
    setup_logging()
    print("DEBUG: Logging setup completed")
    print("🔍 DEBUG: Logging setup completed successfully")
except Exception as e:
    print(f"DEBUG: Logging setup failed: {e}")
    print("🔍 DEBUG: Logging setup failed, continuing...")
    # Continue without logging setup

try:
    print("🔍 DEBUG: About to import src.core.middleware...")
    from src.core.middleware import setup_middleware
    print("🔍 DEBUG: src.core.middleware imported successfully")
    print("🔍 DEBUG: About to call setup_middleware(app)...")
    setup_middleware(app)
    print("DEBUG: setup_middleware(app) completed")
    print("🔍 DEBUG: Middleware setup completed successfully")
    print("🔍 DEBUG: About to exit middleware setup try block...")
except Exception as e:
    print(f"DEBUG: Middleware setup failed: {e}")
    print("🔍 DEBUG: Middleware setup failed, continuing...")
    # Continue without middleware setup

print("🔍 DEBUG: About to start Firebase config import section...")
print("🔍 DEBUG: This print should appear after middleware setup...")
print("🔍 DEBUG: About to reach the Firebase config import section...")
print("🔍 DEBUG: About to reach the Firebase config import section...")
print("🔍 DEBUG: About to reach the Firebase config import section...")
print("🔍 DEBUG: About to reach the Firebase config import section...")
print("🔍 DEBUG: About to reach the Firebase config import section...")
print("🔍 DEBUG: About to reach the Firebase config import section...")
print("🔍 DEBUG: About to reach the Firebase config import section...")

# Try to import Firebase config
print("🔍 DEBUG: Starting Firebase config import...")
print("🔍 DEBUG: About to enter Firebase config import try block...")
print("🔍 DEBUG: About to enter Firebase config import try block...")
print("🔍 DEBUG: About to enter Firebase config import try block...")
print("🔍 DEBUG: About to enter Firebase config import try block...")
print("🔍 DEBUG: About to enter Firebase config import try block...")
print("🔍 DEBUG: About to enter Firebase config import try block...")
print("🔍 DEBUG: About to enter Firebase config import try block...")
try:
    print("🔍 DEBUG: About to import src.config.firebase...")
    from src.config import firebase
    print("DEBUG: Firebase config imported successfully")
    print("🔍 DEBUG: Firebase config import completed successfully")
except Exception as e:
    print(f"DEBUG: Firebase config import failed: {e}")
    print("🔍 DEBUG: Firebase config import failed, continuing...")

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
print("🔍 DEBUG: About to start router loading section...")
print("🔍 DEBUG: This print should appear before router loading...")
ROUTERS = [
    ("src.routes.test_simple", ""),      # Simple test router to verify loading works
    # ("src.routes.auth", "/api/auth"),    # TEMPORARILY DISABLED - causing router loading to fail
    # ("src.routes.image_processing", ""),  # Router already has /api/image prefix - TEMPORARILY DISABLED
    # ("src.routes.image_analysis", ""),   # Router already has /api/image prefix - TEMPORARILY DISABLED
    ("src.routes.weather", ""),          # Router already has /api/weather prefix
    ("src.routes.wardrobe", ""),         # Main wardrobe router with /api/wardrobe prefix
    # ("src.routes.wardrobe_minimal", ""), # Router already has /api/wardrobe prefix - using simplified version
    ("src.routes.wardrobe_analysis", ""), # Router already has /api/wardrobe prefix
    # ("src.routes.outfit", ""),           # Router already has /api/outfit prefix - TEMPORARILY DISABLED
    # ("src.routes.outfits", ""),          # Router already has /api/outfits prefix - TEMPORARILY DISABLED
    ("src.routes.outfit_history", ""),   # Router already has /api prefix
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
print(f"🔍 DEBUG: ROUTERS list contains {len(ROUTERS)} items")
print(f"🔍 DEBUG: ROUTERS = {ROUTERS}")
for mod, prefix in ROUTERS:
    print(f"🔍 DEBUG: About to process router: {mod} with prefix: {prefix}")
    include_router_safe(mod, prefix)
print("🏁 Router loading process complete!")
print("🔍 DEBUG: Router loading process completed successfully!")

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