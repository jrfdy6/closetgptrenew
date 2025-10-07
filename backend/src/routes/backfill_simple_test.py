"""
Ultra-simple backfill test endpoint with no dependencies
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test_backfill():
    """Test if backfill router is loading"""
    return {
        "status": "backfill router loaded",
        "message": "If you see this, the router is working!"
    }

@router.get("/trigger-simple")
async def trigger_simple():
    """Simple trigger that we'll build up gradually"""
    try:
        # Try to import Firebase
        try:
            from src.config.firebase import db
        except ImportError:
            from config.firebase import db
        
        if db is None:
            return {
                "success": False,
                "error": "Firebase not initialized",
                "step": "firebase_check"
            }
        
        # Try to get a count
        try:
            items = list(db.collection('wardrobe').limit(1).stream())
            return {
                "success": True,
                "message": "Firebase connection working!",
                "sample_count": len(items),
                "step": "firebase_working"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "step": "firebase_query_failed"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "step": "import_failed"
        }

