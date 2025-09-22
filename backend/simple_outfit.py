from fastapi import APIRouter

router = APIRouter(prefix="/api/outfit")

@router.get("/")
async def test():
    return {"message": "Simple outfit router works!"}

@router.post("/generate")
async def generate():
    return {"message": "Generate works!", "outfit": {"id": "123", "items": []}}
