#!/usr/bin/env python3
"""
Simple Personalized Outfits Routes - Minimal Version
====================================================

This is a minimal version that doesn't depend on the lightweight services
to test if the basic router loading works.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models
class InteractionRequest(BaseModel):
    outfit_id: Optional[str] = None
    item_id: Optional[str] = None
    interaction_type: str  # view, like, wear, dislike
    rating: Optional[float] = None

class PersonalizationStatusResponse(BaseModel):
    user_id: str
    personalization_enabled: bool
    has_user_embedding: bool
    total_interactions: int
    min_interactions_required: int
    ready_for_personalization: bool
    system_parameters: Dict[str, Any]

@router.get("/health")
async def health_check():
    """Health check for the minimal simple personalization system"""
    try:
        return {
            "status": "healthy",
            "personalization_enabled": True,
            "min_interactions_required": 3,
            "max_outfits": 5,
            "simple_personalization": True,
            "no_external_dependencies": True,
            "minimal_version": True,
            "timestamp": time.time()
        }
    
    except Exception as e:
        logger.error(f"❌ Minimal simple personalization health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "simple_personalization": True,
            "minimal_version": True,
            "timestamp": time.time()
        }

@router.get("/test")
async def test_endpoint():
    """Test endpoint for minimal simple personalization"""
    return {
        "message": "Minimal simple personalization router is working",
        "status": "success",
        "timestamp": time.time()
    }

@router.post("/interaction")
async def record_minimal_interaction(
    interaction: InteractionRequest
):
    """Record user interaction - minimal version"""
    try:
        return {
            "success": True,
            "message": f"Recorded {interaction.interaction_type} interaction",
            "minimal_version": True,
            "timestamp": time.time()
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to record interaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record interaction: {str(e)}"
        )

@router.get("/personalization-status")
async def get_minimal_personalization_status():
    """Get personalization status - minimal version"""
    try:
        return PersonalizationStatusResponse(
            user_id="test-user",
            personalization_enabled=True,
            has_user_embedding=False,
            total_interactions=0,
            min_interactions_required=3,
            ready_for_personalization=False,
            system_parameters={
                "min_interactions": 3,
                "max_outfits": 5,
                "minimal_version": True
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to get personalization status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get personalization status: {str(e)}"
        )
