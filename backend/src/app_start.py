#!/usr/bin/env python3
"""
App Startup Module
==================

Handles startup logging, version tracking, and guarded imports.
"""

import logging
import os
import traceback

# Get commit SHA for version tracking
COMMIT_SHA = os.getenv("COMMIT_SHA", "unknown")
logging.info("Service starting - commit=%s", COMMIT_SHA)

# Guarded import for WardrobePreprocessor
try:
    from src.services.wardrobe_preprocessor import WardrobePreprocessor
    logging.info("🔧 DEBUG v3.0: WardrobePreprocessor imported successfully")
    WARDROBE_PREPROCESSOR_AVAILABLE = True
except Exception as e:
    logging.exception("❌ DEBUG v3.0: WardrobePreprocessor import FAILED: %s", e)
    logging.error("❌ DEBUG v3.0: Traceback: %s", traceback.format_exc())
    WardrobePreprocessor = None
    WARDROBE_PREPROCESSOR_AVAILABLE = False

# Log other critical imports
try:
    from src.services.robust_outfit_generation_service import RobustOutfitGenerationService
    logging.info("✅ RobustOutfitGenerationService imported successfully")
except Exception as e:
    logging.exception("❌ RobustOutfitGenerationService import FAILED: %s", e)

try:
    from src.custom_types.wardrobe import ClothingItem
    logging.info("✅ ClothingItem imported successfully")
except Exception as e:
    logging.exception("❌ ClothingItem import FAILED: %s", e)

logging.info("🚀 App startup completed - commit=%s", COMMIT_SHA)
