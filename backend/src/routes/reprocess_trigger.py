"""
Trigger endpoint for reprocessing all wardrobe items with alpha matting
Access via: POST /api/reprocess/trigger
"""
from fastapi import APIRouter, HTTPException
import logging
import asyncio
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

# Import the reprocess script functions directly
try:
    # Add worker directory to path
    worker_dir = Path(__file__).parent.parent.parent / "worker"
    if worker_dir.exists():
        sys.path.insert(0, str(worker_dir))
    
    # Import the main function from the reprocess script
    from reprocess_all_wardrobe_items import main as reprocess_main
    SCRIPT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import reprocess script: {e}")
    SCRIPT_AVAILABLE = False
    reprocess_main = None

@router.post("/trigger")
async def trigger_reprocess():
    """
    Trigger reprocessing of all wardrobe items with alpha matting.
    This runs the reprocess script directly in the same process.
    """
    if not SCRIPT_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Reprocess script not available. Make sure it's in the worker directory."
        )
    
    try:
        logger.info("🚀 Triggering reprocess of all wardrobe items with alpha matting...")
        
        # Run the reprocess main function in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, reprocess_main)
        
        return {
            "success": True,
            "message": "Reprocess completed successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error during reprocess: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reprocess items: {str(e)}"
        )

