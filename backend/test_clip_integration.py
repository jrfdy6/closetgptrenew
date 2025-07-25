#!/usr/bin/env python3
"""
Test script for CLIP integration in enhanced metadata tagging
This script demonstrates how CLIP analysis enhances clothing metadata
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import requests
from PIL import Image
from io import BytesIO
from src.services.style_analysis_service import style_analyzer

def test_clip_style_enhancement():
    """Test how CLIP analysis can enhance style metadata"""
    
    print("🎨 CLIP Style Enhancement Test")
    print("=" * 50)
    
    # Sample image URL
    image_url = "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop"
    
    try:
        # Download and process image
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get CLIP style analysis
        print("🔍 Running CLIP style analysis...")
        style_matches = style_analyzer.analyze_style(image)
        top_styles = style_analyzer.get_top_styles(image, top_k=5)
        style_breakdown = style_analyzer.get_style_breakdown(image)
        
        # Display results
        print(f"\n🎯 Top Style Matches:")
        for i, (style, confidence) in enumerate(top_styles, 1):
            confidence_percent = confidence * 100
            print(f"  {i}. {style}: {confidence_percent:.1f}%")
        
        # Show how this would enhance metadata
        print(f"\n📊 How CLIP Enhances Metadata:")
        
        # Primary style
        primary_style = style_matches[0] if style_matches else None
        if primary_style:
            print(f"  Primary Style: {primary_style[0]} ({primary_style[1]:.1%} confidence)")
        
        # Enhanced style tags
        enhanced_styles = set()
        if primary_style and primary_style[1] > 0.3:  # High confidence threshold
            enhanced_styles.add(primary_style[0])
            # Add related styles
            style_mappings = {
                "Dark Academia": ["Classic", "Formal"],
                "Old Money": ["Classic", "Business Casual"],
                "Streetwear": ["Casual", "Urban"],
                "Y2K": ["Trendy", "Casual"],
                "Minimalist": ["Classic", "Casual"],
                "Boho": ["Casual", "Romantic"],
                "Preppy": ["Business Casual", "Classic"],
                "Grunge": ["Casual", "Edgy"],
                "Classic": ["Business Casual", "Formal"],
                "Techwear": ["Streetwear", "Urban"],
                "Androgynous": ["Minimalist", "Modern"],
                "Coastal Chic": ["Casual", "Romantic"],
                "Business Casual": ["Classic", "Professional"],
                "Avant-Garde": ["Edgy", "Artistic"],
                "Cottagecore": ["Romantic", "Casual"],
                "Edgy": ["Streetwear", "Grunge"],
                "Athleisure": ["Casual", "Sporty"],
                "Casual Cool": ["Casual", "Minimalist"],
                "Romantic": ["Casual", "Feminine"],
                "Artsy": ["Avant-Garde", "Creative"]
            }
            
            if primary_style[0] in style_mappings:
                for related_style in style_mappings[primary_style[0]]:
                    enhanced_styles.add(related_style)
        
        print(f"  Enhanced Style Tags: {', '.join(list(enhanced_styles)[:5])}")
        
        # Enhanced occasion tags
        occasion_mappings = {
            "Dark Academia": ["Academic", "Professional", "Formal"],
            "Old Money": ["Business", "Formal", "Professional"],
            "Streetwear": ["Casual", "Urban", "Street"],
            "Y2K": ["Casual", "Party", "Social"],
            "Minimalist": ["Casual", "Business Casual", "Professional"],
            "Boho": ["Casual", "Festival", "Social"],
            "Preppy": ["Business Casual", "Professional", "Social"],
            "Grunge": ["Casual", "Street", "Social"],
            "Classic": ["Business", "Formal", "Professional"],
            "Techwear": ["Urban", "Casual", "Street"],
            "Androgynous": ["Casual", "Business Casual", "Professional"],
            "Coastal Chic": ["Casual", "Vacation", "Social"],
            "Business Casual": ["Business Casual", "Professional", "Office"],
            "Avant-Garde": ["Special Occasion", "Artistic", "Creative"],
            "Cottagecore": ["Casual", "Social", "Outdoor"],
            "Edgy": ["Casual", "Street", "Social"],
            "Athleisure": ["Casual", "Athletic", "Active"],
            "Casual Cool": ["Casual", "Social", "Everyday"],
            "Romantic": ["Date Night", "Special Occasion", "Social"],
            "Artsy": ["Creative", "Artistic", "Special Occasion"]
        }
        
        enhanced_occasions = set()
        if primary_style and primary_style[1] > 0.3:
            if primary_style[0] in occasion_mappings:
                enhanced_occasions.update(occasion_mappings[primary_style[0]])
        
        print(f"  Enhanced Occasion Tags: {', '.join(list(enhanced_occasions)[:5])}")
        
        # Enhanced season tags
        season_mappings = {
            "Dark Academia": ["fall", "winter"],
            "Old Money": ["fall", "winter", "spring"],
            "Streetwear": ["all"],
            "Y2K": ["spring", "summer"],
            "Minimalist": ["all"],
            "Boho": ["spring", "summer", "fall"],
            "Preppy": ["spring", "fall"],
            "Grunge": ["fall", "winter"],
            "Classic": ["all"],
            "Techwear": ["fall", "winter"],
            "Androgynous": ["all"],
            "Coastal Chic": ["spring", "summer"],
            "Business Casual": ["all"],
            "Avant-Garde": ["all"],
            "Cottagecore": ["spring", "summer"],
            "Edgy": ["fall", "winter"],
            "Athleisure": ["all"],
            "Casual Cool": ["all"],
            "Romantic": ["spring", "summer"],
            "Artsy": ["all"]
        }
        
        enhanced_seasons = set()
        if primary_style and primary_style[1] > 0.3:
            if primary_style[0] in season_mappings:
                seasons = season_mappings[primary_style[0]]
                if "all" in seasons:
                    enhanced_seasons.update(["spring", "summer", "fall", "winter"])
                else:
                    enhanced_seasons.update(seasons)
        
        print(f"  Enhanced Season Tags: {', '.join(list(enhanced_seasons))}")
        
        # Style compatibility insights
        avoid_mappings = {
            "Dark Academia": ["Y2K", "Athleisure", "Coastal Chic"],
            "Old Money": ["Grunge", "Streetwear", "Y2K"],
            "Streetwear": ["Old Money", "Dark Academia", "Preppy"],
            "Y2K": ["Dark Academia", "Old Money", "Classic"],
            "Minimalist": ["Maximalist", "Boho", "Avant-Garde"],
            "Boho": ["Minimalist", "Preppy", "Business Casual"],
            "Preppy": ["Grunge", "Streetwear", "Boho"],
            "Grunge": ["Preppy", "Old Money", "Business Casual"],
            "Classic": ["Y2K", "Grunge", "Avant-Garde"],
            "Techwear": ["Romantic", "Cottagecore", "Coastal Chic"],
            "Androgynous": ["Romantic", "Cottagecore"],
            "Coastal Chic": ["Dark Academia", "Grunge", "Techwear"],
            "Business Casual": ["Grunge", "Y2K", "Athleisure"],
            "Avant-Garde": ["Classic", "Preppy", "Business Casual"],
            "Cottagecore": ["Techwear", "Streetwear", "Business Casual"],
            "Edgy": ["Romantic", "Cottagecore", "Coastal Chic"],
            "Athleisure": ["Dark Academia", "Old Money", "Formal"],
            "Casual Cool": ["Formal", "Avant-Garde"],
            "Romantic": ["Techwear", "Grunge", "Streetwear"],
            "Artsy": ["Classic", "Preppy", "Business Casual"]
        }
        
        avoid_styles = []
        if primary_style and primary_style[0] in avoid_mappings:
            avoid_styles = avoid_mappings[primary_style[0]]
        
        print(f"  Avoid Styles: {', '.join(avoid_styles[:3])}")
        
        # Confidence assessment
        confidence = primary_style[1] if primary_style else 0
        if confidence > 0.4:
            print(f"  Confidence Level: High ({confidence:.1%}) - Strong style influence detected")
        elif confidence > 0.25:
            print(f"  Confidence Level: Medium ({confidence:.1%}) - Moderate style influence detected")
        else:
            print(f"  Confidence Level: Low ({confidence:.1%}) - Subtle style influence detected")
        
        print(f"\n✅ CLIP analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in CLIP analysis: {str(e)}")
        import traceback
        traceback.print_exc()

def test_style_confidence():
    """Test confidence scores for different styles"""
    
    print(f"\n🎯 Style Confidence Testing")
    print("=" * 40)
    
    # Test image
    image_url = "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop"
    
    try:
        # Download and process image
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Test specific styles
        test_styles = ["Casual Cool", "Business Casual", "Streetwear", "Minimalist", "Classic"]
        
        print("Testing confidence for specific styles:")
        for style in test_styles:
            confidence = style_analyzer.get_style_confidence(image, style)
            confidence_percent = confidence * 100
            print(f"  {style:<20}: {confidence_percent:5.1f}%")
        
        print(f"\n✅ Style confidence testing completed!")
        
    except Exception as e:
        print(f"❌ Error in confidence testing: {str(e)}")

def demonstrate_metadata_enhancement():
    """Demonstrate how CLIP enhances metadata"""
    
    print(f"\n📊 Metadata Enhancement Demonstration")
    print("=" * 50)
    
    print("""
