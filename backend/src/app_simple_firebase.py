print("=== app_simple_firebase.py is being executed ===")
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="ClosetGPT API - Simple Firebase",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0"
)
print("DEBUG: FastAPI app created")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from Firebase ID token."""
    try:
        token = credentials.credentials
        
        # Handle development/test tokens
        if token == "test" or token.startswith("test_"):
            print("DEBUG: Using development test token")
            return "test_user_id"
        
        # Initialize Firebase only when needed
        try:
            import firebase_admin
            from firebase_admin import auth as firebase_auth
            
            if not firebase_admin._apps:
                # Get environment variables
                project_id = os.environ.get("FIREBASE_PROJECT_ID")
                private_key = os.environ.get("FIREBASE_PRIVATE_KEY")
                client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
                
                if not project_id or not private_key or not client_email:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Firebase credentials not configured"
                    )
                
                firebase_creds = {
                    "type": "service_account",
                    "project_id": project_id,
                    "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": private_key.replace("\\n", "\n"),
                    "client_email": client_email,
                    "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
                }
                
                from firebase_admin import credentials
                cred = credentials.Certificate(firebase_creds)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': f"{project_id}.appspot.com"
                })
                print("DEBUG: Firebase initialized successfully")
            
            # Verify Firebase token
            decoded_token = firebase_auth.verify_id_token(token)
            return decoded_token["uid"]
            
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase not available"
            )
        
    except Exception as e:
        print(f"DEBUG: Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        # Check if Firebase credentials are available
        project_id = os.environ.get("FIREBASE_PROJECT_ID")
        private_key = os.environ.get("FIREBASE_PRIVATE_KEY")
        client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
        
        firebase_configured = bool(project_id and private_key and client_email)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0",
            "firebase_configured": firebase_configured,
            "features": ["authentication", "wardrobe", "outfits"],
            "debug_info": {
                "project_id": project_id,
                "client_email": client_email,
                "private_key_exists": bool(private_key)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health/simple")
async def simple_health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {
        "message": "ClosetGPT API is running",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/test")
async def test_endpoint():
    return {"message": "API is working", "timestamp": datetime.now().isoformat()}

@app.get("/api/test/auth")
async def test_auth(current_user_id: str = Depends(get_current_user_id)):
    return {
        "message": "Authentication working",
        "user_id": current_user_id,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 