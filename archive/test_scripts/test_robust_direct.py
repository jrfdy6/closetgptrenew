#!/usr/bin/env python3
"""
Test script to directly test robust service imports.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_robust_service():
    """Test robust service import and instantiation."""
    
    print("🔍 Testing robust service directly...")
    
    # Test 1: Import custom types
    try:
        from src.custom_types.wardrobe import ClothingItem, Metadata
        print("✅ Custom types wardrobe import successful")
    except Exception as e:
        print(f"❌ Custom types wardrobe import failed: {e}")
        return False
    
    try:
        from src.custom_types.outfit import OutfitGeneratedOutfit, OutfitPiece
        print("✅ Custom types outfit import successful")
    except Exception as e:
        print(f"❌ Custom types outfit import failed: {e}")
        return False
    
    try:
        from src.custom_types.weather import WeatherData
        print("✅ Custom types weather import successful")
    except Exception as e:
        print(f"❌ Custom types weather import failed: {e}")
        return False
    
    try:
        from src.custom_types.profile import UserProfile
        print("✅ Custom types profile import successful")
    except Exception as e:
        print(f"❌ Custom types profile import failed: {e}")
        return False
    
    # Test 2: Import robust hydrator
    try:
        from src.services.robust_hydrator import ensure_items_safe_for_pydantic
        print("✅ Robust hydrator import successful")
    except Exception as e:
        print(f"❌ Robust hydrator import failed: {e}")
        return False
    
    # Test 3: Import robust service
    try:
        from src.services.robust_outfit_generation_service import RobustOutfitGenerationService, GenerationContext
        print("✅ Robust service import successful")
        
        # Test instantiation
        service = RobustOutfitGenerationService()
        print("✅ Robust service instantiation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Robust service import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_robust_service()
    sys.exit(0 if success else 1)
