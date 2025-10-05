import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

# Load environment variables
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Debug: Print the API key (first few characters)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("⚠️  WARNING: No OpenAI API key found in environment variables")
    print("   This may cause issues with AI-powered features")
else:
    print(f"✅ API Key loaded (first 10 chars): {api_key[:10]}...")

# Now we can import the app
from app import app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Railway sets this)
    port_str = os.getenv("PORT")
    if port_str:
        try:
            port = int(port_str)
            print(f"✅ Using Railway PORT: {port}")
        except ValueError:
            print(f"⚠️  Invalid PORT value: {port_str}, using 8080")
            port = 8080
    else:
        port = 8080
        print(f"⚠️  No PORT environment variable, using default: {port}")
    
    print(f"🚀 Starting server on host=0.0.0.0, port={port}")
    print(f"🔍 Environment PORT: {os.getenv('PORT')}")
    print(f"🔍 All environment variables: {sorted(os.environ.keys())}")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print(f"   Port: {port}")
        print(f"   Host: 0.0.0.0")
        raise 