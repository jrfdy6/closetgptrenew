from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="ClosetGPT API - Minimal",
    description="Minimal API for testing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Minimal app is working"
    }

@app.get("/")
async def root():
    return {"message": "Minimal app API working"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "api": "working"}

# Basic image analysis endpoint
@app.post("/api/analyze-image")
async def analyze_image(image: dict):
    """Basic image analysis endpoint"""
    try:
        image_url = image.get("image")
        if not image_url:
            return {"error": "No image provided"}
        
        return {
            "analysis": {
                "type": "clothing",
                "dominantColors": ["blue", "white"],
                "style": ["casual", "minimalist"],
                "occasion": ["everyday", "casual"],
                "season": ["spring", "summer"]
            },
            "message": "Analysis completed (minimal version)"
        }
    except Exception as e:
        return {"error": f"Failed to analyze image: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 