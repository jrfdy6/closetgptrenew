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
        api_key = os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
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
            # For city names, try the original format first
            query_location = request.location
            
            # If it's a US city with state (e.g., "New York, NY"), also try without state
            # OpenWeather sometimes doesn't recognize "City, State" format for US cities
            if ", " in request.location and len(request.location.split(", ")[1]) == 2:
                # Looks like "City, State" format - try city only as backup
                city_only = request.location.split(", ")[0]
                logger.info(f"US city format detected: {request.location}, will try '{city_only}' if needed")
            
            params = {
                "q": query_location,
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
                    # Try fallback for US cities (City, State -> City)
                    if not is_coordinates and ", " in request.location and len(request.location.split(", ")[1]) == 2:
                        city_only = request.location.split(", ")[0]
                        logger.info(f"Retrying with city only: {city_only}")
                        
                        try:
                            fallback_params = {
                                "q": city_only,
                                "appid": api_key,
                                "units": "metric"
                            }
                            fallback_response = await client.get(
                                "https://api.openweathermap.org/data/2.5/weather",
                                params=fallback_params
                            )
                            fallback_response.raise_for_status()
                            data = fallback_response.json()
                            logger.info(f"Fallback successful for {data.get('name', 'unknown location')}")
                        except httpx.HTTPStatusError:
                            logger.error(f"Location not found even with fallback: {request.location}")
                            raise HTTPException(status_code=404, detail="Location not found")
                    else:
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