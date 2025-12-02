"""
Outfit management endpoints - Single canonical generator with bulletproof consistency.
All outfits are generated and saved through the same pipeline.
"""

import logging
import time
import urllib.parse
import asyncio
import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

# Set up logger for generation tracking
logger = logging.getLogger(__name__)

# Import cache manager
from ..core.cache import cache_manager

# Debug logging for router loading
logger.error("🚨 FORCE REDEPLOY v13.0: OUTFITS ROUTER LOADING - This should appear in Railway logs")

# All functions have been extracted to modular files:
# - scoring.py: All scoring functions
# - database.py: All database operations
# - helpers.py: Helper functions
# - validation.py: Validation functions
# - routes.py: All route handlers

# Import route handlers from routes module
try:
    from .routes import router
    ROUTES_MODULE_LOADED = True
except ImportError as e:
    logger.warning(f"⚠️ Could not import routes module: {e}")
    # Create empty router as fallback
    from fastapi import APIRouter
    router = APIRouter(tags=["outfits"])
    ROUTES_MODULE_LOADED = False
