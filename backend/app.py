import logging
import sys
import os
import time
from pathlib import Path
from fastapi import Request, HTTPException

# Force Railway deploy - Jan 14 2026 - Cached wardrobe count fix (DEPLOY NOW)
# Configure logging to see what's happening during startup
# Use environment variable for log level (default INFO in dev, WARNING in prod)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)
logger.info(f"🔧 Logging configured at level: {LOG_LEVEL}")
ROUTER_DEBUG = os.getenv("ROUTER_DEBUG", "").lower() in {"1", "true", "yes", "on"}

# Import startup module for version tracking and guarded imports
try:
    from src.app_start import COMMIT_SHA, WARDROBE_PREPROCESSOR_AVAILABLE, WardrobePreprocessor
    logger.info(f"🚀 App startup module loaded - commit={COMMIT_SHA}")
    logger.info(f"🔧 WardrobePreprocessor available: {WARDROBE_PREPROCESSOR_AVAILABLE}")
except Exception as e:
    logger.exception(f"❌ Failed to load startup module: {e}")
    COMMIT_SHA = "unknown"
    WARDROBE_PREPROCESSOR_AVAILABLE = False
    WardrobePreprocessor = None

# Startup logging removed to reduce Railway rate limiting

from fastapi import FastAPI, Request, Depends, HTTPException, status
import re
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
import importlib
import traceback
from datetime import datetime
from fastapi.routing import APIRouter
import json
from pathlib import Path

# Authentication must never degrade to a fabricated user.
from src.auth.auth_service import get_current_user_id, get_current_user

# Create the app first
app = FastAPI(
    title="Easy Outfit API",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0",
    docs_url=None, redoc_url=None, openapi_url=None,
)

TRUTHY_ENV_VALUES = {"1", "true", "yes", "on"}
INTERNAL_BACKEND_ROUTE_EXACT_PATHS = {
    "/api/outfits/check-outfits-db",
    "/api/wardrobe/initialize-my-wardrobe-count",
    "/api/wardrobe/backfill-processing-status",
    "/health/health/reset",
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/api/health/dependencies",
    "/health/health/detailed",
    "/health/health/metrics",
    "/api/image/create-firebase-bucket",
    "/api/image/test-firebase-upload",
    "/api/image/debug-firebase",
}
INTERNAL_BACKEND_ROUTE_PREFIXES = (
    "/__",
    "/debug",
    "/api/monitoring",
    "/api/backfill",
    "/api/reprocess",
    "/api/wardrobe/check-item-public",
    "/api/wardrobe/check-item",
)
INTERNAL_BACKEND_ROUTE_SEGMENTS = {
    "admin",
    "debug",
    "docs",
    "monitoring",
    "openapi.json",
    "redoc",
    "test",
}
INTERNAL_BACKEND_ROUTE_SEGMENT_PREFIXES = (
    "admin-",
    "debug-",
    "seed-",
    "test-",
    "verify-",
)
INTERNAL_BACKEND_ROUTE_SEGMENT_SUFFIXES = (
    "-debug",
    "-test",
)


def env_flag_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in TRUTHY_ENV_VALUES


def internal_backend_routes_enabled() -> bool:
    return env_flag_enabled("ENABLE_INTERNAL_DEBUG_ROUTES")


def is_internal_backend_path(path: str) -> bool:
    normalized = path.rstrip("/") or "/"
    if normalized in INTERNAL_BACKEND_ROUTE_EXACT_PATHS:
        return True

    if any(
        normalized == prefix or normalized.startswith(f"{prefix}/")
        for prefix in INTERNAL_BACKEND_ROUTE_PREFIXES
    ):
        return True

    segments = [segment for segment in normalized.split("/") if segment]
    return any(
        segment in INTERNAL_BACKEND_ROUTE_SEGMENTS
        or any(segment.startswith(prefix) for prefix in INTERNAL_BACKEND_ROUTE_SEGMENT_PREFIXES)
        or any(segment.endswith(suffix) for suffix in INTERNAL_BACKEND_ROUTE_SEGMENT_SUFFIXES)
        for segment in segments
    )


@app.middleware("http")
async def block_internal_backend_routes(request: Request, call_next):
    if is_internal_backend_path(request.url.path):
        if not internal_backend_routes_enabled():
            return Response(content="Not Found", status_code=404)
        from src.auth.operator import require_operator
        from starlette.concurrency import run_in_threadpool
        from fastapi.responses import JSONResponse
        try:
            await run_in_threadpool(require_operator, request, Response())
        except HTTPException as error:
            return JSONResponse(status_code=error.status_code, content={"detail": error.detail})
    response = await call_next(request)
    if is_internal_backend_path(request.url.path):
        response.headers["Cache-Control"] = "private, no-store"
    return response

