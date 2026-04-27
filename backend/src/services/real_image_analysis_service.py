import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
from .ai_runtime.runtime_config import is_openai_configured
from .ai_runtime.vision_runtime import analyze_image_url_with_openai_vision

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class RealImageAnalysisService:
    def __init__(self):
        if not is_openai_configured():
            logger.warning("OPENAI_API_KEY not found in environment variables")
        else:
            logger.info("OpenAI vision runtime available")
    
    async def analyze_clothing_item(self, image_url: str) -> Dict:
        """
        Real clothing item analysis using GPT-4 Vision
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Analysis with GPT-4 insights
        """
        try:
            logger.info(f"Starting real clothing item analysis for: {image_url}")
            
            # Check if OpenAI client is available
            if not is_openai_configured():
                logger.error("OpenAI client not available - API key missing")
                return self._get_fallback_response("OpenAI API key not configured")
            
            logger.info("Calling centralized vision runtime...")
            analysis = await analyze_image_url_with_openai_vision(image_url)
            enhanced_analysis = self._enhance_analysis(analysis)
            logger.info("Real analysis completed successfully")
            return enhanced_analysis
                
        except Exception as e:
            logger.error(f"Error in real analysis: {str(e)}")
            return self._get_fallback_response(str(e))
    
    def _get_fallback_response(self, error_message: str) -> Dict:
        """Get a fallback response when analysis fails"""
        return {
            "analysis": {
                "type": "clothing",
                "dominantColors": ["unknown"],
                "style": ["unknown"],
                "occasion": ["unknown"],
                "season": ["unknown"]
            },
            "error": f"Analysis failed: {error_message}",
            "message": "Real analysis failed, using fallback",
            "metadata": {
                "confidence": 0.0,
                "analysis_method": "fallback",
                "processing_time": "error"
            },
            "recommendations": {
                "matching_colors": [],
                "compatible_styles": [],
                "suggested_occasions": ["unknown"],
                "best_seasons": ["unknown"]
            },
            "style_notes": "Analysis unavailable due to configuration issues."
        }
    
    def _parse_text_response(self, content: str) -> Dict:
        """Parse text response when JSON parsing fails"""
        analysis = {
            "type": "clothing",
            "dominantColors": [],
            "style": [],
            "occasion": [],
            "season": []
        }
        
        # Simple text parsing
        lines = content.lower().split('\n')
        for line in lines:
            if 'color' in line or 'colour' in line:
                # Extract colors
                colors = ['red', 'blue', 'green', 'yellow', 'black', 'white', 'gray', 'grey', 'brown', 'pink', 'purple', 'orange']
                for color in colors:
                    if color in line:
                        analysis["dominantColors"].append(color)
            
            if 'style' in line:
                styles = ['casual', 'formal', 'business', 'streetwear', 'minimalist', 'classic', 'preppy', 'bohemian']
                for style in styles:
                    if style in line:
                        analysis["style"].append(style)
            
            if 'occasion' in line:
                occasions = ['everyday', 'work', 'casual', 'formal', 'party', 'sport']
                for occasion in occasions:
                    if occasion in line:
                        analysis["occasion"].append(occasion)
            
            if 'season' in line:
                seasons = ['spring', 'summer', 'fall', 'autumn', 'winter']
                for season in seasons:
                    if season in line:
                        analysis["season"].append(season)
        
        # Ensure we have at least some data
        if not analysis["dominantColors"]:
            analysis["dominantColors"] = ["unknown"]
        if not analysis["style"]:
            analysis["style"] = ["unknown"]
        if not analysis["occasion"]:
            analysis["occasion"] = ["unknown"]
        if not analysis["season"]:
            analysis["season"] = ["unknown"]
        
        return analysis
    
    def _enhance_analysis(self, analysis: Dict) -> Dict:
        """Enhance the analysis with additional metadata"""
        try:
            # Extract basic information
            clothing_type = (analysis.get("type", "unknown") if analysis else "unknown")
            colors = (analysis.get("dominantColors", []) if analysis else [])
            styles = (analysis.get("style", []) if analysis else [])
            occasions = (analysis.get("occasion", []) if analysis else [])
            seasons = (analysis.get("season", []) if analysis else [])
            
            # Create enhanced analysis
            enhanced = {
                "analysis": analysis,
                "metadata": {
                    "confidence": (analysis.get("confidence", 0.85) if analysis else 0.85),
                    "analysis_method": "gpt4_vision",
                    "processing_time": "real_time"
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
            return analysis
    
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

# Create a global instance
real_analyzer = RealImageAnalysisService() 
