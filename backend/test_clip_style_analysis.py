#!/usr/bin/env python3
"""
Test script for CLIP-based style analysis
This script demonstrates how to use the style analysis service to analyze clothing items
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from PIL import Image
import requests
from io import BytesIO
from src.services.style_analysis_service import style_analyzer

def test_style_analysis():
    """Test the style analysis with a sample image"""
    
    # Sample image URLs for testing (you can replace these with your own)
    test_images = [
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",  # Casual shirt
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",  # Formal blazer
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop",  # Streetwear hoodie
    ]
    
    print("🧥 CLIP Style Analysis Test")
    print("=" * 50)
    
    for i, image_url in enumerate(test_images, 1):
        try:
            print(f"\n📸 Analyzing Image {i}: {image_url}")
            print("-" * 40)
            
            # Download and load image
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get top 5 style matches
            top_styles = style_analyzer.get_top_styles(image, top_k=5)
            
            print("🎯 Top Style Matches:")
            for j, (style_name, confidence) in enumerate(top_styles, 1):
                confidence_percent = confidence * 100
                print(f"  {j}. {style_name}: {confidence_percent:.1f}%")
            
            # Get full breakdown
            breakdown = style_analyzer.get_style_breakdown(image)
            
            print(f"\n📊 Full Style Breakdown (showing top 10):")
            sorted_breakdown = dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))
            for j, (style_name, confidence) in enumerate(list(sorted_breakdown.items())[:10], 1):
                confidence_percent = confidence * 100
                print(f"  {j:2d}. {style_name:<20} {confidence_percent:5.1f}%")
            
        except Exception as e:
            print(f"❌ Error analyzing image {i}: {str(e)}")
            continue
    
    print("\n✅ Style analysis test completed!")

def test_specific_style():
    """Test confidence for a specific style"""
    
    print("\n🎯 Testing Specific Style Confidence")
    print("=" * 50)
    
    # Test image URL
    image_url = "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop"
    
    try:
        # Download and load image
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Test different styles
        test_styles = ["Casual Cool", "Business Casual", "Streetwear", "Minimalist", "Classic"]
        
        for style_name in test_styles:
            confidence = style_analyzer.get_style_confidence(image, style_name)
            confidence_percent = confidence * 100
            print(f"🎨 {style_name:<20}: {confidence_percent:5.1f}%")
            
    except Exception as e:
        print(f"❌ Error in specific style test: {str(e)}")

def list_supported_styles():
    """List all supported styles"""
    
    print("\n📋 Supported Style Types")
    print("=" * 50)
    
    supported_styles = list(style_analyzer.style_prompts.keys())
    
    for i, style_name in enumerate(supported_styles, 1):
        print(f"  {i:2d}. {style_name}")
    
    print(f"\nTotal: {len(supported_styles)} supported styles")

if __name__ == "__main__":
    print("🚀 Starting CLIP Style Analysis Tests...")
    
    try:
        # List supported styles
        list_supported_styles()
        
        # Test general style analysis
        test_style_analysis()
        
        # Test specific style confidence
        test_specific_style()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc() 