from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import weather, wardrobe, auth, analytics, monitoring, image_processing, image_analysis, outfits, outfit, style_analysis, wardrobe_analysis, security, performance, analytics_dashboard, feedback, public_diagnostics, validation_rules, item_analytics, outfit_history, forgotten_gems
from .core.logging import setup_logging
from .core.middleware import setup_middleware

# Import Firebase config to initialize it
try:
    from .config import firebase
    print("DEBUG: Firebase config imported successfully")
except Exception as e:
    print(f"DEBUG: Firebase config import failed: {e}")

# Initialize logging
try:
    setup_logging()
    print("DEBUG: Logging setup completed")
except Exception as e:
    print(f"DEBUG: Logging setup failed: {e}")

app = FastAPI(
    title="ClosetGPT API",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0"
)
print("DEBUG: FastAPI app created")

# Setup production middleware
print("DEBUG: About to call setup_middleware(app)")
setup_middleware(app)
print("DEBUG: setup_middleware(app) completed")

# Configure CORS
import os
from typing import List

# Get allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://localhost:3000,https://closetgpt-clean.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Add production URLs
allowed_origins.extend([
    "https://closetgpt-clean.vercel.app",
    "https://closetgpt-clean-git-main-jrfdy6.vercel.app",
    "https://closetgpt-clean-jrfdy6.vercel.app"
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - ORDER MATTERS! More specific routes must come before catch-all routes
app.include_router(outfit.router, prefix="/api/outfit", tags=["outfit"])
app.include_router(outfits.router, prefix="/api/outfits", tags=["outfits"])
app.include_router(image_processing.router, prefix="/api/image", tags=["images"])
app.include_router(image_analysis.router)
app.include_router(weather.router, prefix="/api", tags=["weather"])
app.include_router(style_analysis.router, prefix="/api", tags=["style-analysis"])
app.include_router(wardrobe_analysis.router)
app.include_router(forgotten_gems.router)  # Register forgotten gems BEFORE wardrobe to avoid route conflict
app.include_router(wardrobe.router)  # Register wardrobe CRUD endpoints AFTER forgotten gems
app.include_router(analytics.router, prefix="/api", tags=["analytics"])
app.include_router(analytics_dashboard.router, prefix="/api", tags=["analytics-dashboard"])
app.include_router(auth.router)
app.include_router(monitoring.router, prefix="/api", tags=["monitoring"])
app.include_router(security.router, prefix="/api/security", tags=["security"])
app.include_router(performance.router, prefix="/api/performance", tags=["performance"])
app.include_router(feedback.router)
app.include_router(public_diagnostics.router, prefix="/api/diagnostics", tags=["public-diagnostics"])
app.include_router(validation_rules.router, prefix="/api", tags=["validation-rules"])
app.include_router(item_analytics.router)
app.include_router(outfit_history.router, prefix="/api", tags=["outfit-history"])

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
    """Simple health check endpoint that responds immediately"""
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "ClosetGPT API is running", "status": "healthy"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "working"}