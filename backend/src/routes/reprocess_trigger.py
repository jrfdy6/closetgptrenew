"""
Trigger endpoint for reprocessing all wardrobe items with alpha matting
Access via: POST /api/reprocess/trigger

This endpoint runs the reprocessing logic directly by importing worker functions.
"""
from fastapi import APIRouter, HTTPException
import logging
import asyncio
import sys
import os
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

# Try to import worker functions directly
try:
    # Add multiple possible paths
    possible_paths = [
        Path(__file__).parent.parent.parent / "worker",
        Path(__file__).parent.parent.parent.parent / "worker",
        Path("/app/worker"),
        Path("/app"),
    ]
    
    for path in possible_paths:
        if path.exists():
            sys.path.insert(0, str(path))
            logger.info(f"Added to path: {path}")
    
    # Try importing from worker main
    try:
        from main import (
            process_item,
            db,
            bucket,
            _alpha_matting,
            remove_hangers,
            smooth_edges,
            add_material_shadow,
            apply_light_gradient,
            resize_image,
            generate_thumbnail,
            upload_png,
            resolve_material,
            MAX_OUTPUT_WIDTH,
            MAX_OUTPUT_HEIGHT,
            THUMBNAIL_SIZE,
            MAX_IMAGE_BYTES,
            ALPHA_TIMEOUT_SECONDS,
        )
        WORKER_FUNCTIONS_AVAILABLE = True
        logger.info("✅ Worker functions imported successfully")
    except ImportError as e:
        logger.warning(f"Could not import from worker main: {e}")
        WORKER_FUNCTIONS_AVAILABLE = False
        
except Exception as e:
    logger.warning(f"Could not set up worker imports: {e}")
    WORKER_FUNCTIONS_AVAILABLE = False

@router.post("/trigger")
async def trigger_reprocess():
    """
    Trigger reprocessing of all wardrobe items with alpha matting.
    This processes items directly using worker functions.
    """
    if not WORKER_FUNCTIONS_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Worker functions not available. The reprocess script must be run in the worker service."
        )
    
    try:
        logger.info("🚀 Starting reprocess of all wardrobe items with alpha matting...")
        
        # Get all wardrobe items
        items_ref = db.collection("wardrobe")
        all_items = list(items_ref.stream())
        
        logger.info(f"📊 Found {len(all_items)} total items")
        
        # Filter items that need processing (not already processed with alpha matting)
        items_to_process = []
        for doc in all_items:
            item_id = doc.id
            item_data = doc.to_dict()
            processing_mode = item_data.get("processing_mode")
            if processing_mode != "alpha":
                items_to_process.append((item_id, item_data))
            else:
                logger.info(f"⏭️  {item_id}: Already processed with alpha matting, skipping")
        
        logger.info(f"🎯 {len(items_to_process)} items need reprocessing")
        
        if not items_to_process:
            return {
                "success": True,
                "message": "All items already processed with alpha matting",
                "total_items": len(all_items),
                "processed": 0,
                "skipped": len(all_items)
            }
        
        # Process items (this will be slow, so run in executor)
        def process_all_items():
            results = {"success": 0, "skipped": 0, "error": 0}
            for i, (item_id, item_data) in enumerate(items_to_process, 1):
                logger.info(f"[{i}/{len(items_to_process)}] Processing {item_id}...")
                try:
                    # Use the worker's process_item function
                    process_item(item_id, item_data)
                    results["success"] += 1
                except Exception as e:
                    logger.error(f"❌ Error processing {item_id}: {e}")
                    results["error"] += 1
            return results
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, process_all_items)
        
        return {
            "success": True,
            "message": f"Reprocess completed. Processed {results['success']} items.",
            "total_items": len(all_items),
            "processed": results["success"],
            "skipped": len(all_items) - len(items_to_process),
            "errors": results["error"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error during reprocess: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reprocess items: {str(e)}"
        )

