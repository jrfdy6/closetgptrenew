"""
Working authentication routes for Easy Outfit App.
Follows the exact pattern used by working wardrobe.py and outfits.py
"""

from fastapi import APIRouter, Depends, Request
import logging
import time
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


async def recalculate_tve_for_user(user_id: str) -> None:
    """
    Background TVE recalculation when spending ranges change.
    Runs after the response is returned so onboarding stays fast.
    """
    try:
        from ..config.firebase import db
        from ..services.tve_service import tve_service

        user_ref = db.collection("users").document(user_id)
        user_ref.set(
            {
                "tveRecalcStatus": "running",
                "tveRecalcStartedAt": int(time.time()),
            },
            merge=True,
        )

        wardrobe_ref = db.collection("wardrobe").where("userId", "==", user_id)
        items = list(wardrobe_ref.stream())

        recalculated_count = 0
        for doc in items:
            try:
                success = await tve_service.initialize_item_tve_fields(user_id, doc.id)
                if success:
                    recalculated_count += 1
            except Exception:
                # Keep going; one bad item shouldn't kill the batch
                continue

        user_ref.set(
            {
                "tveRecalcStatus": "completed",
                "tveRecalcCompletedAt": int(time.time()),
                "tveRecalcUpdatedCount": recalculated_count,
            },
            merge=True,
        )
    except Exception as e:
        try:
            from ..config.firebase import db

            db.collection("users").document(user_id).set(
                {
                    "tveRecalcStatus": "error",
                    "tveRecalcCompletedAt": int(time.time()),
                    "tveRecalcError": str(e)[:500],
                },
                merge=True,
            )
        except Exception:
            pass
