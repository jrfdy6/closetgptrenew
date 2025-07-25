#!/usr/bin/env python3
"""
Analyze existing wardrobe with enhanced analysis system
This script fetches existing wardrobe items and re-analyzes them with the enhanced system
to demonstrate the improvements in metadata quality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any
import firebase_admin
from firebase_admin import credentials, firestore
from src.services.enhanced_image_analysis_service import enhanced_analyzer
from src.services.openai_service import analyze_image_with_gpt4

class WardrobeAnalyzer:
    def __init__(self, service_account_path: str = "service-account-key.json"):
        """Initialize the wardrobe analyzer with Firebase connection"""
        try:
            # Initialize Firebase Admin
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✅ Firebase connection established")
        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {str(e)}")
            raise
    
    async def get_wardrobe_items(self, user_id: str = None) -> List[Dict]:
        """Fetch wardrobe items from Firestore"""
        try:
            wardrobe_ref = self.db.collection('wardrobe')
            
            if user_id:
                # Get items for specific user
                query = wardrobe_ref.where('userId', '==', user_id)
            else:
                # Get all items (for testing)
                query = wardrobe_ref
            
            docs = query.stream()
            items = []
            
            for doc in docs:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                items.append(item_data)
            
            print(f"📦 Found {len(items)} wardrobe items")
            return items
            
        except Exception as e:
            print(f"❌ Error fetching wardrobe items: {str(e)}")
            return []
    
    async def download_image(self, image_url: str, item_id: str) -> str:
        """Download image and save to temporary file"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_path = f"temp_wardrobe_{item_id}.jpg"
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            print(f"❌ Failed to download image for item {item_id}: {str(e)}")
            return None
    
    async def analyze_item_comparison(self, item: Dict) -> Dict:
        """Compare old vs enhanced analysis for a single item"""
        try:
            item_id = item.get('id', 'unknown')
            image_url = item.get('imageUrl')
            
            if not image_url:
                return {
                    'item_id': item_id,
                    'name': item.get('name', 'Unknown'),
                    'error': 'No image URL available'
                }
            
            print(f"🔍 Analyzing item: {item.get('name', 'Unknown')} ({item_id})")
            
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
                    'color': item.get('color', 'unknown'),
                    'brand': item.get('brand')
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
                    'image_url': image_url,
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
            print(f"❌ Error analyzing item {item_id}: {str(e)}")
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
    
    async def analyze_wardrobe(self, user_id: str = None, max_items: int = 10) -> Dict:
        """Analyze entire wardrobe with enhanced system"""
        print("🚀 Starting Enhanced Wardrobe Analysis")
        print("=" * 60)
        
        # Get wardrobe items
        items = await self.get_wardrobe_items(user_id)
        
        if not items:
            print("❌ No wardrobe items found")
            return {'error': 'No items found'}
        
        # Limit items for testing
        if max_items and len(items) > max_items:
            items = items[:max_items]
            print(f"📝 Analyzing first {max_items} items for demonstration")
        
        results = []
        successful_analyses = 0
        failed_analyses = 0
        
        for i, item in enumerate(items, 1):
            print(f"\n📸 Processing item {i}/{len(items)}")
            result = await self.analyze_item_comparison(item)
            results.append(result)
            
            if result.get('success'):
                successful_analyses += 1
            else:
                failed_analyses += 1
        
        # Generate summary
        summary = self._generate_summary(results)
        
        return {
            'total_items': len(items),
            'successful_analyses': successful_analyses,
            'failed_analyses': failed_analyses,
            'results': results,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics from analysis results"""
        successful_results = [r for r in results if r.get('success')]
        
        if not successful_results:
            return {'error': 'No successful analyses'}
        
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
            'total_analyzed': len(successful_results),
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
    
    def print_summary(self, analysis_result: Dict):
        """Print a formatted summary of the analysis"""
        summary = analysis_result.get('summary', {})
        
        print("\n" + "=" * 60)
        print("📊 ENHANCED WARDROBE ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"📦 Total Items Analyzed: {analysis_result.get('total_items', 0)}")
        print(f"✅ Successful Analyses: {analysis_result.get('successful_analyses', 0)}")
        print(f"❌ Failed Analyses: {analysis_result.get('failed_analyses', 0)}")
        
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
    
    def save_results(self, analysis_result: Dict, filename: str = None):
        """Save analysis results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wardrobe_analysis_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(analysis_result, f, indent=2, default=str)
            print(f"💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")

async def main():
    """Main function to run the wardrobe analysis"""
    print("🚀 Enhanced Wardrobe Analysis Tool")
    print("This tool will analyze your existing wardrobe with the enhanced system")
    print("to demonstrate improvements in metadata quality.\n")
    
    try:
        # Initialize analyzer
        analyzer = WardrobeAnalyzer()
        
        # Ask for user ID (optional)
        user_id = input("Enter user ID (or press Enter to analyze all items): ").strip()
        if not user_id:
            user_id = None
        
        # Ask for max items
        max_items_input = input("Enter max number of items to analyze (or press Enter for 10): ").strip()
        max_items = int(max_items_input) if max_items_input else 10
        
        # Run analysis
        print(f"\n🔍 Starting analysis...")
        result = await analyzer.analyze_wardrobe(user_id, max_items)
        
        # Print summary
        analyzer.print_summary(result)
        
        # Save results
        save_results = input("\n💾 Save detailed results to JSON file? (y/n): ").strip().lower()
        if save_results == 'y':
            analyzer.save_results(result)
        
        print("\n✅ Analysis completed!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 