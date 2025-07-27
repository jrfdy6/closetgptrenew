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
            "message": "App.py is working"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/")
async def root():
    return {"message": "App.py API working"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "working"}

# Image analysis endpoint
@app.post("/api/analyze-image")
async def analyze_image(image: dict):
    """Simple image analysis endpoint"""
    try:
        image_url = image.get("image")
        if not image_url:
            return {"error": "No image provided"}
        
        # For now, return a simple response
        # In production, this would call the actual analysis service
        return {
            "analysis": {
                "type": "clothing",
                "dominantColors": ["blue", "white"],
                "style": ["casual", "minimalist"],
                "occasion": ["everyday", "casual"],
                "season": ["spring", "summer"]
            },
            "message": "Analysis completed (simplified version)"
        }
    except Exception as e:
        return {"error": f"Failed to analyze image: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 