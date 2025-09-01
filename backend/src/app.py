from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.3"}

@app.get("/api/wardrobe/")
def mock_wardrobe():
    return {"success": True, "items": [], "count": 0}

@app.get("/api/auth/profile")
def mock_profile():
    return {"id": "mock_user", "name": "Mock User", "gender": "male"}

@app.post("/api/outfits/generate")
def mock_outfit():
    return {"success": True, "outfit": {"id": "mock_1", "name": "Mock Outfit"}}