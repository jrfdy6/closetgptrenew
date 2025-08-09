print("=== app_enhanced.py is being executed ===")
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from datetime import datetime
import firebase_admin
from firebase_admin import auth as firebase_auth, firestore
from pydantic import BaseModel
from typing import Optional, List

# Initialize Firebase if credentials are available
try:
    if not firebase_admin._apps:
        firebase_creds = {
            "type": "service_account",
            "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
        }
        
        # Only initialize if we have the required credentials
        if firebase_creds["project_id"] and firebase_creds["private_key"]:
            from firebase_admin import credentials
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("DEBUG: Firebase initialized successfully")
        else:
            print("DEBUG: Firebase credentials not available, skipping initialization")
            db = None
    else:
        db = firestore.client()
        print("DEBUG: Firebase already initialized")
except Exception as e:
    print(f"DEBUG: Firebase initialization failed: {e}")
    db = None

app = FastAPI(
    title="ClosetGPT API - Enhanced",
    description="AI-powered wardrobe management and outfit generation API",
    version="1.0.0"
)
print("DEBUG: FastAPI app created")

# Configure CORS
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://localhost:3000,https://closetgpt-clean.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Add production URLs
allowed_origins.extend([
    "https://closetgpt-clean.vercel.app",
    "https://closetgpt-clean-git-main-jrfdy6.vercel.app",
    "https://closetgpt-clean-jrfdy6.vercel.app"
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
        
        if not db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase not configured"
            )
        
        # Verify Firebase token
        decoded_token = firebase_auth.verify_id_token(token)
        user_id: str = decoded_token.get("uid")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID found"
            )
        return user_id
    except Exception as e:
        print(f"DEBUG: Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Pydantic models
class WardrobeItem(BaseModel):
    name: str
    category: str
    color: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

class OutfitRequest(BaseModel):
    occasion: str
    weather: Optional[str] = None
    style_preference: Optional[str] = None

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0",
            "firebase_configured": db is not None
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
        "version": "1.0.0",
        "features": ["authentication", "wardrobe", "outfits"]
    }

# Authentication endpoints
@app.post("/auth/verify-token")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Firebase ID token"""
    try:
        user_id = get_current_user_id(credentials)
        return {
            "valid": True,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Wardrobe endpoints
@app.get("/api/wardrobe")
async def get_wardrobe(current_user_id: str = Depends(get_current_user_id)):
    """Get user's wardrobe items"""
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        # Get wardrobe items from Firestore
        wardrobe_ref = db.collection('users').document(current_user_id).collection('wardrobe')
        docs = wardrobe_ref.stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        return {
            "items": items,
            "count": len(items),
            "user_id": current_user_id
        }
    except Exception as e:
        print(f"DEBUG: Error getting wardrobe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get wardrobe"
        )

@app.post("/api/wardrobe")
async def add_wardrobe_item(
    item: WardrobeItem,
    current_user_id: str = Depends(get_current_user_id)
):
    """Add item to wardrobe"""
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        # Add item to Firestore
        wardrobe_ref = db.collection('users').document(current_user_id).collection('wardrobe')
        doc_ref = wardrobe_ref.add(item.dict())
        
        return {
            "message": "Item added successfully",
            "item_id": doc_ref[0].id,
            "item": item.dict()
        }
    except Exception as e:
        print(f"DEBUG: Error adding wardrobe item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item"
        )

# Outfit generation endpoints
@app.post("/api/outfits/generate")
async def generate_outfit(
    request: OutfitRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """Generate outfit based on occasion and preferences"""
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        # Get user's wardrobe
        wardrobe_ref = db.collection('users').document(current_user_id).collection('wardrobe')
        docs = wardrobe_ref.stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            item_data['id'] = doc.id
            items.append(item_data)
        
        # Simple outfit generation logic
        outfit_items = []
        categories_needed = ['top', 'bottom']
        
        for category in categories_needed:
            category_items = [item for item in items if item.get('category', '').lower() == category]
            if category_items:
                outfit_items.append(category_items[0])
        
        return {
            "outfit": {
                "items": outfit_items,
                "occasion": request.occasion,
                "weather": request.weather,
                "style_preference": request.style_preference
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"DEBUG: Error generating outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate outfit"
        )

# Test endpoints
@app.get("/api/test")
async def test_endpoint():
    return {"message": "API is working", "status": "success"}

@app.get("/api/test/auth")
async def test_auth(current_user_id: str = Depends(get_current_user_id)):
    return {
        "message": "Authentication working",
        "user_id": current_user_id,
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 