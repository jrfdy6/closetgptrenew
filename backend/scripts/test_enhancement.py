#!/usr/bin/env python3
"""
Test Enhanced Wardrobe Metadata Update

This script tests the enhancement process on a small sample of wardrobe items
to verify everything works correctly before running the full enhancement.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from scripts.enhance_wardrobe_metadata import WardrobeMetadataEnhancer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_enhancement():
    """Test the enhancement process on a few items"""
    try:
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY environment variable is required")
            return
        
        enhancer = WardrobeMetadataEnhancer()
        
        # Get a few items to test with
        wardrobe_ref = enhancer.db.collection(enhancer.wardrobe_collection)
        docs = list(wardrobe_ref.limit(3).stream())  # Test with 3 items
        
        if not docs:
            logger.warning("No wardrobe items found to test with")
            return
        
        logger.info(f"Testing enhancement on {len(docs)} items...")
        
        for i, doc in enumerate(docs):
            item_id = doc.id
            item_data = doc.to_dict()
            
            logger.info(f"\n--- Testing Item {i+1}/{len(docs)} ---")
            logger.info(f"Item ID: {item_id}")
            logger.info(f"Name: {item_data.get('name', 'Unknown')}")
            logger.info(f"Current styles: {item_data.get('style', [])}")
            logger.info(f"Current occasions: {item_data.get('occasion', [])}")
            
            # Test enhancement
            try:
                enhanced_item = await enhancer.enhance_wardrobe_item(item_id, item_data)
                
                logger.info(f"Enhanced styles: {enhanced_item.get('style', [])}")
                logger.info(f"Enhanced occasions: {enhanced_item.get('occasion', [])}")
                
                # Show what was added
                original_styles = set(item_data.get('style', []))
                enhanced_styles = set(enhanced_item.get('style', []))
                new_styles = enhanced_styles - original_styles
                
                original_occasions = set(item_data.get('occasion', []))
                enhanced_occasions = set(enhanced_item.get('occasion', []))
                new_occasions = enhanced_occasions - original_occasions
                
                if new_styles:
                    logger.info(f"New styles added: {list(new_styles)}")
                if new_occasions:
                    logger.info(f"New occasions added: {list(new_occasions)}")
                
                # Show CLIP analysis if available
                clip_analysis = enhanced_item.get('metadata', {}).get('clipAnalysis')
                if clip_analysis:
                    logger.info(f"CLIP primary style: {clip_analysis.get('primaryStyle')}")
                    logger.info(f"CLIP confidence: {clip_analysis.get('styleConfidence', 0):.2f}")
                
                logger.info("✓ Enhancement successful")
                
            except Exception as e:
                logger.error(f"✗ Enhancement failed: {str(e)}")
        
        logger.info("\n--- Test completed ---")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_enhancement()) 