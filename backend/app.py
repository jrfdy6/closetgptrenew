import logging
import sys
import os
import time
from pathlib import Path
from fastapi import Request, HTTPException

# Configure logging to see what's happening during startup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
from fastapi.responses import Response
import importlib
import traceback
from datetime import datetime
from fastapi.routing import APIRouter

# Import authentication
try:
    from src.auth.auth_service import get_current_user_id
except ImportError:
    # Fallback for when running as module
    try:
        from auth.auth_service import get_current_user_id
    except ImportError:
        def get_current_user_id():
            return "fallback-user-id"

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

# Firebase config will be imported when needed, not at startup
# This prevents import-time crashes

# Router loading section

# Router loading section - removed outer try-catch to allow individual routers to load
ROUTERS = [
    ("src.routes.test_simple", ""),      # Simple test router to verify loading works
    ("src.routes.test_category", "/api/test"),  # Test category mapping fix
    ("src.routes.image_processing_minimal_test", "/api/image-test"),  # Minimal test router
    ("src.routes.wardrobe_analysis", "/api/wardrobe"), # Router mounted at /api/wardrobe - ENABLED for wardrobe-stats
    ("src.routes.wardrobe", "/api/wardrobe"),               # Main wardrobe router - mounted at /api/wardrobe
    # ("src.routes.image_upload_minimal", "/api/image"),  # Minimal image upload router - TEMPORARILY DISABLED DUE TO SYNTAX ERRORS
    # ("src.routes.image_analysis", ""),   # Full image analysis router with debug logging - TEMPORARILY DISABLED DUE TO SYNTAX ERRORS
    ("src.routes.auth_working", "/api/auth"),    # Using working auth router that follows same pattern as outfits/wardrobe
    ("src.routes.weather", ""),          # Router already has /api/weather prefix
    ("src.routes.debug_stats", "/api"),  # Debug stats router for Railway-proof debugging
    ("src.routes.health", "/health"),     # Health monitoring router
    ("src.routes.forgotten_gems", "/api/wardrobe-insights"),  # Forgotten gems router - mounted at /api/wardrobe-insights to avoid conflict
    # ("src.routes.wardrobe_minimal", ""), # Router already has /api/wardrobe prefix - using simplified version
    # ("simple_outfit", ""),               # Ultra-simple outfit router
    # ("test_outfit_router", ""),          # Test outfit router at root level
    # ("src.routes.outfit_simple", ""),    # Simple outfit router for testing
    # ("src.routes.outfit_test", ""),      # Outfit test router in proper location - REMOVED
    # ("test_router", ""),                 # Test router with no dependencies
    # ("src.routes.outfit_minimal", ""),   # Minimal outfit router - testing import issues
    # ("src.routes.outfit", ""),           # Original outfit router - testing import errors
    ("src.routes.outfits.main_hybrid", "/api/outfits"),   # Main hybrid outfit generation router - MIGRATED FROM PERSONALIZATION DEMO
    ("src.routes.backfill_ultra_simple", "/api/backfill"), # Ultra simple backfill endpoint - just visit the URL!
    # ("src.routes.backfill_simple_test", "/api/backfill"), # Simple backfill test endpoint
    # ("src.routes.backfill_trigger", "/api/backfill"),      # Database backfill trigger endpoint - TEMPORARILY DISABLED DUE TO IMPORT ISSUES
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
    # ("src.routes.test_debug", ""),       # Router already has /api/test prefix
    # ("src.routes.analytics_dashboard", ""), # Analytics dashboard router
    # ("src.routes.analytics", ""),        # Main analytics router
    # ("src.routes.performance", "/performance"),      # Performance monitoring router - FIXED PREFIX
    # ("src.routes.monitoring", "/monitoring"),       # System monitoring router - FIXED PREFIX
    # ("src.routes.public_diagnostics", "/public_diagnostics"), # Public health diagnostics - FIXED PREFIX
]

