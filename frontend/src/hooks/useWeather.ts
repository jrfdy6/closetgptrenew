import { useState, useEffect, useCallback } from 'react';
import { WeatherData, WeatherRequest, UserLocation } from '@/types/weather';

interface UseWeatherOptions {
  location?: string;
  autoFetch?: boolean;
  fallbackLocation?: string;
}

interface UseWeatherReturn {
  weather: WeatherData | null;
  loading: boolean;
  error: string | null;
  fetchWeather: (location?: string) => Promise<void>;
  clearError: () => void;
  isStale: boolean;
  lastUpdated: Date | null;
}

const CACHE_DURATION = 10 * 60 * 1000; // 10 minutes
const FALLBACK_WEATHER: WeatherData = {
  temperature: 72,
  condition: "Clear",
  humidity: 65,
  wind_speed: 5,
  location: "Default Location",
  precipitation: 0,
  fallback: true
};

export function useWeather(options: UseWeatherOptions = {}): UseWeatherReturn {
  const { location, autoFetch = false, fallbackLocation = "New York, NY" } = options;
  
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Check if weather data is stale
  const isStale = lastUpdated ? (Date.now() - lastUpdated.getTime()) > CACHE_DURATION : true;

  const fetchWeather = useCallback(async (targetLocation?: string) => {
    const locationToUse = targetLocation || location || fallbackLocation;
    
    if (!locationToUse) {
      setError("No location provided");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log("🌤️ Fetching weather for:", locationToUse);
      
      const response = await fetch('/api/weather', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ location: locationToUse } as WeatherRequest),
      });

      if (!response.ok) {
        throw new Error(`Weather API error: ${response.status}`);
      }

      const weatherData: WeatherData = await response.json();
      console.log("🌤️ Weather data received:", weatherData);
      
      setWeather(weatherData);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      console.error("🌤️ Error fetching weather:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch weather");
      
      // Set fallback weather data
      setWeather(FALLBACK_WEATHER);
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  }, [location, fallbackLocation]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Auto-fetch weather on mount if enabled
  useEffect(() => {
    if (autoFetch && (!weather || isStale)) {
      fetchWeather();
    }
  }, [autoFetch, fetchWeather, weather, isStale]);

  // Get user's location if geolocation is available
  const getUserLocation = useCallback((): Promise<string> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error("Geolocation is not supported"));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          resolve(`${latitude},${longitude}`);
        },
        (error) => {
          console.warn("Geolocation error:", error);
          reject(error);
        },
        {
          timeout: 10000,
          maximumAge: 5 * 60 * 1000, // 5 minutes
          enableHighAccuracy: false
        }
      );
    });
  }, []);

  // Fetch weather using geolocation
  const fetchWeatherByLocation = useCallback(async () => {
    try {
      setLoading(true);
      const coordinates = await getUserLocation();
      await fetchWeather(coordinates);
    } catch (err) {
      console.warn("Could not get user location, using fallback:", err);
      await fetchWeather(fallbackLocation);
    }
  }, [fetchWeather, getUserLocation, fallbackLocation]);

  return {
    weather,
    loading,
    error,
    fetchWeather,
    clearError,
    isStale,
    lastUpdated,
    // Additional utility methods
    fetchWeatherByLocation,
    getUserLocation,
  } as UseWeatherReturn & {
    fetchWeatherByLocation: () => Promise<void>;
    getUserLocation: () => Promise<string>;
  };
}

// Hook for getting weather with automatic location detection
export function useAutoWeather(): UseWeatherReturn & {
  fetchWeatherByLocation: () => Promise<void>;
} {
  const weatherHook = useWeather({ autoFetch: true });
  
  const fetchWeatherByLocation = useCallback(async () => {
    try {
      // First, check if user has saved a preferred location
      const savedLocation = localStorage.getItem('user-location');
      if (savedLocation) {
        console.log("🌤️ Using saved location:", savedLocation);
        await weatherHook.fetchWeather(savedLocation);
        return;
      }

      // If no saved location, try geolocation
      if (!navigator.geolocation) {
        throw new Error("Geolocation not supported");
      }

      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          timeout: 10000,
          maximumAge: 5 * 60 * 1000,
          enableHighAccuracy: false
        });
      });

      const { latitude, longitude } = position.coords;
      await weatherHook.fetchWeather(`${latitude},${longitude}`);
    } catch (err) {
      console.warn("Could not get location, using fallback:", err);
      await weatherHook.fetchWeather("New York, NY");
    }
  }, [weatherHook.fetchWeather]);

  return {
    ...weatherHook,
    fetchWeatherByLocation
  };
}

// Hook for specific location weather
export function useLocationWeather(location: string): UseWeatherReturn {
  return useWeather({ location, autoFetch: true });
}
