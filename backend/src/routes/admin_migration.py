"""
Admin Migration Route - Run gamification migration via API
This allows running the migration from Railway where Firebase credentials are properly configured
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Dict, Any
import logging
import os

from ..config.firebase import db

router = APIRouter(prefix="/admin/migration", tags=["admin"])
logger = logging.getLogger(__name__)

# Secret token for admin operations (set in Railway env)
ADMIN_TOKEN = os.getenv("ADMIN_MIGRATION_TOKEN", "changeme123")


@router.post("/gamification")
async def migrate_gamification_fields(
    x_admin_token: str = Header(None)
) -> Dict[str, Any]:
    """
    Migrate existing users to have gamification fields
    Requires admin token in X-Admin-Token header
    """
    # Verify admin token
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized - invalid admin token")
    
    try:
        logger.info("🚀 Starting gamification migration...")
        
        # Migrate users
        users = db.collection('users').stream()
        updated_count = 0
        skipped_count = 0
        
        for user_doc in users:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            
            updates = {}
            
            if 'xp' not in user_data:
                updates['xp'] = 0
            if 'level' not in user_data:
                updates['level'] = 1
            if 'ai_fit_score' not in user_data:
                updates['ai_fit_score'] = 0.0
            if 'badges' not in user_data:
                updates['badges'] = []
            if 'current_challenges' not in user_data:
                updates['current_challenges'] = {}
            if 'spending_ranges' not in user_data:
                updates['spending_ranges'] = {
                    "annual_total": "unknown",
                    "shoes": "unknown",
                    "jackets": "unknown",
                    "pants": "unknown",
                    "tops": "unknown",
                    "dresses": "unknown",
                    "activewear": "unknown",
                    "accessories": "unknown"
                }
            
            if updates:
                user_doc.reference.update(updates)
                updated_count += 1
                logger.info(f"✅ Updated user {user_id}")
            else:
                skipped_count += 1
        
        # Migrate wardrobe items
        items = db.collection('wardrobe').stream()
        wardrobe_updated = 0
        
        for item_doc in items:
            item_data = item_doc.to_dict()
            
            updates = {}
            
            if 'cpw' not in item_data:
                updates['cpw'] = None
            if 'target_wears' not in item_data:
                updates['target_wears'] = 30
            
            if updates:
                item_doc.reference.update(updates)
                wardrobe_updated += 1
        
        logger.info(f"✅ Gamification migration complete!")
        
        return {
            "success": True,
            "users_updated": updated_count,
            "users_skipped": skipped_count,
            "wardrobe_items_updated": wardrobe_updated,
            "message": "Gamification migration completed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


# Export router
__all__ = ['router']

