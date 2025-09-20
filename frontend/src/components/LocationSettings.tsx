"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { MapPin, Navigation, Save, AlertCircle, CheckCircle } from 'lucide-react';
import { useAutoWeather } from '@/hooks/useWeather';

interface LocationSettingsProps {
  onLocationChange?: (location: string) => void;
  className?: string;
}

export function LocationSettings({ onLocationChange, className }: LocationSettingsProps) {
  const [location, setLocation] = useState('');
  const [isDetecting, setIsDetecting] = useState(false);
  const [savedLocation, setSavedLocation] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { fetchWeatherByLocation } = useAutoWeather();

  // Load saved location from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('user-location');
    if (saved) {
      setSavedLocation(saved);
      setLocation(saved);
    }
  }, []);

  const detectLocation = async () => {
    setIsDetecting(true);
    setError(null);

    try {
      if (!navigator.geolocation) {
        throw new Error('Geolocation is not supported by this browser');
      }

      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
          resolve,
          reject,
          {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 5 * 60 * 1000 // 5 minutes
          }
        );
      });

      const { latitude, longitude } = position.coords;
      const coordinates = `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
      
      setLocation(coordinates);
      
      // Test the coordinates by fetching weather
      await fetchWeatherByLocation();
      
    } catch (err) {
      console.error('Location detection error:', err);
      if (err instanceof GeolocationPositionError) {
        switch (err.code) {
          case err.PERMISSION_DENIED:
            setError('Location access denied. Please enable location permissions.');
            break;
          case err.POSITION_UNAVAILABLE:
            setError('Location information unavailable.');
            break;
          case err.TIMEOUT:
            setError('Location detection timed out.');
            break;
          default:
            setError('An unknown error occurred while detecting location.');
            break;
        }
      } else {
        setError(err instanceof Error ? err.message : 'Failed to detect location');
      }
    } finally {
      setIsDetecting(false);
    }
  };

  const saveLocation = () => {
    if (!location.trim()) {
      setError('Please enter a location');
      return;
    }

    try {
      localStorage.setItem('user-location', location.trim());
      setSavedLocation(location.trim());
      setError(null);
      
      // Notify parent component
      onLocationChange?.(location.trim());
      
      // Test the location by fetching weather
      fetchWeatherByLocation();
      
    } catch (err) {
      setError('Failed to save location');
    }
  };

  const clearLocation = () => {
    localStorage.removeItem('user-location');
    setSavedLocation(null);
    setLocation('');
    setError(null);
    onLocationChange?.('');
  };

  return (
    <Card className={className}>
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-medium flex items-center gap-2">
          <MapPin className="h-5 w-5" />
          Location Settings
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="location" className="text-sm font-medium">
            Your Location
          </Label>
          <div className="flex gap-2">
            <Input
              id="location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Enter city name or coordinates"
              className="flex-1"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={detectLocation}
              disabled={isDetecting}
              className="flex items-center gap-1"
            >
              <Navigation className={`h-4 w-4 ${isDetecting ? 'animate-spin' : ''}`} />
              {isDetecting ? 'Detecting...' : 'Auto'}
            </Button>
          </div>
          <p className="text-xs text-gray-500">
            Use city name (e.g., "New York, NY") or coordinates (e.g., "40.7128, -74.0060")
          </p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <span className="text-sm text-red-600 dark:text-red-400">{error}</span>
          </div>
        )}

        {savedLocation && (
          <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm text-green-600 dark:text-green-400">
              Location saved: {savedLocation}
            </span>
          </div>
        )}

        <div className="flex gap-2">
          <Button
            onClick={saveLocation}
            disabled={!location.trim() || location.trim() === savedLocation}
            className="flex items-center gap-1"
          >
            <Save className="h-4 w-4" />
            Save Location
          </Button>
          
          {savedLocation && (
            <Button
              variant="outline"
              onClick={clearLocation}
              className="text-red-600 hover:text-red-700"
            >
              Clear
            </Button>
          )}
        </div>

        <div className="text-xs text-gray-500 space-y-1">
          <p>• Your location is used to provide accurate weather data for outfit recommendations</p>
          <p>• Location data is stored locally in your browser</p>
          <p>• You can update your location anytime</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default LocationSettings;
