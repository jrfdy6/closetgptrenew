"""
Ultra simple backfill endpoint - minimal dependencies
Just hit the URL and it runs
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/run-now")
async def run_backfill_now():
    """
    Simple endpoint that runs the backfill when you visit it
    No parameters needed - just visit the URL!
    """
    try:
        # Import what we need inline to avoid startup issues
        from datetime import datetime
        
        # Try to import Firebase
        try:
            from src.config.firebase import db
        except:
            try:
                from config.firebase import db
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Could not import Firebase: {e}",
                    "step": "firebase_import_failed"
                }
        
        if db is None:
            return {
                "success": False,
                "error": "Firebase db is None - not initialized",
                "step": "firebase_not_initialized"
            }
        
        # Import normalization inline
        try:
            from src.utils.semantic_normalization import normalize_item_metadata
        except:
            try:
                from utils.semantic_normalization import normalize_item_metadata
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Could not import normalization: {e}",
                    "step": "normalization_import_failed"
                }
        
        # Run the backfill
        logger.info("🚀 Starting inline backfill...")
        
        stats = {
            'processed': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Get first 10 items as a test
        items = db.collection('wardrobe').limit(10).stream()
        
        for doc in items:
            item = doc.to_dict()
            stats['processed'] += 1
            
            # Skip if already normalized
            if 'normalized' in item:
                stats['skipped'] += 1
                logger.info(f"⏭️ Skipped {doc.id}")
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
                
                # Actually update (no dry run for simplicity)
                db.collection('wardrobe').document(doc.id).update({
                    'normalized': normalized_fields
                })
                
                stats['updated'] += 1
                logger.info(f"✅ Updated {doc.id}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing {doc.id}: {e}")
                stats['errors'] += 1
        
        success_rate = (stats['updated'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
        
        return {
            "success": True,
            "message": "Backfill complete! (First 10 items)",
            "stats": stats,
            "success_rate": f"{success_rate:.1f}%",
            "note": "This was a test run with 10 items. Visit /run-all to process everything."
        }
        
    except Exception as e:
        logger.error(f"Backfill failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

@router.get("/run-all")
async def run_backfill_all():
    """
    Run backfill on ALL items
    WARNING: This actually updates the database!
    """
    try:
        from datetime import datetime
        
        # Import Firebase
        try:
            from src.config.firebase import db
        except:
            from config.firebase import db
        
        if db is None:
            return {"success": False, "error": "Firebase not initialized"}
        
        # Import normalization
        try:
            from src.utils.semantic_normalization import normalize_item_metadata
        except:
            from utils.semantic_normalization import normalize_item_metadata
        
        logger.info("🚀 Starting FULL backfill...")
        
        stats = {
            'processed': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Get ALL items
        items = db.collection('wardrobe').stream()
        
        for doc in items:
            item = doc.to_dict()
            stats['processed'] += 1
            
            if 'normalized' in item:
                stats['skipped'] += 1
                continue
            
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
                
                db.collection('wardrobe').document(doc.id).update({
                    'normalized': normalized_fields
                })
                
                stats['updated'] += 1
                
                # Log progress every 50 items
                if stats['processed'] % 50 == 0:
                    logger.info(f"📊 Progress: {stats['processed']} items processed")
                    
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                stats['errors'] += 1
        
        success_rate = (stats['updated'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
        
        return {
            "success": True,
            "message": "FULL BACKFILL COMPLETE!",
            "stats": stats,
            "success_rate": f"{success_rate:.1f}%"
        }
        
    except Exception as e:
        logger.error(f"Full backfill failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/status")
async def check_status():
    """Check how many items are normalized"""
    try:
        try:
            from src.config.firebase import db
        except:
            from config.firebase import db
        
        if db is None:
            return {"error": "Firebase not initialized"}
        
        # Count total
        total_items = []
        for doc in db.collection('wardrobe').stream():
            total_items.append(doc)
        
        # Count normalized
        normalized_items = []
        for doc in db.collection('wardrobe').where('normalized', '!=', None).stream():
            normalized_items.append(doc)
        
        total = len(total_items)
        normalized = len(normalized_items)
        remaining = total - normalized
        progress = (normalized / total * 100) if total > 0 else 0
        
        return {
            "total_items": total,
            "normalized_items": normalized,
            "remaining_items": remaining,
            "progress": f"{progress:.1f}%",
            "complete": remaining == 0
        }
        
    except Exception as e:
        return {"error": str(e)}

