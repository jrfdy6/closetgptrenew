"""
Targeted import test to identify which specific import is failing.
"""

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    tags=["outfits-targeted"]
)

@router.get("/health")
async def targeted_health():
    """Health check for targeted import testing."""
    return {
        "status": "ok",
        "service": "outfits-targeted",
        "message": "Targeted import testing router is working"
    }

# Test 1: Models import only
@router.get("/test-models")
async def test_models_import():
    """Test models import specifically."""
    try:
        from .models import OutfitRequest, OutfitResponse
        return {
            "status": "success",
            "test": "models_import",
            "message": "Models imported successfully",
            "models": {
                "OutfitRequest": str(OutfitRequest),
                "OutfitResponse": str(OutfitResponse)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "test": "models_import",
            "error": str(e),
            "error_type": type(e).__name__
        }

# Test 2: Auth import only
@router.get("/test-auth")
async def test_auth_import():
    """Test auth import specifically."""
    try:
        from src.auth.auth_service import get_current_user, get_current_user_id
        return {
            "status": "success",
            "test": "auth_import",
            "message": "Auth imported successfully",
            "auth_functions": {
                "get_current_user": str(get_current_user),
                "get_current_user_id": str(get_current_user_id)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "test": "auth_import",
            "error": str(e),
            "error_type": type(e).__name__
        }

# Test 3: Utils import only
@router.get("/test-utils")
async def test_utils_import():
    """Test utils import specifically."""
    try:
        from .utils import log_generation_strategy
        return {
            "status": "success",
            "test": "utils_import",
            "message": "Utils imported successfully",
            "utils_functions": {
                "log_generation_strategy": str(log_generation_strategy)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "test": "utils_import",
            "error": str(e),
            "error_type": type(e).__name__
        }

# Test 4: All imports together
@router.get("/test-all-imports")
async def test_all_imports():
    """Test all imports together to see the failure point."""
    results = {}
    
    # Test models
    try:
        from .models import OutfitRequest, OutfitResponse
        results["models"] = {"status": "success", "message": "Models imported"}
    except Exception as e:
        results["models"] = {"status": "error", "error": str(e), "error_type": type(e).__name__}
        return {"status": "error", "failed_at": "models", "results": results}
    
    # Test auth
    try:
        from src.auth.auth_service import get_current_user, get_current_user_id
        results["auth"] = {"status": "success", "message": "Auth imported"}
    except Exception as e:
        results["auth"] = {"status": "error", "error": str(e), "error_type": type(e).__name__}
        return {"status": "error", "failed_at": "auth", "results": results}
    
    # Test utils
    try:
        from .utils import log_generation_strategy
        results["utils"] = {"status": "success", "message": "Utils imported"}
    except Exception as e:
        results["utils"] = {"status": "error", "error": str(e), "error_type": type(e).__name__}
        return {"status": "error", "failed_at": "utils", "results": results}
    
    return {
        "status": "success",
        "message": "All imports successful",
        "results": results
    }

logger.info("✅ Targeted import test router created successfully")
