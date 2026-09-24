"""
Working authentication routes for Easy Outfit App.
Follows the exact pattern used by working wardrobe.py and outfits.py
"""

from fastapi import APIRouter, Depends, Request
import logging
from src.auth.verified_identity import verified_identity
from src.routes.user_profile import get_profile, save_profile_response

logger = logging.getLogger("auth_working")

router = APIRouter(tags=["authentication"])

@router.get("/profile/health")
async def profile_health():
    """Health check for profile route - no authentication required."""
    logger.info("🔍 PROFILE: Health check called")
    try:
        from ..config.firebase import firebase_initialized, db
        return {
            "status": "ok",
            "firebase_initialized": firebase_initialized,
            "db_available": db is not None
        }
    except Exception as e:
        logger.error(f"🔍 PROFILE: Health check failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/profile")
def get_user_profile(request: Request, claims: dict = Depends(verified_identity)):
    """Retain direct clients while sharing the verified, durable profile read."""
    return get_profile(request, claims)


@router.put("/profile")
async def update_user_profile(request: Request, claims: dict = Depends(verified_identity)):
    """Compatibility alias; account and quiz authority follow the main writer."""
    return await save_profile_response(request, claims, wardrobe_aliases=True)
