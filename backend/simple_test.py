from fastapi import APIRouter

router = APIRouter(prefix="/api/simple")

@router.get("/")
async def test():
    return {"message": "Simple test works!"}
