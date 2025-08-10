from fastapi import FastAPI, Request, Response
import re
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
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
        module = __import__(f"src.routes.{module_name}", fromlist=[router_name])
        router = getattr(module, router_name)
        return router
    except Exception as e:
        print(f"DEBUG: Failed to import {module_name}.{router_name}: {e}")
        return None

# Import and include routers with error handling
routers_to_include = [
    ("outfit", "router"),
    ("outfits", "router"),
    ("image_processing", "router"),
    ("image_analysis", "router"),
    ("weather", "router"),
    ("style_analysis", "router"),
    ("wardrobe_analysis", "router"),
    ("forgotten_gems", "router"),
    ("wardrobe_minimal", "router"),  # Use minimal wardrobe router
    ("analytics", "router"),
    ("analytics_dashboard", "router"),
    ("auth", "router"),
    ("monitoring", "router"),
    ("security", "router"),
    ("performance", "router"),
    ("feedback", "router"),
    ("public_diagnostics", "router"),
    ("validation_rules", "router"),
    ("item_analytics", "router"),
    ("outfit_history", "router"),
]

for module_name, router_name in routers_to_include:
    try:
        router = safe_import_router(module_name, router_name)
        if router:
            if module_name == "outfit":
                app.include_router(router, prefix="/api/outfit", tags=["outfit"])
            elif module_name == "outfits":
                app.include_router(router, prefix="/api/outfits", tags=["outfits"])
            elif module_name == "image_processing":
                app.include_router(router, prefix="/api/image", tags=["images"])
            elif module_name == "image_analysis":
                app.include_router(router)
            elif module_name == "weather":
                app.include_router(router, prefix="/api", tags=["weather"])
            elif module_name == "style_analysis":
                app.include_router(router, prefix="/api", tags=["style-analysis"])
            elif module_name == "wardrobe_analysis":
                app.include_router(router)
            elif module_name == "forgotten_gems":
                app.include_router(router)
            elif module_name == "wardrobe_minimal":
                app.include_router(router)
            elif module_name == "analytics":
                app.include_router(router, prefix="/api", tags=["analytics"])
            elif module_name == "analytics_dashboard":
                app.include_router(router, prefix="/api", tags=["analytics-dashboard"])
            elif module_name == "auth":
                app.include_router(router)
            elif module_name == "monitoring":
                app.include_router(router, prefix="/api", tags=["monitoring"])
            elif module_name == "security":
                app.include_router(router, prefix="/api/security", tags=["security"])
            elif module_name == "performance":
                app.include_router(router, prefix="/api/performance", tags=["performance"])
            elif module_name == "feedback":
                app.include_router(router)
            elif module_name == "public_diagnostics":
                app.include_router(router, prefix="/api/diagnostics", tags=["public-diagnostics"])
            elif module_name == "validation_rules":
                app.include_router(router, prefix="/api", tags=["validation-rules"])
            elif module_name == "item_analytics":
                app.include_router(router)
            elif module_name == "outfit_history":
                app.include_router(router, prefix="/api", tags=["outfit-history"])
            print(f"DEBUG: Successfully included {module_name} router")
    except Exception as e:
        print(f"DEBUG: Failed to include {module_name} router: {e}")

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