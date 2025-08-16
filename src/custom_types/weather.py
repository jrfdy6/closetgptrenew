from pydantic import BaseModel
from typing import Optional

class WeatherData(BaseModel):
    temperature: float
    condition: str
    humidity: float
    wind_speed: Optional[float] = None
    location: Optional[str] = None
    precipitation: float = 0.0

# Export types for use in other backend modules
__all__ = ['WeatherData'] 