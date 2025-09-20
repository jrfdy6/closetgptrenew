"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MapPin, Navigation, X } from 'lucide-react';

interface LocationUpdatePromptProps {
  onLocationUpdate: (location: string) => void;
  onDismiss: () => void;
  currentLocation?: string;
}

export function LocationUpdatePrompt({ 
  onLocationUpdate, 
  onDismiss, 
  currentLocation = "Unknown Location" 
}: LocationUpdatePromptProps) {
  const [location, setLocation] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  const handleUpdateLocation = async () => {
    if (!location.trim()) return;
    
    setIsUpdating(true);
    try {
      // Save to localStorage
      localStorage.setItem('user-location', location.trim());
      onLocationUpdate(location.trim());
    } catch (error) {
      console.error('Error saving location:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleUseCurrentLocation = async () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by this browser.');
      return;
    }

    setIsUpdating(true);
    try {
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          timeout: 10000,
          maximumAge: 5 * 60 * 1000,
          enableHighAccuracy: false
        });
      });

      const { latitude, longitude } = position.coords;
      const coordinates = `${latitude},${longitude}`;
      
      // Save coordinates to localStorage
      localStorage.setItem('user-location', coordinates);
      onLocationUpdate(coordinates);
    } catch (error) {
      console.error('Error getting location:', error);
      alert('Could not get your current location. Please enter it manually.');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto border-amber-200 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-800">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MapPin className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            <CardTitle className="text-lg text-amber-900 dark:text-amber-100">
              Update Your Location
            </CardTitle>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onDismiss}
            className="h-6 w-6 p-0 text-amber-600 hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-200"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <CardDescription className="text-amber-700 dark:text-amber-300">
          Get accurate weather data for better outfit recommendations
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {currentLocation && currentLocation !== "Unknown Location" && (
          <div className="text-sm text-amber-800 dark:text-amber-200">
            Current location: <span className="font-medium">{currentLocation}</span>
          </div>
        )}
        
        <div className="space-y-3">
          <div className="space-y-2">
            <label htmlFor="location-input" className="text-sm font-medium text-amber-900 dark:text-amber-100">
              Enter your city or location:
            </label>
            <Input
              id="location-input"
              type="text"
              placeholder="e.g., San Francisco, CA or London, UK"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="border-amber-300 focus:border-amber-500 focus:ring-amber-500"
              onKeyDown={(e) => e.key === 'Enter' && handleUpdateLocation()}
            />
          </div>
          
          <div className="flex gap-2">
            <Button
              onClick={handleUpdateLocation}
              disabled={!location.trim() || isUpdating}
              className="flex-1 bg-amber-600 hover:bg-amber-700 text-white"
            >
              {isUpdating ? 'Updating...' : 'Update Location'}
            </Button>
            
            <Button
              onClick={handleUseCurrentLocation}
              disabled={isUpdating}
              variant="outline"
              className="border-amber-300 text-amber-700 hover:bg-amber-100 dark:border-amber-600 dark:text-amber-300 dark:hover:bg-amber-900/20"
            >
              <Navigation className="h-4 w-4 mr-2" />
              Use GPS
            </Button>
          </div>
        </div>
        
        <p className="text-xs text-amber-600 dark:text-amber-400">
          Your location helps us provide accurate weather data for outfit recommendations. 
          We don't store precise coordinates permanently.
        </p>
      </CardContent>
    </Card>
  );
}
