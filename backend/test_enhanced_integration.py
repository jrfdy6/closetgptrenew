#!/usr/bin/env python3
"""
Test script to verify enhanced analysis integration
"""

import asyncio
import json
import tempfile
import os
from PIL import Image
import numpy as np

# Import the enhanced services
from src.services.enhanced_image_analysis_service import enhanced_analyzer
from src.services.outfit_service import OutfitService
from src.types.wardrobe import ClothingItem
from src.types.weather import WeatherData
from src.types.profile import UserProfile

def create_test_image():
    """Create a simple test image"""
    # Create a 224x224 RGB image
    img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
        img.save(f.name, 'JPEG')
        return f.name

async def test_enhanced_analysis():
    """Test the enhanced analysis service"""
    print("🧪 Testing Enhanced Analysis Integration")
    print("=" * 50)
    
    # Create test image
    test_image_path = create_test_image()
    
    try:
        print("📸 Testing enhanced image analysis...")
        
        # Run enhanced analysis
        analysis = await enhanced_analyzer.analyze_clothing_item(test_image_path)
        
        print("✅ Enhanced analysis completed!")
        print(f"📊 Analysis results:")
        print(f"  - Type: {analysis.get('type', 'N/A')}")
        print(f"  - Style tags: {len(analysis.get('style', []))} tags")
        print(f"  - CLIP analysis: {analysis.get('metadata', {}).get('clipAnalysis') is not None}")
        print(f"  - Style compatibility: {analysis.get('metadata', {}).get('styleCompatibility') is not None}")
        print(f"  - Confidence scores: {analysis.get('metadata', {}).get('confidenceScores') is not None}")
        
        return analysis
        
    finally:
        # Clean up test image
        try:
            os.unlink(test_image_path)
        except:
            pass

