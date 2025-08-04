#!/usr/bin/env python3
print("=== app.py is being executed ===")

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the app from app_full.py
    from app_full import app
    
    print("Successfully imported app from app_full.py")
    
    if __name__ == "__main__":
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        print(f"Starting app on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
        
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 