# Configure CORS first
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://localhost:3000,https://easyoutfit-clean.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Add production URLs
allowed_origins.extend([
    "https://easyoutfit-clean.vercel.app",
    "https://easyoutfit-frontend.vercel.app",
    "https://easyoutfitapp.vercel.app",  # Add the current Vercel domain
    "https://easyoutfit-frontend-ggn2bebjo-johnnie-fields-projects.vercel.app",  # Your specific Vercel domain
    "https://easyoutfit-frontend-lqe5zyn9u-johnnie-fields-projects.vercel.app",  # Your current Vercel preview domain
    # Allow any Vercel preview deployment for this project
    "https://easyoutfitapp-*.vercel.app",
    "https://easyoutfit-frontend-*.vercel.app",
    # New custom domain
    "https://easyoutfitapp.com",
    "https://www.easyoutfitapp.com",
    # ChatGPT plugin origins
    "https://aiclone-production-32dc.up.railway.app",
    "https://chat.openai.com",
    "http://localhost:3000"
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
    # Remove production domain from regex - it's already in allow_origins for exact matching
    # Mobile browsers reject regex-based CORS when allow_credentials=True
    # Keep regex only for Vercel preview URLs which don't need credentials
    allow_origin_regex=r"^https://easyoutfit(app|frontend)-[a-z0-9-]*\.vercel\.app$|^https://easyoutfit-frontend-[a-z0-9]+-[a-z0-9-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers in response
)

# Add GZip compression middleware to reduce response size for mobile
from starlette.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB

# Add explicit OPTIONS handler for all routes to ensure CORS headers are sent
@app.options("/{full_path:path}")
async def options_handler(full_path: str, request: Request):
    """Explicit OPTIONS handler for all routes to ensure CORS headers are sent."""
    from fastapi.responses import Response
    
    # Get the origin from the request
    origin = request.headers.get("origin")
    
    # Check if origin is in allowed origins or matches regex patterns
    # Production domain (easyoutfitapp.com) should use exact matching, not regex
    # Mobile browsers reject regex-based CORS when credentials are enabled
    is_allowed = (
        origin in allowed_origins or
        (origin and re.match(r"^https://easyoutfit(app|frontend)-[a-z0-9-]*\.vercel\.app$", origin)) or
        (origin and re.match(r"^https://easyoutfit-frontend-[a-z0-9]+-[a-z0-9-]+\.vercel\.app$", origin))
    )
    
    if is_allowed and origin:
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
        response.headers["Access-Control-Allow-Credentials"] = "true"
        logger.info(f"✅ CORS OPTIONS request allowed for origin: {origin}")
        return response
    else:
        # Return a simple response for non-allowed origins
        logger.warning(f"⚠️ CORS OPTIONS request blocked for origin: {origin}")
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

# Firebase config will be imported when needed, not at startup
# This prevents import-time crashes

# Router loading section

# Router loading section - removed outer try-catch to allow individual routers to load
ROUTERS = [
    ("src.routes.onboarding", "/api/onboarding"),
    ("src.routes.style_quiz", "/api/style-quiz"),
    ("src.routes.user_profile", "/api/user"),
    ("src.routes.test_category", "/api/test"),  # Test category mapping fix
    ("src.routes.image_processing_minimal_test", "/api/image-test"),  # Minimal test router
    ("src.routes.wardrobe_analysis", "/api/wardrobe-analysis"), # Router mounted at /api/wardrobe-analysis - ENABLED for gap analysis
    ("src.routes.wardrobe", "/api/wardrobe"),               # Main wardrobe router - mounted at /api/wardrobe
    ("src.routes.garment_processing", "/api/wardrobe"),    # Authenticated, attempt-fenced image retries
    ("src.routes.image_upload_minimal", "/api/image"),  # Minimal image upload router - RE-ENABLED
    ("src.routes.image_analysis", ""),   # Full image analysis router - RE-ENABLED for image hash generation
    ("src.routes.auth_working", "/api/auth"),    # Using working auth router that follows same pattern as outfits/wardrobe
    ("src.routes.weather", ""),          # Router already has /api/weather prefix
    ("src.routes.debug_stats", "/api"),  # Debug stats router for Railway-proof debugging
    ("src.routes.health", "/health"),     # Health monitoring router
    ("src.routes.forgotten_gems", "/api/wardrobe-insights"),  # Forgotten gems router - mounted at /api/wardrobe-insights to avoid conflict
    ("src.routes.gamification", "/api"),  # Gamification router for XP, levels, badges
    ("src.routes.challenges", "/api"),   # Challenges router for gamification challenges
    # ("src.routes.wardrobe_minimal", ""), # Router already has /api/wardrobe prefix - using simplified version
    # ("simple_outfit", ""),               # Ultra-simple outfit router
    # ("test_outfit_router", ""),          # Test outfit router at root level
    # ("src.routes.outfit_simple", ""),    # Simple outfit router for testing
    # ("src.routes.outfit_test", ""),      # Outfit test router in proper location - REMOVED
    # ("test_router", ""),                 # Test router with no dependencies
    # ("src.routes.outfit_minimal", ""),   # Minimal outfit router - testing import issues
    # ("src.routes.outfit", ""),           # Original outfit router - testing import errors
    ("src.routes.outfits", "/api/outfits"),               # Main outfits router with all endpoints including flatlay processing
    # ("src.routes.outfits.main_hybrid", "/api/outfits"),   # Main hybrid outfit generation router - DISABLED to use main router with performance monitoring
    ("src.routes.backfill_ultra_simple", "/api/backfill"), # Ultra simple backfill endpoint - just visit the URL!
    # ("src.routes.backfill_simple_test", "/api/backfill"), # Simple backfill test endpoint
    # ("src.routes.backfill_trigger", "/api/backfill"),      # Database backfill trigger endpoint - TEMPORARILY DISABLED DUE TO IMPORT ISSUES
    ("src.routes.reprocess_trigger", "/api/reprocess"),    # Reprocess wardrobe items with alpha matting
    # ("src.routes.semantic_telemetry", ""),                # Semantic filtering telemetry router - TEMPORARILY DISABLED DUE TO IMPORT ISSUES
    # ("src.routes.outfits.working_complex", "/api/outfits"),   # Working complex router - TEMPORARILY DISABLED TO TEST RUNTIME ISSUE
    # ("src.routes.personalization_demo.simple_routes", ""),    # Simple personalization demo router - TEMPORARILY DISABLED DUE TO RUNTIME ISSUES
    # ("src.routes.outfits.targeted_test", "/api/outfits"),   # Targeted import test router - ALL IMPORTS WORKING
    # ("src.routes.outfits.routes", "/api/outfits"),   # Complex modular outfits router - STILL HAS IMPORT ISSUES
    # ("src.routes.outfits.test_routes", "/api/outfits"),   # Minimal test outfits router - WORKING
    # ("src.routes.outfits.progressive_routes", "/api/outfits"),   # Progressive outfits router - FAILED (import error)
    # ("src.routes.outfits.debug", "/api/outfits-debug"), # Debug endpoints for outfits - TEMPORARILY DISABLED
    # ("src.routes.strategy_analytics", ""),           # Strategy analytics router - TEMPORARILY DISABLED FOR DEBUGGING
    # ("src.routes.diversity_analytics", ""),          # Diversity analytics router - TEMPORARILY DISABLED FOR DEBUGGING
    # ("src.routes.adaptive_tuning", ""),              # Adaptive tuning router - TEMPORARILY DISABLED FOR DEBUGGING
    # ("src.routes.outfits_with_embeddings", "/api/outfits-personalized"), # Embedding-based personalized outfit generation - TEMPORARILY DISABLED DUE TO SYNTAX ERRORS
    # ("src.routes.lightweight_outfits", "/api/outfits-lightweight"), # Lightweight embeddings without external dependencies - TEMPORARILY DISABLED FOR DEBUGGING
    # ("src.routes.validation_analytics", "/api/validation-analytics"), # Validation failure analytics and insights - TEMPORARILY DISABLED FOR DEBUGGING
    # ("src.routes.generation_metrics", "/api/generation-metrics"), # Generation strategy metrics and monitoring - TEMPORARILY DISABLED FOR DEBUGGING
    # ("src.routes.simple_personalized_outfits", "/api/outfits-simple"), # Simple personalization integration with existing system - TEMPORARILY DISABLED
    ("src.routes.test_simple", "/api/test-simple"), # Test router to verify router loading
    ("src.routes.simple_personalized_outfits_minimal", "/api/outfits-simple-minimal"), # Minimal simple personalization router
    ("src.routes.existing_data_personalized_outfits", "/api/outfits-existing-data"), # Personalization using existing Firebase data
    # ("src.routes.outfits_fast", "/api/outfits-fast"),       # Fast outfit loading with pre-aggregated stats - TEMPORARILY DISABLED
    ("src.routes.outfit_stats_simple", "/api/outfit-stats"), # Simple outfit stats router - fixes 405 errors
    ("src.routes.simple_analytics", ""),                     # NEW: Simple, reliable analytics - no prefix needed
    ("src.routes.outfit_history", "/api/outfit-history"),   # Full outfit history router with daily generation
    ("src.routes.style_inspiration", "/api/style-inspiration"), # Style inspiration recommendations - NEW
    ("src.routes.codex_jobs", ""),  # Firestore-backed EasyOutfit local Codex job queue
    ("src.routes.rag_ingest", "/api"),  # RAG ingestion endpoint at /api/ingest_drive
    ("src.routes.knowledge", "/api"),  # Knowledge endpoints: /api/chat, /api/knowledge/*
    ("src.routes.payments", "/api/payments"),  # Payment and subscription management
    ("src.routes.style_analytics", "/api"),  # Style analytics and reports
    ("src.routes.data_privacy", "/api"),  # Data privacy controls
    # ("src.routes.test_debug", ""),       # Router already has /api/test prefix
    # ("src.routes.analytics_dashboard", ""), # Analytics dashboard router
    ("src.routes.analytics", "/api/analytics"),        # Main analytics router - ENABLED for performance targets
    # ("src.routes.performance", "/performance"),      # Performance monitoring router - FIXED PREFIX
    # ("src.routes.monitoring", "/monitoring"),       # System monitoring router - FIXED PREFIX
    # ("src.routes.public_diagnostics", "/public_diagnostics"), # Public health diagnostics - FIXED PREFIX
    ("src.routes.production_monitoring", "/api/monitoring"),  # NEW: Production monitoring dashboard
    ("src.routes.admin_migration", "/api"),  # Admin migration endpoint
    ("src.routes.gacha", "/api"),  # Gacha & Style Tokens (Variable Ratio Reinforcement)
    ("src.routes.roles", "/api"),  # Internal Status Roles (Status & Power)
    ("src.routes.audit", "/api"),  # Wardrobe Audit (ROI-focused, subscription-gated)
    ("src.routes.wardrobe_admin", "/api/wardrobe"),  # Wardrobe admin utilities (temporary)
]

def include_router_safe(module_name: str, prefix: str):
    """Required routers fail startup rather than silently disappearing."""
    from src.core.route_registry import mount_router
    return mount_router(app, module_name, prefix, importer=importlib.import_module)

# Router loading
# Router loading process

# Direct import test to force visibility of import errors
try:
    from src.routes import outfits
    if ROUTER_DEBUG:
        print("✅ outfits.py imported successfully")
except Exception as e:
    import traceback
    print("❌ outfits.py import failed")
    traceback.print_exc()

for mod, prefix in ROUTERS:
    # Processing router
    include_router_safe(mod, prefix)

# Router loading complete

# Debug: Print all registered routes (as requested)
registered_routes = [f"{r.path} {r.methods}" if hasattr(r, 'path') and hasattr(r, 'methods') else str(r) for r in app.routes]
if ROUTER_DEBUG:
    print("✅ ROUTES REGISTERED:", registered_routes)

# Store routes for debugging endpoint
REGISTERED_ROUTES = registered_routes

# Debug: Log all registered routes only when explicitly requested
if ROUTER_DEBUG:
    logger.info("=== ALL REGISTERED ROUTES ===")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            logger.info(f"PATH={route.path}, METHODS={route.methods}, NAME={route.name}")
    logger.info("=== END ROUTE LIST ===")

# Startup events section

# Image processing router is now working with optional imports

# ---------------- STARTUP EVENTS ----------------
@app.on_event("startup")
async def startup_event():
    """Startup event handler - re-enabled now that Uvicorn startup is stable"""
    # Startup event triggered
    
    from src.core.route_registry import validate_route_table
    validate_route_table(app)
    from src.config.firebase import firebase_initialized, db
    if not firebase_initialized or db is None:
        raise RuntimeError("Authenticated storage is unavailable; refusing unhealthy startup")
    from firebase_admin import storage
    storage.bucket()  # Validate configuration, without an external object fetch.

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

# Self-diagnostics endpoints added

# Add simple debug endpoint for outfit filtering
@app.post("/api/outfits/debug-filter")
async def debug_outfit_filtering(request: Request):
    """Simple debug endpoint to test outfit filtering without complex dependencies."""
    try:
        from src.utils.auth_utils import extract_uid_from_request
        
        # Extract user ID
        uid = extract_uid_from_request(request)
        logger.info(f"🔍 DEBUG FILTER: Request from user: {uid}")
        
        # Get request body
        body = await request.json()
        logger.info(f"🔍 DEBUG FILTER: Request data: {body}")
        
        # Get actual request data
        requested_occasion = body.get("occasion", "unknown")
        requested_style = body.get("style", "unknown")
        requested_mood = body.get("mood", "unknown")
        wardrobe_items = body.get("wardrobe", [])
        
        # If no wardrobe items provided, fetch from database
        if not wardrobe_items:
            try:
                from firebase_admin import firestore
                db = firestore.client()
                if db:
                    q = db.collection("wardrobe").where("userId", "==", uid)
                    docs = q.stream()
                    wardrobe_items = []
                    for doc in docs:
                        data = doc.to_dict() or {}
                        data["id"] = doc.id
                        wardrobe_items.append(data)
                    logger.info(f"🔍 DEBUG FILTER: Fetched {len(wardrobe_items)} items from database")
            except Exception as e:
                logger.error(f"❌ DEBUG FILTER: Failed to fetch wardrobe: {e}")
                wardrobe_items = []
        
        # Analyze actual wardrobe items
        debug_analysis = []
        passed_items = 0
        hard_rejected = 0
        weather_rejected = 0
        
        for item in wardrobe_items[:5]:  # Analyze first 5 items for demo
            item_occasions = item.get("occasion", [])
            item_styles = item.get("style", [])
            item_mood = item.get("mood", [])
            
            # Check if item matches requested occasion
            occasion_match = requested_occasion.lower() in [occ.lower() for occ in item_occasions]
            
            reasons = []
            if not occasion_match:
                reasons.append(f"Occasion mismatch: item occasions {item_occasions} don't include '{requested_occasion}'")
            
            # Simple style check
            style_match = requested_style.lower() in [style.lower() for style in item_styles] if item_styles else True
            
            if not style_match:
                reasons.append(f"Style mismatch: item styles {item_styles} don't include '{requested_style}'")
            
            # Simple mood check
            mood_match = requested_mood.lower() in [mood.lower() for mood in item_mood] if item_mood else True
            
            if not mood_match:
                reasons.append(f"Mood mismatch: item moods {item_mood} don't include '{requested_mood}'")
            
            is_valid = len(reasons) == 0
            
            if is_valid:
                passed_items += 1
            else:
                hard_rejected += 1
            
            debug_analysis.append({
                "id": item.get("id", "unknown"),
                "name": item.get("name", "Unknown Item"),
                "type": item.get("type", "unknown"),
                "valid": is_valid,
                "reasons": reasons,
                "item_data": {
                    "occasion": item_occasions,
                    "style": item_styles,
                    "mood": item_mood
                }
            })
        
        debug_response = {
            "success": True,
            "debug_analysis": {
                "total_items": len(wardrobe_items),
                "filtered_items": passed_items,
                "hard_rejected": hard_rejected,
                "weather_rejected": weather_rejected,
                "debug_analysis": debug_analysis
            },
            "filters_applied": {
                "occasion": requested_occasion,
                "style": requested_style,
                "mood": requested_mood,
                "weather": body.get("weather", {})
            },
            "timestamp": time.time(),
            "user_id": uid,
            "message": f"Real analysis of {len(wardrobe_items)} wardrobe items for {requested_occasion} occasion"
        }
        
        logger.info(f"✅ DEBUG FILTER: Simple debug response sent")
        return debug_response
        
    except Exception as e:
        logger.error(f"❌ DEBUG FILTER: Failed: {e}")
        import traceback
        logger.error(f"❌ DEBUG FILTER: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug analysis failed: {str(e)}"
        )

# ---------------- ROUTER LOADER ----------------
@app.on_event("startup")
async def show_all_routes():
    # Routes table removed to reduce Railway rate limiting
    pass

# ---------------- CHATGPT PLUGIN ROUTES ----------------
# Mount static files directory
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve ChatGPT plugin manifest
@app.get("/.well-known/ai-plugin.json")
async def ai_plugin_manifest():
    """Serve the AI plugin manifest for ChatGPT discovery"""
    plugin_manifest_path = Path(__file__).parent.parent / ".well-known" / "ai-plugin.json"
    if plugin_manifest_path.exists():
        return FileResponse(str(plugin_manifest_path), media_type="application/json")
    else:
        # Fallback: return default manifest
        return {
            "schema_version": "v1",
            "name_for_human": "AI Clone Backend",
            "name_for_model": "aiclone_backend",
            "description_for_human": "Provides Drive ingestion, knowledge storage, and RAG retrieval for your AI Clone.",
            "description_for_model": "Backend for ingestion, chunking, embedding, Firestore storage, and retrieval. Use these endpoints to ingest Google Drive folders, retrieve knowledge, and perform grounded reasoning.",
            "auth": {"type": "none"},
            "api": {
                "type": "openapi",
                "url": "https://aiclone-production-32dc.up.railway.app/openapi.json"
            },
            "logo_url": "https://aiclone-production-32dc.up.railway.app/static/logo.png",
            "contact_email": "support@yourdomain.com",
            "legal_info_url": "https://yourdomain.com/legal"
        }

# Serve OpenAPI spec
@app.get("/openapi.json")
async def openapi_spec():
    """Serve the OpenAPI specification"""
    openapi_path = Path(__file__).parent.parent / "openapi.json"
    if openapi_path.exists():
        return FileResponse(str(openapi_path), media_type="application/json")
    else:
        # Fallback: return auto-generated OpenAPI spec
        return app.openapi()

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "API running", "message": "Easy Outfit API is running with DASHBOARD ROUTERS ENABLED - Analytics, Performance, Monitoring all working!", "version": "1.0.8", "deployment": "FORCE_REDEPLOY_OUTFIT_ROUTER", "timestamp": "2024-01-01T00:00:00Z"}

