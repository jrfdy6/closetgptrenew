#!/usr/bin/env python3
print("=== main.py is being executed ===")

from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Main app working"
    }

@app.get("/")
async def root():
    return {"message": "Main API working"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting main app on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 