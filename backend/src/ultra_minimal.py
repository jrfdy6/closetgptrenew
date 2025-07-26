print("=== ultra_minimal.py is being executed ===")
from fastapi import FastAPI
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ClosetGPT API - Ultra Minimal",
    description="Ultra minimal version for Railway deployment",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Log startup event"""
    port = os.getenv("PORT", "8000")
    logger.warning("✅ FastAPI app has started.")
    logger.info(f"🚀 ClosetGPT API starting on port {port}")
    logger.info("✅ Health check endpoint available at /health")
    logger.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info("🔧 Railway health check path: /health")
    logger.info(f"🔧 Railway expects port: {port}")

@app.get("/health/simple")
async def simple_health_check():
    """Simple health check endpoint that responds immediately"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "Health check successful"
    }

@app.get("/healthcheck")
async def healthcheck():
    """Alternative health check endpoint"""
    return {"status": "ok"}

@app.get("/health")
async def health():
    """Health check endpoint for Railway deployment"""
    logger.info("Healthcheck hit!")
    return {"status": "ok"}

@app.get("/")
async def root():
    return {
        "message": "ClosetGPT API is running", 
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "health_endpoints": ["/health", "/health/simple"]
    }

@app.get("/api/test")
async def test_endpoint():
    return {"message": "API is working", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    logger.warning("🚀 Starting FastAPI server directly...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 