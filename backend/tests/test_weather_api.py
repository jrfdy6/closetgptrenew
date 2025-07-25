import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import httpx
from app import app
from typing import Dict, Any, List, Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = TestClient(app)

# Type definitions for better code understanding
WeatherResponse = Dict[str, Any]
TemperatureTestCase = Tuple[float, float]  # (celsius, fahrenheit)

# Mock response data with TypeScript-like structure
MOCK_WEATHER_RESPONSE: WeatherResponse = {
    "weather": [{"main": "Clear", "description": "clear sky"}],
    "main": {
        "temp": 20.0,  # 20°C
        "feels_like": 19.5,
        "temp_min": 18.0,
        "temp_max": 22.0,
        "pressure": 1015,
        "humidity": 65
    },
    "wind": {
        "speed": 5.5,
        "deg": 280
    },
    "rain": {
        "1h": 0.0
    },
    "name": "London",
    "sys": {
        "country": "GB"
    }
}

def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius to Fahrenheit.
    Formula: °F = (°C × 9/5) + 32
    
    Args:
        celsius: Temperature in Celsius
        
    Returns:
        Temperature in Fahrenheit, rounded to 1 decimal place
    """
    return round((celsius * 9/5) + 32, 1)

def create_mock_response(status_code: int = 200, json_data: WeatherResponse = None) -> httpx.Response:
    """
    Create a mock response with a request instance.
    
    Args:
        status_code: HTTP status code
        json_data: Response data in OpenWeather API format
        
    Returns:
        Mocked httpx.Response with request instance
    """
    if json_data is None:
        json_data = MOCK_WEATHER_RESPONSE
    response = httpx.Response(
        status_code=status_code,
        json=json_data
    )
    mock_request = AsyncMock()
    response._request = mock_request
    return response

@pytest.fixture
def mock_httpx_client():
    """Fixture to mock httpx.AsyncClient for testing."""
    with patch("httpx.AsyncClient") as mock:
        mock_client = AsyncMock()
        mock.return_value.__aenter__.return_value = mock_client
        yield mock_client

class TestWeatherAPI:
    """Test suite for the Weather API endpoints."""

    @pytest.mark.real_api
    def test_real_weather_by_city(self):
        """Test getting weather by city name using real OpenWeather API."""
        response = client.post(
            "/api/weather",
            json={"location": "London"}
        )

        assert response.status_code == 200
        data = response.json()
        
        # Verify the response structure
        assert "temperature" in data
        assert "condition" in data
        assert "humidity" in data
        assert "wind_speed" in data
        assert "location" in data
        assert "precipitation" in data
        
        # Verify data types
        assert isinstance(data["temperature"], float)
        assert isinstance(data["condition"], str)
        assert isinstance(data["humidity"], int)
        assert isinstance(data["wind_speed"], float)
        assert isinstance(data["location"], str)
        assert isinstance(data["precipitation"], float)
        
        # Verify reasonable ranges
        assert -50 <= data["temperature"] <= 120  # Reasonable temperature range in Fahrenheit
        assert 0 <= data["humidity"] <= 100
        assert data["wind_speed"] >= 0
        assert data["precipitation"] >= 0

    @pytest.mark.real_api
    def test_real_weather_by_coordinates(self):
        """Test getting weather by coordinates using real OpenWeather API."""
        response = client.post(
            "/api/weather",
            json={"location": "51.5074,-0.1278"}  # London coordinates
        )

        assert response.status_code == 200
        data = response.json()
        
        # Verify the response structure
        assert "temperature" in data
        assert "condition" in data
        assert "humidity" in data
        assert "wind_speed" in data
        assert "location" in data
        assert "precipitation" in data
        
        # Verify data types
        assert isinstance(data["temperature"], float)
        assert isinstance(data["condition"], str)
        assert isinstance(data["humidity"], int)
        assert isinstance(data["wind_speed"], float)
        assert isinstance(data["location"], str)
        assert isinstance(data["precipitation"], float)
        
        # Verify reasonable ranges
        assert -50 <= data["temperature"] <= 120  # Reasonable temperature range in Fahrenheit
        assert 0 <= data["humidity"] <= 100
        assert data["wind_speed"] >= 0
        assert data["precipitation"] >= 0

    @pytest.mark.real_api
    def test_real_weather_multiple_cities(self):
        """Test getting weather for multiple cities using real OpenWeather API."""
        cities = [
            "New York",
            "Tokyo",
            "Sydney",
            "Paris",
            "Dubai"
        ]
        
        for city in cities:
            response = client.post(
                "/api/weather",
                json={"location": city}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify the response structure
            assert "temperature" in data
            assert "condition" in data
            assert "humidity" in data
            assert "wind_speed" in data
            assert "location" in data
            assert "precipitation" in data
            
            # Verify data types
            assert isinstance(data["temperature"], float)
            assert isinstance(data["condition"], str)
            assert isinstance(data["humidity"], int)
            assert isinstance(data["wind_speed"], float)
            assert isinstance(data["location"], str)
            assert isinstance(data["precipitation"], float)
            
            # Verify reasonable ranges
            assert -50 <= data["temperature"] <= 120  # Reasonable temperature range in Fahrenheit
            assert 0 <= data["humidity"] <= 100
            assert data["wind_speed"] >= 0
            assert data["precipitation"] >= 0

    def test_get_weather_by_city(self, mock_httpx_client):
        """Test getting weather by city name with mock data."""
        mock_httpx_client.get.return_value = create_mock_response()

        response = client.post(
            "/api/weather",
            json={"location": "London"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] == celsius_to_fahrenheit(20.0)  # 20°C = 68.0°F
        assert data["condition"] == "Clear"
        assert data["humidity"] == 65
        assert data["wind_speed"] == 5.5
        assert data["location"] == "London"
        assert data["precipitation"] == 0.0

        # Verify the API call
        mock_httpx_client.get.assert_called_once()
        call_args = mock_httpx_client.get.call_args[1]
        assert call_args["params"]["q"] == "London"
        assert call_args["params"]["units"] == "metric"

    def test_get_weather_by_coordinates(self, mock_httpx_client):
        """Test getting weather by coordinates."""
        mock_httpx_client.get.return_value = create_mock_response()

        response = client.post(
            "/api/weather",
            json={"location": "51.5074,-0.1278"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] == celsius_to_fahrenheit(20.0)
        assert data["location"] == "London"  # OpenWeather returns the city name for coordinates

        # Verify the API call
        mock_httpx_client.get.assert_called_once()
        call_args = mock_httpx_client.get.call_args[1]
        assert call_args["params"]["lat"] == 51.5074
        assert call_args["params"]["lon"] == -0.1278

    def test_temperature_conversion_edge_cases(self, mock_httpx_client):
        """Test temperature conversion for edge cases."""
        test_cases: List[TemperatureTestCase] = [
            (0, 32.0),      # Freezing point of water
            (20, 68.0),     # Room temperature
            (-10, 14.0),    # Cold winter day
            (100, 212.0),   # Boiling point of water
            (-40, -40.0),   # Where Celsius equals Fahrenheit
            (37, 98.6),     # Human body temperature
            (-273.15, -459.7),  # Absolute zero
            (1000, 1832.0),  # Extreme heat
        ]

        for celsius, expected_fahrenheit in test_cases:
            mock_response = MOCK_WEATHER_RESPONSE.copy()
            mock_response["main"]["temp"] = celsius
            mock_httpx_client.get.return_value = create_mock_response(json_data=mock_response)

            response = client.post(
                "/api/weather",
                json={"location": "London"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["temperature"] == expected_fahrenheit, \
                f"Failed to convert {celsius}°C to {expected_fahrenheit}°F"

    def test_weather_with_rain(self, mock_httpx_client):
        """Test getting weather data with rain."""
        mock_response = MOCK_WEATHER_RESPONSE.copy()
        mock_response["rain"] = {"1h": 2.5}
        mock_httpx_client.get.return_value = create_mock_response(json_data=mock_response)

        response = client.post(
            "/api/weather",
            json={"location": "London"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["precipitation"] == 2.5

    def test_weather_without_rain(self, mock_httpx_client):
        """Test getting weather data without rain data."""
        mock_response = MOCK_WEATHER_RESPONSE.copy()
        mock_response.pop("rain", None)
        mock_httpx_client.get.return_value = create_mock_response(json_data=mock_response)

        response = client.post(
            "/api/weather",
            json={"location": "London"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["precipitation"] == 0.0

    def test_invalid_location(self, mock_httpx_client):
        """Test getting weather with an invalid location."""
        mock_httpx_client.get.return_value = create_mock_response(
            status_code=404,
            json_data={"message": "city not found"}
        )

        response = client.post(
            "/api/weather",
            json={"location": "InvalidCity123"}
        )

        assert response.status_code == 404

    def test_api_error(self, mock_httpx_client):
        """Test handling of API errors."""
        mock_httpx_client.get.return_value = create_mock_response(
            status_code=401,
            json_data={"message": "Invalid API key"}
        )

        response = client.post(
            "/api/weather",
            json={"location": "London"}
        )

        assert response.status_code == 500

    def test_network_error(self, mock_httpx_client):
        """Test handling of network errors."""
        mock_httpx_client.get.side_effect = httpx.RequestError("Network error")

        response = client.post(
            "/api/weather",
            json={"location": "London"}
        )

        assert response.status_code == 500

    def test_invalid_coordinates(self, mock_httpx_client):
        """Test getting weather with invalid coordinates format."""
        response = client.post(
            "/api/weather",
            json={"location": "invalid,coordinates"}
        )

        assert response.status_code == 400

    def test_missing_location(self):
        """Test getting weather without providing a location."""
        response = client.post(
            "/api/weather",
            json={}
        )

        assert response.status_code == 422  # Validation error 