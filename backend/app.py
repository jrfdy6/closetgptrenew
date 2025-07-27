from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "App.py is working"
    }

@app.get("/")
async def root():
    return {"message": "App.py API working"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    print(f"Starting app.py on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 