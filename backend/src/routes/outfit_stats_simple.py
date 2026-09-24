"""Compatibility statistics route backed by owned records, without GET writes."""
from fastapi import APIRouter, HTTPException, Depends, Query
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile
from ..services.wear_statistics import weekly_wear_summary, _owned_records

router = APIRouter(tags=["outfit-stats"])

@router.get("/stats")
async def get_simple_outfit_stats(
    current_user: UserProfile = Depends(get_current_user),
    days: int = Query(7, ge=1, le=366, description="Compatibility parameter; weekly counts use the profile calendar week"),
):
    from ..config.firebase import db
    if db is None:
        raise HTTPException(status_code=503, detail="Statistics temporarily unavailable")
    try:
        summary = weekly_wear_summary(db, current_user.id)
        total = sum(1 for record in _owned_records(db, "outfits", current_user.id)
                    if not any(record.get(key) for key in ("deleted", "isDeleted", "deletedAt", "deleted_at")))
        count = summary["outfits_worn_this_week"]
        return {**summary, "total_outfits": total, "outfits_this_week": count,
                "totalThisWeek": count, "days_queried": days}
    except Exception as error:
        raise HTTPException(status_code=503, detail="Statistics temporarily unavailable") from error