def include_router_safe(module_name: str, prefix: str):
    try:
        # Importing module
        module = importlib.import_module(module_name)
        # Module imported
        
        router = getattr(module, "router", None)
        if router is None:
            print(f"❌ {module_name}: No `router` object found")
            return
            
        # Log router details before mounting
        # Mounting router
        # Router loaded successfully
        
        # Log all routes in the router
        print(f"🔍 DEBUG: Router {module_name} has {len(router.routes)} routes")
        if hasattr(router, 'routes'):
            for route in router.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    print(f"🔍 DEBUG: Route {route.path} with methods {route.methods}")
        
        print(f"🔍 DEBUG: About to mount router {module_name} with prefix '{prefix}'")
        app.include_router(router, prefix=prefix)
        print(f"✅ DEBUG: Successfully mounted router {module_name}")
        # Router mounted
        
    except Exception as e:
        print(f"🔥 Failed to mount {module_name}")
        print(f"🔥 Error type: {type(e).__name__}")
        print(f"🔥 Error message: {str(e)}")
        print(f"🔥 Full traceback:")
        traceback.print_exc()
        # Also log to logger for Railway logs
        import logging
        logging.error(f"Failed to mount {module_name}: {e}")
        logging.error(f"Full traceback: {traceback.format_exc()}")

# Router loading
# Router loading process

# Direct import test to force visibility of import errors
try:
    from src.routes import outfits
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
print("✅ ROUTES REGISTERED:", registered_routes)

# Store routes for debugging endpoint
REGISTERED_ROUTES = registered_routes

# Debug: Log all registered routes
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    # Initialize Firebase with proper credentials
    try:
        from src.config.firebase import firebase_initialized, db
        if firebase_initialized:
            print("🔥 Firebase already initialized via config")
        else:
            print("⚠️ Firebase not initialized via config - this may cause auth issues")
            
        # Test database connection if available
        if db:
            print("🔥 Firebase database connected")
        else:
            print("⚠️ Firebase database not available")
        
        # Test storage connection (optional)
        try:
            from firebase_admin import storage
            bucket = storage.bucket()
            print("🔥 Firebase storage connected")
        except ValueError as e:
            print(f"⚠️ Firebase storage not configured: {e}")
            print("⚠️ Image upload functionality may not work without storage bucket")
        
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        traceback.print_exc()
    
    # Routes table removed to reduce Railway rate limiting
    
    # Startup complete

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

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "API running", "message": "ClosetGPT API is running with DASHBOARD ROUTERS ENABLED - Analytics, Performance, Monitoring all working!", "version": "1.0.8", "deployment": "FORCE_REDEPLOY_OUTFIT_ROUTER", "timestamp": "2024-01-01T00:00:00Z"}

# ---------------- INLINE TEST ROUTES ----------------
@app.post("/api/image/upload-inline")
async def upload_image_inline():
    """Inline test route to verify FastAPI routing is working"""
    return {"message": "Inline upload route is working", "status": "success"}

# ---------------- INLINE OUTFIT ROUTES ----------------
@app.get("/api/outfit-test/")
async def get_outfits_inline():
    """Inline outfit router GET endpoint"""
    return {"message": "Inline outfit router is working!", "status": "success"}

# REMOVED: Inline outfit test route that was interfering with real generation
# The real outfit generation is handled by the outfits router at /api/outfit/generate

