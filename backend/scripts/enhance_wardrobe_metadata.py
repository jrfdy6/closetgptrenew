#!/usr/bin/env python3
"""
Enhanced Wardrobe Metadata Update Script

This script fetches all wardrobe items from Firestore, runs enhanced analysis
on each item's image, and merges the new metadata with existing metadata
without creating duplicates or erasing existing data.
"""

import os
import sys
import asyncio
import logging
import tempfile
import requests
from typing import Dict, List, Set, Any
from pathlib import Path
from dotenv import load_dotenv
from collections import Counter, defaultdict

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.services.enhanced_image_analysis_service import EnhancedImageAnalysisService
from src.config.firebase import db
from src.types.wardrobe import ClothingItem

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WardrobeMetadataEnhancer:
    def __init__(self):
        self.db = db
        self.analysis_service = EnhancedImageAnalysisService()
        self.wardrobe_collection = "wardrobe"
        
    async def download_image(self, image_url: str) -> str:
        """Download image from URL and save to temporary file"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Failed to download image {image_url}: {str(e)}")
            raise
    
    def merge_metadata(self, existing_metadata: Dict, new_metadata: Dict) -> Dict:
        """
        Merge new metadata with existing metadata, avoiding duplicates
        """
        merged = existing_metadata.copy() if existing_metadata else {}
        
        # Merge style tags (avoid duplicates)
        existing_styles = set(merged.get('style', []))
        new_styles = set(new_metadata.get('style', []))
        merged['style'] = list(existing_styles.union(new_styles))
        
        # Merge occasion tags (avoid duplicates)
        existing_occasions = set(merged.get('occasion', []))
        new_occasions = set(new_metadata.get('occasion', []))
        merged['occasion'] = list(existing_occasions.union(new_occasions))
        
        # Merge season tags (avoid duplicates)
        existing_seasons = set(merged.get('season', []))
        new_seasons = set(new_metadata.get('season', []))
        merged['season'] = list(existing_seasons.union(new_seasons))
        
        # Merge tags (avoid duplicates)
        existing_tags = set(merged.get('tags', []))
        new_tags = set(new_metadata.get('tags', []))
        merged['tags'] = list(existing_tags.union(new_tags))
        
        # Merge dominant colors (avoid duplicates)
        existing_dominant = merged.get('dominantColors', [])
        new_dominant = new_metadata.get('dominantColors', [])
        merged['dominantColors'] = self._merge_colors(existing_dominant, new_dominant)
        
        # Merge matching colors (avoid duplicates)
        existing_matching = merged.get('matchingColors', [])
        new_matching = new_metadata.get('matchingColors', [])
        merged['matchingColors'] = self._merge_colors(existing_matching, new_matching)
        
        # Merge metadata object (nested merge)
        existing_metadata_obj = merged.get('metadata', {})
        new_metadata_obj = new_metadata.get('metadata', {})
        merged['metadata'] = self._merge_nested_metadata(existing_metadata_obj, new_metadata_obj)
        
        # Update other fields if they're missing or empty
        for field in ['name', 'type', 'subType', 'brand', 'color', 'colorName']:
            if not merged.get(field) and new_metadata.get(field):
                merged[field] = new_metadata[field]
        
        return merged
    
    def _merge_colors(self, existing_colors: List, new_colors: List) -> List:
        """Merge color lists, avoiding duplicates by hex value"""
        if not existing_colors:
            return new_colors
        if not new_colors:
            return existing_colors
            
        # Create a set of existing hex values
        existing_hexes = set()
        for color in existing_colors:
            if isinstance(color, dict) and 'hex' in color:
                existing_hexes.add(color['hex'].lower())
            elif isinstance(color, str):
                existing_hexes.add(color.lower())
        
        # Add new colors that don't already exist
        merged = existing_colors.copy()
        for color in new_colors:
            if isinstance(color, dict) and 'hex' in color:
                if color['hex'].lower() not in existing_hexes:
                    merged.append(color)
                    existing_hexes.add(color['hex'].lower())
            elif isinstance(color, str):
                if color.lower() not in existing_hexes:
                    merged.append(color)
                    existing_hexes.add(color.lower())
        
        return merged
    
    def _merge_nested_metadata(self, existing: Dict, new: Dict) -> Dict:
        """Merge nested metadata objects"""
        merged = existing.copy() if existing else {}
        
        for key, new_value in new.items():
            if key not in merged:
                merged[key] = new_value
            elif isinstance(merged[key], dict) and isinstance(new_value, dict):
                merged[key] = self._merge_nested_metadata(merged[key], new_value)
            elif isinstance(merged[key], list) and isinstance(new_value, list):
                # Merge lists, avoiding duplicates
                existing_set = set(str(item) for item in merged[key])
                for item in new_value:
                    if str(item) not in existing_set:
                        merged[key].append(item)
                        existing_set.add(str(item))
            else:
                # For other types, prefer new value if it's not None/empty
                if new_value is not None and new_value != "":
                    merged[key] = new_value
        
        return merged
    
    async def enhance_wardrobe_item(self, item_id: str, item_data: Dict) -> Dict:
        """
        Enhance a single wardrobe item with new metadata
        """
        try:
            logger.info(f"Processing item: {item_data.get('name', 'Unknown')} (ID: {item_id})")
            
            # Check if item has an image URL
            image_url = item_data.get('imageUrl')
            if not image_url:
                logger.warning(f"Item {item_id} has no image URL, skipping")
                return item_data
            
            # Download image
            temp_image_path = await self.download_image(image_url)
            
            try:
                # Run enhanced analysis
                enhanced_analysis = await self.analysis_service.analyze_clothing_item(temp_image_path)
                
                # Merge with existing metadata
                enhanced_item = self.merge_metadata(item_data, enhanced_analysis)
                
                # Add enhancement timestamp
                if 'metadata' not in enhanced_item:
                    enhanced_item['metadata'] = {}
                enhanced_item['metadata']['enhancedAnalysisTimestamp'] = asyncio.get_event_loop().time()
                enhanced_item['metadata']['analysisMethod'] = 'Enhanced (GPT-4 + CLIP)'
                
                logger.info(f"Successfully enhanced item {item_id}")
                return enhanced_item
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_image_path):
                    os.unlink(temp_image_path)
                    
        except Exception as e:
            logger.error(f"Error enhancing item {item_id}: {str(e)}")
            return item_data  # Return original data on error
    
    async def enhance_all_wardrobe_items(self, user_id: str = None) -> Dict[str, Any]:
        """
        Enhance all wardrobe items with new metadata
        """
        try:
            logger.info("Starting wardrobe enhancement process...")
            
            # Get all wardrobe items
            wardrobe_ref = self.db.collection(self.wardrobe_collection)
            if user_id:
                wardrobe_ref = wardrobe_ref.where('userId', '==', user_id)
            
            docs = wardrobe_ref.stream()
            items = [(doc.id, doc.to_dict()) for doc in docs]
            
            logger.info(f"Found {len(items)} items to process")
            
            # Stats trackers
            total_new_styles = 0
            total_new_occasions = 0
            total_new_bodytypes = 0
            style_counter = Counter()
            occasion_counter = Counter()
            bodytype_counter = Counter()
            
            enhanced_count = 0
            error_count = 0
            skipped_count = 0
            
            for item_id, item_data in items:
                try:
                    # Skip items that already have enhanced analysis
                    if (item_data.get('metadata', {}).get('analysisMethod') == 'Enhanced (GPT-4 + CLIP)'):
                        logger.info(f"Skipping item {item_id} - already enhanced")
                        skipped_count += 1
                        continue
                    
                    # Enhance the item
                    enhanced_item = await self.enhance_wardrobe_item(item_id, item_data)
                    
                    # Count new styles
                    orig_styles = set(item_data.get('style', []))
                    new_styles = set(enhanced_item.get('style', [])) - orig_styles
                    total_new_styles += len(new_styles)
                    for s in new_styles:
                        style_counter[s] += 1
                    
                    # Count new occasions
                    orig_occasions = set(item_data.get('occasion', []))
                    new_occasions = set(enhanced_item.get('occasion', [])) - orig_occasions
                    total_new_occasions += len(new_occasions)
                    for o in new_occasions:
                        occasion_counter[o] += 1
                    
                    # Count new body types (from metadata.visualAttributes.bodyTypeCompatibility or similar)
                    orig_bodytypes = set()
                    new_bodytypes = set()
                    orig_meta = item_data.get('metadata', {})
                    enh_meta = enhanced_item.get('metadata', {})
                    # Try to get body type recommendations from enhanced metadata
                    enh_bodytype_compat = enh_meta.get('visualAttributes', {}).get('bodyTypeCompatibility', {})
                    orig_bodytype_compat = orig_meta.get('visualAttributes', {}).get('bodyTypeCompatibility', {})
                    if isinstance(enh_bodytype_compat, dict):
                        new_bodytypes = set(enh_bodytype_compat.keys())
                    if isinstance(orig_bodytype_compat, dict):
                        orig_bodytypes = set(orig_bodytype_compat.keys())
                    actually_new_bodytypes = new_bodytypes - orig_bodytypes
                    total_new_bodytypes += len(actually_new_bodytypes)
                    for b in actually_new_bodytypes:
                        bodytype_counter[b] += 1
                    
                    # Update in database
                    doc_ref = self.db.collection(self.wardrobe_collection).document(item_id)
                    doc_ref.set(enhanced_item, merge=True)
                    
                    enhanced_count += 1
                    logger.info(f"Enhanced and updated item {item_id} ({enhanced_count}/{len(items)})")
                    
                    # Add small delay to avoid overwhelming the API
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to enhance item {item_id}: {str(e)}")
                    error_count += 1
            
            # Summary
            summary = {
                'total_items': len(items),
                'enhanced_count': enhanced_count,
                'skipped_count': skipped_count,
                'error_count': error_count,
                'success_rate': (enhanced_count / len(items) * 100) if items else 0,
                'total_new_styles': total_new_styles,
                'total_new_occasions': total_new_occasions,
                'total_new_bodytypes': total_new_bodytypes,
                'most_added_style': style_counter.most_common(1)[0] if style_counter else None,
                'most_added_occasion': occasion_counter.most_common(1)[0] if occasion_counter else None,
                'most_added_bodytype': bodytype_counter.most_common(1)[0] if bodytype_counter else None,
            }
            
            logger.info("Enhancement process completed!")
            logger.info(f"Summary: {summary}")

            # Persist analytics to Firestore
            stats_ref = self.db.collection('wardrobe_stats').document('global')
            stats_ref.set(summary, merge=True)

            print("\n" + "="*50)
            print("WARDROBE ENHANCEMENT COMPLETED")
            print("="*50)
            print(f"Total items processed: {summary['total_items']}")
            print(f"Successfully enhanced: {summary['enhanced_count']}")
            print(f"Skipped (already enhanced): {summary['skipped_count']}")
            print(f"Errors: {summary['error_count']}")
            print(f"Success rate: {summary['success_rate']:.1f}%")
            print(f"\nNew tags added:")
            print(f"  Styles: {summary['total_new_styles']}")
            print(f"  Occasions: {summary['total_new_occasions']}")
            print(f"  Body types: {summary['total_new_bodytypes']}")
            if summary['most_added_style']:
                print(f"Most added style: {summary['most_added_style'][0]} (added {summary['most_added_style'][1]} times)")
            if summary['most_added_occasion']:
                print(f"Most added occasion: {summary['most_added_occasion'][0]} (added {summary['most_added_occasion'][1]} times)")
            if summary['most_added_bodytype']:
                print(f"Most added body type: {summary['most_added_bodytype'][0]} (added {summary['most_added_bodytype'][1]} times)")
            print("="*50)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in enhancement process: {str(e)}")
            raise

async def main():
    """Main function to run the wardrobe enhancement"""
    try:
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY environment variable is required")
            sys.exit(1)
        
        enhancer = WardrobeMetadataEnhancer()
        
        # You can specify a user_id to process only their items, or None for all users
        user_id = None  # Set to a specific user ID if needed
        
        summary = await enhancer.enhance_all_wardrobe_items(user_id)
        
        print("\n" + "="*50)
        print("WARDROBE ENHANCEMENT COMPLETED")
        print("="*50)
        print(f"Total items processed: {summary['total_items']}")
        print(f"Successfully enhanced: {summary['enhanced_count']}")
        print(f"Skipped (already enhanced): {summary['skipped_count']}")
        print(f"Errors: {summary['error_count']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 