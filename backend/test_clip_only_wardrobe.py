#!/usr/bin/env python3
"""
Test script to demonstrate CLIP-only wardrobe analysis
This script shows how CLIP analysis can enhance wardrobe metadata
without requiring OpenAI API keys.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List
from src.services.style_analysis_service import style_analyzer

# Sample wardrobe data for testing
SAMPLE_WARDROBE = [
    {
        "id": "sample_1",
        "name": "Blue Denim Jacket",
        "type": "jacket",
        "subType": "denim_jacket",
        "color": "blue",
        "style": ["casual", "streetwear"],
        "occasion": ["casual", "daily"],
        "season": ["spring", "fall"],
        "tags": ["denim", "jacket", "casual"],
        "imageUrl": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop"
    },
    {
        "id": "sample_2", 
        "name": "White Business Shirt",
        "type": "shirt",
        "subType": "dress_shirt",
        "color": "white",
        "style": ["business_casual", "classic"],
        "occasion": ["business", "professional"],
        "season": ["spring", "summer", "fall", "winter"],
        "tags": ["white", "shirt", "business"],
        "imageUrl": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop"
    },
    {
        "id": "sample_3",
        "name": "Black Hoodie",
        "type": "sweater",
        "subType": "hoodie",
        "color": "black",
        "style": ["casual", "streetwear"],
        "occasion": ["casual", "daily"],
        "season": ["fall", "winter"],
        "tags": ["black", "hoodie", "casual"],
        "imageUrl": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop"
    }
]

class CLIPWardrobeTester:
    def __init__(self):
        """Initialize the CLIP wardrobe tester"""
        self.results = []
    
    async def download_image(self, image_url: str, item_id: str) -> str:
        """Download image and save to temporary file"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_path = f"temp_clip_{item_id}.jpg"
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            print(f"❌ Failed to download image for item {item_id}: {str(e)}")
            return None
    
    async def test_item_clip_analysis(self, item: Dict) -> Dict:
        """Test CLIP analysis on a single item"""
        try:
            item_id = item.get('id', 'unknown')
            image_url = item.get('imageUrl')
            
            print(f"🔍 Testing item: {item.get('name', 'Unknown')} ({item_id})")
            
            # Download image
            temp_image_path = await self.download_image(image_url, item_id)
            if not temp_image_path:
                return {
                    'item_id': item_id,
                    'name': item.get('name', 'Unknown'),
                    'error': 'Failed to download image'
                }
            
            try:
                from PIL import Image
                
                # Load image for CLIP analysis
                with Image.open(temp_image_path) as image:
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Get current metadata
                    current_metadata = {
                        'style': item.get('style', []),
                        'occasion': item.get('occasion', []),
                        'season': item.get('season', []),
                        'tags': item.get('tags', []),
                        'type': item.get('type', 'unknown'),
                        'subType': item.get('subType'),
                        'color': item.get('color', 'unknown')
                    }
                    
                    # Run CLIP analysis
                    print(f"  🎨 Running CLIP style analysis...")
                    style_matches = style_analyzer.analyze_style(image)
                    top_styles = style_analyzer.get_top_styles(image, top_k=5)
                    style_breakdown = style_analyzer.get_style_breakdown(image)
                    
                    # Generate enhanced metadata using CLIP insights
                    enhanced_metadata = self._enhance_metadata_with_clip(
                        current_metadata, style_matches, top_styles, style_breakdown
                    )
                    
                    # Compare results
                    comparison = self._compare_metadata(current_metadata, enhanced_metadata)
                    
                    return {
                        'item_id': item_id,
                        'name': item.get('name', 'Unknown'),
                        'current_metadata': current_metadata,
                        'enhanced_metadata': enhanced_metadata,
                        'clip_analysis': {
                            'style_matches': style_matches,
                            'top_styles': top_styles,
                            'style_breakdown': style_breakdown
                        },
                        'comparison': comparison,
                        'success': True
                    }
                
            finally:
                # Clean up temporary file
                try:
                    os.remove(temp_image_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error testing item {item_id}: {str(e)}")
            return {
                'item_id': item.get('id', 'unknown'),
                'name': item.get('name', 'Unknown'),
                'error': str(e)
            }
    
    def _enhance_metadata_with_clip(self, current: Dict, style_matches: List, top_styles: List, style_breakdown: Dict) -> Dict:
        """Enhance metadata using CLIP analysis insights"""
        enhanced = current.copy()
        
        # Get primary style and confidence
        primary_style = style_matches[0] if style_matches else None
        style_confidence = primary_style[1] if primary_style else 0.0
        
        # Enhanced style tags
        enhanced_styles = set(current.get('style', []))
        if style_confidence > 0.3:  # Threshold for considering CLIP styles
            for style, _ in top_styles[:3]:  # Top 3 CLIP styles
                enhanced_styles.add(style)
        
        # Style mappings for better compatibility
        style_mappings = {
            "Dark Academia": ["Dark Academia", "Classic", "Formal"],
            "Old Money": ["Old Money", "Classic", "Business Casual"],
            "Streetwear": ["Streetwear", "Casual", "Urban"],
            "Y2K": ["Y2K", "Trendy", "Casual"],
            "Minimalist": ["Minimalist", "Classic", "Casual"],
            "Boho": ["Boho", "Casual", "Romantic"],
            "Preppy": ["Preppy", "Business Casual", "Classic"],
            "Grunge": ["Grunge", "Casual", "Edgy"],
            "Classic": ["Classic", "Business Casual", "Formal"],
            "Techwear": ["Techwear", "Streetwear", "Urban"],
            "Androgynous": ["Androgynous", "Minimalist", "Modern"],
            "Coastal Chic": ["Coastal Chic", "Casual", "Romantic"],
            "Business Casual": ["Business Casual", "Classic", "Professional"],
            "Avant-Garde": ["Avant-Garde", "Edgy", "Artistic"],
            "Cottagecore": ["Cottagecore", "Romantic", "Casual"],
            "Edgy": ["Edgy", "Streetwear", "Grunge"],
            "Athleisure": ["Athleisure", "Casual", "Sporty"],
            "Casual Cool": ["Casual Cool", "Casual", "Minimalist"],
            "Romantic": ["Romantic", "Casual", "Feminine"],
            "Artsy": ["Artsy", "Avant-Garde", "Creative"]
        }
        
        # Add mapped styles for high-confidence CLIP styles
        for style, _ in top_styles[:2]:  # Top 2 for mapping
            if style in style_mappings:
                for mapped_style in style_mappings[style]:
                    enhanced_styles.add(mapped_style)
        
        enhanced['style'] = list(enhanced_styles)
        
        # Enhanced occasion tags
        enhanced_occasions = set(current.get('occasion', []))
        style_occasion_mappings = {
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
        
        if style_confidence > 0.3:
            for style, _ in top_styles[:2]:
                if style in style_occasion_mappings:
                    for occasion in style_occasion_mappings[style]:
                        enhanced_occasions.add(occasion)
        
        enhanced['occasion'] = list(enhanced_occasions)
        
        # Enhanced season tags
        enhanced_seasons = set(current.get('season', []))
        style_season_mappings = {
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
        
        if style_confidence > 0.3:
            for style, _ in top_styles[:2]:
                if style in style_season_mappings:
                    seasons = style_season_mappings[style]
                    if "all" in seasons:
                        enhanced_seasons.update(["spring", "summer", "fall", "winter"])
                    else:
                        enhanced_seasons.update(seasons)
        
        enhanced['season'] = list(enhanced_seasons)
        
        # Add CLIP analysis metadata
        enhanced['metadata'] = {
            'clipAnalysis': {
                'primaryStyle': primary_style[0] if primary_style else None,
                'styleConfidence': style_confidence,
                'topStyles': [style for style, _ in top_styles],
                'styleBreakdown': style_breakdown,
                'analysisMethod': 'CLIP Style Analysis'
            },
            'confidenceScores': {
                'styleAnalysis': style_confidence,
                'overallConfidence': style_confidence
            },
            'styleCompatibility': {
                'primaryStyle': primary_style[0] if primary_style else None,
                'compatibleStyles': [style for style, _ in top_styles[:3]],
                'avoidStyles': self._get_avoid_styles([style for style, _ in top_styles]),
                'styleNotes': self._generate_style_notes(primary_style[0] if primary_style else None, style_confidence)
            }
        }
        
        return enhanced
    
    def _get_avoid_styles(self, top_styles: List[str]) -> List[str]:
        """Get styles to avoid based on the primary style"""
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
        
        if top_styles and top_styles[0] in avoid_mappings:
            return avoid_mappings[top_styles[0]]
        return []
    
    def _generate_style_notes(self, primary_style: str, confidence: float) -> str:
        """Generate style notes based on the primary style and confidence"""
        if not primary_style:
            return "Style analysis inconclusive"
        
        if confidence > 0.4:
            return f"Strong {primary_style} aesthetic detected. This item clearly embodies {primary_style} characteristics."
        elif confidence > 0.25:
            return f"Moderate {primary_style} influence detected. This item has some {primary_style} elements."
        else:
            return f"Subtle {primary_style} influence detected. This item may work with {primary_style} styling."
    
    def _compare_metadata(self, current: Dict, enhanced: Dict) -> Dict:
        """Compare current vs enhanced metadata"""
        comparison = {
            'style_tags': {
                'current_count': len(current.get('style', [])),
                'enhanced_count': len(enhanced.get('style', [])),
                'improvement': len(enhanced.get('style', [])) - len(current.get('style', [])),
                'current': current.get('style', []),
                'enhanced': enhanced.get('style', [])
            },
            'occasion_tags': {
                'current_count': len(current.get('occasion', [])),
                'enhanced_count': len(enhanced.get('occasion', [])),
                'improvement': len(enhanced.get('occasion', [])) - len(current.get('occasion', [])),
                'current': current.get('occasion', []),
                'enhanced': enhanced.get('occasion', [])
            },
            'season_tags': {
                'current_count': len(current.get('season', [])),
                'enhanced_count': len(enhanced.get('season', [])),
                'improvement': len(enhanced.get('season', [])) - len(current.get('season', [])),
                'current': current.get('season', []),
                'enhanced': enhanced.get('season', [])
            },
            'metadata_quality': {
                'enhanced_confidence': enhanced.get('metadata', {}).get('confidenceScores', {}).get('overallConfidence', 0),
                'clip_analysis': enhanced.get('metadata', {}).get('clipAnalysis', {}),
                'style_compatibility': enhanced.get('metadata', {}).get('styleCompatibility', {}),
                'additional_insights': bool(enhanced.get('metadata', {}).get('clipAnalysis'))
            }
        }
        
        return comparison
    
    async def test_wardrobe_clip_analysis(self, items: List[Dict] = None) -> Dict:
        """Test CLIP analysis on wardrobe items"""
        if items is None:
            items = SAMPLE_WARDROBE
        
        print("🚀 Testing CLIP-Enhanced Wardrobe Analysis")
        print("=" * 50)
        print(f"📦 Testing {len(items)} sample items")
        
        results = []
        successful_tests = 0
        failed_tests = 0
        
        for i, item in enumerate(items, 1):
            print(f"\n📸 Testing item {i}/{len(items)}")
            result = await self.test_item_clip_analysis(item)
            results.append(result)
            
            if result.get('success'):
                successful_tests += 1
                self._print_item_results(result)
            else:
                failed_tests += 1
        
        # Generate summary
        summary = self._generate_summary(results)
        
        return {
            'total_items': len(items),
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'results': results,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def _print_item_results(self, result: Dict):
        """Print detailed results for a single item"""
        item_name = result.get('name', 'Unknown')
        comparison = result.get('comparison', {})
        clip_analysis = result.get('clip_analysis', {})
        
        print(f"\n📊 Results for: {item_name}")
        print("-" * 40)
        
        # CLIP analysis results
        if clip_analysis.get('style_matches'):
            print(f"🎨 CLIP Style Analysis:")
            print(f"  Primary Style: {clip_analysis['style_matches'][0][0]} ({clip_analysis['style_matches'][0][1]:.1%} confidence)")
            print(f"  Top 3 Styles:")
            for i, (style, confidence) in enumerate(clip_analysis.get('top_styles', [])[:3], 1):
                print(f"    {i}. {style}: {confidence:.1%}")
        
        # Style tags comparison
        style_comp = comparison.get('style_tags', {})
        print(f"\n🎨 Style Tags:")
        print(f"  Current: {style_comp.get('current_count', 0)} tags - {', '.join(style_comp.get('current', []))}")
        print(f"  Enhanced: {style_comp.get('enhanced_count', 0)} tags - {', '.join(style_comp.get('enhanced', []))}")
        print(f"  Improvement: +{style_comp.get('improvement', 0)} tags")
        
        # Occasion tags comparison
        occasion_comp = comparison.get('occasion_tags', {})
        print(f"📅 Occasion Tags:")
        print(f"  Current: {occasion_comp.get('current_count', 0)} tags - {', '.join(occasion_comp.get('current', []))}")
        print(f"  Enhanced: {occasion_comp.get('enhanced_count', 0)} tags - {', '.join(occasion_comp.get('enhanced', []))}")
        print(f"  Improvement: +{occasion_comp.get('improvement', 0)} tags")
        
        # Season tags comparison
        season_comp = comparison.get('season_tags', {})
        print(f"🌤️ Season Tags:")
        print(f"  Current: {season_comp.get('current_count', 0)} tags - {', '.join(season_comp.get('current', []))}")
        print(f"  Enhanced: {season_comp.get('enhanced_count', 0)} tags - {', '.join(season_comp.get('enhanced', []))}")
        print(f"  Improvement: +{season_comp.get('improvement', 0)} tags")
        
        # Style compatibility
        style_compat = comparison.get('metadata_quality', {}).get('style_compatibility', {})
        if style_compat:
            print(f"\n🔄 Style Compatibility:")
            print(f"  Compatible: {', '.join(style_compat.get('compatibleStyles', [])[:3])}")
            print(f"  Avoid: {', '.join(style_compat.get('avoidStyles', [])[:3])}")
            print(f"  Notes: {style_compat.get('styleNotes', 'No notes')}")
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics from test results"""
        successful_results = [r for r in results if r.get('success')]
        
        if not successful_results:
            return {'error': 'No successful tests'}
        
        # Calculate improvements
        style_improvements = []
        occasion_improvements = []
        season_improvements = []
        confidence_scores = []
        
        for result in successful_results:
            comparison = result.get('comparison', {})
            
            style_improvements.append(comparison.get('style_tags', {}).get('improvement', 0))
            occasion_improvements.append(comparison.get('occasion_tags', {}).get('improvement', 0))
            season_improvements.append(comparison.get('season_tags', {}).get('improvement', 0))
            
            confidence = comparison.get('metadata_quality', {}).get('enhanced_confidence', 0)
            confidence_scores.append(confidence)
        
        # Calculate averages
        avg_style_improvement = sum(style_improvements) / len(style_improvements)
        avg_occasion_improvement = sum(occasion_improvements) / len(occasion_improvements)
        avg_season_improvement = sum(season_improvements) / len(season_improvements)
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Count items with CLIP insights
        items_with_clip = sum(1 for r in successful_results 
                            if r.get('comparison', {}).get('metadata_quality', {}).get('additional_insights', False))
        
        return {
            'total_tested': len(successful_results),
            'average_improvements': {
                'style_tags': avg_style_improvement,
                'occasion_tags': avg_occasion_improvement,
                'season_tags': avg_season_improvement
            },
            'average_confidence': avg_confidence,
            'items_with_clip_insights': items_with_clip,
            'clip_insight_percentage': (items_with_clip / len(successful_results)) * 100 if successful_results else 0,
            'improvement_breakdown': {
                'style_tags_improved': sum(1 for imp in style_improvements if imp > 0),
                'occasion_tags_improved': sum(1 for imp in occasion_improvements if imp > 0),
                'season_tags_improved': sum(1 for imp in season_improvements if imp > 0)
            }
        }
    
    def print_summary(self, test_result: Dict):
        """Print a formatted summary of the test results"""
        summary = test_result.get('summary', {})
        
        print("\n" + "=" * 60)
        print("📊 CLIP-ENHANCED WARDROBE ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"📦 Total Items Tested: {test_result.get('total_items', 0)}")
        print(f"✅ Successful Tests: {test_result.get('successful_tests', 0)}")
        print(f"❌ Failed Tests: {test_result.get('failed_tests', 0)}")
        
        if 'error' not in summary:
            print(f"\n🎯 Average Improvements:")
            avg_improvements = summary.get('average_improvements', {})
            print(f"  Style Tags: +{avg_improvements.get('style_tags', 0):.1f} tags")
            print(f"  Occasion Tags: +{avg_improvements.get('occasion_tags', 0):.1f} tags")
            print(f"  Season Tags: +{avg_improvements.get('season_tags', 0):.1f} tags")
            
            print(f"\n📈 Quality Metrics:")
            print(f"  Average Confidence: {summary.get('average_confidence', 0):.1%}")
            print(f"  Items with CLIP Insights: {summary.get('items_with_clip_insights', 0)}")
            print(f"  CLIP Insight Coverage: {summary.get('clip_insight_percentage', 0):.1f}%")
            
            print(f"\n🔄 Improvement Breakdown:")
            breakdown = summary.get('improvement_breakdown', {})
            print(f"  Style Tags Improved: {breakdown.get('style_tags_improved', 0)} items")
            print(f"  Occasion Tags Improved: {breakdown.get('occasion_tags_improved', 0)} items")
            print(f"  Season Tags Improved: {breakdown.get('season_tags_improved', 0)} items")
        
        print("\n" + "=" * 60)
    
    def save_results(self, test_result: Dict, filename: str = None):
        """Save test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clip_wardrobe_test_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(test_result, f, indent=2, default=str)
            print(f"💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")

async def main():
    """Main function to run the CLIP wardrobe test"""
    print("🚀 CLIP-Enhanced Wardrobe Analysis Test")
    print("This test demonstrates how CLIP analysis can enhance wardrobe metadata")
    print("without requiring OpenAI API keys.\n")
    
    try:
        # Initialize tester
        tester = CLIPWardrobeTester()
        
        # Run test
        print("🔍 Starting CLIP analysis test...")
        result = await tester.test_wardrobe_clip_analysis()
        
        # Print summary
        tester.print_summary(result)
        
        # Save results
        save_results = input("\n💾 Save test results to JSON file? (y/n): ").strip().lower()
        if save_results == 'y':
            tester.save_results(result)
        
        print("\n✅ CLIP enhancement test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 