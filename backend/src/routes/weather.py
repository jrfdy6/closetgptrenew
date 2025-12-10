from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import logging
import httpx
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional, Dict, Any

# Import custom types and services
from ..custom_types.weather import WeatherData
from ..auth.auth_service import get_current_user_optional
from ..custom_types.profile import UserProfile
from ..services.profile_service import update_user_location_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api", tags=["weather"])

# Try to import timezonefinder for IANA timezone conversion
try:
    from timezonefinder import TimezoneFinder
    TF = TimezoneFinder()
    HAS_TIMEZONEFINDER = True
except ImportError:
    HAS_TIMEZONEFINDER = False
    logger.warning("timezonefinder not installed - will use offset only")

# Weather API models
class WeatherRequest(BaseModel):
    location: str

@router.post("/weather")
async def get_weather(
    request: WeatherRequest,
    current_user: Optional[UserProfile] = Depends(get_current_user_optional)
):
    """
    Get current weather data for a location.
    Location can be a city name or coordinates (latitude,longitude).
    
    If user is authenticated, stores location/timezone data in their profile.
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
                error=error_msg,
                timezone_offset=None,
                timezone=None,
                coordinates=None,
                country=None,
                city_name=None,
                last_updated=datetime.now().isoformat()
            )

        # Get OpenWeather API key from environment
        api_key = os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API_KEY")
        if not api_key:
            return build_fallback("OpenWeather API key not configured")

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
                logger.info(f"Weather data retrieved successfully for {(data.get('name', 'unknown location') if data else 'unknown location')}")
            except httpx.TimeoutException:
                logger.error("Timeout while fetching weather data")
                return build_fallback("Weather service timeout")
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
                            logger.info(f"Fallback successful for {(data.get('name', 'unknown location') if data else 'unknown location')}")
                        except httpx.HTTPStatusError:
                            logger.error(f"Location not found even with fallback: {request.location}")
                            raise HTTPException(status_code=404, detail="Location not found")
                    else:
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

        # Extract ALL relevant data from OpenWeather response
        timezone_offset = data.get('timezone')  # Offset in seconds from UTC
        coordinates = None
        iana_timezone = None
        
        # Extract coordinates
        if 'coord' in data:
            lat = data['coord'].get('lat')
            lon = data['coord'].get('lon')
            if lat is not None and lon is not None:
                coordinates = {"lat": float(lat), "lon": float(lon)}
                
                # Convert coordinates to IANA timezone
                if HAS_TIMEZONEFINDER:
                    try:
                        iana_timezone = TF.timezone_at(lat=lat, lng=lon)
                        logger.info(f"Detected IANA timezone: {iana_timezone} for coordinates ({lat}, {lon})")
                    except Exception as e:
                        logger.warning(f"Could not determine IANA timezone: {e}")
        
        # Extract country
        country = None
        if 'sys' in data:
            country = data['sys'].get('country')
        
        # Extract official city name
        city_name = data.get('name')
        
        # Build WeatherData with all extracted information
        weather_data = WeatherData(
            temperature=round((data["main"]["temp"] * 9/5) + 32, 1),  # Convert Celsius to Fahrenheit
            condition=data["weather"][0]["main"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            location=city_name or request.location,
            precipitation=(data.get("rain", {}) if data else {}).get("1h", 0.0),
            fallback=False,
            error=None,
            timezone_offset=timezone_offset,
            timezone=iana_timezone,
            coordinates=coordinates,
            country=country,
            city_name=city_name,
            last_updated=datetime.now().isoformat()
        )

        # Store location/timezone data in user profile if authenticated
        if current_user:
            try:
                # Update user profile with location/timezone data
                await update_user_location_data(
                    user_id=current_user.id,
                    location_data={
                        'timezone_offset': timezone_offset,
                        'timezone': iana_timezone,
                        'coordinates': coordinates,
                        'country': country,
                        'city_name': city_name,
                        'last_location': request.location,
                        'last_weather_fetch': datetime.now().isoformat()
                    }
                )
                logger.info(f"✅ Updated location/timezone data for user {current_user.id}")
            except Exception as e:
                logger.warning(f"Could not update user location data: {e}")
                # Don't fail the request if profile update fails

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
            error="Unexpected server error",
            timezone_offset=None,
            timezone=None,
            coordinates=None,
            country=None,
            city_name=None,
            last_updated=datetime.now().isoformat()
        )