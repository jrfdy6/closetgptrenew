#!/usr/bin/env python3
"""
Test script to demonstrate enhanced wardrobe analysis
This script uses sample wardrobe data to show the improvements in metadata quality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List
from src.services.enhanced_image_analysis_service import enhanced_analyzer
from src.services.openai_service import analyze_image_with_gpt4

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

class WardrobeEnhancementTester:
    def __init__(self):
        """Initialize the wardrobe enhancement tester"""
        self.results = []
    
    async def download_image(self, image_url: str, item_id: str) -> str:
        """Download image and save to temporary file"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_path = f"temp_test_{item_id}.jpg"
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            print(f"❌ Failed to download image for item {item_id}: {str(e)}")
            return None
    
    async def test_item_enhancement(self, item: Dict) -> Dict:
        """Test enhanced analysis on a single item"""
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
                
                # Run enhanced analysis
                print(f"  🚀 Running enhanced analysis...")
                enhanced_analysis = await enhanced_analyzer.analyze_clothing_item(temp_image_path)
                
                # Run legacy analysis for comparison
                print(f"  📊 Running legacy analysis...")
                legacy_analysis = await analyze_image_with_gpt4(temp_image_path)
                
                # Compare results
                comparison = self._compare_analyses(current_metadata, enhanced_analysis, legacy_analysis)
                
                return {
                    'item_id': item_id,
                    'name': item.get('name', 'Unknown'),
                    'current_metadata': current_metadata,
                    'enhanced_analysis': enhanced_analysis,
                    'legacy_analysis': legacy_analysis,
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
    
    def _compare_analyses(self, current: Dict, enhanced: Dict, legacy: Dict) -> Dict:
        """Compare the three analysis methods"""
        comparison = {
            'style_tags': {
                'current_count': len(current.get('style', [])),
                'enhanced_count': len(enhanced.get('style', [])),
                'legacy_count': len(legacy.get('style', [])),
                'improvement': len(enhanced.get('style', [])) - len(current.get('style', [])),
                'current': current.get('style', []),
                'enhanced': enhanced.get('style', []),
                'legacy': legacy.get('style', [])
            },
            'occasion_tags': {
                'current_count': len(current.get('occasion', [])),
                'enhanced_count': len(enhanced.get('occasion', [])),
                'legacy_count': len(legacy.get('occasion', [])),
                'improvement': len(enhanced.get('occasion', [])) - len(current.get('occasion', [])),
                'current': current.get('occasion', []),
                'enhanced': enhanced.get('occasion', []),
                'legacy': legacy.get('occasion', [])
            },
            'season_tags': {
                'current_count': len(current.get('season', [])),
                'enhanced_count': len(enhanced.get('season', [])),
                'legacy_count': len(legacy.get('season', [])),
                'improvement': len(enhanced.get('season', [])) - len(current.get('season', [])),
                'current': current.get('season', []),
                'enhanced': enhanced.get('season', []),
                'legacy': legacy.get('season', [])
            },
            'metadata_quality': {
                'enhanced_confidence': enhanced.get('metadata', {}).get('confidenceScores', {}).get('overallConfidence', 0),
                'clip_analysis': enhanced.get('metadata', {}).get('clipAnalysis', {}),
                'style_compatibility': enhanced.get('metadata', {}).get('styleCompatibility', {}),
                'additional_insights': bool(enhanced.get('metadata', {}).get('clipAnalysis'))
            }
        }
        
        return comparison
    
    async def test_wardrobe_enhancement(self, items: List[Dict] = None) -> Dict:
        """Test enhanced analysis on wardrobe items"""
        if items is None:
            items = SAMPLE_WARDROBE
        
        print("🚀 Testing Enhanced Wardrobe Analysis")
        print("=" * 50)
        print(f"📦 Testing {len(items)} sample items")
        
        results = []
        successful_tests = 0
        failed_tests = 0
        
        for i, item in enumerate(items, 1):
            print(f"\n📸 Testing item {i}/{len(items)}")
            result = await self.test_item_enhancement(item)
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
        
        print(f"\n📊 Results for: {item_name}")
        print("-" * 40)
        
        # Style tags comparison
        style_comp = comparison.get('style_tags', {})
        print(f"🎨 Style Tags:")
        print(f"  Current: {style_comp.get('current_count', 0)} tags - {', '.join(style_comp.get('current', []))}")
        print(f"  Enhanced: {style_comp.get('enhanced_count', 0)} tags - {', '.join(style_comp.get('enhanced', []))}")
        print(f"  Legacy: {style_comp.get('legacy_count', 0)} tags - {', '.join(style_comp.get('legacy', []))}")
        print(f"  Improvement: +{style_comp.get('improvement', 0)} tags")
        
        # Occasion tags comparison
        occasion_comp = comparison.get('occasion_tags', {})
        print(f"📅 Occasion Tags:")
        print(f"  Current: {occasion_comp.get('current_count', 0)} tags - {', '.join(occasion_comp.get('current', []))}")
        print(f"  Enhanced: {occasion_comp.get('enhanced_count', 0)} tags - {', '.join(occasion_comp.get('enhanced', []))}")
        print(f"  Legacy: {occasion_comp.get('legacy_count', 0)} tags - {', '.join(occasion_comp.get('legacy', []))}")
        print(f"  Improvement: +{occasion_comp.get('improvement', 0)} tags")
        
        # Season tags comparison
        season_comp = comparison.get('season_tags', {})
        print(f"🌤️ Season Tags:")
        print(f"  Current: {season_comp.get('current_count', 0)} tags - {', '.join(season_comp.get('current', []))}")
        print(f"  Enhanced: {season_comp.get('enhanced_count', 0)} tags - {', '.join(season_comp.get('enhanced', []))}")
        print(f"  Legacy: {season_comp.get('legacy_count', 0)} tags - {', '.join(season_comp.get('legacy', []))}")
        print(f"  Improvement: +{season_comp.get('improvement', 0)} tags")
        
        # CLIP insights
        clip_analysis = comparison.get('metadata_quality', {}).get('clip_analysis', {})
        if clip_analysis:
            print(f"🔍 CLIP Analysis:")
            print(f"  Primary Style: {clip_analysis.get('primaryStyle', 'Unknown')}")
            print(f"  Style Confidence: {clip_analysis.get('styleConfidence', 0):.1%}")
            print(f"  Top Styles: {', '.join(clip_analysis.get('topStyles', [])[:3])}")
        
        # Style compatibility
        style_compat = comparison.get('metadata_quality', {}).get('style_compatibility', {})
        if style_compat:
            print(f"🔄 Style Compatibility:")
            print(f"  Compatible: {', '.join(style_compat.get('compatibleStyles', [])[:3])}")
            print(f"  Avoid: {', '.join(style_compat.get('avoidStyles', [])[:3])}")
    
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
        print("📊 ENHANCED WARDROBE ANALYSIS TEST SUMMARY")
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
            filename = f"wardrobe_enhancement_test_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(test_result, f, indent=2, default=str)
            print(f"💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")

async def main():
    """Main function to run the wardrobe enhancement test"""
    print("🚀 Enhanced Wardrobe Analysis Test")
    print("This test demonstrates the improvements in metadata quality")
    print("using sample wardrobe data.\n")
    
    try:
        # Initialize tester
        tester = WardrobeEnhancementTester()
        
        # Run test
        print("🔍 Starting enhancement test...")
        result = await tester.test_wardrobe_enhancement()
        
        # Print summary
        tester.print_summary(result)
        
        # Save results
        save_results = input("\n💾 Save test results to JSON file? (y/n): ").strip().lower()
        if save_results == 'y':
            tester.save_results(result)
        
        print("\n✅ Enhancement test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 