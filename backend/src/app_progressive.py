from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="ClosetGPT API",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0"
)

# Configure CORS
allowed_origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "https://closetgpt-frontend.vercel.app",
    "https://closetgpt-clean.vercel.app",
    "https://closetgpt-clean-git-main-jrfdy6.vercel.app",
    "https://closetgpt-clean-jrfdy6.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0",
            "message": "Progressive app is working"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/")
async def root():
    return {"message": "Progressive app API working"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "working"}

# Step 1: Basic image analysis (working)
@app.post("/api/analyze-image")
async def analyze_image(image: dict):
    """Image analysis endpoint"""
    try:
        image_url = image.get("image")
        if not image_url:
            return {"error": "No image provided"}
        
        # For now, return a simple response
        # TODO: Add real GPT-4 analysis
        return {
            "analysis": {
                "type": "clothing",
                "dominantColors": ["blue", "white"],
                "style": ["casual", "minimalist"],
                "occasion": ["everyday", "casual"],
                "season": ["spring", "summer"]
            },
            "message": "Analysis completed (progressive version)"
        }
    except Exception as e:
        return {"error": f"Failed to analyze image: {str(e)}"}

# Step 2: Add basic wardrobe endpoints
@app.get("/api/wardrobe")
async def get_wardrobe():
    """Get wardrobe items"""
    return {"items": [], "message": "Wardrobe endpoint (progressive)"}

@app.post("/api/wardrobe")
async def add_wardrobe_item(item: dict):
    """Add wardrobe item"""
    return {"message": "Item added (progressive)", "item": item}

# Step 3: Add basic outfits endpoints
@app.get("/api/outfits")
async def get_outfits():
    """Get outfits"""
    return {"outfits": [], "message": "Outfits endpoint (progressive)"}

@app.post("/api/outfits")
async def create_outfit(outfit: dict):
    """Create outfit"""
    return {"message": "Outfit created (progressive)", "outfit": outfit}

# Step 4: Add weather endpoint
@app.get("/api/weather")
async def get_weather():
    """Get weather data"""
    return {"weather": "sunny", "temperature": 72, "message": "Weather endpoint (progressive)"}

# Step 5: Add analytics endpoint
@app.get("/api/analytics")
async def get_analytics():
    """Get analytics data"""
    return {"analytics": {}, "message": "Analytics endpoint (progressive)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 