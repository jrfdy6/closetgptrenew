#!/usr/bin/env python3
"""
Test script to identify robust service import issues.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test each import step by step to identify the failure point."""
    
    print("🔍 Testing imports step by step...")
    
    # Test 1: Basic imports
    try:
        import logging
        from typing import Dict, List, Any, Optional
        from datetime import datetime
        from uuid import uuid4
        print("✅ Basic imports successful")
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False
    
    # Test 2: Models import
    try:
        from src.routes.outfits.models import OutfitRequest, OutfitResponse
        print("✅ Models import successful")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    # Test 3: Utils import
    try:
        from src.routes.outfits.utils import log_generation_strategy, clean_for_firestore
        print("✅ Utils import successful")
    except Exception as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    # Test 4: Validation import
    try:
        from src.routes.outfits.validation import validate_style_gender_compatibility
        print("✅ Validation import successful")
    except Exception as e:
        print(f"❌ Validation import failed: {e}")
        return False
    
    # Test 5: Generation import
    try:
        from src.routes.outfits.generation import ensure_base_item_included
        print("✅ Generation import successful")
    except Exception as e:
        print(f"❌ Generation import failed: {e}")
        return False
    
    # Test 6: Full generation service import
    try:
        from src.services.outfits.generation_service import OutfitGenerationService
        print("✅ Generation service import successful")
        
        # Test instantiation
        service = OutfitGenerationService()
        print("✅ Generation service instantiation successful")
        
    except Exception as e:
        print(f"❌ Generation service import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("🎉 All imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
