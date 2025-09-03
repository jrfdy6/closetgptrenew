from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="ClosetGPT Backend", version="1.0.5")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "ClosetGPT Backend is running!", "version": "1.0.5"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "version": "1.0.5",
        "port": os.getenv("PORT", "8080"),
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/api/wardrobe/")
async def get_wardrobe_items():
    """Get all wardrobe items for the current user."""
    try:
        # Try to import Firebase modules
        try:
            from src.config.firebase import firebase_initialized, db
        except ImportError as e:
            return {"error": f"Firebase import failed: {str(e)}"}
        
        if not firebase_initialized or db is None:
            return {"error": "Firebase not initialized"}
        
        # Get current user (simplified for now)
        current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Your user ID
        
        # Get all documents and filter by user ID
        all_docs = db.collection('wardrobe').stream()
        
        items = []
        for doc in all_docs:
            data = doc.to_dict()
            data['id'] = doc.id
            
            # Check all possible user ID field names
            user_id = (data.get('userId') or 
                      data.get('uid') or 
                      data.get('ownerId') or 
                      data.get('user_id'))
            
            # If this item belongs to the current user, include it
            if user_id == current_user_id:
                items.append(data)
        
        return {
            "success": True,
            "items": items,
            "count": len(items),
            "user_id": current_user_id
        }
        
    except Exception as e:
        return {"error": f"Wardrobe fetch failed: {str(e)}"}

@app.get("/api/auth/profile")
def mock_profile():
    return {
        "id": "dANqjiI0CKgaitxzYtw1bhtvQrG3",
        "name": "Johnnie Fields",
        "email": "johnnie@example.com",
        "gender": "male",
        "onboardingCompleted": True
    }

@app.post("/api/outfits/generate")
def mock_outfit():
    return {
        "success": True, 
        "outfit": {
            "id": "outfit_1",
            "name": "Dark Academia Confident Look",
            "occasion": "Casual",
            "style": "Dark Academia",
            "mood": "Confident",
            "items": [
                {
                    "id": "item_1",
                    "name": "Dark Academia Blazer",
                    "type": "blazer",
                    "color": "charcoal"
                }
            ],
            "matchScore": 86
        }
    }

@app.get("/api/outfits/")
async def get_outfits(limit: int = 50, offset: int = 0):
    """Get all outfits for the current user."""
    try:
        # Try to import Firebase modules
        try:
            from src.config.firebase import firebase_initialized, db
        except ImportError as e:
            return {"error": f"Firebase import failed: {str(e)}"}
        
        if not firebase_initialized or db is None:
            return {"error": "Firebase not initialized"}
        
        # Get current user (simplified for now)
        current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Your user ID
        
        # Get all outfit documents and filter by user ID
        all_docs = db.collection('outfits').stream()
        
        outfits = []
        for doc in all_docs:
            data = doc.to_dict()
            data['id'] = doc.id
            
            # Check all possible user ID field names
            user_id = (data.get('userId') or 
                      data.get('uid') or 
                      data.get('ownerId') or 
                      data.get('user_id'))
            
            # If this outfit belongs to the current user, include it
            if user_id == current_user_id:
                outfits.append(data)
        
        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        paginated_outfits = outfits[start_idx:end_idx]
        
        return {
            "success": True,
            "outfits": paginated_outfits,
            "total": len(outfits),
            "limit": limit,
            "offset": offset,
            "user_id": current_user_id
        }
        
    except Exception as e:
        return {"error": f"Outfits fetch failed: {str(e)}"}

@app.get("/api/outfits/stats/summary")
def get_outfit_stats():
    """Get outfit statistics for the current user."""
    try:
        # Try to import Firebase modules
        try:
            from src.config.firebase import firebase_initialized, db
        except ImportError as e:
            return {"error": f"Firebase import failed: {str(e)}"}
        
        if not firebase_initialized or db is None:
            return {"error": "Firebase not initialized"}
        
        # Get current user (simplified for now)
        current_user_id = "dANqjiI0CKgaitxzYtw1bhtvQrG3"  # Your user ID
        
        # Get all outfit documents and filter by user ID
        all_docs = db.collection('outfits').stream()
        
        outfits = []
        for doc in all_docs:
            data = doc.to_dict()
            data['id'] = doc.id
            
            # Check all possible user ID field names
            user_id = (data.get('userId') or 
                      data.get('uid') or 
                      data.get('ownerId') or 
                      data.get('user_id'))
            
            # If this outfit belongs to the current user, include it
            if user_id == current_user_id:
                outfits.append(data)
        
        # Calculate basic stats
        total_outfits = len(outfits)
        styles = {}
        occasions = {}
        
        for outfit in outfits:
            style = outfit.get('style', 'Unknown')
            occasion = outfit.get('occasion', 'Unknown')
            
            styles[style] = styles.get(style, 0) + 1
            occasions[occasion] = occasions.get(occasion, 0) + 1
        
        return {
            "success": True,
            "stats": {
                "total_outfits": total_outfits,
                "styles": styles,
                "occasions": occasions,
                "user_id": current_user_id
            }
        }
        
    except Exception as e:
        return {"error": f"Stats fetch failed: {str(e)}"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
