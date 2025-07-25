from fastapi import FastAPI
import os

app = FastAPI(
    title="ClosetGPT API - Minimal Test",
    description="Minimal test version for Railway deployment",
    version="1.0.0"
)

@app.get("/health/simple")
async def simple_health_check():
    """Simple health check endpoint that responds immediately"""
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {"message": "ClosetGPT API is running", "status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 