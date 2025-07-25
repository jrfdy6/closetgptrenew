from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
from pathlib import Path
import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://closetgpt.com",
        "https://www.closetgpt.com",
        "https://app.closetgpt.com",
        "https://staging.closetgpt.com",
        "https://dev.closetgpt.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/api/weather")
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
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail="Location not found")
                raise HTTPException(status_code=500, detail="Error fetching weather data")
            except httpx.RequestError as e:
                logger.error(f"Network error: {str(e)}")
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))  # Use Railway's PORT or fallback to 8080 locally
    uvicorn.run(app, host="0.0.0.0", port=port) 