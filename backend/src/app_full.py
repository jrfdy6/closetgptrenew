print("=== app_full.py is being executed ===")
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
import uuid
import json

# Global variables for Firebase
db = None
bucket = None
firebase_configured = False

# Initialize Firebase if credentials are available
def initialize_firebase():
    global db, bucket, firebase_configured
    try:
        print("DEBUG: Attempting to initialize Firebase...")
        
        import firebase_admin
        from firebase_admin import firestore, storage
        
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            print("DEBUG: Firebase already initialized")
            db = firestore.client()
            bucket = storage.bucket()
            firebase_configured = True
            return
        
        # Get environment variables
        project_id = os.environ.get("FIREBASE_PROJECT_ID")
        private_key = os.environ.get("FIREBASE_PRIVATE_KEY")
        client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
        
        print(f"DEBUG: Project ID: {project_id}")
        print(f"DEBUG: Client Email: {client_email}")
        print(f"DEBUG: Private Key exists: {bool(private_key)}")
        
        if not project_id or not private_key or not client_email:
            print("DEBUG: Missing required Firebase credentials")
            firebase_configured = False
            return
        
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
        
        db = firestore.client()
        bucket = storage.bucket()
        firebase_configured = True
        print("DEBUG: Firebase initialized successfully")
        
    except Exception as e:
        print(f"DEBUG: Firebase initialization failed: {e}")
        firebase_configured = False
        db = None
        bucket = None

