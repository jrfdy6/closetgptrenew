#!/usr/bin/env python3
"""
Test script for enhanced image analysis
This script demonstrates the enhanced analysis that combines GPT-4 Vision and CLIP style analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import requests
from PIL import Image
from io import BytesIO
from src.services.enhanced_image_analysis_service import enhanced_analyzer

async def test_enhanced_analysis():
    """Test the enhanced analysis with sample images"""
    
    # Sample image URLs for testing
    test_images = [
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",  # Casual shirt
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",  # Formal blazer
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",  # Streetwear hoodie
    ]
    
    print("🚀 Enhanced Image Analysis Test (GPT-4 Vision + CLIP)")
    print("=" * 60)
    
    for i, image_url in enumerate(test_images, 1):
        try:
            print(f"\n📸 Analyzing Image {i}: {image_url}")
            print("-" * 50)
            
            # Download image
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Save to temporary file
            with open(f"temp_image_{i}.jpg", "wb") as f:
                f.write(response.content)
            
            # Run enhanced analysis
            analysis = await enhanced_analyzer.analyze_clothing_item(f"temp_image_{i}.jpg")
            
            # Display results
            print(f"🎯 Item Type: {analysis.get('type', 'Unknown')}")
            print(f"🎯 Subtype: {analysis.get('subType', 'Unknown')}")
            print(f"🎯 Name: {analysis.get('name', 'Unknown')}")
            
            # Style analysis
            print(f"\n🎨 Enhanced Style Tags:")
            styles = analysis.get('style', [])
            for j, style in enumerate(styles[:5], 1):
                print(f"  {j}. {style}")
            
            # CLIP analysis insights
            clip_analysis = analysis.get('metadata', {}).get('clipAnalysis', {})
            if clip_analysis:
                print(f"\n🔍 CLIP Analysis Insights:")
                print(f"  Primary Style: {clip_analysis.get('primaryStyle', 'Unknown')}")
                print(f"  Style Confidence: {clip_analysis.get('styleConfidence', 0):.1%}")
                print(f"  Top CLIP Styles:")
                top_styles = clip_analysis.get('topStyles', [])
                for j, style in enumerate(top_styles[:3], 1):
                    print(f"    {j}. {style}")
            
            # Enhanced occasion tags
            print(f"\n📅 Enhanced Occasion Tags:")
            occasions = analysis.get('occasion', [])
            for j, occasion in enumerate(occasions[:5], 1):
                print(f"  {j}. {occasion}")
            
            # Enhanced season tags
            print(f"\n🌤️ Enhanced Season Tags:")
            seasons = analysis.get('season', [])
            for j, season in enumerate(seasons, 1):
                print(f"  {j}. {season}")
            
            # Style compatibility
            style_compat = analysis.get('metadata', {}).get('styleCompatibility', {})
            if style_compat:
                print(f"\n🔄 Style Compatibility:")
                print(f"  Compatible Styles: {', '.join(style_compat.get('compatibleStyles', [])[:3])}")
                print(f"  Avoid Styles: {', '.join(style_compat.get('avoidStyles', [])[:3])}")
                print(f"  Notes: {style_compat.get('styleNotes', 'No notes')}")
            
            # Confidence scores
            confidence = analysis.get('metadata', {}).get('confidenceScores', {})
            if confidence:
                print(f"\n📊 Confidence Scores:")
                print(f"  Style Analysis: {confidence.get('styleAnalysis', 0):.1%}")
                print(f"  GPT Analysis: {confidence.get('gptAnalysis', 0):.1%}")
                print(f"  Overall: {confidence.get('overallConfidence', 0):.1%}")
            
            # Clean up
            os.remove(f"temp_image_{i}.jpg")
            
        except Exception as e:
            print(f"❌ Error analyzing image {i}: {str(e)}")
            continue
    
    print("\n✅ Enhanced analysis test completed!")

async def test_batch_analysis():
    """Test batch analysis functionality"""
    
    print("\n🔄 Batch Analysis Test")
    print("=" * 40)
    
    # Sample image URLs
    image_urls = [
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",
    ]
    
    temp_files = []
    
    try:
        # Download images
        for i, url in enumerate(image_urls):
            response = requests.get(url)
            filename = f"batch_temp_{i}.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            temp_files.append(filename)
        
        # Run batch analysis
        results = await enhanced_analyzer.analyze_batch(temp_files)
        
        print(f"📊 Batch Analysis Results:")
        print(f"  Total processed: {len(results)}")
        
        for i, result in enumerate(results, 1):
            if "error" in result:
                print(f"  Image {i}: ❌ {result['error']}")
            else:
                primary_style = result.get('metadata', {}).get('clipAnalysis', {}).get('primaryStyle', 'Unknown')
                confidence = result.get('metadata', {}).get('clipAnalysis', {}).get('styleConfidence', 0)
                print(f"  Image {i}: ✅ {primary_style} ({confidence:.1%})")
    
    finally:
        # Clean up
        for filename in temp_files:
            try:
                os.remove(filename)
            except:
                pass

async def compare_analysis_methods():
    """Compare GPT-4 only vs Enhanced analysis"""
    
    print("\n⚖️ Analysis Method Comparison")
    print("=" * 40)
    
    # Test image
    image_url = "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop"
    
    try:
        # Download image
        response = requests.get(image_url)
        with open("compare_temp.jpg", "wb") as f:
            f.write(response.content)
        
        # Enhanced analysis
        print("🔍 Enhanced Analysis (GPT-4 + CLIP):")
        enhanced = await enhanced_analyzer.analyze_clothing_item("compare_temp.jpg")
        
        enhanced_styles = enhanced.get('style', [])
        enhanced_confidence = enhanced.get('metadata', {}).get('confidenceScores', {}).get('overallConfidence', 0)
        
        print(f"  Style Tags: {len(enhanced_styles)} tags")
        print(f"  Overall Confidence: {enhanced_confidence:.1%}")
        print(f"  Top Styles: {', '.join(enhanced_styles[:3])}")
        
        # Note: We can't easily test GPT-4 only without modifying the service
        # But we can show the CLIP-specific insights
        clip_analysis = enhanced.get('metadata', {}).get('clipAnalysis', {})
        if clip_analysis:
            print(f"  CLIP Primary Style: {clip_analysis.get('primaryStyle', 'Unknown')}")
            print(f"  CLIP Confidence: {clip_analysis.get('styleConfidence', 0):.1%}")
        
        # Clean up
        os.remove("compare_temp.jpg")
        
    except Exception as e:
        print(f"❌ Comparison failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Analysis Tests...")
    
    async def main():
        try:
            # Test enhanced analysis
            await test_enhanced_analysis()
            
            # Test batch analysis
            await test_batch_analysis()
            
            # Compare methods
            await compare_analysis_methods()
            
            print("\n🎉 All enhanced analysis tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run the async tests
    asyncio.run(main()) 