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

router = APIRouter()

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
    fallback: bool = False
    error: str | None = None

@router.post("/weather")
async def get_weather(request: WeatherRequest):
    """
    Get current weather data for a location.
    Location can be a city name or coordinates (latitude,longitude).
    """
    try:
        def build_fallback(error_msg: str) -> WeatherData:
            logger.warning(f"Using fallback weather response: {error_msg}")
            return WeatherData(
                temperature=68.0,
                condition="Clear",
                humidity=55,
                wind_speed=3.0,
                location=request.location or "Unknown Location",
                precipitation=0.0,
                fallback=True,
                error=error_msg
            )

        # Get OpenWeather API key from environment
        api_key = os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
        if not api_key:
            return build_fallback("OpenWeather API key not configured")

        # Determine if location is coordinates or city name
        if "," in request.location:
            try:
                lat, lon = request.location.split(",")
                lat = float(lat.strip())
                lon = float(lon.strip())
                params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": api_key,
                    "units": "metric"  # Use metric for Celsius
                }
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid coordinates format")
        else:
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
                return build_fallback("Weather service timeout")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.error(f"Location not found: {request.location}")
                    raise HTTPException(status_code=404, detail="Location not found")
                elif e.response.status_code == 401:
                    logger.error("Invalid OpenWeather API key")
                    return build_fallback("Weather service configuration error")
                else:
                    logger.error(f"OpenWeather API error: {e.response.status_code}")
                    return build_fallback(f"Weather provider error {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"Network error while fetching weather: {str(e)}")
                return build_fallback("Network error while fetching weather data")

        # Extract relevant weather data
        weather_data = WeatherData(
            temperature=round((data["main"]["temp"] * 9/5) + 32, 1),  # Convert Celsius to Fahrenheit
            condition=data["weather"][0]["main"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            location=data["name"],
            precipitation=data.get("rain", {}).get("1h", 0.0),  # Get 1h rain if available
            fallback=False,
            error=None
        )

        return weather_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return WeatherData(
            temperature=68.0,
            condition="Clear",
            humidity=55,
            wind_speed=3.0,
            location=request.location or "Unknown Location",
            precipitation=0.0,
            fallback=True,
            error="Unexpected server error"
        )