from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import logging
import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api", tags=["weather"])

# Weather API models
class WeatherRequest(BaseModel):
    location: str

class WeatherData(BaseModel):
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    location: str
    precipitation: float = 0.0

@router.post("/weather")
async def get_weather(request: WeatherRequest):
    """
    Get current weather data for a location.
    Location can be a city name or coordinates (latitude,longitude).
    """
    try:
        # Get OpenWeather API key from environment
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenWeather API key not configured")

        # Determine if location is coordinates or city name
        # Check if it looks like coordinates (numbers with comma)
        is_coordinates = False
        if "," in request.location:
            parts = request.location.split(",")
            if len(parts) == 2:
                try:
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    # Valid coordinate ranges: lat [-90, 90], lon [-180, 180]
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        is_coordinates = True
                        params = {
                            "lat": lat,
                            "lon": lon,
                            "appid": api_key,
                            "units": "metric"  # Use metric for Celsius
                        }
                except ValueError:
                    # Not coordinates, treat as city name
                    is_coordinates = False
        
        if not is_coordinates:
            params = {
                "q": request.location,
                "appid": api_key,
                "units": "metric"  # Use metric for Celsius
            }

        # Make request to OpenWeather API
        async with httpx.AsyncClient(timeout=10.0) as client:  # 10 second timeout
            try:
                logger.info(f"Fetching weather for location: {request.location}")
                response = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"Weather data retrieved successfully for {data.get('name', 'unknown location')}")
            except httpx.TimeoutException:
                logger.error("Timeout while fetching weather data")
                raise HTTPException(status_code=500, detail="Weather service timeout")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.error(f"Location not found: {request.location}")
                    raise HTTPException(status_code=404, detail="Location not found")
                elif e.response.status_code == 401:
                    logger.error("Invalid OpenWeather API key")
                    raise HTTPException(status_code=500, detail="Weather service configuration error")
                else:
                    logger.error(f"OpenWeather API error: {e.response.status_code}")
                    raise HTTPException(status_code=500, detail="Error fetching weather data")
            except httpx.RequestError as e:
                logger.error(f"Network error while fetching weather: {str(e)}")
                raise HTTPException(status_code=500, detail="Network error while fetching weather data")

        # Extract relevant weather data
        weather_data = WeatherData(
            temperature=round((data["main"]["temp"] * 9/5) + 32, 1),  # Convert Celsius to Fahrenheit
            condition=data["weather"][0]["main"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            location=data["name"],
            precipitation=data.get("rain", {}).get("1h", 0.0)  # Get 1h rain if available
        )

        return weather_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 