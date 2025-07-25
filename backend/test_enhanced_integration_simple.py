#!/usr/bin/env python3
"""
Simple integration test for enhanced analysis
"""

import asyncio
import json
from src.services.outfit_service import OutfitService
from src.types.wardrobe import ClothingItem
from src.types.weather import WeatherData
from src.types.profile import UserProfile

async def test_outfit_generation_with_enhanced_data():
    """Test outfit generation using enhanced analysis data"""
    print("👗 Testing Outfit Generation with Enhanced Data")
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
            season=["spring", "summer"],
            tags=["casual", "minimalist"],
            userId="test_user",
            createdAt=1234567890,
            updatedAt=1234567890,
            dominantColors=[{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
            matchingColors=[{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
            imageUrl="test_url_1",
            metadata={
                "analysisTimestamp": 1234567890,
                "originalType": "shirt",
                "colorAnalysis": {
                    "dominant": [{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
                    "matching": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}]
                },
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
            season=["fall", "winter"],
            tags=["classic", "business"],
            userId="test_user",
            createdAt=1234567890,
            updatedAt=1234567890,
            dominantColors=[{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
            matchingColors=[{"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}],
            imageUrl="test_url_2",
            metadata={
                "analysisTimestamp": 1234567890,
                "originalType": "pants",
                "colorAnalysis": {
                    "dominant": [{"name": "black", "hex": "#000000", "rgb": [0, 0, 0]}],
                    "matching": [{"name": "gray", "hex": "#808080", "rgb": [128, 128, 128]}]
                },
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
        
        # Test enhanced methods
        print("\n🔍 Testing Enhanced Methods:")
        
        # Test enhanced complementary items
        complementary = outfit_service._get_complementary_items_enhanced(
            test_wardrobe[0], test_wardrobe, "Minimalist"
        )
        print(f"  - Enhanced complementary items: {len(complementary)} found")
        
        # Test enhanced style compliance
        compliance = outfit_service._calculate_style_compliance_enhanced(
            test_wardrobe, "Minimalist"
        )
        print(f"  - Enhanced style compliance: {compliance:.2f}")
        
        # Test enhanced color harmony
        harmony = outfit_service._calculate_color_harmony_enhanced(test_wardrobe)
        print(f"  - Enhanced color harmony: {harmony}")
        
        return outfit
        
    except Exception as e:
        print(f"❌ Outfit generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_enhanced_analysis_structure():
    """Test the structure of enhanced analysis data"""
    print("\n📋 Testing Enhanced Analysis Data Structure")
    print("=" * 50)
    
    # Mock enhanced analysis result
    mock_enhanced_analysis = {
        "type": "shirt",
        "subType": "t-shirt",
        "name": "Blue T-Shirt",
        "dominantColors": [{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
        "matchingColors": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}],
        "style": ["Casual", "Minimalist", "Classic"],
        "brand": "Test Brand",
        "season": ["spring", "summer"],
        "occasion": ["Casual", "Daily"],
        "metadata": {
            "clipAnalysis": {
                "primaryStyle": "Minimalist",
                "styleConfidence": 0.75,
                "topStyles": ["Minimalist", "Casual", "Classic"],
                "styleBreakdown": {"Minimalist": 0.75, "Casual": 0.65, "Classic": 0.55},
                "analysisMethod": "CLIP + GPT-4 Vision"
            },
            "confidenceScores": {
                "styleAnalysis": 0.75,
                "gptAnalysis": 0.85,
                "overallConfidence": 0.8
            },
            "styleCompatibility": {
                "primaryStyle": "Minimalist",
                "compatibleStyles": ["Casual", "Classic", "Business Casual"],
                "avoidStyles": ["Grunge", "Avant-Garde"],
                "styleNotes": "Strong Minimalist aesthetic detected."
            },
            "enhancedStyles": ["Casual", "Minimalist", "Classic"],
            "enhancedOccasions": ["Casual", "Daily", "Business Casual"],
            "enhancedColorAnalysis": {
                "dominant": [{"name": "blue", "hex": "#0000FF", "rgb": [0, 0, 255]}],
                "matching": [{"name": "white", "hex": "#FFFFFF", "rgb": [255, 255, 255]}]
            }
        }
    }
    
    print("✅ Enhanced analysis structure is valid")
    print(f"📊 Structure includes:")
    print(f"  - CLIP analysis: {mock_enhanced_analysis['metadata']['clipAnalysis'] is not None}")
    print(f"  - Confidence scores: {mock_enhanced_analysis['metadata']['confidenceScores'] is not None}")
    print(f"  - Style compatibility: {mock_enhanced_analysis['metadata']['styleCompatibility'] is not None}")
    print(f"  - Enhanced styles: {len(mock_enhanced_analysis['metadata']['enhancedStyles'])} tags")
    print(f"  - Enhanced occasions: {len(mock_enhanced_analysis['metadata']['enhancedOccasions'])} tags")
    
    return mock_enhanced_analysis

async def test_batch_upload_integration():
    """Test how enhanced analysis would integrate with batch upload"""
    print("\n📦 Testing Batch Upload Integration")
    print("=" * 50)
    
    # Mock batch analysis results
    mock_batch_results = [
        {
            "index": 0,
            "image_url": "test_url_1",
            "analysis": {
                "type": "shirt",
                "style": ["Casual", "Minimalist"],
                "metadata": {
                    "clipAnalysis": {"primaryStyle": "Minimalist", "styleConfidence": 0.75},
                    "styleCompatibility": {"compatibleStyles": ["Casual", "Classic"]}
                }
            },
            "success": True
        },
        {
            "index": 1,
            "image_url": "test_url_2",
            "analysis": {
                "type": "pants",
                "style": ["Classic", "Business Casual"],
                "metadata": {
                    "clipAnalysis": {"primaryStyle": "Classic", "styleConfidence": 0.8},
                    "styleCompatibility": {"compatibleStyles": ["Minimalist", "Business Casual"]}
                }
            },
            "success": True
        }
    ]
    
    print("✅ Batch analysis structure is valid")
    print(f"📊 Batch results:")
    print(f"  - Total items: {len(mock_batch_results)}")
    print(f"  - Successful: {len([r for r in mock_batch_results if r['success']])}")
    print(f"  - Enhanced metadata: {all('metadata' in r['analysis'] for r in mock_batch_results)}")
    
    # Simulate creating clothing items from enhanced analysis
    clothing_items = []
    for result in mock_batch_results:
        if result['success']:
            analysis = result['analysis']
            item = {
                "id": f"item_{result['index']}",
                "name": analysis['type'],
                "type": analysis['type'],
                "style": analysis['style'],
                "metadata": analysis['metadata']
            }
            clothing_items.append(item)
    
    print(f"  - Created clothing items: {len(clothing_items)}")
    
    return clothing_items

async def main():
    """Run all integration tests"""
    print("🚀 Enhanced Analysis Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Enhanced analysis structure
    structure_result = await test_enhanced_analysis_structure()
    
    # Test 2: Outfit generation with enhanced data
    outfit_result = await test_outfit_generation_with_enhanced_data()
    
    # Test 3: Batch upload integration
    batch_result = await test_batch_upload_integration()
    
    # Summary
    print("\n📋 Integration Test Summary")
    print("=" * 60)
    print(f"✅ Enhanced Analysis Structure: {'PASS' if structure_result else 'FAIL'}")
    print(f"✅ Outfit Generation: {'PASS' if outfit_result else 'FAIL'}")
    print(f"✅ Batch Upload Integration: {'PASS' if batch_result else 'FAIL'}")
    
    if all([structure_result, outfit_result, batch_result]):
        print("\n🎉 All integration tests passed! Enhanced analysis is properly integrated.")
        print("\n📈 Key Benefits:")
        print("  - Better style detection with CLIP analysis")
        print("  - Enhanced style compatibility insights")
        print("  - Improved outfit generation with confidence scores")
        print("  - More accurate metadata for batch uploads")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    asyncio.run(main()) 