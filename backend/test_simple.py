#!/usr/bin/env python3
print("=== test_simple.py is being executed ===")
print("Hello from Railway!")
print("Python is working!")

import os
print(f"PORT: {os.getenv('PORT', 'Not set')}")
print(f"Current directory: {os.getcwd()}")

try:
    from fastapi import FastAPI
    import uvicorn
    print("✅ FastAPI and uvicorn imported successfully!")
    
    app = FastAPI()
    
    @app.get("/health")
    async def health():
        return {"status": "ok", "message": "test_simple working"}
    
    if __name__ == "__main__":
        port = int(os.getenv("PORT", 8000))
        print(f"Starting test_simple on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("=== test_simple.py completed ===") 