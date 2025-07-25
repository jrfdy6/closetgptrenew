import type { WeatherData } from "../types/weather";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
const WEATHER_CACHE_KEY = 'weather_cache';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

interface WeatherCache {
  data: WeatherData;
  timestamp: number;
}

export async function getWeather(location?: string): Promise<WeatherData> {
  try {
    // Check cache first
    const cachedWeather = getCachedWeather();
    if (cachedWeather) {
      return cachedWeather;
    }

    // If no location provided, try to get user's location
    if (!location) {
      console.log("No location provided, getting user's location...");
      location = await getUserLocation();
      console.log("Got user location:", location);
    }

    console.log("Making weather request with location:", location);
    const response = await fetch(`${API_BASE_URL}/api/weather`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ location: location }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Weather API error response:", errorText);
      throw new Error(`Failed to fetch weather: ${response.statusText}`);
    }

    const data = await response.json();
    const weatherData = {
      temperature: data.temperature,
      condition: data.condition,
      location: data.location,
      humidity: data.humidity,
      wind_speed: data.wind_speed,
      precipitation: data.precipitation
    };

    // Cache the weather data
    cacheWeather(weatherData);

    return weatherData;
  } catch (error) {
    console.error("Error fetching weather:", error);
    throw error;
  }
}

async function getUserLocation(): Promise<string> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by your browser'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        // Return coordinates in the format "latitude,longitude"
        resolve(`${latitude},${longitude}`);
      },
      (error) => {
        reject(new Error('Unable to retrieve your location'));
      }
    );
  });
}

function getCachedWeather(): WeatherData | null {
  try {
    const cached = localStorage.getItem(WEATHER_CACHE_KEY);
    if (!cached) return null;

    const { data, timestamp }: WeatherCache = JSON.parse(cached);
    const now = Date.now();

    // Check if cache is still valid
    if (now - timestamp < CACHE_DURATION) {
      return data;
    }

    // Cache expired
    localStorage.removeItem(WEATHER_CACHE_KEY);
    return null;
  } catch (error) {
    console.error('Error reading weather cache:', error);
    return null;
  }
}

function cacheWeather(data: WeatherData): void {
  try {
    const cache: WeatherCache = {
      data,
      timestamp: Date.now()
    };
    localStorage.setItem(WEATHER_CACHE_KEY, JSON.stringify(cache));
  } catch (error) {
    console.error('Error caching weather data:', error);
  }
}

export function getWeatherIcon(condition: string): string {
  const icons: Record<string, string> = {
    'Clear': '☀️',
    'Clouds': '☁️',
    'Rain': '🌧️',
    'Drizzle': '🌦️',
    'Snow': '🌨️',
    'Mist': '🌫️',
    'Fog': '🌫️',
  };

  return icons[condition] || '❓';
}

export function formatTemperature(temp: number): string {
  return `${Math.round(temp)}°C`;
} 