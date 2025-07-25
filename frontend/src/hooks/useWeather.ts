import { useState, useEffect } from 'react';
import { WeatherData } from '@/types/weather';

export function useWeather() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeather = async (retryCount = 0) => {
      try {
        setLoading(true);
        setError(null);

        // Get user's location with fallback
        let latitude = 40.7128; // Default to NYC
        let longitude = -74.0060;

        try {
          const position = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
              timeout: 10000, // 10 second timeout
              enableHighAccuracy: false, // Don't require high accuracy
            });
          });
          latitude = position.coords.latitude;
          longitude = position.coords.longitude;
          console.log("🌤️ Using geolocation:", { latitude, longitude });
        } catch (geoError) {
          console.warn('🌤️ Geolocation failed, using default coordinates:', geoError);
          // Continue with default coordinates
        }

        const requestBody = {
          location: `${latitude},${longitude}`,
        };
        
        console.log("🌤️ Fetching weather with:", requestBody);

        const response = await fetch('/api/weather', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        });

        console.log("🌤️ Weather API response status:", response.status);

        if (!response.ok) {
          const errorData = await response.json();
          console.error("🌤️ Weather API error:", errorData);
          throw new Error(errorData.error || errorData.details || 'Failed to fetch weather data');
        }

        const data = await response.json();
        console.log("🌤️ Weather data received:", data);
        
        if (data.fallback) {
          console.warn("🌤️ Using fallback weather data - backend may be unavailable");
        }
        
        setWeather(data);
      } catch (err) {
        console.error('🌤️ Error fetching weather:', err);
        
        // Retry logic for network errors
        if (retryCount < 2 && (err instanceof TypeError || (err instanceof Error && err.message.includes('fetch')))) {
          console.log(`🌤️ Retrying weather fetch (attempt ${retryCount + 1})...`);
          setTimeout(() => fetchWeather(retryCount + 1), 1000 * (retryCount + 1)); // Exponential backoff
          return;
        }
        
        setError(err instanceof Error ? err.message : 'Failed to fetch weather data');
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, []);

  return { weather, loading, error };
} 