# ---------------- INLINE TEST ROUTES ----------------
@app.post("/api/image/upload-inline")
async def upload_image_inline():
    raise HTTPException(status_code=410, detail="Use the authenticated image upload endpoint")
    """Inline test route to verify FastAPI routing is working"""
    return {"message": "Inline upload route is working", "status": "success"}

# ---------------- INLINE OUTFIT ROUTES ----------------
@app.get("/api/outfit-test/")
async def get_outfits_inline():
    """Inline outfit router GET endpoint"""
    return {"message": "Inline outfit router is working!", "status": "success"}

# REMOVED: Inline outfit test route that was interfering with real generation
# The real outfit generation is handled by the outfits router at /api/outfit/generate


@app.get("/api/test-inline")
async def test_inline():
    """Inline test route to verify FastAPI routing is working"""
    return {"message": "Inline test route is working", "status": "success"}

@app.get("/health")
@app.get("/health/simple")
@app.get("/api/health")
async def health_check():
    """Minimal liveness after required routers and Firebase passed startup."""
    from datetime import timezone
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to show all registered routes"""
    return {
        "total_routes": len(app.routes),
        "registered_routes": REGISTERED_ROUTES,
        "outfits_routes": [f"{r.path} {r.methods}" for r in app.routes if hasattr(r, 'path') and '/outfits' in r.path]
    }

@app.get("/api/health/dependencies")
async def check_dependencies():
    """Check if all required dependencies are installed"""
    dependencies = {}
    
    try:
        import openai
        dependencies["openai"] = {"status": "ok", "version": openai.__version__}
    except ImportError as e:
        dependencies["openai"] = {"status": "error", "error": str(e)}
    
    try:
        from PIL import Image
        dependencies["PIL"] = {"status": "ok", "version": Image.__version__}
    except ImportError as e:
        dependencies["PIL"] = {"status": "error", "error": str(e)}
    
    try:
        from dotenv import load_dotenv
        dependencies["dotenv"] = {"status": "ok"}
    except ImportError as e:
        dependencies["dotenv"] = {"status": "error", "error": str(e)}
    
    try:
        from firebase_admin import firestore
        dependencies["firebase_admin"] = {"status": "ok"}
    except ImportError as e:
        dependencies["firebase_admin"] = {"status": "error", "error": str(e)}
    
    all_ok = all(dep["status"] == "ok" for dep in dependencies.values())
    
    return {
        "status": "ok" if all_ok else "error",
        "dependencies": dependencies,
        "all_dependencies_installed": all_ok
    }

@app.get("/api/test/openai")
async def test_openai_client():
    """Test OpenAI client initialization"""
    try:
        import os
        import sys
        import importlib
        
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"error": "OPENAI_API_KEY not set"}
        
        # Strip all proxy-related environment variables
        proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "all_proxy", "no_proxy"]
        for var in proxy_vars:
            os.environ.pop(var, None)
        
        # Try to inspect what's happening with the OpenAI import
        try:
            # First, let's see what's in the openai module
            import openai
            print(f"OpenAI module version: {openai.__version__}")
            print(f"OpenAI module file: {openai.__file__}")
            
            # Check if there are any global configurations
            print(f"OpenAI module attributes: {[attr for attr in dir(openai) if not attr.startswith('_')]}")
            
            # Try to create client with explicit inspection
            from openai import OpenAI
            
            # Inspect the OpenAI class
            print(f"OpenAI class: {OpenAI}")
            print(f"OpenAI.__init__ signature: {OpenAI.__init__.__doc__}")
            
            # Try to create client with explicit HTTP client configuration
            import httpx
            
            # Create a custom httpx client without proxy configuration
            http_client = httpx.Client(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            
            # Create OpenAI client with explicit HTTP client
            client = OpenAI(
                api_key=api_key,
                http_client=http_client
            )
            
            return {
                "status": "ok",
                "message": "OpenAI client initialized successfully",
                "api_key_present": bool(api_key),
                "api_key_length": len(api_key) if api_key else 0,
                "openai_version": openai.__version__
            }
            
        except Exception as e:
            # If that fails, let's try to see what parameters are being passed
            import traceback
            return {
                "error": f"OpenAI client test failed: {str(e)}",
                "traceback": traceback.format_exc(),
                "api_key_present": bool(api_key),
                "api_key_length": len(api_key) if api_key else 0
            }
        
    except Exception as e:
        return {"error": f"OpenAI client test failed: {str(e)}"}

@app.get("/api/debug/environment")
async def debug_environment():
    """Debug Railway environment variables"""
    import os
    
    # Check for proxy-related environment variables
    proxy_vars = {k: v for k, v in os.environ.items() if "PROXY" in k.upper()}
    
    # Check for other potentially problematic variables
    openai_vars = {k: v for k, v in os.environ.items() if "OPENAI" in k.upper()}
    
    # Check for HTTP/HTTPS related variables
    http_vars = {k: v for k, v in os.environ.items() if k.upper().startswith(("HTTP", "HTTPS"))}
    
    return {
        "proxy_variables": proxy_vars,
        "openai_variables": openai_vars,
        "http_variables": http_vars,
        "total_env_vars": len(os.environ),
        "python_version": os.sys.version
    }

# Add Railway health check endpoints




@app.get("/api/debug/whoami")
async def debug_whoami(request: Request):
    """Debug endpoint to verify token extraction."""
    try:
        from src.utils.auth_utils import extract_uid_from_request
        uid = extract_uid_from_request(request)
        return {"ok": True, "uid": uid}
    except Exception as e:
        return {"ok": False, "error": str(e)}



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

@app.get("/api/wardrobe/debug-metadata-public")
async def debug_metadata_public():
    """PUBLIC DEBUG: Check wardrobe metadata without auth (TEMPORARY)"""
    try:
        from src.config.firebase import db, firebase_initialized
        
        if not firebase_initialized or db is None:
            return {"error": "Firebase not initialized"}
        
        # Get a few items from the test user
        test_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        
        docs = db.collection('wardrobe').where('userId', '==', test_user_id).limit(5).stream()
        
        items_data = []
        for doc in docs:
            item = doc.to_dict()
            metadata = item.get("metadata", {})
            visual_attrs = metadata.get("visualAttributes") if isinstance(metadata, dict) else None
            
            items_data.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "type": item.get("type"),
                "occasion": item.get("occasion", []),
                "style": item.get("style", []),
                "mood": item.get("mood", []),
                "has_metadata_object": "metadata" in item,
                "metadata_type": type(metadata).__name__ if metadata else None,
                "has_visualAttributes": visual_attrs is not None,
                "visualAttributes_type": type(visual_attrs).__name__ if visual_attrs else None,
                "visualAttributes_keys": list(visual_attrs.keys()) if isinstance(visual_attrs, dict) else None,
                "visualAttributes_wearLayer": visual_attrs.get("wearLayer") if isinstance(visual_attrs, dict) else None,
                "visualAttributes_sleeveLength": visual_attrs.get("sleeveLength") if isinstance(visual_attrs, dict) else None,
                "visualAttributes_fit": visual_attrs.get("fit") if isinstance(visual_attrs, dict) else None,
                "metadata_occasionTags": metadata.get("occasionTags") if isinstance(metadata, dict) else None,
                "metadata_styleTags": metadata.get("styleTags") if isinstance(metadata, dict) else None,
            })
        
        return {
            "success": True,
            "items_checked": len(items_data),
            "items": items_data
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/wardrobe/debug-structure")
async def debug_wardrobe_structure():
    """Debug the actual Firestore wardrobe data structure."""
    try:
        from firebase_admin import firestore
        from src.config.firebase import db
        
        if not db:
            return {"error": "Database not available"}
        
        # Test user ID (from your logs)
        test_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        
        results = {
            "test_user_id": test_user_id,
            "structure_tests": {}
        }
        
        # First, let's get a few sample documents to see the actual structure
        print("🔍 Getting sample wardrobe documents...")
        sample_docs = []
        try:
            all_docs = db.collection('wardrobe').limit(3).stream()
            for doc in all_docs:
                item_data = doc.to_dict()
                sample_docs.append({
                    "doc_id": doc.id,
                    "data": item_data,
                    "fields": list(item_data.keys()) if item_data else []
                })
            
            results["sample_documents"] = sample_docs
            print(f"Found {len(sample_docs)} sample documents")
            
        except Exception as e:
            results["sample_documents"] = {"error": str(e)}
        
        # Test different possible field names for user ID
        user_id_fields = ['userId', 'user_id', 'uid', 'user', 'owner', 'ownerId']
        
        for field_name in user_id_fields:
            try:
                print(f"🔍 Testing field '{field_name}'...")
                wardrobe_ref = db.collection('wardrobe')
                docs = wardrobe_ref.where(field_name, '==', test_user_id).stream()
                
                items = []
                for doc in docs:
                    item_data = doc.to_dict()
                    items.append(item_data)
                
                results["structure_tests"][f"field_{field_name}"] = {
                    "found_items": len(items),
                    "query": f"db.collection('wardrobe').where('{field_name}', '==', user_id)",
                    "sample_item": items[0] if items else None
                }
                
                if len(items) > 0:
                    print(f"✅ Found {len(items)} items with field '{field_name}'")
                    break
                    
            except Exception as e:
                results["structure_tests"][f"field_{field_name}"] = {
                    "error": str(e),
                    "query": f"db.collection('wardrobe').where('{field_name}', '==', user_id)"
                }
        
        # Test Structure 2: Subcollection under users
        try:
            print("🔍 Testing user subcollection structure...")
            user_ref = db.collection('users').document(test_user_id)
            wardrobe_subcollection = user_ref.collection('wardrobe')
            docs = wardrobe_subcollection.stream()
            
            items_structure2 = []
            for doc in docs:
                item_data = doc.to_dict()
                items_structure2.append(item_data)
            
            results["structure_tests"]["user_subcollection"] = {
                "found_items": len(items_structure2),
                "query": "db.collection('users').document(user_id).collection('wardrobe')",
                "sample_item": items_structure2[0] if items_structure2 else None
            }
            
            if len(items_structure2) > 0:
                print(f"✅ Found {len(items_structure2)} items in user subcollection")
            
        except Exception as e:
            results["structure_tests"]["user_subcollection"] = {
                "error": str(e),
                "query": "db.collection('users').document(user_id).collection('wardrobe')"
            }
        
        # Check total items and unique user IDs found
        try:
            print("🔍 Analyzing all wardrobe items...")
            all_docs = db.collection('wardrobe').stream()
            all_items = []
            user_ids_found = {}
            
            for doc in all_docs:
                item_data = doc.to_dict()
                all_items.append(item_data)
                
                # Check all possible user ID fields
                for field_name in user_id_fields:
                    user_id = item_data.get(field_name)
                    if user_id:
                        if user_id not in user_ids_found:
                            user_ids_found[user_id] = []
                        user_ids_found[user_id].append(field_name)
            
            results["analysis"] = {
                "total_items": len(all_items),
                "unique_user_ids": list(user_ids_found.keys())[:10],  # Limit to first 10
                "user_id_fields_found": user_ids_found,
                "test_user_id_in_data": test_user_id in user_ids_found
            }
            
        except Exception as e:
            results["analysis"] = {"error": str(e)}
        
        return results
        
    except Exception as e:
        return {"error": f"Failed to debug Firestore structure: {str(e)}"}

@app.post("/api/test-upload")
async def test_upload():
    """Test endpoint to verify routing is working"""
    return {"message": "Test upload endpoint is working", "status": "success"}

@app.get("/api/wardrobe/check-item-public/{user_id}/{item_name}")
async def check_wardrobe_item_public(user_id: str, item_name: str):
    """Check the data structure of a specific wardrobe item (no auth required for debugging)"""
    try:
        from src.config.firebase import db
        
        if not db:
            return {"error": "Database not available"}
        
        # Query for items matching the name
        items = db.collection('wardrobe').where('userId', '==', user_id).stream()
        
        matching_items = []
        for doc in items:
            item_data = doc.to_dict()
            if item_name.lower() in item_data.get('name', '').lower():
                matching_items.append(item_data)
        
        if not matching_items:
            return {"error": f"No items found matching '{item_name}' for user {user_id}"}
        
        item = matching_items[0]  # Get first match
        
        # Analyze the structure
        analysis_summary = {
            "item_name": item.get('name'),
            "item_id": item.get('id'),
            "top_level_fields": {
                "sleeveLength": item.get('sleeveLength'),
                "fit": item.get('fit'),
                "material": item.get('material'),
                "description": item.get('description'),
                "length": item.get('length'),
                "pattern": item.get('pattern'),
            },
            "has_analysis": bool(item.get('analysis')),
            "has_metadata": bool(item.get('analysis', {}).get('metadata')),
            "has_visual_attributes": bool(item.get('analysis', {}).get('metadata', {}).get('visualAttributes')),
            "visual_attributes": item.get('analysis', {}).get('metadata', {}).get('visualAttributes', {}),
            "natural_description": item.get('analysis', {}).get('metadata', {}).get('naturalDescription'),
            "full_analysis": item.get('analysis')
        }
        
        return analysis_summary
        
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/api/wardrobe/check-item/{item_name}")
async def check_wardrobe_item(item_name: str, current_user_id: str = Depends(get_current_user_id)):
    """Check the data structure of a specific wardrobe item"""
    try:
        from src.config.firebase import db
        
        if not db:
            return {"error": "Database not available"}
        
        # Query for items matching the name
        items = db.collection('wardrobe').where('userId', '==', current_user_id).stream()
        
        matching_items = []
        for doc in items:
            item_data = doc.to_dict()
            if item_name.lower() in item_data.get('name', '').lower():
                matching_items.append(item_data)
        
        if not matching_items:
            return {"error": f"No items found matching '{item_name}'"}
        
        item = matching_items[0]  # Get first match
        
        # Analyze the structure
        analysis_summary = {
            "item_name": item.get('name'),
            "item_id": item.get('id'),
            "top_level_fields": {
                "sleeveLength": item.get('sleeveLength'),
                "fit": item.get('fit'),
                "material": item.get('material'),
                "description": item.get('description'),
                "length": item.get('length'),
                "pattern": item.get('pattern'),
            },
            "has_analysis": bool(item.get('analysis')),
            "has_metadata": bool(item.get('analysis', {}).get('metadata')),
            "has_visual_attributes": bool(item.get('analysis', {}).get('metadata', {}).get('visualAttributes')),
            "visual_attributes": item.get('analysis', {}).get('metadata', {}).get('visualAttributes', {}),
            "natural_description": item.get('analysis', {}).get('metadata', {}).get('naturalDescription'),
            "full_item": item
        }
        
        return analysis_summary
        
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

from src.auth.verified_identity import verified_identity as verified_wardrobe_identity, reject_identity_overrides as reject_wardrobe_identity_overrides


@app.post("/api/wardrobe/")
@app.post("/api/wardrobe/add-direct")
async def add_wardrobe_item_direct(item_data: dict, claims: dict = Depends(verified_wardrobe_identity)):
    """Create an owned garment, or acknowledge an already-persisted owned retry."""
    reject_wardrobe_identity_overrides(claims, item_data)
    current_user_id = claims['uid']
    from src.config.firebase import db
    from src.services.app_data_privacy import AppDataDeletionError
    from src.services.wardrobe_persistence import create_owned_wardrobe_item, WardrobeOwnershipConflict, WardrobeInputError
    from starlette.concurrency import run_in_threadpool

    if db is None:
        raise HTTPException(status_code=503, detail="Wardrobe storage is unavailable")
    try:
        wardrobe_item = await run_in_threadpool(create_owned_wardrobe_item, db, current_user_id, item_data)
        try:
            from src.services.challenge_actions import refresh_action_rewards
            await refresh_action_rewards(current_user_id, expected_epoch=wardrobe_item.get('app_data_epoch', 0), include_upload_milestones=True)
        except Exception:
            logger.exception('Item saved; wardrobe rewards will be reconciled by maintenance')
        return {
            "success": True,
            "message": "Item saved",
            "item_id": wardrobe_item["id"],
            "item": wardrobe_item,
        }
    except AppDataDeletionError as error:
        raise HTTPException(error.status_code, error.detail) from None
    except WardrobeOwnershipConflict:
        raise HTTPException(status_code=409, detail="This item ID is already in use")
    except WardrobeInputError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except Exception:
        raise HTTPException(status_code=503, detail="Your item was not confirmed saved. Please retry.")

@app.post("/api/wardrobe/backfill-processing-status")
async def backfill_processing_status(current_user_id: str = Depends(get_current_user_id)):
    """Backfill processing_status/background fields for wardrobe items that pre-date the worker."""
    try:
        from src.config.firebase import db
        if not db:
            return {"success": False, "error": "Database not available"}
        
        print(f"🧹 Backfill requested by user {current_user_id}")
        
        wardrobe_ref = db.collection('wardrobe').where('userId', '==', current_user_id)
        docs = list(wardrobe_ref.stream())
        
        total_items = len(docs)
        updated_items = 0
        
        for doc in docs:
            data = doc.to_dict() or {}
            updates = {}
            
            if 'processing_status' not in data or data.get('processing_status') is None:
                updates['processing_status'] = 'pending'
            if 'backgroundRemovedUrl' not in data:
                updates['backgroundRemovedUrl'] = data.get('backgroundRemovedUrl', None)
            if 'thumbnailUrl' not in data:
                updates['thumbnailUrl'] = data.get('thumbnailUrl', None)
            
            if updates:
                print(f"   • Updating {doc.id} with {updates}")
                doc.reference.update(updates)
                # VERIFY the update
                verify_doc = doc.reference.get()
                verify_data = verify_doc.to_dict() if verify_doc.exists else {}
                print(f"   ✅ Verified: {doc.id} now has processing_status={verify_data.get('processing_status', 'MISSING')}")
                updated_items += 1
        
        return {
            "success": True,
            "total_items": total_items,
            "updated_items": updated_items,
            "message": f"Backfill complete. Updated {updated_items} of {total_items} items."
        }
    except Exception as e:
        print(f"❌ Error during backfill: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/today-suggestion")
async def get_todays_outfit_suggestion(current_user=Depends(get_current_user)):
    """Compatibility alias; generation and cache behavior have one owner."""
    from src.routes.outfit_history import get_todays_outfit_suggestion as canonical_suggestion
    return await canonical_suggestion(current_user=current_user)

# Flatlay image proxy endpoint to fix CORS issues
@app.get("/api/flatlay/{outfit_id}")
async def proxy_flatlay_image(outfit_id: str):
    """Retired guessed-path reader; current viewer uses verified saved-result URLs."""
    raise HTTPException(status_code=410, detail="Reopen the saved outfit to view its current flatlay")

# Force Railway redeploy - Wed Sep  3 02:41:38 EDT 2025
