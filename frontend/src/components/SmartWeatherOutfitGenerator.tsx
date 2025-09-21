"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  MapPin, 
  Navigation, 
  RefreshCw, 
  Sparkles, 
  Shirt, 
  AlertCircle,
  CheckCircle,
  Clock,
  Thermometer,
  Wind,
  Droplets,
  Sun,
  Cloud,
  Zap,
  Calendar,
  Eye,
  Heart
} from 'lucide-react';
import { useAutoWeather } from '@/hooks/useWeather';
import { formatWeatherForDisplay, getClothingRecommendations } from '@/lib/weather';
import { useAuthContext } from '@/contexts/AuthContext';

interface SmartWeatherOutfitGeneratorProps {
  className?: string;
  onOutfitGenerated?: (outfit: any) => void;
}

interface GeneratedOutfit {
  id: string;
  name: string;
  items: Array<{
    id: string;
    name: string;
    type: string;
    color: string;
    image?: string;
    imageUrl?: string;
    material?: string;
    brand?: string;
  }>;
  weather: {
    temperature: number;
    condition: string;
    location: string;
  };
  reasoning: string;
  confidence: number;
  generatedAt: string;
  isWorn?: boolean;
}

export function SmartWeatherOutfitGenerator({ 
  className, 
  onOutfitGenerated 
}: SmartWeatherOutfitGeneratorProps) {
  const { user } = useAuthContext();
  const { weather, loading: weatherLoading, fetchWeatherByLocation, error: weatherError } = useAutoWeather();
  
  // Debug logging
  console.log('🔍 SmartWeatherOutfitGenerator mounted:', {
    user: !!user,
    weather: !!weather,
    weatherLoading,
    weatherError
  });
  
  const [locationStatus, setLocationStatus] = useState<'idle' | 'requesting' | 'granted' | 'denied'>('idle');
  const [isGeneratingOutfit, setIsGeneratingOutfit] = useState(false);
  const [isWearingOutfit, setIsWearingOutfit] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<GeneratedOutfit | null>(null);
  const [outfitError, setOutfitError] = useState<string | null>(null);
  const [lastGenerated, setLastGenerated] = useState<Date | null>(null);
  const [todayKey, setTodayKey] = useState<string>('');

  // Initialize today's key for daily outfit generation
  useEffect(() => {
    const today = new Date().toDateString();
    setTodayKey(today);
  }, []);

  // Auto-detect location and fetch weather on component mount
  useEffect(() => {
    const initializeWeatherAndLocation = async () => {
      // Check if we have saved location
      const savedLocation = localStorage.getItem('user-location');
      if (savedLocation) {
        console.log("🌤️ Using saved location:", savedLocation);
        await fetchWeatherByLocation();
        return;
      }

      // Auto-request location permission if not saved
      if (navigator.geolocation && locationStatus === 'idle') {
        requestLocationPermission();
      }
    };

    initializeWeatherAndLocation();
  }, []);

  // Auto-generate outfit once per day when weather is available
  useEffect(() => {
    if (weather && user && !generatedOutfit && todayKey) {
      const storedOutfit = getTodaysOutfit();
      if (storedOutfit) {
        // Check if stored outfit is a fallback (low confidence, no items, or fallback name)
        const isFallback = storedOutfit.confidence <= 0.6 || 
                          !storedOutfit.items || 
                          storedOutfit.items.length === 0 || 
                          storedOutfit.name.includes('Weather-Appropriate');
        
        if (isFallback) {
          console.log('🗑️ Clearing cached fallback outfit, regenerating with real backend...');
          clearTodaysOutfit();
          generateTodaysOutfit();
        } else {
          console.log('📅 Loading today\'s outfit from storage:', storedOutfit);
          setGeneratedOutfit(storedOutfit);
          setLastGenerated(new Date(storedOutfit.generatedAt));
        }
      } else {
        console.log('🎯 Auto-generating today\'s weather outfit...');
        generateTodaysOutfit();
      }
    }
  }, [weather, user, todayKey]);

  // Helper functions for daily outfit management
  const getTodaysOutfit = (): GeneratedOutfit | null => {
    if (!todayKey) return null;
    try {
      const stored = localStorage.getItem(`daily-outfit-${todayKey}`);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Error loading today\'s outfit:', error);
      return null;
    }
  };

  const saveTodaysOutfit = (outfit: GeneratedOutfit) => {
    if (!todayKey) return;
    try {
      localStorage.setItem(`daily-outfit-${todayKey}`, JSON.stringify(outfit));
      console.log('💾 Saved today\'s outfit to storage');
    } catch (error) {
      console.error('Error saving today\'s outfit:', error);
    }
  };

  const clearTodaysOutfit = () => {
    if (!todayKey) return;
    try {
      localStorage.removeItem(`daily-outfit-${todayKey}`);
      console.log('🗑️ Cleared today\'s cached outfit');
      setGeneratedOutfit(null);
      setLastGenerated(null);
    } catch (error) {
      console.error('Error clearing today\'s outfit:', error);
    }
  };

  const requestLocationPermission = async () => {
    setLocationStatus('requesting');
    
    try {
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
      
      // Save location
      localStorage.setItem('user-location', coordinates);
      setLocationStatus('granted');
      
      // Fetch weather for this location
      await fetchWeatherByLocation();
      
    } catch (error) {
      console.warn('Location permission denied or failed:', error);
      setLocationStatus('denied');
      
      // Fallback to default location
      localStorage.setItem('user-location', 'New York, NY');
      await fetchWeatherByLocation();
    }
  };

  const generateTodaysOutfit = async () => {
    if (!user) {
      setOutfitError('Please sign in to generate outfits');
      return;
    }

    if (!weather) {
      setOutfitError('Weather data not available');
      return;
    }

    setIsGeneratingOutfit(true);
    setOutfitError(null);

    try {
      console.log('🎯 Auto-generating today\'s weather-perfect outfit for:', weather);
      
      // Get Firebase ID token for authentication
      const token = await user.getIdToken();
      
      // Fetch wardrobe items first
      console.log('📦 Fetching wardrobe items for outfit generation...');
      let wardrobeItems: any[] = [];
      
      try {
        const wardrobeResponse = await fetch('/api/wardrobe', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (wardrobeResponse.ok) {
          const wardrobeData = await wardrobeResponse.json();
          wardrobeItems = Array.isArray(wardrobeData) ? wardrobeData : (wardrobeData as any)?.items || [];
          console.log(`✅ Fetched ${wardrobeItems.length} wardrobe items for outfit generation`);
        } else {
          console.warn('⚠️ Failed to fetch wardrobe items, using empty array');
        }
      } catch (wardrobeError) {
        console.error('❌ Error fetching wardrobe items:', wardrobeError);
      }
      
      // Prepare request with weather-optimized parameters
      const requestData = {
        occasion: determineOccasionFromWeather(weather),
        style: determineStyleFromWeather(weather),
        mood: determineMoodFromWeather(weather),
        weather: weather,
        wardrobe: wardrobeItems, // Send actual wardrobe items
        user_profile: {
          id: user.uid,
          name: user.displayName || "User",
          email: user.email || "",
        },
        likedOutfits: [],
        trendingStyles: [],
        preferences: {
          weatherOptimized: true,
          autoGenerated: true,
          temperature: weather.temperature,
          condition: weather.condition
        }
      };

      console.log('🌤️ Auto-generating outfit with weather data:', {
        temperature: weather.temperature,
        condition: weather.condition,
        location: weather.location,
        occasion: requestData.occasion,
        style: requestData.style,
        mood: requestData.mood
      });

      const response = await fetch('/api/outfits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Backend error response:', response.status, errorText);
        
        // Create fallback outfit when backend fails
        const fallbackOutfit: GeneratedOutfit = {
          id: `fallback-outfit-${Date.now()}`,
          name: `Weather-Appropriate ${weather.condition} Look`,
          items: [], // Empty items array - will show recommendations instead
          weather: {
            temperature: weather.temperature,
            condition: weather.condition,
            location: weather.location
          },
          reasoning: `This outfit recommendation is based on ${weather.temperature}°F ${weather.condition.toLowerCase()} weather in ${weather.location}. The backend outfit generation is temporarily unavailable, but here are weather-appropriate clothing recommendations based on current conditions.`,
          confidence: 0.6,
          generatedAt: new Date().toISOString(),
          isWorn: false
        };

        setGeneratedOutfit(fallbackOutfit);
        setLastGenerated(new Date());
        saveTodaysOutfit(fallbackOutfit);
        setOutfitError('Backend temporarily unavailable - showing weather recommendations instead');
        return;
      }

      const outfitData = await response.json();
      console.log('✅ Today\'s weather-perfect outfit generated:', outfitData);
      
      // Transform the response into our format
      const outfit: GeneratedOutfit = {
        id: outfitData.id || `daily-outfit-${Date.now()}`,
        name: `Today's Perfect Weather Outfit`,
        items: outfitData.items || [],
        weather: {
          temperature: weather.temperature,
          condition: weather.condition,
          location: weather.location
        },
        reasoning: outfitData.reasoning || `This weather-optimized outfit is perfect for today's ${weather.temperature}°F ${weather.condition.toLowerCase()} conditions in ${weather.location}. The carefully selected pieces balance comfort and style while ensuring weather appropriateness. Each item works harmoniously to create a cohesive look that matches the current environmental conditions.`,
        confidence: outfitData.confidence || 0.9,
        generatedAt: new Date().toISOString(),
        isWorn: false
      };

      setGeneratedOutfit(outfit);
      setLastGenerated(new Date());
      saveTodaysOutfit(outfit);
      onOutfitGenerated?.(outfit);

    } catch (error) {
      console.error('❌ Error generating today\'s weather outfit:', error);
      
      // Create fallback outfit for any other errors
      const fallbackOutfit: GeneratedOutfit = {
        id: `fallback-outfit-${Date.now()}`,
        name: `Weather-Appropriate ${weather.condition} Look`,
        items: [],
        weather: {
          temperature: weather.temperature,
          condition: weather.condition,
          location: weather.location
        },
        reasoning: `This outfit recommendation is based on ${weather.temperature}°F ${weather.condition.toLowerCase()} weather. The outfit generation service is temporarily unavailable, but here are weather-appropriate clothing recommendations.`,
        confidence: 0.5,
        generatedAt: new Date().toISOString(),
        isWorn: false
      };

      setGeneratedOutfit(fallbackOutfit);
      setLastGenerated(new Date());
      saveTodaysOutfit(fallbackOutfit);
      setOutfitError('Service temporarily unavailable - showing weather recommendations instead');
    } finally {
      setIsGeneratingOutfit(false);
    }
  };

  const wearTodaysOutfit = async () => {
    if (!generatedOutfit || !user) return;

    setIsWearingOutfit(true);

    try {
      console.log('👕 Wearing today\'s outfit:', generatedOutfit.name);
      
      const token = await user.getIdToken();
      
      // Mark outfit as worn
      const response = await fetch(`/api/outfits/${generatedOutfit.id}/worn`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Outfit marked as worn:', result);
        
        // Update local state
        const updatedOutfit = { ...generatedOutfit, isWorn: true };
        setGeneratedOutfit(updatedOutfit);
        saveTodaysOutfit(updatedOutfit);
        
        // Dispatch event to refresh dashboard stats with a small delay 
        // to allow database transaction to complete
        setTimeout(() => {
          const event = new CustomEvent('outfitMarkedAsWorn', {
            detail: {
              outfitId: generatedOutfit.id,
              outfitName: generatedOutfit.name,
              timestamp: new Date().toISOString()
            }
          });
          window.dispatchEvent(event);
          console.log('🔄 Dispatched outfitMarkedAsWorn event for dashboard refresh');
        }, 1500); // 1.5 second delay to allow DB transaction to complete
        
        // Show success message briefly
        setTimeout(() => {
          console.log('🎉 Outfit worn successfully!');
        }, 1000);
      } else {
        throw new Error('Failed to mark outfit as worn');
      }
    } catch (error) {
      console.error('❌ Error wearing outfit:', error);
      setOutfitError('Failed to mark outfit as worn');
    } finally {
      setIsWearingOutfit(false);
    }
  };

  // Enhanced weather-based outfit parameters with comprehensive logic
  const determineOccasionFromWeather = (weather: any): string => {
    const temp = weather.temperature;
    const condition = weather.condition.toLowerCase();
    const precipitation = weather.precipitation || 0;
    const windSpeed = weather.wind_speed || 0;
    
    // Priority weather conditions
    if (condition.includes('rain') || condition.includes('storm') || precipitation > 50) {
      return 'Rainy Day';
    }
    if (condition.includes('snow') || condition.includes('blizzard')) {
      return 'Cold Weather';
    }
    
    // Temperature-based occasions
    if (temp >= 90) return 'Hot Weather';
    if (temp >= 80) return 'Warm Day';
    if (temp <= 32) return 'Cold Weather';
    if (temp <= 45) return 'Cool Weather';
    
    // Condition-based occasions
    if (windSpeed > 20) return 'Windy Day';
    if (condition.includes('fog') || condition.includes('mist')) return 'Overcast Day';
    if (condition.includes('sun') || condition.includes('clear')) return 'Sunny Day';
    if (condition.includes('cloud')) return 'Overcast Day';
    
    return 'Daily Casual';
  };

  const determineStyleFromWeather = (weather: any): string => {
    const temp = weather.temperature;
    const condition = weather.condition.toLowerCase();
    const humidity = weather.humidity || 50;
    const windSpeed = weather.wind_speed || 0;
    
    // Extreme temperature styles
    if (temp >= 90) return 'Minimal Summer';
    if (temp >= 85) return 'Light & Breezy';
    if (temp <= 25) return 'Winter Layers';
    if (temp <= 40) return 'Cozy Warm';
    
    // Weather condition styles
    if (condition.includes('rain') || condition.includes('storm')) {
      return 'Weather-Resistant';
    }
    if (condition.includes('snow')) {
      return 'Winter Chic';
    }
    if (windSpeed > 15) {
      return 'Wind-Friendly';
    }
    if (humidity > 80) {
      return 'Breathable Comfort';
    }
    
    // Moderate weather styles
    if (temp >= 70 && temp <= 80) {
      if (condition.includes('sun') || condition.includes('clear')) {
        return 'Bright & Cheerful';
      }
      return 'Comfortable Casual';
    }
    
    if (temp >= 55 && temp < 70) {
      return 'Layered Classic';
    }
    
    return 'Adaptable Classic';
  };

  const determineMoodFromWeather = (weather: any): string => {
    const temp = weather.temperature;
    const condition = weather.condition.toLowerCase();
    const humidity = weather.humidity || 50;
    const windSpeed = weather.wind_speed || 0;
    
    // Weather condition moods
    if (condition.includes('sun') || condition.includes('clear')) {
      return temp > 85 ? 'Relaxed' : 'Energetic';
    }
    if (condition.includes('rain') || condition.includes('storm')) {
      return 'Cozy';
    }
    if (condition.includes('snow')) {
      return 'Warm & Comfortable';
    }
    if (condition.includes('cloud') || condition.includes('overcast')) {
      return 'Mellow';
    }
    
    // Temperature-based moods
    if (temp >= 85) return 'Relaxed';
    if (temp >= 75) return 'Cheerful';
    if (temp <= 35) return 'Warm & Comfortable';
    if (temp <= 50) return 'Cozy';
    
    // Environmental factor moods
    if (windSpeed > 15) return 'Bold';
    if (humidity > 85) return 'Fresh';
    
    return 'Balanced';
  };

  const getClothingRecommendations = (weather: any): string[] => {
    const temp = weather.temperature;
    const condition = weather.condition.toLowerCase();
    const recommendations: string[] = [];
    
    // Temperature recommendations
    if (temp >= 90) {
      recommendations.push('Light, breathable fabrics', 'Minimal layers', 'Sun protection');
    } else if (temp >= 80) {
      recommendations.push('Cotton or linen', 'Light colors', 'Comfortable fit');
    } else if (temp >= 70) {
      recommendations.push('Versatile layers', 'Medium-weight fabrics');
    } else if (temp >= 55) {
      recommendations.push('Light jacket or cardigan', 'Long sleeves');
    } else if (temp >= 40) {
      recommendations.push('Warm layers', 'Closed-toe shoes');
    } else {
      recommendations.push('Heavy layers', 'Winter accessories', 'Insulated outerwear');
    }
    
    // Condition recommendations
    if (condition.includes('rain') || condition.includes('storm')) {
      recommendations.push('Water-resistant items', 'Covered shoes', 'Umbrella-friendly');
    }
    if (condition.includes('snow')) {
      recommendations.push('Waterproof boots', 'Warm accessories', 'Layered warmth');
    }
    if (weather.wind_speed > 15) {
      recommendations.push('Fitted clothing', 'Secure accessories');
    }
    
    return recommendations;
  };

  const formattedWeather = weather ? formatWeatherForDisplay(weather) : null;
  const recommendations = weather ? getClothingRecommendations(weather) : [];

  // Always render the component with debug info
  return (
    <Card className={`border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm hover:shadow-xl transition-all duration-300 ${className}`}>
      <CardHeader className="pb-4">
        <CardTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100 flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          Smart Weather Outfit
        </CardTitle>
        <p className="text-stone-600 dark:text-stone-400">
          Perfect outfit recommendations based on your exact location and current weather
        </p>
        {/* Debug info */}
        <div className="text-xs text-gray-500 mt-2">
          Debug: User: {user ? '✅' : '❌'}, Weather: {weather ? '✅' : '❌'}, Loading: {weatherLoading ? '⏳' : '✅'}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Weather Status Section */}
        <div className="space-y-4">
          {weatherLoading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin text-blue-500 mr-3" />
              <span className="text-stone-600 dark:text-stone-400">Getting your weather...</span>
            </div>
          ) : weather ? (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white/50 dark:bg-black/20 rounded-full flex items-center justify-center">
                    {weather.condition.toLowerCase().includes('clear') || weather.condition.toLowerCase().includes('sun') ? 
                      <Sun className="h-6 w-6 text-yellow-500" /> : 
                      <Cloud className="h-6 w-6 text-blue-500" />
                    }
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-stone-900 dark:text-white">
                      {formattedWeather?.temperature}
                    </h3>
                    <p className="text-stone-600 dark:text-stone-400 text-sm">
                      {formattedWeather?.condition}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-sm text-stone-600 dark:text-stone-400 mb-1">
                    <MapPin className="h-4 w-4" />
                    <span>{weather.location}</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-stone-500">
                    <div className="flex items-center gap-1">
                      <Droplets className="h-3 w-3" />
                      <span>{weather.humidity}%</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Wind className="h-3 w-3" />
                      <span>{weather.wind_speed} mph</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Weather Recommendations */}
              {recommendations.length > 0 && (
                <div className="border-t border-blue-200 dark:border-blue-700 pt-4">
                  <h4 className="text-sm font-medium text-stone-700 dark:text-stone-300 mb-2">
                    Weather Recommendations:
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {recommendations.slice(0, 4).map((rec, index) => (
                      <Badge 
                        key={index} 
                        variant="secondary" 
                        className="text-xs bg-white/70 dark:bg-black/20 text-stone-700 dark:text-stone-300"
                      >
                        {rec}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 text-center">
              <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
              <p className="text-red-600 dark:text-red-400 mb-3">Weather data unavailable</p>
              <Button onClick={fetchWeatherByLocation} variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </div>
          )}
        </div>

        {/* Location Permission Section */}
        {locationStatus === 'denied' && (
          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <MapPin className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              <div className="flex-1">
                <h4 className="text-sm font-medium text-amber-800 dark:text-amber-200">
                  Location Access Needed
                </h4>
                <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
                  Grant location access for more accurate weather-based outfit recommendations
                </p>
              </div>
              <Button onClick={requestLocationPermission} size="sm" variant="outline">
                <Navigation className="h-4 w-4 mr-1" />
                Enable
              </Button>
            </div>
          </div>
        )}

        {/* Today's Weather Outfit Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-stone-900 dark:text-stone-100">
              Today's Weather Outfit
            </h3>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-stone-500" />
              <span className="text-xs text-stone-500">
                {new Date().toLocaleDateString()}
              </span>
            </div>
          </div>

          {generatedOutfit ? (
            <div className="bg-gradient-to-r from-emerald-50 to-blue-50 dark:from-emerald-900/20 dark:to-blue-900/20 border border-emerald-200 dark:border-emerald-800 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center">
                  <Shirt className="h-5 w-5 text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-stone-900 dark:text-stone-100">
                    {generatedOutfit.name}
                  </h4>
                  <p className="text-sm text-stone-600 dark:text-stone-400">
                    Perfect for {generatedOutfit.weather.temperature}°F {generatedOutfit.weather.condition.toLowerCase()} weather
                  </p>
                </div>
                {generatedOutfit.isWorn && (
                  <div className="flex items-center gap-1 text-emerald-600">
                    <CheckCircle className="h-4 w-4" />
                    <span className="text-xs font-medium">Worn</span>
                  </div>
                )}
              </div>
              
              {/* Outfit Items Display */}
              {generatedOutfit.items && generatedOutfit.items.length > 0 ? (
                <div className="space-y-3 mb-6">
                  <h5 className="text-sm font-medium text-stone-700 dark:text-stone-300">
                    Outfit Items ({generatedOutfit.items.length}):
                  </h5>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {generatedOutfit.items.map((item, index) => (
                      <div key={index} className="bg-white/70 dark:bg-black/30 rounded-lg p-4 border border-stone-200 dark:border-stone-700">
                        <div className="flex items-start gap-3">
                          {/* Item Image or Placeholder */}
                          <div className="w-12 h-12 bg-stone-100 dark:bg-stone-800 rounded-lg flex items-center justify-center flex-shrink-0">
                            {item.imageUrl || item.image ? (
                              <img 
                                src={item.imageUrl || item.image} 
                                alt={item.name}
                                className="w-full h-full object-cover rounded-lg"
                              />
                            ) : (
                              <Shirt className="h-6 w-6 text-stone-400" />
                            )}
                          </div>
                          
                          {/* Item Details */}
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-stone-900 dark:text-stone-100 text-sm truncate">
                              {item.name}
                            </div>
                            <div className="text-xs text-stone-600 dark:text-stone-400 mt-1">
                              {item.type} • {item.color}
                            </div>
                            {item.brand && (
                              <div className="text-xs text-stone-500 dark:text-stone-500 mt-1">
                                {item.brand}
                              </div>
                            )}
                            {item.material && (
                              <div className="text-xs text-stone-500 dark:text-stone-500">
                                {item.material}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                /* Weather Recommendations when no items available */
                <div className="space-y-3 mb-6">
                  <h5 className="text-sm font-medium text-stone-700 dark:text-stone-300">
                    Weather-Appropriate Recommendations:
                  </h5>
                  <div className="bg-white/70 dark:bg-black/30 rounded-lg p-4 border border-stone-200 dark:border-stone-700">
                    <div className="space-y-2">
                      {recommendations.slice(0, 5).map((rec, index) => (
                        <div key={index} className="flex items-center gap-2 text-sm text-stone-700 dark:text-stone-300">
                          <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></div>
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-stone-500 dark:text-stone-500 mt-3">
                      Based on current weather conditions: {weather.temperature}°F {weather.condition.toLowerCase()}
                    </p>
                  </div>
                </div>
              )}
              
              {/* Weather Advisory */}
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Eye className="h-3 w-3 text-white" />
                  </div>
                  <div>
                    <h6 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                      Weather Advisory
                    </h6>
                    <p className="text-xs text-blue-800 dark:text-blue-200 leading-relaxed">
                      {generatedOutfit.reasoning}
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Wear Outfit Button */}
              <div className="flex items-center justify-between pt-4 border-t border-emerald-200 dark:border-emerald-700">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-emerald-600" />
                  <span className="text-sm text-emerald-700 dark:text-emerald-300">
                    Confidence: {Math.round((generatedOutfit.confidence || 0.9) * 100)}%
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Button 
                    onClick={() => {
                      clearTodaysOutfit();
                      generateTodaysOutfit();
                    }}
                    variant="outline"
                    size="sm"
                    disabled={isGeneratingOutfit}
                    className="text-stone-600 border-stone-300 hover:bg-stone-50"
                  >
                    <RefreshCw className={`h-4 w-4 mr-2 ${isGeneratingOutfit ? 'animate-spin' : ''}`} />
                    Regenerate
                  </Button>
                  <Button 
                    onClick={wearTodaysOutfit}
                    disabled={isWearingOutfit || generatedOutfit.isWorn}
                    className={`${
                      generatedOutfit.isWorn 
                        ? 'bg-green-600 hover:bg-green-700 text-white' 
                        : 'bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white'
                    }`}
                  >
                    {isWearingOutfit ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Wearing...
                      </>
                    ) : generatedOutfit.isWorn ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Worn Today
                      </>
                    ) : (
                      <>
                        <Heart className="h-4 w-4 mr-2" />
                        Wear This Outfit
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              {outfitError ? (
                <div className="text-red-600 dark:text-red-400 mb-4">
                  <AlertCircle className="h-6 w-6 mx-auto mb-2" />
                  {outfitError}
                </div>
              ) : isGeneratingOutfit ? (
                <div className="text-stone-600 dark:text-stone-400 mb-4">
                  <RefreshCw className="h-8 w-8 mx-auto mb-3 text-blue-500 animate-spin" />
                  <p>Generating today's perfect weather outfit...</p>
                </div>
              ) : (
                <div className="text-stone-600 dark:text-stone-400 mb-4">
                  <Shirt className="h-12 w-12 mx-auto mb-3 text-stone-400" />
                  <p>Auto-generating outfit for today's weather</p>
                </div>
              )}
              
              {!user && (
                <p className="text-xs text-stone-500 mt-2">
                  Sign in to get your daily weather outfit
                </p>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default SmartWeatherOutfitGenerator;
