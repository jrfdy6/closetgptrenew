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
    raise ValueError(f"No OpenAI API key found in environment variables. Please check {env_path}")
print(f"API Key loaded (first 10 chars): {api_key[:10]}...")

# Now we can import the app
from app import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))  # Use Railway's PORT or fallback to 8080 locally
    uvicorn.run(app, host="0.0.0.0", port=port) 