#!/usr/bin/env python3
"""
Test script to verify that the validation pipeline now catches inappropriate formal outfits
"""

import asyncio
import sys
import os

# Add the backend src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.outfit_validation_pipeline import validation_pipeline, ValidationContext

async def test_formal_outfit_validation():
    """Test validation of the inappropriate formal outfit from the user's example"""
    
    print("🧪 Testing Formal Outfit Validation Fix")
    print("=" * 50)
    
    # Recreate the inappropriate formal outfit from the user's example
    inappropriate_formal_outfit = {
        "items": [
            {
                "name": "A loose, short, solid, smooth t shirt by Zegna",
                "type": "shirt",
                "color": "White"
            },
            {
                "name": "Pants pleated trousers khaki by unknown", 
                "type": "pants",
                "color": "khaki"
            },
            {
                "name": "A solid, smooth shoes",
                "type": "shoes", 
                "color": "White"
            },
            {
                "name": "A slim, long, herringbone, smooth jacket by Savile Row",
                "type": "jacket",
                "color": "Gray"
            }
        ]
    }
    
    # Create validation context for formal occasion
    validation_context = ValidationContext(
        occasion="Formal",
        style="Classic", 
        mood="Bold",
        weather={"temperature": 72, "condition": "Clear"},
        user_profile={"id": "test-user"},
        temperature=72.0
    )
    
    print(f"🔍 Testing outfit with {len(inappropriate_formal_outfit['items'])} items:")
    for i, item in enumerate(inappropriate_formal_outfit['items'], 1):
        print(f"   {i}. {item['name']} ({item['type']})")
    
    print(f"\n📋 Validation Context:")
    print(f"   Occasion: {validation_context.occasion}")
    print(f"   Style: {validation_context.style}")
    print(f"   Mood: {validation_context.mood}")
    print(f"   Temperature: {validation_context.temperature}°F")
    
    print(f"\n🔍 Running validation pipeline...")
    
    try:
        # Run the validation pipeline
        result = await validation_pipeline.validate_outfit(inappropriate_formal_outfit, validation_context)
        
        print(f"\n📊 VALIDATION RESULTS:")
        print(f"   Valid: {result.valid}")
        print(f"   Severity: {result.severity}")
        
        if result.errors:
            print(f"\n❌ ERRORS ({len(result.errors)}):")
            for i, error in enumerate(result.errors, 1):
                print(f"   {i}. {error}")
        
        if result.warnings:
            print(f"\n⚠️ WARNINGS ({len(result.warnings)}):")
            for i, warning in enumerate(result.warnings, 1):
                print(f"   {i}. {warning}")
        
        if result.suggestions:
            print(f"\n💡 SUGGESTIONS ({len(result.suggestions)}):")
            for i, suggestion in enumerate(result.suggestions, 1):
                print(f"   {i}. {suggestion}")
        
        # Check if the validation caught the inappropriate items
        if not result.valid:
            print(f"\n✅ SUCCESS: Validation correctly REJECTED the inappropriate formal outfit!")
            print(f"   The outfit contained inappropriate items for a formal occasion.")
            
            # Check if it caught the specific problematic items
            error_text = " ".join(result.errors).lower()
            if "t shirt" in error_text or "t-shirt" in error_text:
                print(f"   ✅ Caught the inappropriate T-shirt!")
            if "shoes" in error_text and ("sneaker" in error_text or "generic" in error_text):
                print(f"   ✅ Caught the inappropriate shoes!")
                
        else:
            print(f"\n❌ FAILURE: Validation incorrectly APPROVED the inappropriate formal outfit!")
            print(f"   This means the validation rules need further improvement.")
            
        return result.valid
        
    except Exception as e:
        print(f"❌ ERROR: Validation pipeline failed: {e}")
        return False

async def test_appropriate_formal_outfit():
    """Test validation of an appropriate formal outfit"""
    
    print(f"\n🧪 Testing Appropriate Formal Outfit")
    print("=" * 50)
    
    # Create an appropriate formal outfit
    appropriate_formal_outfit = {
        "items": [
            {
                "name": "A slim, long, solid, smooth dress shirt by Brooks Brothers",
                "type": "shirt",
                "color": "White"
            },
            {
                "name": "A slim, solid, smooth dress pants by Hugo Boss", 
                "type": "pants",
                "color": "Navy"
            },
            {
                "name": "A solid, smooth oxford shoes by Allen Edmonds",
                "type": "shoes", 
                "color": "Black"
            },
            {
                "name": "A slim, long, herringbone, smooth blazer by Savile Row",
                "type": "jacket",
                "color": "Gray"
            }
        ]
    }
    
    # Create validation context for formal occasion
    validation_context = ValidationContext(
        occasion="Formal",
        style="Classic", 
        mood="Professional",
        weather={"temperature": 72, "condition": "Clear"},
        user_profile={"id": "test-user"},
        temperature=72.0
    )
    
    print(f"🔍 Testing appropriate outfit with {len(appropriate_formal_outfit['items'])} items:")
    for i, item in enumerate(appropriate_formal_outfit['items'], 1):
        print(f"   {i}. {item['name']} ({item['type']})")
    
    print(f"\n🔍 Running validation pipeline...")
    
    try:
        # Run the validation pipeline
        result = await validation_pipeline.validate_outfit(appropriate_formal_outfit, validation_context)
        
        print(f"\n📊 VALIDATION RESULTS:")
        print(f"   Valid: {result.valid}")
        print(f"   Severity: {result.severity}")
        
        if result.errors:
            print(f"\n❌ ERRORS ({len(result.errors)}):")
            for i, error in enumerate(result.errors, 1):
                print(f"   {i}. {error}")
        
        if result.warnings:
            print(f"\n⚠️ WARNINGS ({len(result.warnings)}):")
            for i, warning in enumerate(result.warnings, 1):
                print(f"   {i}. {warning}")
        
        if result.suggestions:
            print(f"\n💡 SUGGESTIONS ({len(result.suggestions)}):")
            for i, suggestion in enumerate(result.suggestions, 1):
                print(f"   {i}. {suggestion}")
        
        if result.valid:
            print(f"\n✅ SUCCESS: Validation correctly APPROVED the appropriate formal outfit!")
        else:
            print(f"\n❌ FAILURE: Validation incorrectly REJECTED the appropriate formal outfit!")
            
        return result.valid
        
    except Exception as e:
        print(f"❌ ERROR: Validation pipeline failed: {e}")
        return False

async def main():
    """Run all validation tests"""
    print("🚀 Starting Validation Pipeline Tests")
    print("=" * 60)
    
    # Test inappropriate formal outfit
    inappropriate_result = await test_formal_outfit_validation()
    
    # Test appropriate formal outfit  
    appropriate_result = await test_appropriate_formal_outfit()
    
    print(f"\n📋 FINAL TEST RESULTS:")
    print("=" * 60)
    print(f"   Inappropriate formal outfit: {'❌ REJECTED' if not inappropriate_result else '✅ APPROVED (WRONG!)'}")
    print(f"   Appropriate formal outfit: {'✅ APPROVED' if appropriate_result else '❌ REJECTED (WRONG!)'}")
    
    # Overall success
    success = (not inappropriate_result) and appropriate_result
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")
    
    if success:
        print(f"   The validation pipeline is now working correctly!")
        print(f"   It will reject inappropriate formal outfits and prevent them from reaching users.")
    else:
        print(f"   The validation pipeline needs further improvement.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