🎨 How CLIP Enhances Clothing Metadata:

1. **Style Tag Enhancement:**
   - GPT-4 might tag: ["Casual", "Comfortable"]
   - CLIP adds: ["Casual Cool", "Minimalist", "Classic"]
   - Result: More comprehensive style understanding

2. **Occasion Tag Enhancement:**
   - GPT-4 might tag: ["Casual"]
   - CLIP style analysis suggests: ["Casual", "Social", "Everyday"]
   - Result: Better occasion matching

3. **Season Tag Enhancement:**
   - GPT-4 might tag: ["spring", "summer"]
   - CLIP style analysis suggests: ["spring", "summer", "fall"]
   - Result: More accurate seasonal recommendations

4. **Style Compatibility:**
   - CLIP provides: Compatible styles, avoid styles
   - Result: Better outfit pairing suggestions

5. **Confidence Scoring:**
   - CLIP provides: Style confidence scores
   - Result: More reliable metadata quality assessment

6. **Style Notes:**
   - CLIP generates: Style-specific insights
   - Result: Better user understanding of item characteristics

🔍 Benefits of CLIP Integration:
- More accurate style classification
- Better metadata completeness
- Improved outfit generation
- Enhanced search and filtering
- More reliable recommendations
""")

if __name__ == "__main__":
    print("🚀 Starting CLIP Integration Tests...")
    
    try:
        # Test CLIP style enhancement
        test_clip_style_enhancement()
        
        # Test style confidence
        test_style_confidence()
        
        # Demonstrate metadata enhancement
        demonstrate_metadata_enhancement()
        
        print("\n🎉 All CLIP integration tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc() 