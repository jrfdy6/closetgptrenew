"""
Minimal test router for outfits to isolate import issues.
"""

import logging
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

# Create a minimal router without complex imports
router = APIRouter(
    tags=["outfits-test"]
)

@router.get("/health")
async def outfits_health():
    """Simple health check for outfits router."""
    return {
        "status": "ok",
        "service": "outfits-test",
        "message": "Minimal outfits router is working"
    }

@router.post("/generate")
async def test_generate():
    """Test outfit generation endpoint."""
    return {
        "status": "ok",
        "message": "Test outfit generation endpoint is working",
        "outfit": {
            "id": "test-outfit-1",
            "name": "Test Outfit",
            "items": [],
            "style": "test",
            "occasion": "test"
        }
    }

logger.info("✅ Minimal outfits test router created successfully")
