"""
Outfit Scoring Service
All scoring and calculation methods with proper temperature handling.
"""

from typing import List, Dict, Any, Optional
from ..custom_types.wardrobe import ClothingItem
from ..custom_types.weather import WeatherData

class OutfitScoringService:
    def __init__(self):
        pass
        
    def _safe_temperature_convert(self, temperature) -> float:
        """Safely convert temperature to float to prevent string vs float comparison errors."""
        if isinstance(temperature, str):
            try:
                return float(temperature)
            except (ValueError, TypeError):
                return 70.0
        elif temperature is None:
            return 70.0
        else:
            return float(temperature)
            
    def calculate_weather_appropriateness(self, items: List[ClothingItem], weather: WeatherData) -> float:
        """Calculate weather appropriateness score with proper temperature handling."""
        if not items:
            return 0.0
            
        temperature = self._safe_temperature_convert(weather.temperature)
        total_score = 0.0
        
        for item in items:
            if self._is_weather_appropriate(item, temperature):
                total_score += 1.0
                
        return total_score / len(items) if items else 0.0
        
    def _is_weather_appropriate(self, item: ClothingItem, temperature: float) -> bool:
        """Check if item is appropriate for the given temperature."""
        temp = self._safe_temperature_convert(temperature)
        
        # Get material from metadata if available
        material = ""
        if item.metadata and item.metadata.visualAttributes and item.metadata.visualAttributes.material:
            material = item.metadata.visualAttributes.material.lower()
        
        # Hot weather (80°F+)
        if temp >= 80:
            winter_materials = ["wool", "fleece", "thick", "heavy"]
            if material and any(mat in material for mat in winter_materials):
                return False
        
        # Cold weather (<50°F)
        elif temp < 50:
            summer_materials = ["linen", "light cotton"]
            if material and any(mat in material for mat in summer_materials):
                return False
        
        return True
        
    def calculate_style_compliance(self, items: List[ClothingItem], style: Optional[str]) -> float:
        """Calculate style compliance score."""
        # Implementation will be moved from main service
        pass
        
    def calculate_occasion_appropriateness(self, items: List[ClothingItem], occasion: str) -> float:
        """Calculate occasion appropriateness score."""
        # Implementation will be moved from main service
        pass
        
    def calculate_color_harmony(self, items: List[ClothingItem]) -> str:
        """Calculate color harmony."""
        # Implementation will be moved from main service
        pass
