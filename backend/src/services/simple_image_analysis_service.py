import os
import base64
import json
import logging
from openai import OpenAI
from PIL import Image
import tempfile
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
from .openai_service import analyze_image_with_gpt4

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class SimpleImageAnalysisService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def analyze_clothing_item(self, image_path: str) -> Dict:
        """
        Simple clothing item analysis using only GPT-4 Vision
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Analysis with GPT-4 insights
        """
        try:
            logger.info("Starting simple clothing item analysis")
            
            # GPT-4 Vision Analysis
            logger.info("Running GPT-4 Vision analysis...")
            gpt_analysis = await analyze_image_with_gpt4(image_path)
            
            # Enhance the analysis with additional metadata
            enhanced_analysis = self._enhance_analysis(gpt_analysis)
            
            logger.info("Simple analysis completed successfully")
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error in simple analysis: {str(e)}")
            raise
    
    def _enhance_analysis(self, gpt_analysis: Dict) -> Dict:
        """
        Enhance GPT-4 analysis with additional metadata
        """
        try:
            # Extract basic information
            clothing_type = (gpt_analysis.get("type", "unknown") if gpt_analysis else "unknown")
            colors = (gpt_analysis.get("dominantColors", []) if gpt_analysis else [])
            styles = (gpt_analysis.get("style", []) if gpt_analysis else [])
            occasions = (gpt_analysis.get("occasion", []) if gpt_analysis else [])
            seasons = (gpt_analysis.get("season", []) if gpt_analysis else [])
            
            # Create enhanced analysis
            enhanced = {
                "analysis": gpt_analysis,
                "metadata": {
                    "confidence": 0.85,  # Default confidence for GPT-4
                    "analysis_method": "gpt4_vision",
                    "processing_time": "fast"
                },
                "recommendations": {
                    "matching_colors": self._generate_matching_colors(colors),
                    "compatible_styles": self._generate_compatible_styles(styles),
                    "suggested_occasions": occasions,
                    "best_seasons": seasons
                },
                "style_notes": self._generate_style_notes(styles, clothing_type)
            }
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing analysis: {str(e)}")
            return gpt_analysis
    
    def _generate_matching_colors(self, colors: List[str]) -> List[str]:
        """Generate matching colors based on input colors"""
        color_matches = {
            "black": ["white", "gray", "navy", "red"],
            "white": ["black", "navy", "gray", "pink"],
            "blue": ["white", "gray", "navy", "black"],
            "red": ["black", "white", "navy", "gray"],
            "gray": ["black", "white", "navy", "pink"],
            "navy": ["white", "gray", "black", "red"],
            "brown": ["beige", "cream", "white", "navy"],
            "beige": ["brown", "navy", "black", "white"]
        }
        
        matching = []
        for color in colors:
            if color.lower() in color_matches:
                matching.extend(color_matches[color.lower()])
        
        return list(set(matching))  # Remove duplicates
    
    def _generate_compatible_styles(self, styles: List[str]) -> List[str]:
        """Generate compatible styles based on input styles"""
        style_matches = {
            "casual": ["minimalist", "streetwear", "athleisure"],
            "formal": ["business", "classic", "preppy"],
            "minimalist": ["casual", "business", "classic"],
            "streetwear": ["casual", "athleisure", "urban"],
            "business": ["formal", "classic", "preppy"],
            "classic": ["business", "formal", "preppy"],
            "preppy": ["business", "classic", "formal"]
        }
        
        compatible = []
        for style in styles:
            if style.lower() in style_matches:
                compatible.extend(style_matches[style.lower()])
        
        return list(set(compatible))  # Remove duplicates
    
    def _generate_style_notes(self, styles: List[str], clothing_type: str) -> str:
        """Generate style notes based on analysis"""
        if not styles:
            return f"This {clothing_type} has a versatile style that can be dressed up or down."
        
        style_str = ", ".join(styles)
        return f"This {clothing_type} features a {style_str} aesthetic that works well for various occasions."
    
    async def analyze_batch(self, image_paths: List[str]) -> List[Dict]:
        """
        Analyze multiple clothing items
        """
        results = []
        for image_path in image_paths:
            try:
                result = await self.analyze_clothing_item(image_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {image_path}: {str(e)}")
                results.append({"error": str(e)})
        
        return results

# Create a global instance
simple_analyzer = SimpleImageAnalysisService() 