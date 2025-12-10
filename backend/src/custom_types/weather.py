from pydantic import BaseModel
from typing import Optional, Dict, Any

class WeatherData(BaseModel):
    temperature: float
    condition: str
    humidity: float
    wind_speed: Optional[float] = None
    location: Optional[str] = None
    precipitation: float = 0.0
    
    # Location and timezone data (from OpenWeather API)
    timezone_offset: Optional[int] = None  # Seconds from UTC
    timezone: Optional[str] = None  # IANA timezone (e.g., "America/New_York")
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 40.7128, "lon": -74.0060}
    country: Optional[str] = None
    city_name: Optional[str] = None  # Official city name from API
    
    # Metadata
    fallback: bool = False
    error: Optional[str] = None
    last_updated: Optional[str] = None  # ISO timestamp of when weather was fetched

# Export types for use in other backend modules
__all__ = ['WeatherData'] 