#!/usr/bin/env python3
"""
Test script to verify that athletic occasions no longer include formal blazers
"""

import asyncio
import sys
import os

# Add the backend src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.outfit_validation_pipeline import validation_pipeline, ValidationContext

async def test_athletic_outfit_validation():
    """Test validation of an inappropriate athletic outfit with blazer"""
    
    print("🧪 Testing Athletic Outfit Validation Fix")
    print("=" * 50)
    
    # Recreate the inappropriate athletic outfit from the user's example
    inappropriate_athletic_outfit = {
        "items": [
            {
                "name": "A loose, short, textured, ribbed sweater by Abercrombie Fitch",
                "type": "sweater",
                "color": "Beige"
            },
            {
                "name": "A loose, solid, smooth casual shorts", 
                "type": "shorts",
                "color": "Brown"
            },
            {
                "name": "A solid, smooth shoes by Nautica",
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
    
    # Create validation context for athletic occasion
    validation_context = ValidationContext(
        occasion="Athletic",
        style="Bohemian", 
        mood="Playful",
        weather={"temperature": 72, "condition": "Clear"},
        user_profile={"id": "test-user"},
        temperature=72.0
    )
    
    print(f"🔍 Testing athletic outfit with {len(inappropriate_athletic_outfit['items'])} items:")
    for i, item in enumerate(inappropriate_athletic_outfit['items'], 1):
        print(f"   {i}. {item['name']} ({item['type']})")
    
    print(f"\n📋 Validation Context:")
    print(f"   Occasion: {validation_context.occasion}")
    print(f"   Style: {validation_context.style}")
    print(f"   Mood: {validation_context.mood}")
    print(f"   Temperature: {validation_context.temperature}°F")
    
    print(f"\n🔍 Running validation pipeline...")
    
    try:
        # Run the validation pipeline
        result = await validation_pipeline.validate_outfit(inappropriate_athletic_outfit, validation_context)
        
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
        
        # Check if the validation caught the inappropriate blazer
        if not result.valid:
            print(f"\n✅ SUCCESS: Validation correctly REJECTED the inappropriate athletic outfit!")
            print(f"   The outfit contained inappropriate formal items for an athletic occasion.")
            
            # Check if it caught the specific problematic blazer
            error_text = " ".join(result.errors).lower()
            if "blazer" in error_text or "jacket" in error_text:
                print(f"   ✅ Caught the inappropriate blazer/jacket!")
            if "formal" in error_text:
                print(f"   ✅ Caught formal items!")
                
        else:
            print(f"\n❌ FAILURE: Validation incorrectly APPROVED the inappropriate athletic outfit!")
            print(f"   This means the validation rules need further improvement.")
            
        return result.valid
        
    except Exception as e:
        print(f"❌ ERROR: Validation pipeline failed: {e}")
        return False

async def test_appropriate_athletic_outfit():
    """Test validation of an appropriate athletic outfit"""
    
    print(f"\n🧪 Testing Appropriate Athletic Outfit")
    print("=" * 50)
    
    # Create an appropriate athletic outfit
    appropriate_athletic_outfit = {
        "items": [
            {
                "name": "A loose, athletic tank top by Nike",
                "type": "shirt",
                "color": "Black"
            },
            {
                "name": "A loose, athletic shorts by Adidas", 
                "type": "shorts",
                "color": "Gray"
            },
            {
                "name": "A solid, athletic sneakers by Nike",
                "type": "shoes", 
                "color": "White"
            },
            {
                "name": "A loose, athletic hoodie by Under Armour",
                "type": "hoodie",
                "color": "Blue"
            }
        ]
    }
    
    # Create validation context for athletic occasion
    validation_context = ValidationContext(
        occasion="Athletic",
        style="Bohemian", 
        mood="Playful",
        weather={"temperature": 72, "condition": "Clear"},
        user_profile={"id": "test-user"},
        temperature=72.0
    )
    
    print(f"🔍 Testing appropriate athletic outfit with {len(appropriate_athletic_outfit['items'])} items:")
    for i, item in enumerate(appropriate_athletic_outfit['items'], 1):
        print(f"   {i}. {item['name']} ({item['type']})")
    
    print(f"\n🔍 Running validation pipeline...")
    
    try:
        # Run the validation pipeline
        result = await validation_pipeline.validate_outfit(appropriate_athletic_outfit, validation_context)
        
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
            print(f"\n✅ SUCCESS: Validation correctly APPROVED the appropriate athletic outfit!")
        else:
            print(f"\n❌ FAILURE: Validation incorrectly REJECTED the appropriate athletic outfit!")
            
        return result.valid
        
    except Exception as e:
        print(f"❌ ERROR: Validation pipeline failed: {e}")
        return False

async def main():
    """Run all validation tests"""
    print("🚀 Starting Athletic Outfit Validation Tests")
    print("=" * 60)
    
    # Test inappropriate athletic outfit
    inappropriate_result = await test_athletic_outfit_validation()
    
    # Test appropriate athletic outfit  
    appropriate_result = await test_appropriate_athletic_outfit()
    
    print(f"\n📋 FINAL TEST RESULTS:")
    print("=" * 60)
    print(f"   Inappropriate athletic outfit: {'❌ REJECTED' if not inappropriate_result else '✅ APPROVED (WRONG!)'}")
    print(f"   Appropriate athletic outfit: {'✅ APPROVED' if appropriate_result else '❌ REJECTED (WRONG!)'}")
    
    # Overall success
    success = (not inappropriate_result) and appropriate_result
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")
    
    if success:
        print(f"   The validation pipeline now correctly blocks blazers for athletic occasions!")
    else:
        print(f"   The validation pipeline needs further improvement.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
