#!/usr/bin/env python3
"""
Test script to check router import issues
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_router_imports():
    """Test importing routers to identify issues"""
    
    print("🧪 Testing Router Imports")
    print("=" * 50)
    
    routers_to_test = [
        "outfit",
        "outfits", 
        "image_processing",
        "image_analysis",
        "weather",
        "style_analysis",
        "wardrobe_analysis",
        "forgotten_gems",
        "wardrobe",
        "analytics",
        "analytics_dashboard",
        "auth",
        "monitoring",
        "security",
        "performance",
        "feedback",
        "public_diagnostics",
        "validation_rules",
        "item_analytics",
        "outfit_history",
    ]
    
    for router_name in routers_to_test:
        try:
            print(f"\nTesting {router_name} router...")
            
            # Try to import the module
            module = __import__(f"routes.{router_name}", fromlist=["router"])
            router = getattr(module, "router")
            
            print(f"✅ {router_name} router imported successfully")
            print(f"   Routes: {[route.path for route in router.routes]}")
            
        except Exception as e:
            print(f"❌ {router_name} router failed: {e}")
            print(f"   Error type: {type(e).__name__}")
    
    print("\n" + "=" * 50)
    print("🏁 Router import testing complete!")

if __name__ == "__main__":
    test_router_imports() 