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
def mock_wardrobe():
    return {
        "success": True, 
        "items": [
            {
                "id": "item_1",
                "name": "Dark Academia Blazer",
                "type": "blazer",
                "color": "charcoal",
                "brand": "The Savile Row Company",
                "isFavorite": True
            }
        ], 
        "count": 1,
        "user_id": "dANqjiI0CKgaitxzYtw1bhtvQrG3"
    }

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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
