from fastapi import APIRouter

router = APIRouter(prefix="/api/test-simple", tags=["test"])

@router.get("/")
async def test_simple():
    """Simple test endpoint to verify router loading works"""
    return {"message": "Simple test router loaded successfully", "status": "success"}
