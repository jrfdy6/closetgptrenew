from fastapi import APIRouter, HTTPException
from firebase_admin import firestore
import time
import platform
import sys
from typing import Dict, Any

router = APIRouter()
db = firestore.client()

@router.get("/public/health")
async def get_public_health():
    """
    Completely public health check endpoint for diagnostic testing.
    """
    try:
        # Get outfit count from Firestore
        outfits_ref = db.collection('outfits')
        outfit_count = len(list(outfits_ref.stream()))
        
        # Get trace count
        traces_ref = db.collection('generation_traces')
        trace_count = len(list(traces_ref.stream()))
        
        return {
            "status": "healthy",
            "timestamp": int(time.time()),
            "system_info": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "uptime": "running"
            },
            "diagnostic_data": {
                "outfits_count": outfit_count,
                "traces_count": trace_count,
                "last_test_outfit_id": "c833709e-c1b6-4618-8c87-0ceede11acf7"
            },
            "message": "Public diagnostic system is operational"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": int(time.time())
        }

@router.get("/public/outfit-traces")
async def get_public_outfit_traces():
    """
    Completely public outfit traces endpoint for diagnostic testing.
    """
    try:
        # Get the most recent outfit trace
        outfits_ref = db.collection('outfits')
        outfits = list(outfits_ref.order_by('createdAt', direction='DESCENDING').limit(1).stream())
        
        if not outfits:
            return {
                "status": "no_data",
                "message": "No outfit traces found",
                "timestamp": int(time.time())
            }
        
        outfit_data = outfits[0].to_dict()
        outfit_data['outfit_id'] = outfits[0].id
        
        return {
            "status": "success",
            "timestamp": int(time.time()),
            "latest_outfit": {
                "id": outfit_data['outfit_id'],
                "name": outfit_data.get('name', 'Unknown'),
                "generation_method": outfit_data.get('generation_method', 'unknown'),
                "was_successful": outfit_data.get('wasSuccessful', False),
                "items_count": len(outfit_data.get('items', [])),
                "created_at": outfit_data.get('createdAt', 0),
                "validation_errors": outfit_data.get('validationErrors', []),
                "generation_trace": outfit_data.get('generation_trace', [])
            },
            "message": "Latest outfit trace retrieved successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": int(time.time())
        } 