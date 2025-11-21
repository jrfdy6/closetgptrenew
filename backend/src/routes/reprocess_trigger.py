"""
Trigger endpoint for reprocessing all wardrobe items with alpha matting
Access via: POST /api/reprocess/trigger

This endpoint marks items as "pending" so the worker automatically picks them up and processes them.
"""
from fastapi import APIRouter, HTTPException
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

try:
    from src.config.firebase import db
    FIREBASE_AVAILABLE = True
except ImportError:
    try:
        from config.firebase import db
        FIREBASE_AVAILABLE = True
    except ImportError:
        FIREBASE_AVAILABLE = False
        db = None

@router.post("/trigger")
async def trigger_reprocess():
    """
    Trigger reprocessing of all wardrobe items with alpha matting.
    This marks items as "pending" so the worker automatically processes them.
    """
    if not FIREBASE_AVAILABLE or not db:
        raise HTTPException(
            status_code=500,
            detail="Firebase not available"
        )
    
    try:
        logger.info("🚀 Starting reprocess trigger - marking items as pending...")
        
        # Get all wardrobe items
        items_ref = db.collection("wardrobe")
        all_items = list(items_ref.stream())
        
        logger.info(f"📊 Found {len(all_items)} total items")
        
        # Filter items that need processing (not already processed with alpha matting)
        items_to_mark = []
        skipped_count = 0
        
        for doc in all_items:
            item_id = doc.id
            item_data = doc.to_dict()
            processing_mode = item_data.get("processing_mode")
            
            if processing_mode != "alpha":
                items_to_mark.append(item_id)
            else:
                skipped_count += 1
                logger.debug(f"⏭️  {item_id}: Already processed with alpha matting, skipping")
        
        logger.info(f"🎯 Marking {len(items_to_mark)} items as pending for reprocessing")
        
        if not items_to_mark:
            return {
                "success": True,
                "message": "All items already processed with alpha matting",
                "total_items": len(all_items),
                "marked_pending": 0,
                "skipped": skipped_count
            }
        
        # Mark items as pending - the worker will pick them up automatically
        marked_count = 0
        for item_id in items_to_mark:
            try:
                doc_ref = db.collection("wardrobe").document(item_id)
                doc_ref.update({
                    "processing_status": "pending",
                    "processing_retry_count": 0,  # Reset retry count
                    "processing_error": None,
                })
                marked_count += 1
            except Exception as e:
                logger.error(f"❌ Error marking {item_id} as pending: {e}")
        
        logger.info(f"✅ Marked {marked_count} items as pending. Worker will process them automatically.")
        
        return {
            "success": True,
            "message": f"Marked {marked_count} items as pending. The worker will automatically process them with alpha matting.",
            "total_items": len(all_items),
            "marked_pending": marked_count,
            "skipped": skipped_count,
            "note": "Check the worker logs to see processing progress. Items will be processed one at a time."
        }
        
    except Exception as e:
        logger.error(f"❌ Error during reprocess trigger: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger reprocess: {str(e)}"
        )