app = FastAPI(
    title="ClosetGPT API - Full",
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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
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
        
        # Initialize Firebase if not already done
        if not firebase_configured:
            initialize_firebase()
        
        if not firebase_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase not configured"
            )
        
        # Verify Firebase token
        from firebase_admin import auth as firebase_auth
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token["uid"]
        
    except Exception as e:
        print(f"DEBUG: Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

# Pydantic models
class WardrobeItem(BaseModel):
    name: str
    category: str
    color: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[List[str]] = None
    material: Optional[str] = None

class OutfitRequest(BaseModel):
    occasion: str
    weather: Optional[str] = None
    style_preference: Optional[str] = None
    season: Optional[str] = None
    include_accessories: Optional[bool] = True

class OutfitResponse(BaseModel):
    outfit_id: str
    items: List[dict]
    occasion: str
    weather: Optional[str]
    style_preference: Optional[str]
    generated_at: str
    confidence_score: float

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        # Try to initialize Firebase if not already done
        if not firebase_configured:
            initialize_firebase()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0",
            "firebase_configured": firebase_configured,
            "storage_configured": bucket is not None,
            "features": ["authentication", "wardrobe", "outfits", "image_processing"],
            "debug_info": {
                "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
                "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
                "private_key_exists": bool(os.environ.get("FIREBASE_PRIVATE_KEY"))
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
        "version": "1.0.0",
        "features": ["authentication", "wardrobe", "outfits", "image_processing", "analytics"]
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

# Image processing endpoints
@app.post("/api/image/upload")
async def upload_image(
    file: UploadFile = File(...),
    category: str = Form(...),
    name: str = Form(...),
    current_user_id: str = Depends(get_current_user_id)
):
    """Upload and process clothing image"""
    if not bucket:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage not available"
        )
    
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        filename = f"wardrobe/{current_user_id}/{uuid.uuid4()}.{file_extension}"
        
        # Upload to Firebase Storage
        blob = bucket.blob(filename)
        blob.upload_from_string(
            await file.read(),
            content_type=file.content_type
        )
        
        # Make the blob publicly readable
        blob.make_public()
        
        # Create wardrobe item
        item_data = {
            "name": name,
            "category": category,
            "image_url": blob.public_url,
            "uploaded_at": datetime.now().isoformat(),
            "file_size": blob.size,
            "content_type": file.content_type
        }
        
        # Save to Firestore
        wardrobe_ref = db.collection('users').document(current_user_id).collection('wardrobe')
        doc_ref = wardrobe_ref.add(item_data)
        
        return {
            "message": "Image uploaded successfully",
            "item_id": doc_ref[0].id,
            "image_url": blob.public_url,
            "item": item_data
        }
    except Exception as e:
        print(f"DEBUG: Error uploading image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )

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
        print(f"DEBUG: Getting wardrobe for user: {current_user_id}")
        
        # Get wardrobe items from Firestore using flat collection structure
        wardrobe_ref = db.collection('wardrobe')
        docs = wardrobe_ref.where('userId', '==', current_user_id).stream()
        
        items = []
        errors = []
        
        for doc in docs:
            try:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                
                # Ensure required fields exist
                if 'name' not in item_data:
                    item_data['name'] = 'Unknown Item'
                if 'type' not in item_data:
                    item_data['type'] = 'unknown'
                if 'color' not in item_data:
                    item_data['color'] = 'unknown'
                if 'style' not in item_data:
                    item_data['style'] = []
                if 'occasion' not in item_data:
                    item_data['occasion'] = []
                if 'season' not in item_data:
                    item_data['season'] = ['all']
                if 'tags' not in item_data:
                    item_data['tags'] = []
                if 'dominantColors' not in item_data:
                    item_data['dominantColors'] = []
                if 'matchingColors' not in item_data:
                    item_data['matchingColors'] = []
                if 'imageUrl' not in item_data:
                    item_data['imageUrl'] = ''
                if 'metadata' not in item_data:
                    item_data['metadata'] = {}
                if 'favorite' not in item_data:
                    item_data['favorite'] = False
                if 'wearCount' not in item_data:
                    item_data['wearCount'] = 0
                if 'lastWorn' not in item_data:
                    item_data['lastWorn'] = None
                
                # Handle timestamp conversion
                try:
                    if 'createdAt' in item_data:
                        if isinstance(item_data['createdAt'], str):
                            item_data['createdAt'] = int(datetime.fromisoformat(item_data['createdAt'].replace('Z', '+00:00')).timestamp())
                        elif hasattr(item_data['createdAt'], 'timestamp'):
                            item_data['createdAt'] = int(item_data['createdAt'].timestamp())
                    else:
                        item_data['createdAt'] = int(datetime.now().timestamp())
                except Exception as e:
                    print(f"DEBUG: Error converting createdAt for item {doc.id}: {e}")
                    item_data['createdAt'] = int(datetime.now().timestamp())
                
                try:
                    if 'updatedAt' in item_data:
                        if isinstance(item_data['updatedAt'], str):
                            item_data['updatedAt'] = int(datetime.fromisoformat(item_data['updatedAt'].replace('Z', '+00:00')).timestamp())
                        elif hasattr(item_data['updatedAt'], 'timestamp'):
                            item_data['updatedAt'] = int(item_data['updatedAt'].timestamp())
                    else:
                        item_data['updatedAt'] = int(datetime.now().timestamp())
                except Exception as e:
                    print(f"DEBUG: Error converting updatedAt for item {doc.id}: {e}")
                    item_data['updatedAt'] = int(datetime.now().timestamp())
                
                items.append(item_data)
                print(f"DEBUG: Successfully processed item {doc.id}")
                
            except Exception as e:
                print(f"DEBUG: Error processing wardrobe item {doc.id}: {e}")
                errors.append(f"Failed to process item {doc.id}: {str(e)}")
        
        # Sort items by creation date (newest first)
        items.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        print(f"DEBUG: Retrieved {len(items)} wardrobe items for user {current_user_id}")
        if errors:
            print(f"DEBUG: Encountered {len(errors)} errors while processing items")
        
        return {
            "success": True,
            "items": items,
            "count": len(items),
            "errors": errors if errors else None
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
        print(f"DEBUG: Adding wardrobe item for user: {current_user_id}")
        
        # Convert to the expected structure
        item_data = {
            "userId": current_user_id,
            "name": item.name,
            "type": item.category,
            "color": item.color or "unknown",
            "style": [],
            "occasion": item.occasion or [],
            "season": ["all"],
            "tags": [],
            "imageUrl": item.image_url or "",
            "dominantColors": [],
            "matchingColors": [],
            "createdAt": int(datetime.now().timestamp()),
            "updatedAt": int(datetime.now().timestamp()),
            "metadata": {
                "brand": item.brand,
                "material": item.material,
                "description": item.description
            },
            "favorite": False,
            "wearCount": 0,
            "lastWorn": None
        }
        
        # Add item to Firestore using flat collection structure
        wardrobe_ref = db.collection('wardrobe')
        doc_ref = wardrobe_ref.add(item_data)
        
        print(f"DEBUG: Successfully added item with ID: {doc_ref[0].id}")
        
        return {
            "success": True,
            "message": "Item added successfully",
            "item_id": doc_ref[0].id,
            "item": item_data
        }
    except Exception as e:
        print(f"DEBUG: Error adding wardrobe item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item"
        )

@app.delete("/api/wardrobe/{item_id}")
async def delete_wardrobe_item(
    item_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete item from wardrobe"""
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        print(f"DEBUG: Deleting wardrobe item {item_id} for user: {current_user_id}")
        
        # Delete from Firestore using flat collection structure
        wardrobe_ref = db.collection('wardrobe')
        doc_ref = wardrobe_ref.document(item_id)
        
        # Check if item exists and belongs to user
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        item_data = doc.to_dict()
        if item_data.get('userId') != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this item"
            )
        
        # Delete the document
        doc_ref.delete()
        
        print(f"DEBUG: Successfully deleted item {item_id}")
        
        return {
            "success": True,
            "message": "Item deleted successfully",
            "item_id": item_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Error deleting wardrobe item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item"
        )

# Enhanced outfit generation
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
        
        # Enhanced outfit generation logic
        outfit_items = []
        confidence_score = 0.8
        
        # Define outfit structure based on occasion
        outfit_structure = {
            "casual": ["top", "bottom"],
            "business": ["top", "bottom"],
            "formal": ["top", "bottom", "outerwear"],
            "party": ["top", "bottom", "accessories"],
            "sport": ["top", "bottom"]
        }
        
        categories_needed = outfit_structure.get(request.occasion.lower(), ["top", "bottom"])
        
        # Filter items by season if specified
        if request.season:
            items = [item for item in items if not item.get('season') or item.get('season') == request.season]
        
        # Select items for each category
        for category in categories_needed:
            category_items = [item for item in items if item.get('category', '').lower() == category]
            
            if category_items:
                # Simple selection logic (could be enhanced with AI)
                selected_item = category_items[0]
                outfit_items.append(selected_item)
            else:
                confidence_score -= 0.2  # Reduce confidence if category missing
        
        # Generate outfit ID
        outfit_id = str(uuid.uuid4())
        
        return OutfitResponse(
            outfit_id=outfit_id,
            items=outfit_items,
            occasion=request.occasion,
            weather=request.weather,
            style_preference=request.style_preference,
            generated_at=datetime.now().isoformat(),
            confidence_score=max(0.1, confidence_score)
        )
    except Exception as e:
        print(f"DEBUG: Error generating outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate outfit"
        )

# Analytics endpoints
@app.post("/api/analytics/outfit-feedback")
async def log_outfit_feedback(
    outfit_id: str,
    rating: int,
    feedback: Optional[str] = None,
    current_user_id: str = Depends(get_current_user_id)
):
    """Log user feedback for generated outfits"""
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        feedback_data = {
            "outfit_id": outfit_id,
            "user_id": current_user_id,
            "rating": rating,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save feedback to Firestore
        analytics_ref = db.collection('analytics').document('outfit_feedback')
        feedback_collection = analytics_ref.collection('feedback')
        feedback_collection.add(feedback_data)
        
        return {
            "message": "Feedback logged successfully",
            "outfit_id": outfit_id
        }
    except Exception as e:
        print(f"DEBUG: Error logging feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log feedback"
        )

@app.get("/api/analytics/wardrobe-stats")
async def get_wardrobe_stats(current_user_id: str = Depends(get_current_user_id)):
    """Get wardrobe statistics"""
    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    
    try:
        # Get wardrobe items
        wardrobe_ref = db.collection('users').document(current_user_id).collection('wardrobe')
        docs = wardrobe_ref.stream()
        
        items = []
        for doc in docs:
            item_data = doc.to_dict()
            items.append(item_data)
        
        # Calculate statistics
        total_items = len(items)
        categories = {}
        colors = {}
        
        for item in items:
            category = item.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
            
            color = item.get('color', 'unknown')
            colors[color] = colors.get(color, 0) + 1
        
        return {
            "total_items": total_items,
            "categories": categories,
            "colors": colors,
            "user_id": current_user_id
        }
    except Exception as e:
        print(f"DEBUG: Error getting wardrobe stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get wardrobe statistics"
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

# Weather endpoint
class WeatherRequest(BaseModel):
    location: str

class WeatherData(BaseModel):
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    location: str
    precipitation: float = 0.0

@app.post("/api/weather")
async def get_weather(request: WeatherRequest):
    """
    Get current weather data for a location.
    Location can be a city name or coordinates (latitude,longitude).
    """
    try:
        # Get OpenWeather API key from environment
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            # Return fallback weather data if API key is not configured
            return WeatherData(
                temperature=72.0,
                condition="Clear",
                humidity=65,
                wind_speed=5.0,
                location=request.location,
                precipitation=0.0
            )

        # For now, return fallback data to avoid external API dependencies
        # In production, you would make a request to OpenWeather API here
        return WeatherData(
            temperature=72.0,
            condition="Clear",
            humidity=65,
            wind_speed=5.0,
            location=request.location,
            precipitation=0.0
        )

    except Exception as e:
        print(f"DEBUG: Error getting weather: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get weather data"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 