#!/usr/bin/env python3
"""
Test Simple Router
=================

A minimal test router to verify the router loading system is working.
"""

from fastapi import APIRouter

# Create router
router = APIRouter()

@(router.get("/health") if router else None)
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "message": "Test simple router is working",
        "timestamp": "2025-09-23T10:25:00Z"
    }

@(router.get("/test") if router else None)
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "Test endpoint is working",
        "router": "test_simple"
    }