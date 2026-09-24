"""Authenticated, read-only aliases for canonical weekly wear statistics."""
from fastapi import APIRouter, HTTPException, Depends
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile
from ..services.wear_statistics import weekly_wear_summary

router = APIRouter(prefix="/api/simple-analytics", tags=["simple-analytics"])

def read_weekly_stats(uid):
    from ..config.firebase import db
    if db is None:
        raise HTTPException(status_code=503, detail="Statistics temporarily unavailable")
    try:
        result = weekly_wear_summary(db, uid)
        return {**result, "worn_this_week": result["outfits_worn_this_week"]}
    except Exception as error:
        raise HTTPException(status_code=503, detail="Statistics temporarily unavailable") from error

@router.get("/outfits-worn-this-week")
async def get_outfits_worn_this_week(current_user: UserProfile = Depends(get_current_user)):
    return read_weekly_stats(current_user.id)

@router.get("/dashboard-stats")
async def get_dashboard_stats(current_user: UserProfile = Depends(get_current_user)):
    return read_weekly_stats(current_user.id)
