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
    ("src.routes.image_processing_minimal_test", "/api/image-test"),  # Minimal test router
    ("src.routes.wardrobe", "/api/wardrobe"),               # Main wardrobe router - mounted at /api/wardrobe
    ("src.routes.image_upload_minimal", "/api/image"),  # Minimal image upload router
    ("src.routes.image_analysis_minimal", ""),   # Minimal image analysis router (working)
    # ("src.routes.auth_working", "/api/auth"),    # Using working auth router that follows same pattern as outfits/wardrobe
    # ("src.routes.weather", ""),          # Router already has /api/weather prefix
    # ("src.routes.forgotten_gems", "/api/wardrobe"),  # Forgotten gems router - CONFLICTING with wardrobe_simple
    # ("src.routes.wardrobe_minimal", ""), # Router already has /api/wardrobe prefix - using simplified version
    # ("src.routes.wardrobe_analysis", ""), # Router already has /api/wardrobe prefix - TEMPORARILY DISABLED
    # ("src.routes.outfit", ""),           # Router already has /api/outfit prefix - TEMPORARILY DISABLED
    # ("src.routes.outfits", "/api/outfits"),          # Outfits router - mounted at /api/outfits for frontend compatibility
    # ("src.routes.outfit_history", "/api"),   # Full outfit history router with daily generation
    # ("src.routes.test_debug", ""),       # Router already has /api/test prefix
    # ("src.routes.analytics_dashboard", ""), # Analytics dashboard router
    # ("src.routes.analytics", ""),        # Main analytics router
    # ("src.routes.performance", "/performance"),      # Performance monitoring router - FIXED PREFIX
    # ("src.routes.monitoring", "/monitoring"),       # System monitoring router - FIXED PREFIX
    # ("src.routes.public_diagnostics", "/public_diagnostics"), # Public health diagnostics - FIXED PREFIX
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

# Image processing router is now working with optional imports

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

@app.post("/analyze-image")
async def analyze_image_real(request: dict):
    """Real AI-powered image analysis endpoint using GPT-4 Vision"""
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
            print(f"✅ GPT-4 Vision analysis completed: {analysis_result}")
            
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
            if os.path.exists(temp_file_path):
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
async def test_wardrobe_get():
    """Test wardrobe GET endpoint directly in app.py."""
    try:
        from firebase_admin import firestore
        db = firestore.client()
        
        if not db:
            return {"error": "Database not available"}
        
        # Get wardrobe items from Firestore
        wardrobe_ref = db.collection('wardrobe')
        docs = wardrobe_ref.where('userId', '==', 'dANqjiI0CKgaitxzYtw1bhtvQrG3').stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            items.append(item_data)
        
        return {
            "success": True,
            "items": items,
            "count": len(items),
            "user_id": "dANqjiI0CKgaitxzYtw1bhtvQrG3"
        }
    except Exception as e:
        return {"error": f"Failed to get wardrobe items: {str(e)}"}

@app.post("/api/wardrobe/")
async def test_wardrobe_post(request: dict):
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
            "userId": "dANqjiI0CKgaitxzYtw1bhtvQrG3",  # Use hardcoded user ID for now
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
        
        print(f"DEBUG: Successfully added item with ID: {item_id}")
        print(f"DEBUG: Item saved with userId: {wardrobe_item['userId']}")
        print(f"DEBUG: Item name: {wardrobe_item['name']}")
        print(f"DEBUG: Item type: {wardrobe_item['type']}")
        print(f"DEBUG: Item color: {wardrobe_item['color']}")
        
        return {
            "success": True,
            "message": "Item added successfully",
            "item_id": item_id,
            "item": wardrobe_item
        }
    except Exception as e:
        print(f"DEBUG: Error adding wardrobe item: {e}")
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

@app.post("/api/test-upload")
async def test_upload():
    """Test endpoint to verify routing is working"""
    return {"message": "Test upload endpoint is working", "status": "success"}



# Force Railway redeploy - Wed Sep  3 02:41:38 EDT 2025
