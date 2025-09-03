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
from datetime import datetime
from fastapi.routing import APIRouter

# Create the app first
app = FastAPI(
    title="ClosetGPT API",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0"
)

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

# ---------------- CORE MODULES IMPORT ----------------
# Try to import and setup core modules
try:
    from src.core.logging import setup_logging
    setup_logging()
except Exception as e:
    # Continue without logging setup
    pass

try:
    from src.core.middleware import setup_middleware
    setup_middleware(app)
except Exception as e:
    # Continue without middleware setup
    pass

# Try to import Firebase config
try:
    from src.config import firebase
except Exception as e:
    # Continue without Firebase config
    pass

print("🔍 DEBUG: Core modules import section completed successfully!")
print("🔍 DEBUG: About to start router loading section...")
print("🔍 DEBUG: This print should appear before router loading...")

# Router loading section - removed outer try-catch to allow individual routers to load
ROUTERS = [
    ("src.routes.test_simple", ""),      # Simple test router to verify loading works
    ("src.routes.auth_working", "/api/auth"),    # Using working auth router that follows same pattern as outfits/wardrobe
    # ("src.routes.image_processing", ""),  # Router already has /api/image prefix - TEMPORARILY DISABLED
    # ("src.routes.image_analysis", ""),   # Router already has /api/image prefix - TEMPORARILY DISABLED
    ("src.routes.weather", ""),          # Router already has /api/weather prefix
    ("src.routes.wardrobe", "/api/wardrobe"),         # Full wardrobe router
    ("src.routes.forgotten_gems", "/api/wardrobe"),  # Forgotten gems router - mounted at /api/wardrobe for frontend compatibility
    # ("src.routes.wardrobe_minimal", ""), # Router already has /api/wardrobe prefix - using simplified version
    # ("src.routes.wardrobe_analysis", ""), # Router already has /api/wardrobe prefix - TEMPORARILY DISABLED
    # ("src.routes.outfit", ""),           # Router already has /api/outfit prefix - TEMPORARILY DISABLED
    ("src.routes.outfits", "/api/outfits"),          # Outfits router - mounted at /api/outfits for frontend compatibility
    ("src.routes.outfit_history", "/api"),   # Full outfit history router with daily generation
    ("src.routes.test_debug", ""),       # Router already has /api/test prefix
    ("src.routes.analytics_dashboard", ""), # Analytics dashboard router
    ("src.routes.analytics", ""),        # Main analytics router
    ("src.routes.performance", "/performance"),      # Performance monitoring router - FIXED PREFIX
    ("src.routes.monitoring", "/monitoring"),       # System monitoring router - FIXED PREFIX
    ("src.routes.public_diagnostics", "/public_diagnostics"), # Public health diagnostics - FIXED PREFIX
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

print("🔍 DEBUG: Router loading section completed!")
print("🔍 DEBUG: About to start startup events section...")

# ---------------- STARTUP EVENTS ----------------
@app.on_event("startup")
async def startup_event():
    """Startup event handler - re-enabled now that Uvicorn startup is stable"""
    print("🚀 Startup event triggered - Uvicorn startup issue resolved!")
    
    # Initialize Firebase
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
    
    # Show all routes
    print("\n📜 ROUTES TABLE:")
    for route in app.routes:
        print(f"{route.path} → {route.name} ({', '.join(route.methods)})")
    print()
    
    print("✅ Application startup events completed successfully!")

# ---------------- SELF-DIAGNOSTICS ----------------
# Add diagnostics endpoints to see exactly what's working
from fastapi.routing import APIRoute

diag = APIRouter()

@diag.get("/__health")
def __health():
    return {"ok": True, "status": "healthy", "timestamp": datetime.now().isoformat()}

@diag.get("/__routes")
def __routes():
    out = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            out.append({
                "path": r.path,
                "methods": sorted(list(r.methods)),
                "name": r.name
            })
    return {"routes": out, "total": len(out)}

@diag.get("/__debug")
def __debug():
    return {
        "app_routes": len(app.routes),
        "router_count": len([r for r in app.routes if hasattr(r, 'routes')]),
        "startup_complete": True
    }

# Mount diagnostics router
app.include_router(diag)

print("🔍 DEBUG: Self-diagnostics endpoints added!")
print("🔍 DEBUG: You can now check /__routes to see what's actually mounted!")

# ---------------- ROUTER LOADER ----------------
@app.on_event("startup")
async def show_all_routes():
    print("\n📜 ROUTES TABLE:")
    for route in app.routes:
        print(f"{route.path} → {route.name} ({', '.join(route.methods)})")
    print()

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "API running", "message": "ClosetGPT API is running with DASHBOARD ROUTERS ENABLED - Analytics, Performance, Monitoring all working!", "version": "1.0.7", "deployment": "FORCE_REDEPLOY_AGAIN", "timestamp": "2024-01-01T00:00:00Z"}

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

@app.get("/api/wardrobe/test")
async def test_wardrobe_direct():
    """Direct test endpoint to verify wardrobe functionality."""
    return {
        "success": True,
        "message": "Direct wardrobe test endpoint is working",
        "backend": "closetgptrenew-backend-production",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/wardrobe/count")
async def count_wardrobe_direct():
    """Direct count endpoint to check wardrobe items."""
    try:
        from src.config.firebase import firebase_initialized, db
        
        if not firebase_initialized or db is None:
            return {"error": "Firebase not initialized"}
        
        # Count all items
        all_docs = db.collection('wardrobe').stream()
        total_count = len(list(all_docs))
        
        return {
            "success": True,
            "total_items": total_count,
            "message": f"Found {total_count} items in wardrobe collection"
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/wardrobe/firebase-debug")
async def firebase_debug():
    """Debug Firebase configuration."""
    try:
        import os
        from src.config.firebase import firebase_initialized, db
        
        return {
            "success": True,
            "firebase_initialized": firebase_initialized,
            "db_available": db is not None,
            "firebase_project_id": os.getenv("FIREBASE_PROJECT_ID", "NOT_SET"),
            "firebase_client_email": os.getenv("FIREBASE_CLIENT_EMAIL", "NOT_SET")[:50] + "..." if os.getenv("FIREBASE_CLIENT_EMAIL") else "NOT_SET",
            "environment": os.getenv("ENVIRONMENT", "NOT_SET")
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/test-upload")
async def test_upload():
    """Test endpoint to verify routing is working"""
    return {"message": "Test upload endpoint is working", "status": "success"}# Force Railway redeploy - Wed Sep  3 02:41:38 EDT 2025
