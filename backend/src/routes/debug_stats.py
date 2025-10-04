from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

# Import Firebase
try:
    from ..config.firebase import db, firebase_initialized
    if not firebase_initialized:
        raise ImportError("Firebase not initialized")
except ImportError as e:
    logging.error(f"Firebase import failed: {e}")
    db = None

router = APIRouter()
logger = logging.getLogger(__name__)

@(router.get("/debug-stats") if router else None)
async def get_debug_stats(user_id: str = Query(..., description="User ID to get debug stats for")) -> Dict[str, Any]:
    """
    Get debug stats updates for a user (bypasses Railway rate limiting).
    This shows the actual backend increment/reset operations.
    """
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Firebase not available")

        # Get debug stats from the last 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Query debug_stats_updates collection
        debug_ref = db.collection('debug_stats_updates').where('user_id', '==', user_id)
        debug_docs = debug_ref.stream()
        
        debug_entries = []
        for doc in debug_docs:
            doc_data = doc.to_dict()
            
            # Parse timestamp and filter to last 24 hours
            try:
                doc_timestamp = datetime.fromisoformat((doc_data.get('timestamp', '') if doc_data else ''))
                if doc_timestamp >= cutoff_time:
                    debug_entries.append({
                        'id': doc.id,
                        **doc_data
                    })
            except:
                # Include entries without valid timestamps
                debug_entries.append({
                    'id': doc.id,
                    **doc_data
                })
        
        # Sort by timestamp (newest first)
        debug_entries.sort(key=lambda x: (x.get('timestamp', '') if x else ''), reverse=True)
        
        # Get current user_stats for comparison
        user_stats_ref = db.collection('user_stats').document(user_id)
        user_stats_doc = user_stats_ref.get() if user_stats_ref else None
        
        current_stats = None
        if user_stats_doc.exists:
            current_stats = user_stats_doc.to_dict()
        
        return {
            "success": True,
            "user_id": user_id,
            "current_stats": current_stats,
            "debug_entries": debug_entries[:20],  # Limit to 20 most recent
            "total_entries": len(debug_entries),
            "message": f"Found {len(debug_entries)} debug entries in last 24 hours"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting debug stats for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get debug stats: {str(e)}"
        )
