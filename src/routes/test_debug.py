from fastapi import APIRouter

router = APIRouter(prefix="/api/test", tags=["test"])

@router.get("/debug")
async def test_debug():
    """Simple test endpoint to verify router mounting"""
    return {"message": "Test debug router is working", "status": "success"}

@router.post("/debug")
async def test_debug_post():
    """Simple test POST endpoint"""
    return {"message": "Test debug POST is working", "status": "success"}
