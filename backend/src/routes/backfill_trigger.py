"""
Simple backfill trigger endpoint
Access via: /api/backfill/trigger?dry_run=true&max_items=10
"""
from fastapi import APIRouter, Query
from typing import Optional
from config.firebase import db
from utils.semantic_normalization import normalize_item_metadata
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/trigger")
async def trigger_backfill(
    dry_run: bool = Query(True, description="Run in dry-run mode (no changes)"),
    max_items: Optional[int] = Query(None, description="Maximum items to process (default: all)")
):
    """
    Trigger database backfill for semantic filtering
    
    Examples:
    - /api/backfill/trigger?dry_run=true&max_items=10  (test with 10 items)
    - /api/backfill/trigger?dry_run=true               (dry run all items)
    - /api/backfill/trigger?dry_run=false              (PRODUCTION - update all items)
    """
    
    mode = "DRY RUN" if dry_run else "PRODUCTION"
    logger.info(f"🚀 Backfill triggered [{mode}]")
    
    if not db:
        return {
            "success": False,
            "error": "Firebase not initialized"
        }
    
    stats = {
        'processed': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    try:
        # Get wardrobe items
        query = db.collection('wardrobe')
        if max_items:
            query = query.limit(max_items)
        
        items = query.stream()
        
        for doc in items:
            item = doc.to_dict()
            stats['processed'] += 1
            
            # Skip if already normalized
            if 'normalized' in item:
                stats['skipped'] += 1
                continue
            
            # Normalize
            try:
                normalized = normalize_item_metadata(item)
                normalized_fields = {
                    'style': normalized.get('style', []),
                    'occasion': normalized.get('occasion', []),
                    'mood': normalized.get('mood', []),
                    'season': normalized.get('season', []),
                    'normalized_at': datetime.utcnow().isoformat(),
                    'normalized_version': '1.0'
                }
                
                if not dry_run:
                    db.collection('wardrobe').document(doc.id).update({
                        'normalized': normalized_fields
                    })
                
                stats['updated'] += 1
                    
            except Exception as e:
                logger.error(f"❌ Error processing {doc.id}: {e}")
                stats['errors'] += 1
        
        success_rate = (stats['updated'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
        
        return {
            "success": True,
            "mode": mode,
            "stats": stats,
            "success_rate": f"{success_rate:.1f}%",
            "message": f"Backfill complete! Processed {stats['processed']} items."
        }
        
    except Exception as e:
        logger.error(f"❌ Backfill failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "stats": stats
        }

@router.get("/status")
async def backfill_status():
    """Check how many items need normalization"""
    
    if not db:
        return {"error": "Firebase not initialized"}
    
    try:
        # Count total items
        total_count = len(list(db.collection('wardrobe').stream()))
        
        # Count normalized items
        normalized_count = len(list(db.collection('wardrobe').where('normalized', '!=', None).stream()))
        
        remaining = total_count - normalized_count
        progress = (normalized_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "total_items": total_count,
            "normalized_items": normalized_count,
            "remaining_items": remaining,
            "progress": f"{progress:.1f}%",
            "complete": remaining == 0
        }
        
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return {"error": str(e)}

