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
from .style_analysis_service import style_analyzer

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedImageAnalysisService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def analyze_clothing_item(self, image_path: str) -> Dict:
        """
        Enhanced clothing item analysis combining GPT-4 Vision and CLIP style analysis
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Enhanced analysis with both GPT-4 and CLIP insights
        """
        try:
            logger.info("Starting enhanced clothing item analysis")
            
            # Step 1: GPT-4 Vision Analysis
            logger.info("Running GPT-4 Vision analysis...")
            gpt_analysis = await analyze_image_with_gpt4(image_path)
            
            # Step 2: CLIP Style Analysis
            logger.info("Running CLIP style analysis...")
            clip_analysis = await self._analyze_with_clip(image_path)
            
            # Step 3: Merge and enhance the analysis
            logger.info("Merging and enhancing analysis...")
            enhanced_analysis = self._merge_analyses(gpt_analysis, clip_analysis)
            
            logger.info("Enhanced analysis completed successfully")
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error in enhanced analysis: {str(e)}")
            raise
    
    async def _analyze_with_clip(self, image_path: str) -> Dict:
        """
        Analyze image using CLIP for style insights
        """
        try:
            # Load and process image for CLIP
            with Image.open(image_path) as image:
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Get style analysis
                style_matches = style_analyzer.analyze_style(image)
                top_styles = style_analyzer.get_top_styles(image, top_k=5)
                style_breakdown = style_analyzer.get_style_breakdown(image)
                
                return {
                    "clip_style_analysis": {
                        "top_matches": style_matches,
                        "top_5_styles": top_styles,
                        "full_breakdown": style_breakdown,
                        "primary_style": style_matches[0] if style_matches else None,
                        "style_confidence": style_matches[0][1] if style_matches else 0.0
                    }
                }
                
        except Exception as e:
            logger.error(f"CLIP analysis failed: {str(e)}")
            return {
                "clip_style_analysis": {
                    "top_matches": [],
                    "top_5_styles": [],
                    "full_breakdown": {},
                    "primary_style": None,
                    "style_confidence": 0.0
                }
            }
    
    def _merge_analyses(self, gpt_analysis: Dict, clip_analysis: Dict) -> Dict:
        """
        Merge GPT-4 and CLIP analyses to create enhanced metadata
        """
        try:
            # Extract CLIP insights
            clip_insights = (clip_analysis.get("clip_style_analysis", {}) if clip_analysis else {})
            top_clip_styles = [style for style, _ in (clip_insights.get("top_5_styles", []) if clip_insights else [])]
            primary_clip_style = (clip_insights.get("primary_style") if clip_insights else None)
            style_confidence = (clip_insights.get("style_confidence", 0.0) if clip_insights else 0.0)
            
            # Get GPT-4 style tags
            gpt_styles = (gpt_analysis.get("style", []) if gpt_analysis else [])
            
            # Create enhanced style tags by combining both analyses
            enhanced_styles = self._enhance_style_tags(gpt_styles, top_clip_styles, style_confidence)
            
            # Enhance other metadata based on CLIP insights
            enhanced_analysis = gpt_analysis.copy()
            
            # Update style tags with CLIP insights
            enhanced_analysis["style"] = enhanced_styles
            
            # Add CLIP analysis metadata
            enhanced_analysis["metadata"]["clipAnalysis"] = {
                "primaryStyle": primary_clip_style,
                "styleConfidence": style_confidence,
                "topStyles": top_clip_styles,
                "styleBreakdown": (clip_insights.get("full_breakdown", {}) if clip_insights else {}),
                "analysisMethod": "CLIP + GPT-4 Vision"
            }
            
            # Enhance occasion tags based on style insights
            enhanced_analysis["occasion"] = self._enhance_occasion_tags(
                (gpt_analysis.get("occasion", []) if gpt_analysis else []),
                top_clip_styles,
                style_confidence
            )
            
            # Enhance season tags based on style insights
            enhanced_analysis["season"] = self._enhance_season_tags(
                (gpt_analysis.get("season", []) if gpt_analysis else []),
                top_clip_styles,
                style_confidence
            )
            
            # Add confidence scores for metadata quality
            enhanced_analysis["metadata"]["confidenceScores"] = {
                "styleAnalysis": style_confidence,
                "gptAnalysis": 0.85,  # Estimated GPT-4 confidence
                "overallConfidence": (style_confidence + 0.85) / 2
            }
            
            # Add style compatibility insights
            enhanced_analysis["metadata"]["styleCompatibility"] = {
                "primaryStyle": primary_clip_style,
                "compatibleStyles": top_clip_styles[:3],
                "avoidStyles": self._get_avoid_styles(top_clip_styles),
                "styleNotes": self._generate_style_notes(primary_clip_style, style_confidence)
            }
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error merging analyses: {str(e)}")
            return gpt_analysis  # Fallback to original GPT analysis
    
    def _enhance_style_tags(self, gpt_styles: List[str], clip_styles: List[str], confidence: float) -> List[str]:
        """
        Enhance style tags by combining GPT-4 and CLIP insights
        """
        enhanced_styles = set(gpt_styles)  # Start with GPT styles
        
        # Add high-confidence CLIP styles
        if confidence > 0.3:  # Threshold for considering CLIP styles
            for clip_style in clip_styles[:3]:  # Top 3 CLIP styles
                enhanced_styles.add(clip_style)
        
        # Add style mappings for better compatibility
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
        for clip_style in clip_styles[:2]:  # Top 2 for mapping
            if clip_style in style_mappings:
                for mapped_style in style_mappings[clip_style]:
                    enhanced_styles.add(mapped_style)
        
        return list(enhanced_styles)
    
    def _enhance_occasion_tags(self, gpt_occasions: List[str], clip_styles: List[str], confidence: float) -> List[str]:
        """
        Enhance occasion tags based on style insights
        """
        enhanced_occasions = set(gpt_occasions)
        
        # Style to occasion mappings
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
        
        # Add occasion mappings for high-confidence styles
        if confidence > 0.3:
            for clip_style in clip_styles[:2]:
                if clip_style in style_occasion_mappings:
                    for occasion in style_occasion_mappings[clip_style]:
                        enhanced_occasions.add(occasion)
        
        return list(enhanced_occasions)
    
    def _enhance_season_tags(self, gpt_seasons: List[str], clip_styles: List[str], confidence: float) -> List[str]:
        """
        Enhance season tags based on style insights
        """
        enhanced_seasons = set(gpt_seasons)
        
        # Style to season mappings
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
        
        # Add season mappings for high-confidence styles
        if confidence > 0.3:
            for clip_style in clip_styles[:2]:
                if clip_style in style_season_mappings:
                    seasons = style_season_mappings[clip_style]
                    if "all" in seasons:
                        enhanced_seasons.update(["spring", "summer", "fall", "winter"])
                    else:
                        enhanced_seasons.update(seasons)
        
        return list(enhanced_seasons)
    
    def _get_avoid_styles(self, top_styles: List[str]) -> List[str]:
        """
        Get styles to avoid based on the primary style
        """
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
    
    def _generate_style_notes(self, primary_style: Optional[str], confidence: float) -> str:
        """
        Generate style notes based on the primary style and confidence
        """
        if not primary_style:
            return "Style analysis inconclusive"
        
        if confidence > 0.4:
            return f"Strong {primary_style} aesthetic detected. This item clearly embodies {primary_style} characteristics."
        elif confidence > 0.25:
            return f"Moderate {primary_style} influence detected. This item has some {primary_style} elements."
        else:
            return f"Subtle {primary_style} influence detected. This item may work with {primary_style} styling."
    
    async def analyze_batch(self, image_paths: List[str]) -> List[Dict]:
        """
        Analyze multiple clothing items with enhanced analysis
        """
        results = []
        for i, image_path in enumerate(image_paths):
            try:
                logger.info(f"Analyzing image {i+1}/{len(image_paths)}: {image_path}")
                analysis = await self.analyze_clothing_item(image_path)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze {image_path}: {str(e)}")
                results.append({"error": str(e), "image_path": image_path})
        
        return results

# Create singleton instance
enhanced_analyzer = EnhancedImageAnalysisService() 