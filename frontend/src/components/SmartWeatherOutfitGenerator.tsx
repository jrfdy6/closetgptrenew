"use client";

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { buildOutfitGenerationUserProfile } from '@/lib/outfitGenerationContract';
import { claimDailyOutfitAttempt, dailyOutfitKey, hasCompleteDailyOutfit } from '@/lib/dailyOutfitAttempt';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
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
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface SmartWeatherOutfitGeneratorProps {
  className?: string;
  generationEnabled?: boolean;
  readinessMessage?: string;
  onOutfitGenerated?: (outfit: any) => void;
  noCard?: boolean; // If true, render without outer Card wrapper (for embedding in other cards)
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
    source?: string;
    fallback?: boolean;
  };
  reasoning: string;
  confidence?: number | null;
  generatedAt: string;
  isWorn?: boolean;
  userId?: string; // Added for user isolation validation
}

export function SmartWeatherOutfitGenerator({ 
  className, 
  onOutfitGenerated,
  noCard = false,
  generationEnabled = false,
  readinessMessage = "Finish your capsule with ten saved pieces and the essentials for a complete outfit."
}: SmartWeatherOutfitGeneratorProps) {
  const { user } = useAuthContext();
  const { weather, loading: weatherLoading, fetchWeatherByLocation, error: weatherError, isStale: weatherIsStale } = useAutoWeather();
  
  // Debug logging
  console.log('🔍 SmartWeatherOutfitGenerator mounted:', {
    user: !!user,
    weather: !!weather,
    weatherLoading,
    weatherError
  });
  
  const [locationStatus, setLocationStatus] = useState<'idle' | 'requesting' | 'granted' | 'denied'>('idle');
  const [isGeneratingOutfit, setIsGeneratingOutfit] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<GeneratedOutfit | null>(null);
  const [outfitError, setOutfitError] = useState<string | null>(null);
  const [lastGenerated, setLastGenerated] = useState<Date | null>(null);
  const [todayKey, setTodayKey] = useState<string>('');
  const generationInFlightRef = useRef(false);
  const currentUserIdRef = useRef(user?.uid);
  currentUserIdRef.current = user?.uid;
  const activeRef = useRef(true);
  useEffect(() => {
    activeRef.current = true;
    return () => { activeRef.current = false; };
  }, []);
  const [isWeatherExpanded, setIsWeatherExpanded] = useState(false);
  const [isReasoningExpanded, setIsReasoningExpanded] = useState(false);
  const [isOutfitExpanded, setIsOutfitExpanded] = useState(false);
  
  // Default to expanded on all devices for better visibility
  useEffect(() => {
    const checkMobile = () => {
      // Always expanded by default for better UX
      setIsOutfitExpanded(true);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Initialize today's key for daily outfit generation
  useEffect(() => {
    const today = new Date().toDateString();
    setTodayKey(today);
  }, []);

  useEffect(() => {
    setGeneratedOutfit(null);
    setLastGenerated(null);
    setOutfitError(null);
  }, [todayKey, user?.uid]);

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

  // Load today's outfit from storage if available (but don't auto-generate)

  // Helper functions for daily outfit management
  const getTodaysOutfit = (): GeneratedOutfit | null => {
    if (!todayKey || !user) return null;
    try {
      const cacheKey = dailyOutfitKey(user.uid, todayKey);
      const currentStored = localStorage.getItem(cacheKey);
      const stored = currentStored || localStorage.getItem(`daily-outfit-${todayKey}`);
      if (!stored) return null;
      
      const outfit: GeneratedOutfit = JSON.parse(stored);
      
      // SECURITY: Validate that the outfit belongs to the current user
      if (outfit.userId !== user.uid) {
        console.warn('🚨 SECURITY: Outfit belongs to different user, clearing cached data');
        console.log(`Cached outfit user: ${outfit.userId}, Current user: ${user.uid}`);
        localStorage.removeItem(cacheKey);
        return null;
      }
      if (!currentStored && hasCompleteDailyOutfit(outfit.items)) {
        try { localStorage.setItem(cacheKey, stored); } catch { /* Cached reads still work when writes are unavailable. */ }
      }
      return outfit;
    } catch (error) {
      console.error('Error loading today\'s outfit:', error);
      return null;
    }
  };

  const saveTodaysOutfit = (outfit: GeneratedOutfit) => {
    if (!todayKey || !user) return;
    try {
      // SECURITY: Always include userId when saving outfit
      const outfitWithUser = {
        ...outfit,
        userId: user.uid
      };
      localStorage.setItem(dailyOutfitKey(user.uid, todayKey), JSON.stringify(outfitWithUser));
      console.log('💾 Saved today\'s outfit to storage with user ID');
    } catch (error) {
      console.error('Error saving today\'s outfit:', error);
    }
  };

  const clearTodaysOutfit = () => {
    if (!todayKey || !user) return;
    try {
      localStorage.removeItem(dailyOutfitKey(user.uid, todayKey));
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
    if (generationInFlightRef.current) return;
    if (!generationEnabled) {
      setOutfitError(readinessMessage);
      return;
    }
    if (!user) {
      setOutfitError('Please sign in to generate outfits');
      return;
    }

    if (!weather) {
      setOutfitError('Weather data not available');
      return;
    }

    generationInFlightRef.current = true;
    const requestUserId = user.uid;
    setIsGeneratingOutfit(true);
    setOutfitError(null);

    try {
      console.log('🎯 Auto-generating today\'s weather-perfect outfit for:', weather);
      
      // Get Firebase ID token for authentication
      const authToken = await user.getIdToken();
      
      // Fetch wardrobe items first
      console.log('📦 Fetching wardrobe items for outfit generation...');
      const wardrobeResponse = await fetch('/api/wardrobe', {
        headers: { 'Authorization': `Bearer ${authToken}` },
      });
      if (!wardrobeResponse.ok) {
        throw new Error("We couldn't load your wardrobe. Please try again.");
      }
      const wardrobeData = await wardrobeResponse.json();
      const wardrobeItems = Array.isArray(wardrobeData) ? wardrobeData : wardrobeData?.items;
      if (!hasCompleteDailyOutfit(wardrobeItems)) {
        throw new Error('Add a top, bottom and shoes, or a one-piece and shoes, before generating an outfit.');
      }
      if (!activeRef.current || currentUserIdRef.current !== requestUserId) return;

      const profileResponse = await fetch('/api/user/profile', {
        headers: { 'Authorization': `Bearer ${authToken}` },
        cache: 'no-store',
      });
      if (!profileResponse.ok) {
        throw new Error("We couldn't load your style profile. Please try again.");
      }
      const userProfile = await profileResponse.json();
      if (!activeRef.current || currentUserIdRef.current !== requestUserId) return;

      // Prepare request with the same saved quiz signals as manual generation
      const requestData = {
        occasion: determineOccasionFromWeather(weather),
        style: determineStyleFromWeather(weather),
        mood: determineMoodFromWeather(weather),
        weather: weather,
        wardrobe: wardrobeItems, // Send actual wardrobe items
        user_profile: buildOutfitGenerationUserProfile(userProfile, user),
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

      // Convert frontend data to Pydantic-compatible format
      const { convertToPydanticShape, validateConvertedData } = await import('@/lib/outfitDataConverter');
      const { generateOutfit } = await import('@/lib/robustApiClient');
      
      const convertedData = convertToPydanticShape(requestData);
      
      if (!validateConvertedData(convertedData)) {
        throw new Error('Data validation failed');
      }

      console.log('🌤️ Making ROBUST API call for weather-based outfit generation');
      
      // Use robust API client with comprehensive error handling
      const response = await generateOutfit(convertedData, authToken);
      const data = response.data;
      
      console.log('✅ Today\'s weather-perfect outfit generated:', data);
      console.log('🔍 DEBUG: Backend response items:', data.items);
      console.log('🔍 DEBUG: Items count:', data.items?.length || 0);
      console.log('🔍 DEBUG: Full data structure:', JSON.stringify(data, null, 2));
      
      if (!activeRef.current || currentUserIdRef.current !== requestUserId) return;
      if (!data?.id || !hasCompleteDailyOutfit(data.items)) {
        throw new Error("We couldn't create a complete saved outfit. Please try again.");
      }

      // Transform the response into our format
      const outfit: GeneratedOutfit = {
        id: data.id,
        userId: user.uid,
        name: data.name || `Today's Outfit`,
        items: Array.isArray(data.items) ? data.items : [],
        weather: data.weather || { ...convertedData.weather },
        reasoning: data.outfitAnalysis?.styleSynergy?.insight || data.reasoning || `Selected from your wardrobe for the requested occasion and weather context.`,
        confidence: typeof data.confidence_score === 'number' ? data.confidence_score : null,
        generatedAt: new Date().toISOString(),
        isWorn: false
      };

      setGeneratedOutfit(outfit);
      setLastGenerated(new Date());
      saveTodaysOutfit(outfit);
      onOutfitGenerated?.(outfit);

    } catch (error) {
      console.error('❌ Error generating today\'s weather outfit:', error);
      
      if (activeRef.current && currentUserIdRef.current === requestUserId) {
        setOutfitError(error instanceof Error ? error.message : "Your outfit couldn't be generated. Please try again.");
      }
    } finally {
      generationInFlightRef.current = false;
      if (activeRef.current) setIsGeneratingOutfit(false);
    }
  };

  useEffect(() => {
    if (!todayKey || !user) return;
    const storedOutfit = getTodaysOutfit();
    if (storedOutfit && hasCompleteDailyOutfit(storedOutfit.items)) {
      if (generatedOutfit?.id !== storedOutfit.id) {
        setGeneratedOutfit(storedOutfit);
        setLastGenerated(new Date(storedOutfit.generatedAt));
      }
      return;
    }
    if (storedOutfit) clearTodaysOutfit();
    if (
      generationEnabled && weather && !generatedOutfit && !isGeneratingOutfit &&
      claimDailyOutfitAttempt(dailyOutfitKey(user.uid, todayKey))
    ) {
      void generateTodaysOutfit();
    }
  }, [weather, user, todayKey, generatedOutfit, isGeneratingOutfit, generationEnabled, generateTodaysOutfit]);

  // Enhanced weather-based outfit parameters with comprehensive logic
  const determineOccasionFromWeather = (weather: any): string => {
    const temp = weather.temperature;
    const condition = weather.condition.toLowerCase();
    const precipitation = weather.precipitation || 0;
    const windSpeed = weather.wind_speed || 0;
    
    // Priority weather conditions (matching backend validation error)
    if (condition.includes('rain') || condition.includes('storm') || precipitation > 50) {
      return 'Casual'; // Use simple occasion for rainy weather
    }
    if (condition.includes('snow') || condition.includes('blizzard')) {
      return 'Casual'; // Use simple occasion for snowy weather
    }
    
    // Temperature-based occasions (matching backend validation error)
    if (temp >= 90) return 'Casual'; // Hot weather = casual
    if (temp <= 32) return 'Casual'; // Cold weather = casual
    if (temp <= 45) return 'Casual'; // Cool weather = casual
    
    // Default to Casual for normal weather conditions
    return 'Casual';
  };

  const determineStyleFromWeather = (weather: any): string => {
    const temp = weather.temperature;
    const condition = weather.condition.toLowerCase();
    const humidity = weather.humidity || 50;
    const windSpeed = weather.wind_speed || 0;
    
    // Map weather-based styles to valid backend enum values
    // Extreme temperature styles
    if (temp >= 90) return 'Minimalist'; // Minimal Summer -> Minimalist
    if (temp >= 85) return 'Casual Cool'; // Light & Breezy -> Casual Cool
    if (temp <= 25) return 'Classic'; // Winter Layers -> Classic
    if (temp <= 40) return 'Classic'; // Cozy Warm -> Classic
    
    // Weather condition styles
    if (condition.includes('rain') || condition.includes('storm')) {
      return 'Urban Professional'; // Weather-Resistant -> Urban Professional
    }
    if (condition.includes('snow')) {
      return 'Classic'; // Winter Chic -> Classic
    }
    if (windSpeed > 15) {
      return 'Athleisure'; // Wind-Friendly -> Athleisure
    }
    if (humidity > 80) {
      return 'Athleisure'; // Breathable Comfort -> Athleisure
    }
    
    // Moderate weather styles
    if (temp >= 70 && temp <= 80) {
      if (condition.includes('sun') || condition.includes('clear')) {
        return 'Colorblock'; // Bright & Cheerful -> Colorblock
      }
      return 'Casual Cool'; // Comfortable Casual -> Casual Cool
    }
    
    if (temp >= 55 && temp < 70) {
      return 'Classic'; // Layered Classic -> Classic
    }
    
    return 'Classic'; // Adaptable Classic -> Classic
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
      return 'Comfortable';
    }
    if (condition.includes('snow')) {
      return 'Comfortable';
    }
    if (condition.includes('cloud') || condition.includes('overcast')) {
      return 'Relaxed';
    }
    
    // Temperature-based moods
    if (temp >= 85) return 'Relaxed';
    if (temp >= 75) return 'Playful';
    if (temp <= 35) return 'Comfortable';
    if (temp <= 50) return 'Comfortable';
    
    // Environmental factor moods
    if (windSpeed > 15) return 'Bold';
    if (humidity > 85) return 'Energetic';
    
    return 'Comfortable';
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

  // Get weather icon based on condition - moved outside for use in weather section
  const getWeatherIcon = () => {
    if (!weather) return null;
    const condition = weather.condition.toLowerCase();
    if (condition.includes('clear') || condition.includes('sun')) {
      return <Sun className="h-6 w-6 text-[var(--copper-mid)]" />;
    } else if (condition.includes('rain') || condition.includes('storm')) {
      return <Droplets className="h-6 w-6 text-blue-500" />;
    } else if (condition.includes('snow')) {
      return <Cloud className="h-6 w-6 text-blue-300" />;
    }
    return <Cloud className="h-6 w-6 text-[var(--copper-mid)]" />;
  };

  const content = (
    <div className={`space-y-2 sm:space-y-3 ${noCard ? '' : ''}`}>
        {generatedOutfit && outfitError && <p role="alert" className="text-red-600 dark:text-red-400">{outfitError}</p>}
        {/* Today's Outfit Section - Collapsible on Mobile */}
        <Collapsible open={isOutfitExpanded} onOpenChange={setIsOutfitExpanded}>
          <div className="space-y-2">
            <CollapsibleTrigger asChild>
              <div className="flex items-center justify-between cursor-pointer hover:opacity-80 transition-opacity">
                <h3 className="text-xl sm:text-2xl font-display font-semibold text-card-foreground">
                  Today&apos;s Outfit
                </h3>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>{new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                  </div>
                  <div className="md:hidden">
                    {isOutfitExpanded ? (
                      <ChevronUp className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-muted-foreground" />
                    )}
                  </div>
                </div>
              </div>
            </CollapsibleTrigger>
          </div>
          
          <CollapsibleContent>
          {generatedOutfit ? (
            <div className="card-surface backdrop-blur-xl rounded-2xl p-2 sm:p-4 lg:p-5 border border-border/60 dark:border-border/70 space-y-1.5 sm:space-y-3">
              {/* Weather Section - Collapsed by default, above items */}
              {weather && (
                <Collapsible open={isWeatherExpanded} onOpenChange={setIsWeatherExpanded}>
                  <CollapsibleTrigger asChild>
                    <div className="card-surface backdrop-blur-xl rounded-xl p-2 sm:p-4 border border-border/60 dark:border-border/70 cursor-pointer hover:opacity-80 transition-opacity">
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                          <div className="w-10 h-10 sm:w-16 sm:h-16 bg-gradient-to-br from-[#D4A574]/30 to-[#C9956F]/30 dark:from-[#D4A574]/20 dark:to-[#C9956F]/20 rounded-lg sm:rounded-2xl flex items-center justify-center flex-shrink-0">
                            {getWeatherIcon()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-[#D4A574] to-[#C9956F] bg-clip-text text-transparent">
                              {formattedWeather?.temperature}
                            </div>
                            <p className="text-xs sm:text-sm text-muted-foreground truncate">
                              {formattedWeather?.condition}
                            </p>
                          </div>
                        </div>
                        <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform flex-shrink-0 ${isWeatherExpanded ? 'rotate-180' : ''}`} />
                      </div>
                    </div>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <div className="mt-2 pt-2 border-t border-border/60 dark:border-border/60 space-y-1.5 sm:space-y-2">
                      <div className="flex items-center gap-1.5 text-xs sm:text-sm text-muted-foreground">
                        <MapPin className="h-3.5 w-3.5 text-[var(--copper-mid)]" />
                        <span className="font-medium">{weather.location}</span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Droplets className="h-3 w-3 text-blue-500" />
                          <span>{weather.humidity}%</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Wind className="h-3 w-3 text-[var(--copper-mid)]" />
                          <span>{weather.wind_speed} mph</span>
                        </div>
                      </div>
                      {(weather.fallback || weatherIsStale || weatherLoading) && (
                        <div className="flex items-center gap-2 flex-wrap">
                          {weather.fallback && (
                            <Badge variant="secondary" className="text-xs bg-[var(--copper-light)]/20 dark:bg-[var(--copper-dark)]/20 text-[var(--copper-dark)] dark:text-[var(--copper-light)] border-0">
                              Fallback Data
                            </Badge>
                          )}
                          {weatherIsStale && (
                            <Badge variant="secondary" className="text-xs bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300 border-0">
                              Outdated
                            </Badge>
                          )}
                          {weatherLoading && (
                            <Badge variant="secondary" className="text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 border-0 flex items-center gap-1">
                              <RefreshCw className="h-3 w-3 animate-spin" />
                              Updating
                            </Badge>
                          )}
                        </div>
                      )}
                      {recommendations.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {recommendations.slice(0, 3).map((rec, index) => (
                            <Badge 
                              key={index} 
                              variant="secondary" 
                              className="text-xs bg-secondary/60 dark:bg-muted/60 text-muted-foreground border-0"
                            >
                              {rec}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </CollapsibleContent>
                </Collapsible>
              )}
              
              {/* Worn Badge - If outfit is worn */}
              {generatedOutfit.isWorn && (
                <div className="flex justify-end">
                  <Badge className="bg-[var(--copper-mid)] text-white border-0 flex items-center gap-1.5 flex-shrink-0 text-xs">
                    <CheckCircle className="h-3 w-3" />
                    Worn
                  </Badge>
                </div>
              )}
              
              {/* Outfit Items Grid - 3 columns, pictures only */}
              {generatedOutfit.items && generatedOutfit.items.length > 0 ? (
                <div className="space-y-1 sm:space-y-2">
                  <h5 className="text-xs font-semibold text-muted-foreground">
                    Items ({generatedOutfit.items.length})
                  </h5>
                  <div className="grid grid-cols-3 gap-1.5 sm:gap-3">
                    {generatedOutfit.items.map((item, index) => (
                      <div 
                        key={index} 
                        className="card-surface backdrop-blur-xl rounded-lg sm:rounded-xl p-1 sm:p-3 border border-border/60 dark:border-border/70"
                      >
                        {/* Photo Only - No Text */}
                        <div className="w-full aspect-square bg-secondary dark:bg-muted rounded-lg flex items-center justify-center overflow-hidden">
                          {item.imageUrl || item.image ? (
                            <img 
                              src={item.imageUrl || item.image} 
                              alt={item.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <Shirt className="h-6 w-6 sm:h-8 sm:w-8 text-muted-foreground" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="card-surface backdrop-blur-xl rounded-xl p-4 border border-border/60 dark:border-border/70">
                  <h5 className="text-sm font-semibold text-muted-foreground mb-3">
                    Weather Recommendations
                  </h5>
                    <div className="space-y-2">
                      {recommendations.slice(0, 5).map((rec, index) => (
                      <div key={index} className="flex items-center gap-2 text-sm text-muted-foreground">
                        <div className="w-1.5 h-1.5 bg-[var(--copper-mid)] rounded-full flex-shrink-0"></div>
                          <span>{rec}</span>
                        </div>
                      ))}
                  </div>
                </div>
              )}
              
              {/* Reasoning/Advisory - Collapsed by default on mobile */}
              {generatedOutfit.reasoning && (
                <div className="card-surface backdrop-blur-xl rounded-xl p-2 sm:p-3 border border-border/60 dark:border-border/70 bg-muted/80 dark:bg-muted/90">
                  <div className="flex items-start gap-2 sm:gap-3">
                    <div className="w-5 h-5 sm:w-8 sm:h-8 bg-gradient-to-br from-[#D4A574]/30 to-[#C9956F]/30 dark:from-[#D4A574]/20 dark:to-[#C9956F]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Eye className="h-3 w-3 sm:h-4 sm:w-4 text-[var(--copper-mid)] dark:text-[var(--copper-mid)]" />
                  </div>
                    <div className="flex-1 min-w-0">
                      <h6 className="text-xs sm:text-sm font-semibold text-card-foreground mb-0.5 sm:mb-1">
                        Why this outfit?
                    </h6>
                      <p className={`text-xs text-muted-foreground leading-relaxed ${!isReasoningExpanded ? 'line-clamp-1 sm:line-clamp-2' : ''}`}>
                      {generatedOutfit.reasoning}
                    </p>
                      {generatedOutfit.reasoning.length > 50 && (
                        <button
                          onClick={() => setIsReasoningExpanded(!isReasoningExpanded)}
                          className="text-xs text-[var(--copper-mid)] dark:text-[var(--copper-mid)] mt-0.5 sm:mt-1 font-medium hover:underline"
                        >
                          {isReasoningExpanded ? 'Read less' : 'Read more'}
                        </button>
                      )}
                  </div>
                </div>
              </div>
              )}
              
              {/* Action Buttons - Removed Confidence */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-1.5 sm:gap-2 pt-1.5 sm:pt-3 border-t border-border/60 dark:border-border/60">
                <div className="flex items-center gap-2">
                  <Button 
                    onClick={() => { void generateTodaysOutfit(); }}
                    variant="outline"
                    size="sm"
                    disabled={isGeneratingOutfit || !generationEnabled}
                    className="border-border/70 dark:border-border/80 text-muted-foreground hover:bg-secondary text-xs sm:text-sm h-8 sm:h-9"
                  >
                    <RefreshCw className={`h-3.5 w-3.5 sm:h-4 sm:w-4 mr-1.5 ${isGeneratingOutfit ? 'animate-spin' : ''}`} />
                    Regenerate
                  </Button>
                  <Button asChild size="sm" className="min-h-11">
                    <Link href={'/outfits/' + encodeURIComponent(generatedOutfit.id)}>Open outfit</Link>
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="card-surface backdrop-blur-xl rounded-2xl p-6 sm:p-8 text-center border border-border/60 dark:border-border/70">
              {outfitError ? (
                <div className="space-y-3">
                  <AlertCircle className="h-10 w-10 text-red-500 mx-auto" />
                  <p role="alert" className="text-red-600 dark:text-red-400 font-medium">{outfitError}</p>
                </div>
              ) : isGeneratingOutfit ? (
                <div className="space-y-4">
                  <RefreshCw className="h-12 w-12 text-[var(--copper-mid)] mx-auto animate-spin" />
                  <div>
                    <p className="text-card-foreground font-medium mb-1">Generating your perfect outfit...</p>
                    <p className="text-sm text-muted-foreground">Analyzing weather and your wardrobe</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-[#E8C8A0]/20 to-[#C9956F]/20 dark:from-[#D4A574]/15 dark:to-[#C9956F]/15 rounded-2xl flex items-center justify-center mx-auto">
                    <Shirt className="h-8 w-8 text-[var(--copper-mid)]" />
                  </div>
                  <div>
                    <p className="text-card-foreground font-medium mb-1">{generationEnabled ? "Today's outfit" : 'Build your capsule'}</p>
                    <p className="text-sm text-muted-foreground">{generationEnabled ? 'Create a look from your saved wardrobe and today’s weather.' : readinessMessage}</p>
                  </div>
                </div>
              )}
              
              {user && generationEnabled && !isGeneratingOutfit && (
                <Button className="mt-4" disabled={!weather} onClick={() => { void generateTodaysOutfit(); }}>
                  Generate today's outfit
                </Button>
              )}
              {!user && (
                <p className="text-xs text-muted-foreground mt-4">
                  Sign in to get your daily weather outfit
                </p>
              )}
            </div>
          )}
          </CollapsibleContent>
        </Collapsible>

        {/* Location Permission Prompt */}
        {locationStatus === 'denied' && (
          <div className="card-surface backdrop-blur-xl rounded-2xl p-4 border border-[var(--copper-mid)]/30 dark:border-[var(--copper-mid)]/30 bg-gradient-to-r from-[var(--copper-mid)]/5 to-[var(--copper-mid)]/5 dark:from-[var(--copper-mid)]/10 dark:to-[var(--copper-mid)]/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#D4A574]/20 to-[#C9956F]/20 rounded-xl flex items-center justify-center flex-shrink-0">
                <MapPin className="h-5 w-5 text-[var(--copper-mid)]" />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-semibold text-card-foreground mb-1">
                  Location Access Needed
                </h4>
                <p className="text-xs text-muted-foreground">
                  Enable location for accurate weather-based recommendations
                </p>
              </div>
              <Button 
                onClick={requestLocationPermission} 
                size="sm" 
                className="bg-gradient-to-r from-[#D4A574] to-[#C9956F] text-white hover:from-[#D4A574] hover:to-[#FF7700] flex-shrink-0"
              >
                <Navigation className="h-4 w-4 mr-1" />
                Enable
              </Button>
            </div>
          </div>
        )}

    </div>
  );

  if (noCard) {
    return <div className={className}>{content}</div>;
  }

  return (
    <Card className={`card-surface backdrop-blur-xl rounded-2xl sm:rounded-3xl shadow-lg border border-border/60 dark:border-border/70 hover:shadow-xl hover:shadow-[var(--copper-mid)]/20 transition-all duration-300 bg-card/85 dark:bg-card/85 ${className}`}>
      <CardContent className="p-3 sm:p-4 lg:p-6">
        {content}
      </CardContent>
    </Card>
  );
}

export default SmartWeatherOutfitGenerator;