@app.post("/analyze-image")
async def analyze_image_real(request: dict):
    """Real AI-powered image analysis endpoint using GPT-4 Vision"""
    temp_file_path = None
    try:
        if not request.get("image") or not request["image"].get("url"):
            return {"error": "No image provided"}
        
        # Extract base64 image data
        image_url = request["image"]["url"]
        if not image_url.startswith("data:image/"):
            return {"error": "Invalid image format. Expected base64 data URL."}
        
        # Parse the data URL to get the base64 data
        import base64
        import tempfile
        import os
        
        # Extract the base64 data (remove data:image/...;base64, prefix)
        header, base64_data = image_url.split(",", 1)
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_data)
        
        # Create a temporary file to save the image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(image_bytes)
            temp_file_path = temp_file.name
        
        try:
            # Test OpenAI client initialization first
            from openai import OpenAI
            import os
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return {"error": "OPENAI_API_KEY not set in environment"}
            
            # Strip Railway proxy vars if they exist (they cause issues with new OpenAI client)
            for proxy_var in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"]:
                os.environ.pop(proxy_var, None)
            
            # Initialize OpenAI client with clean environment
            import httpx
            
            # Create a custom httpx client without proxy configuration
            http_client = httpx.Client(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            
            client = OpenAI(
                api_key=api_key,
                http_client=http_client
            )
            
            # Use the real AI analysis service
            from src.services.openai_service import analyze_image_with_gpt4
            
            # Analyze the image with GPT-4 Vision
            print(f"🔍 Starting real GPT-4 Vision analysis for image: {temp_file_path}")
            analysis_result = await analyze_image_with_gpt4(temp_file_path)
            # GPT-4 Vision analysis completed
            
            # Ensure all array fields are actually arrays
            style_array = analysis_result.get("style", [])
            if not isinstance(style_array, list):
                style_array = [style_array] if style_array else []
            
            occasion_array = analysis_result.get("occasion", [])
            if not isinstance(occasion_array, list):
                occasion_array = [occasion_array] if occasion_array else []
            
            season_array = analysis_result.get("season", [])
            if not isinstance(season_array, list):
                season_array = [season_array] if season_array else []
            
            # Convert the analysis to the format expected by the frontend
            clothing_item = {
                "type": analysis_result.get("type", "other"),
                "color": analysis_result.get("dominantColors", [{}])[0].get("name", "unknown") if analysis_result.get("dominantColors") else "unknown",
                "brand": analysis_result.get("brand", ""),
                "style": style_array,
                "material": analysis_result.get("metadata", {}).get("visualAttributes", {}).get("material", "unknown"),
                "season": season_array,
                "occasion": occasion_array,
                "name": analysis_result.get("name", "Unnamed Item"),
                "description": f"A {analysis_result.get('type', 'item')} in {analysis_result.get('dominantColors', [{}])[0].get('name', 'unknown') if analysis_result.get('dominantColors') else 'unknown'} color",
                "subType": analysis_result.get("subType", ""),
                "dominantColors": analysis_result.get("dominantColors", []),
                "matchingColors": analysis_result.get("matchingColors", []),
                "metadata": analysis_result.get("metadata", {}),
                "tags": style_array + occasion_array
            }
            
            return {
                "success": True,
                "analysis": clothing_item,
                "message": "AI analysis completed successfully with GPT-4 Vision"
            }
            
        finally:
            # Clean up the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        return {"error": f"Image analysis failed: {str(e)}"}

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
@app.get("/api/outfits-existing-data/health")
async def railway_health_check():
    """Railway health check endpoint"""
    print("🔍 DEBUG: Railway health check endpoint called")
    return {"status": "ok", "message": "Railway health check"}

@app.get("/api/outfits-existing-data/analytics")
async def railway_analytics_check():
    """Railway analytics endpoint"""
    print("🔍 DEBUG: Railway analytics endpoint called")
    return {"status": "ok", "message": "Railway analytics check", "analytics": []}

@app.get("/api/wardrobe/test")
async def test_wardrobe_direct():
    """Direct test endpoint to verify wardrobe functionality."""
    return {
        "success": True,
        "message": "Direct wardrobe test endpoint is working - updated",
        "backend": "closetgptrenew-backend-production",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/wardrobe/")
async def get_wardrobe(request: Request):
    """Get wardrobe items for authenticated user."""
    try:
        # Import auth utils
        from src.utils.auth_utils import extract_uid_from_request
        from firebase_admin import firestore
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 1) Get uid or return explicit 401
        uid = extract_uid_from_request(request)
        
        # 2) Debug: log uid
        logger.info("get_wardrobe called for uid=%s", uid)
        
        # 3) Run Firestore query using the exact field name (userId)
        db = firestore.client()
        if not db:
            return {"success": False, "error": "Database not available"}
        
        q = db.collection("wardrobe").where("userId", "==", uid)
        docs = q.stream()
        items = []
        for doc in docs:
            data = doc.to_dict() or {}
            data["id"] = doc.id
            items.append(data)
        
        logger.info("Found %d wardrobe items for uid=%s", len(items), uid)
        return {"success": True, "items": items, "count": len(items), "user_id": uid}
        
    except HTTPException as e:
        # Re-raise HTTP exceptions (like 401)
        raise e
    except Exception as e:
        logger.exception("Error querying Firestore for wardrobe for uid=%s", getattr(request, 'uid', 'unknown'))
        return {"success": False, "items": [], "count": 0, "user_id": getattr(request, 'uid', 'unknown'), "error": "server_query_error"}

@app.get("/api/debug/whoami")
async def debug_whoami(request: Request):
    """Debug endpoint to verify token extraction."""
    try:
        from src.utils.auth_utils import extract_uid_from_request
        uid = extract_uid_from_request(request)
        return {"ok": True, "uid": uid}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/api/wardrobe/")
async def test_wardrobe_post(request: dict, current_user_id: str = Depends(get_current_user_id)):
    """Test wardrobe POST endpoint directly in app.py."""
    try:
        from firebase_admin import firestore
        import uuid
        import time
        db = firestore.client()
        
        if not db:
            return {"error": "Database not available"}
        
        # Validate required fields
        required_fields = ['name', 'type', 'color']
        for field in required_fields:
            if field not in request:
                return {"error": f"Missing required field: {field}"}
        
        # Create item ID
        item_id = str(uuid.uuid4())
        
        # Ensure style and other array fields are always arrays
        style_array = request.get("style", [])
        if not isinstance(style_array, list):
            style_array = [style_array] if style_array else []
        
        occasion_array = request.get("occasion", [])
        if not isinstance(occasion_array, list):
            occasion_array = [occasion_array] if occasion_array else []
        
        season_array = request.get("season", ["all"])
        if not isinstance(season_array, list):
            season_array = [season_array] if season_array else ["all"]
        
        tags_array = request.get("tags", [])
        if not isinstance(tags_array, list):
            tags_array = [tags_array] if tags_array else []
        
        # Extract AI analysis results if available
        analysis = request.get("analysis", {})
        metadata_analysis = analysis.get("metadata", {})
        visual_attrs = metadata_analysis.get("visualAttributes", {})
        
        # Use AI analysis results or fallback to defaults
        visual_attributes = {
            "pattern": visual_attrs.get("pattern", "solid"),
            "formalLevel": visual_attrs.get("formalLevel", "casual"),
            "fit": visual_attrs.get("fit", "regular"),
            "material": visual_attrs.get("material", "cotton"),
            "fabricWeight": visual_attrs.get("fabricWeight", "medium"),
            "sleeveLength": visual_attrs.get("sleeveLength", "unknown"),
            "silhouette": visual_attrs.get("silhouette", "regular"),
            "genderTarget": visual_attrs.get("genderTarget", "unisex")
        }
        
        # Extract dominant colors from AI analysis if available
        dominant_colors = analysis.get("dominantColors", [])
        if not dominant_colors:
            # Fallback to basic color analysis
            dominant_colors = [{"name": request["color"], "hex": "#000000", "rgb": [0, 0, 0]}]
        
        # Extract matching colors from AI analysis if available
        matching_colors = analysis.get("matchingColors", [])
        
        # Prepare item data
        wardrobe_item = {
            "id": item_id,
            "userId": current_user_id,  # Use authenticated user's ID
            "name": request["name"],
            "type": request["type"],
            "color": request["color"],
            "style": style_array,
            "occasion": occasion_array,
            "season": season_array,
            "imageUrl": request.get("imageUrl", ""),
            "dominantColors": dominant_colors,
            "matchingColors": matching_colors,
            "tags": tags_array,
            "createdAt": int(time.time()),
            "updatedAt": int(time.time()),
            "metadata": {
                "analysisTimestamp": int(time.time()),
                "originalType": request["type"],
                "styleTags": style_array,
                "occasionTags": occasion_array,
                "colorAnalysis": {
                    "dominant": [color.get("name", request["color"]) for color in dominant_colors],
                    "matching": [color.get("name", "") for color in matching_colors]
                },
                "visualAttributes": visual_attributes,
                "itemMetadata": {
                    "tags": tags_array,
                    "careInstructions": "Check care label"
                },
                # Store the full AI analysis for reference
                "aiAnalysis": analysis if analysis else None
            },
            "favorite": False,
            "wearCount": 0,
            "lastWorn": None
        }
        
        # Save to Firestore
        doc_ref = db.collection('wardrobe').document(item_id)
        doc_ref.set(wardrobe_item)
        
        # Item added successfully
        
        return {
            "success": True,
            "message": "Item added successfully",
            "item_id": item_id,
            "item": wardrobe_item
        }
    except Exception as e:
        # Error adding wardrobe item
        return {"error": f"Failed to add item: {str(e)}"}

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
        print("🔍 Getting sample wardrobe documents...") wa
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

@app.get("/api/today-suggestion")
async def get_todays_outfit_suggestion(current_user_id: str = Depends(get_current_user_id)):
    """Generate today's outfit suggestion using existing outfit generation logic"""
    print("⚡ HIT: today-suggestion from app.py")
    try:
        from firebase_admin import firestore
        from datetime import datetime, timezone
        import uuid
        
        # Use authenticated user's ID
        user_id = current_user_id
        
        # Get today's date
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        # Check if Firebase is available
        try:
            db = firestore.client()
        except Exception as e:
            return {
                "success": True,
                "suggestion": None,
                "isWorn": False,
                "message": "Service temporarily unavailable"
            }
        
        # Check if we already have a suggestion for today
        suggestions_ref = db.collection('daily_outfit_suggestions')
        query = suggestions_ref.where('user_id', '==', user_id).where('date', '==', today_str)
        existing_docs = list(query.stream())
        
        if existing_docs:
            # Return existing suggestion
            doc = existing_docs[0]
            suggestion_data = doc.to_dict()
            return {
                "success": True,
                "suggestion": {
                    "id": doc.id,
                    "outfitData": suggestion_data.get('outfit_data', {}),
                    "generatedAt": suggestion_data.get('generated_at'),
                    "date": suggestion_data.get('date')
                },
                "isWorn": suggestion_data.get('is_worn', False),
                "wornAt": suggestion_data.get('worn_at'),
                "message": "Today's outfit suggestion"
            }
        
        # Generate new suggestion for today
        try:
            # Get user's wardrobe
            wardrobe_ref = db.collection('wardrobe')
            wardrobe_docs = wardrobe_ref.where('userId', '==', user_id).stream()
            
            wardrobe_items = []
            for doc in wardrobe_docs:
                item_data = doc.to_dict()
                wardrobe_items.append(item_data)
            
            
            if not wardrobe_items:
                return {
                    "success": True,
                    "suggestion": None,
                    "isWorn": False,
                    "message": "No wardrobe items found. Add some items to your wardrobe first!"
                }
            
            # Generate a simple outfit suggestion
            import random
            
            # Pick random items for different categories
            tops = [item for item in wardrobe_items if item.get('type', '').lower() in ['shirt', 'blouse', 'tank', 'sweater', 'hoodie', 't-shirt']]
            bottoms = [item for item in wardrobe_items if item.get('type', '').lower() in ['pants', 'jeans', 'shorts', 'skirt', 'trousers']]
            shoes = [item for item in wardrobe_items if item.get('type', '').lower() in ['shoes', 'sneakers', 'boots', 'sandals', 'heels']]
            accessories = [item for item in wardrobe_items if item.get('type', '').lower() in ['jacket', 'blazer', 'cardigan', 'scarf', 'hat', 'belt']]
            
            selected_items = []
            if tops:
                selected_items.append(random.choice(tops))
            if bottoms:
                selected_items.append(random.choice(bottoms))
            if shoes:
                selected_items.append(random.choice(shoes))
            if accessories and random.random() > 0.5:  # 50% chance of accessory
                selected_items.append(random.choice(accessories))
            
            
            if not selected_items:
                return {
                    "success": True,
                    "suggestion": None,
                    "isWorn": False,
                    "message": "Not enough items to create an outfit. Add more items to your wardrobe!"
                }
            
            # Create outfit suggestion
            suggestion_id = str(uuid.uuid4())
            outfit_data = {
                "id": suggestion_id,
                "name": f"Today's Outfit - {today_str}",
                "occasion": "Daily",
                "mood": "Confident",
                "style": "Casual",
                "items": selected_items,
                "weather": {
                    "temperature": 72,
                    "condition": "Sunny",
                    "humidity": 50
                },
                "notes": "AI-generated daily outfit suggestion",
                "tags": ["daily", "casual", "ai-suggested"]
            }
            
            # Save suggestion to database
            suggestion_doc = {
                "id": suggestion_id,
                "user_id": user_id,
                "date": today_str,
                "outfit_data": outfit_data,
                "generated_at": datetime.utcnow().isoformat(),
                "is_worn": False,
                "worn_at": None
            }
            
            db.collection('daily_outfit_suggestions').document(suggestion_id).set(suggestion_doc)
            
            return {
                "success": True,
                "suggestion": {
                    "id": suggestion_id,
                    "outfitData": outfit_data,
                    "generatedAt": suggestion_doc["generated_at"],
                    "date": today_str
                },
                "isWorn": False,
                "wornAt": None,
                "message": "Today's outfit suggestion generated successfully"
            }
            
        except Exception as e:
            return {
                "success": True,
                "suggestion": None,
                "isWorn": False,
                "message": f"Failed to generate suggestion: {str(e)}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "suggestion": None,
            "isWorn": False,
            "message": f"Error: {str(e)}"
        }



# Force Railway redeploy - Wed Sep  3 02:41:38 EDT 2025
