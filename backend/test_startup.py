#!/usr/bin/env python3
"""
Test script to identify startup issues with the full app.
"""

import sys
import os
import traceback

def test_imports():
    """Test each import step by step to identify the failing module."""
    
    print("🔍 Testing imports step by step...")
    
    # Test 1: Basic FastAPI
    try:
        from fastapi import FastAPI
        print("✅ FastAPI import successful")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    # Test 2: Firebase
    try:
        import firebase_admin
        from firebase_admin import firestore
        print("✅ Firebase import successful")
    except Exception as e:
        print(f"❌ Firebase import failed: {e}")
        return False
    
    # Test 3: OpenAI
    try:
        from openai import OpenAI
        print("✅ OpenAI import successful")
    except Exception as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    # Test 4: Pydantic
    try:
        from pydantic import BaseModel
        print("✅ Pydantic import successful")
    except Exception as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    # Test 5: Core modules
    try:
        from src.core.logging import setup_logging
        print("✅ Core logging import successful")
    except Exception as e:
        print(f"❌ Core logging import failed: {e}")
        return False
    
    # Test 6: Routes
    try:
        from src.routes import outfits
        print("✅ Routes import successful")
    except Exception as e:
        print(f"❌ Routes import failed: {e}")
        return False
    
    # Test 7: Config
    try:
        from src.config import firebase
        print("✅ Config import successful")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    # Test 8: Full app creation
    try:
        from src.app import app
        print("✅ Full app creation successful")
    except Exception as e:
        print(f"❌ Full app creation failed: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False
    
    print("🎉 All imports successful!")
    return True

def test_minimal_app():
    """Test if the minimal app works as a fallback."""
    try:
        print("\n🔍 Testing minimal app...")
        from src.app_progressive import app
        print("✅ Minimal app creation successful")
        return True
    except Exception as e:
        print(f"❌ Minimal app creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting startup diagnostics...")
    
    # Test imports
    if test_imports():
        print("\n✅ All imports passed!")
    else:
        print("\n❌ Import test failed!")
    
    # Test minimal app as fallback
    test_minimal_app()
    
    print("\n🔍 Startup diagnostics complete!") 