from fastapi import FastAPI
import os
from datetime import datetime

app = FastAPI(
    title="ClosetGPT API - Ultra Minimal",
    description="Ultra minimal version for Railway deployment",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Log startup event"""
    print(f"🚀 ClosetGPT API starting on port {os.getenv('PORT', '8000')}")
    print("✅ Health check endpoints available at /health and /health/simple")

@app.get("/health/simple")
async def simple_health_check():
    """Simple health check endpoint that responds immediately"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "Health check successful"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/")
async def root():
    return {"message": "ClosetGPT API is running", "status": "healthy"}

@app.get("/api/test")
async def test_endpoint():
    return {"message": "API is working", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 