async def test_outfit_generation_with_enhanced_data():
    """Test outfit generation using enhanced analysis data"""
    print("\n👗 Testing Outfit Generation with Enhanced Data")
    print("=" * 50)
    
    # Create test wardrobe items with enhanced analysis data
    test_wardrobe = [
        ClothingItem(
            id="test_item_1",
            name="Test Shirt",
            type="shirt",
            color="blue",
            style=["Casual", "Minimalist"],
            occasion=["Casual", "Daily"],
            dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
            imageUrl="test_url_1",
            metadata={
                "clipAnalysis": {
                    "primaryStyle": "Minimalist",
                    "styleConfidence": 0.75,
                    "topStyles": ["Minimalist", "Casual", "Classic"],
                    "analysisMethod": "CLIP + GPT-4 Vision"
                },
                "styleCompatibility": {
                    "primaryStyle": "Minimalist",
                    "compatibleStyles": ["Casual", "Classic", "Business Casual"],
                    "avoidStyles": ["Grunge", "Avant-Garde"],
                    "styleNotes": "Strong Minimalist aesthetic detected."
                },
                "confidenceScores": {
                    "styleAnalysis": 0.75,
                    "gptAnalysis": 0.85,
                    "overallConfidence": 0.8
                }
            }
        ),
        ClothingItem(
            id="test_item_2",
            name="Test Pants",
            type="pants",
            color="black",
            style=["Classic", "Business Casual"],
            occasion=["Business", "Casual"],
            dominantColors=[{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
            matchingColors=[{"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
            imageUrl="test_url_2",
            metadata={
                "clipAnalysis": {
                    "primaryStyle": "Classic",
                    "styleConfidence": 0.8,
                    "topStyles": ["Classic", "Business Casual", "Minimalist"],
                    "analysisMethod": "CLIP + GPT-4 Vision"
                },
                "styleCompatibility": {
                    "primaryStyle": "Classic",
                    "compatibleStyles": ["Minimalist", "Business Casual", "Preppy"],
                    "avoidStyles": ["Streetwear", "Grunge"],
                    "styleNotes": "Strong Classic aesthetic detected."
                },
                "confidenceScores": {
                    "styleAnalysis": 0.8,
                    "gptAnalysis": 0.9,
                    "overallConfidence": 0.85
                }
            }
        )
    ]
    
    # Create test user profile
    test_user_profile = UserProfile(
        id="test_user",
        name="Test User",
        email="test@example.com",
        preferences={
            "style": ["Minimalist", "Classic"],
            "colors": ["blue", "black", "white"],
            "occasions": ["Casual", "Business"]
        },
        measurements={
            "height": 175,
            "weight": 70,
            "bodyType": "average",
            "skinTone": "neutral"
        },
        stylePreferences=["Minimalist", "Classic"],
        bodyType="average",
        skinTone="neutral",
        createdAt=1234567890,
        updatedAt=1234567890
    )
    
    # Create test weather data
    test_weather = WeatherData(
        temperature=22,
        condition="sunny",
        location="test_location",
        humidity=50,
        wind_speed=5,
        precipitation=0
    )
    
    # Test outfit generation
    outfit_service = OutfitService()
    
    try:
        print("🎯 Generating outfit with enhanced data...")
        
        outfit = await outfit_service.generate_outfit(
            occasion="Casual",
            weather=test_weather,
            wardrobe=test_wardrobe,
            user_profile=test_user_profile,
            likedOutfits=[],
            trendingStyles=[],
            style="Minimalist"
        )
        
        print("✅ Outfit generation completed!")
        print(f"📊 Outfit results:")
        print(f"  - Name: {outfit.name}")
        print(f"  - Pieces: {len(outfit.pieces)} items")
        print(f"  - Style tags: {outfit.styleTags}")
        print(f"  - Enhanced analysis: {outfit.metadata.get('enhancedAnalysis', False)}")
        print(f"  - CLIP insights: {outfit.metadata.get('clipInsights') is not None}")
        print(f"  - Style compatibility: {outfit.metadata.get('styleCompatibility') is not None}")
        
        return outfit
        
    except Exception as e:
        print(f"❌ Outfit generation failed: {str(e)}")
        return None

async def test_batch_analysis():
    """Test batch analysis functionality"""
    print("\n📦 Testing Batch Analysis")
    print("=" * 50)
    
    # Create multiple test images
    test_image_paths = []
    for i in range(3):
        test_image_paths.append(create_test_image())
    
    try:
        print(f"📸 Running batch analysis on {len(test_image_paths)} images...")
        
        # Run batch analysis
        results = await enhanced_analyzer.analyze_batch(test_image_paths)
        
        print("✅ Batch analysis completed!")
        print(f"📊 Batch results:")
        print(f"  - Total images: {len(results)}")
        print(f"  - Successful: {len([r for r in results if 'error' not in r])}")
        print(f"  - Failed: {len([r for r in results if 'error' in r])}")
        
        # Show sample results
        for i, result in enumerate(results[:2]):
            if 'error' not in result:
                print(f"  - Image {i+1}: {result.get('type', 'N/A')} with {len(result.get('style', []))} style tags")
        
        return results
        
    finally:
        # Clean up test images
        for path in test_image_paths:
            try:
                os.unlink(path)
            except:
                pass

async def main():
    """Run all integration tests"""
    print("🚀 Enhanced Analysis Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Enhanced analysis
    analysis_result = await test_enhanced_analysis()
    
    # Test 2: Outfit generation with enhanced data
    outfit_result = await test_outfit_generation_with_enhanced_data()
    
    # Test 3: Batch analysis
    batch_result = await test_batch_analysis()
    
    # Summary
    print("\n📋 Integration Test Summary")
    print("=" * 60)
    print(f"✅ Enhanced Analysis: {'PASS' if analysis_result else 'FAIL'}")
    print(f"✅ Outfit Generation: {'PASS' if outfit_result else 'FAIL'}")
    print(f"✅ Batch Analysis: {'PASS' if batch_result else 'FAIL'}")
    
    if all([analysis_result, outfit_result, batch_result]):
        print("\n🎉 All integration tests passed! Enhanced analysis is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    asyncio.run(main()) 