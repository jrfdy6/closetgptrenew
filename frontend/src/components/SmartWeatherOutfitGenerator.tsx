"use client";

import { useState, useEffect, useRef } from 'react';
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
  Heart,
  ChevronDown
} from 'lucide-react';
import { useAutoWeather } from '@/hooks/useWeather';
import { formatWeatherForDisplay, getClothingRecommendations } from '@/lib/weather';
import { useAuthContext } from '@/contexts/AuthContext';

interface SmartWeatherOutfitGeneratorProps {
  className?: string;
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
  };
  reasoning: string;
  confidence: number;
  generatedAt: string;
  isWorn?: boolean;
  userId?: string; // Added for user isolation validation
}

export function SmartWeatherOutfitGenerator({ 
  className, 
  onOutfitGenerated,
  noCard = false
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
  const [isWearingOutfit, setIsWearingOutfit] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<GeneratedOutfit | null>(null);
  const [outfitError, setOutfitError] = useState<string | null>(null);
  const [lastGenerated, setLastGenerated] = useState<Date | null>(null);
  const [todayKey, setTodayKey] = useState<string>('');
  const hasTriggeredAutoGenerationRef = useRef(false);
  const [isWeatherExpanded, setIsWeatherExpanded] = useState(false);
  const [isReasoningExpanded, setIsReasoningExpanded] = useState(false);

  // Initialize today's key for daily outfit generation
  useEffect(() => {
    const today = new Date().toDateString();
    setTodayKey(today);
  }, []);

  useEffect(() => {
    hasTriggeredAutoGenerationRef.current = false;
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
      const stored = localStorage.getItem(`daily-outfit-${todayKey}`);
      if (!stored) return null;
      
      const outfit: GeneratedOutfit = JSON.parse(stored);
      
      // SECURITY: Validate that the outfit belongs to the current user
      if (outfit.userId && outfit.userId !== user.uid) {
        console.warn('🚨 SECURITY: Outfit belongs to different user, clearing cached data');
        console.log(`Cached outfit user: ${outfit.userId}, Current user: ${user.uid}`);
        clearTodaysOutfit();
        return null;
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
      localStorage.setItem(`daily-outfit-${todayKey}`, JSON.stringify(outfitWithUser));
      console.log('💾 Saved today\'s outfit to storage with user ID');
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
      const authToken = await user.getIdToken();
      
      // Fetch wardrobe items first
      console.log('📦 Fetching wardrobe items for outfit generation...');
      let wardrobeItems: any[] = [];
      
      try {
        const wardrobeResponse = await fetch('/api/wardrobe', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authToken}`,
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
      
      // Transform the response into our format
      const outfit: GeneratedOutfit = {
        id: data.id || `outfit_${Date.now()}`,
        name: data.name || `Today's Perfect Weather Outfit`,
        items: Array.isArray(data.items) ? data.items : [],
        weather: {
          temperature: weather.temperature,
          condition: weather.condition,
          location: weather.location
        },
        reasoning: data.reasoning || `This weather-optimized outfit is perfect for today's ${weather.temperature}°F ${weather.condition.toLowerCase()} conditions in ${weather.location}. The carefully selected pieces balance comfort and style while ensuring weather appropriateness. Each item works harmoniously to create a cohesive look that matches the current environmental conditions.`,
        confidence: data.confidence || 0.9,
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

  useEffect(() => {
    if (!todayKey || !user) return;

    const storedOutfit = getTodaysOutfit();
    let validOutfit = storedOutfit;

    if (storedOutfit) {
      // Check if stored outfit is a fallback (low confidence, no items, or fallback name)
      const isFallback = storedOutfit.confidence <= 0.6 || 
                        !storedOutfit.items || 
                        storedOutfit.items.length === 0 || 
                        storedOutfit.name.includes('Weather-Appropriate');
      
      if (isFallback) {
        console.log('🗑️ Clearing cached fallback outfit');
        clearTodaysOutfit();
        validOutfit = null;
      } else if (!generatedOutfit) {
        console.log('📅 Loading today\'s outfit from storage:', storedOutfit);
        console.log('🔍 DEBUG: Loaded outfit items:', storedOutfit.items);
        console.log('🔍 DEBUG: Loaded items count:', storedOutfit.items?.length || 0);
        if (!storedOutfit.items || storedOutfit.items.length === 0) {
          console.warn('⚠️ WARNING: Loaded outfit has no items! Clearing...');
          clearTodaysOutfit();
          validOutfit = null;
        } else {
          setGeneratedOutfit(storedOutfit);
          setLastGenerated(new Date(storedOutfit.generatedAt));
        }
      }
    }

    if (
      !validOutfit &&
      weather &&
      !generatedOutfit &&
      !isGeneratingOutfit &&
      !hasTriggeredAutoGenerationRef.current
    ) {
      console.log('⚡ Auto-generating today\'s outfit based on current weather');
      hasTriggeredAutoGenerationRef.current = true;
      generateTodaysOutfit();
    }
  }, [weather, user, todayKey, generatedOutfit, isGeneratingOutfit, generateTodaysOutfit]);

  const wearTodaysOutfit = async () => {
    if (!generatedOutfit || !user) return;

    setIsWearingOutfit(true);

    try {
      console.log('👕 Wearing today\'s outfit:', generatedOutfit.name);
      
      const currentTimestamp = Date.now();
      const currentDate = new Date(currentTimestamp);
      console.log(`📅 [Weather] Sending timestamp: ${currentTimestamp} (${currentDate.toLocaleString()})`);
      
      const token = await user.getIdToken();
      
      // Mark outfit as worn - send required data
      const response = await fetch(`/api/outfit-history/mark-worn`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          outfitId: generatedOutfit.id,
          outfitName: generatedOutfit.name,
          dateWorn: currentTimestamp, // Send current timestamp in milliseconds to avoid timezone issues
          occasion: 'Daily',
          mood: 'Confident',
          weather: generatedOutfit.weather || {},
          notes: `Weather-based outfit: ${generatedOutfit.name}`,
          tags: ['weather-optimized', 'daily-suggestion'],
          items: generatedOutfit.items // Include items for wear count updates
        }),
      });

      console.log('🔍 DEBUG: Mark-worn response status:', response.status);
      const result = await response.json();
      console.log('🔍 DEBUG: Mark-worn response data:', result);
      
      if (response.ok) {
        console.log('✅ Outfit marked as worn:', result);
        
        // ✅ Show XP notification if XP was awarded
        if (result.xp_earned && result.xp_earned > 0) {
          window.dispatchEvent(new CustomEvent('xpAwarded', {
            detail: {
              xp: result.xp_earned,
              reason: 'Outfit worn',
              level_up: result.level_up || false,
              new_level: result.new_level
            }
          }));
        }
        
        // Update local state
        const updatedOutfit = { ...generatedOutfit, isWorn: true };
        setGeneratedOutfit(updatedOutfit);
        saveTodaysOutfit(updatedOutfit);
        
        // Dispatch event to notify dashboard to refresh
        const event = new CustomEvent('outfitMarkedAsWorn', {
          detail: {
            outfitId: generatedOutfit.id,
            outfitName: generatedOutfit.name,
            timestamp: new Date().toISOString()
          }
        });
        window.dispatchEvent(event);
        console.log('🔄 [Weather Generator] Dispatched outfitMarkedAsWorn event for dashboard refresh');
        
            // Test: Directly check user_stats after wear action
            setTimeout(async () => {
              try {
                console.log('🧪 Testing: Fetching user_stats directly to check increment...');
                const token = await user.getIdToken();
                const testResponse = await fetch('/api/simple-analytics/outfits-worn-this-week', {
                  method: 'GET',
                  headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                  },
                });
                
                if (testResponse.ok) {
                  const testData = await testResponse.json();
                  console.log('🧪 Direct user_stats check:', testData);
                  console.log(`🧪 Current worn count: ${testData.outfits_worn_this_week}`);
                }
              } catch (error) {
                console.error('🧪 Error testing user_stats:', error);
              }
            }, 500); // Quick test
            
            // RAILWAY-PROOF: Check debug stats to see actual backend operations
            setTimeout(async () => {
              try {
                console.log('🔍 Railway-proof debug: Checking backend increment operations...');
                const debugResponse = await fetch(`/api/debug-stats?userId=${user.uid}`, {
                  method: 'GET',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                });
                
                if (debugResponse.ok) {
                  const debugData = await debugResponse.json();
                  console.log('🔍 Debug stats response:', debugData);
                  console.log(`🔍 Current user_stats from debug: ${debugData.current_stats?.worn_this_week || 'N/A'}`);
                  console.log(`🔍 Recent debug entries (${debugData.debug_entries?.length || 0}):`);
                  debugData.debug_entries?.slice(0, 3).forEach((entry: any, index: number) => {
                    // Handle different debug entry formats
                    const event = entry.event || entry.action || 'unknown_event';
                    const oldCount = entry.old_count || entry.old_wear_count || 'N/A';
                    const newCount = entry.new_count || entry.new_wear_count || 'N/A';
                    const timestamp = entry.timestamp || 'N/A';
                    console.log(`🔍   ${index + 1}. ${event}: ${oldCount} -> ${newCount} at ${timestamp}`);
                  });
                } else {
                  console.log('🔍 Debug stats endpoint not ready yet (expected during deployment)');
                }
              } catch (error) {
                console.log('🔍 Debug stats not available yet:', error);
              }
            }, 2000); // Wait longer for debug endpoint
        
        // Dispatch event to refresh dashboard stats with a longer delay 
        // to allow Firestore write to be fully committed and readable
        setTimeout(() => {
          const event = new CustomEvent('outfitMarkedAsWorn', {
            detail: {
              outfitId: generatedOutfit.id,
              outfitName: generatedOutfit.name,
              timestamp: new Date().toISOString(),
              forceFresh: true  // Force analytics to bypass cache
            }
          });
          window.dispatchEvent(event);
          console.log('🔄 Dispatched outfitMarkedAsWorn event for dashboard refresh (force fresh)');
        }, 5000); // 5 second delay for stronger Firestore consistency
        
        // Show success message briefly
        setTimeout(() => {
          console.log('🎉 Outfit worn successfully!');
        }, 1000);
      } else {
        console.error('❌ MARK-WORN FAILED:', {
          status: response.status,
          errorData: result
        });
        throw new Error(`Failed to mark outfit as worn: ${result.detail || result.error || 'Unknown error'}`);
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

  // Get weather icon based on condition
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
        {/* Today's Outfit Section - Moved to Top */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-base sm:text-lg font-display font-semibold text-card-foreground">
              Today&apos;s Outfit
            </h3>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              <span>{new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
            </div>
          </div>

          {generatedOutfit ? (
            <div className="card-surface backdrop-blur-xl rounded-2xl p-3 sm:p-4 lg:p-5 border border-border/60 dark:border-border/70 space-y-2 sm:space-y-3">
              {/* Outfit Header - More Compact */}
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-[var(--copper-light)]/35 to-[var(--copper-mid)]/35 dark:from-[var(--copper-mid)]/20 dark:to-[var(--copper-mid)]/20 rounded-xl sm:rounded-2xl flex items-center justify-center shadow-inner flex-shrink-0">
                  <Shirt className="h-6 w-6 sm:h-7 sm:w-7 text-[var(--copper-mid)] dark:text-[var(--copper-mid)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-display font-semibold text-sm sm:text-base text-card-foreground mb-0.5">
                    {generatedOutfit.name}
                  </h4>
                  <p className="text-xs sm:text-sm text-muted-foreground">
                    Perfect for {generatedOutfit.weather.temperature}°F {generatedOutfit.weather.condition.toLowerCase()}
                  </p>
                </div>
                {generatedOutfit.isWorn && (
                  <Badge className="bg-[var(--copper-mid)] text-white border-0 flex items-center gap-1.5 flex-shrink-0 text-xs">
                    <CheckCircle className="h-3 w-3" />
                    Worn
                  </Badge>
                )}
              </div>
              
              {/* Outfit Items Grid - Compact with Prominent Photos */}
              {generatedOutfit.items && generatedOutfit.items.length > 0 ? (
                <div className="space-y-2">
                  <h5 className="text-xs sm:text-sm font-semibold text-muted-foreground">
                    Items ({generatedOutfit.items.length})
                  </h5>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 sm:gap-3">
                    {generatedOutfit.items.map((item, index) => (
                      <div 
                        key={index} 
                        className="card-surface backdrop-blur-xl rounded-lg sm:rounded-xl p-2 sm:p-3 border border-border/60 dark:border-border/70"
                      >
                        <div className="space-y-2">
                          {/* Prominent Photo */}
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
                          {/* Compact Info */}
                          <div className="space-y-0.5">
                            <div className="font-medium text-xs text-card-foreground truncate">
                              {item.name}
                            </div>
                            <div className="text-xs text-muted-foreground truncate">
                              {item.type} • {item.color}
                            </div>
                            {item.brand && (
                              <div className="text-xs text-muted-foreground/70 truncate">
                                {item.brand}
                              </div>
                            )}
                          </div>
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
              
              {/* Reasoning/Advisory - Truncated with Read More */}
              {generatedOutfit.reasoning && (
                <div className="card-surface backdrop-blur-xl rounded-xl p-2.5 sm:p-3 border border-border/60 dark:border-border/70 bg-card/85 dark:bg-card/85">
                  <div className="flex items-start gap-2 sm:gap-3">
                    <div className="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-br from-[#D4A574]/30 to-[#C9956F]/30 dark:from-[#D4A574]/20 dark:to-[#C9956F]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Eye className="h-3 w-3 sm:h-4 sm:w-4 text-[var(--copper-mid)] dark:text-[var(--copper-mid)]" />
                  </div>
                    <div className="flex-1 min-w-0">
                      <h6 className="text-xs sm:text-sm font-semibold text-card-foreground mb-1">
                        Why this outfit?
                    </h6>
                      <p className={`text-xs text-muted-foreground leading-relaxed ${!isReasoningExpanded ? 'line-clamp-2' : ''}`}>
                      {generatedOutfit.reasoning}
                    </p>
                      {generatedOutfit.reasoning.length > 100 && (
                        <button
                          onClick={() => setIsReasoningExpanded(!isReasoningExpanded)}
                          className="text-xs text-[var(--copper-mid)] dark:text-[var(--copper-mid)] mt-1 font-medium hover:underline"
                        >
                          {isReasoningExpanded ? 'Read less' : 'Read more'}
                        </button>
                      )}
                  </div>
                </div>
              </div>
              )}
              
              {/* Action Buttons - Removed Confidence */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-2 pt-2 sm:pt-3 border-t border-border/60 dark:border-border/60">
                <div className="flex items-center gap-2">
                  <Button 
                    onClick={() => {
                      clearTodaysOutfit();
                      generateTodaysOutfit();
                    }}
                    variant="outline"
                    size="sm"
                    disabled={isGeneratingOutfit}
                    className="border-border/70 dark:border-border/80 text-muted-foreground hover:bg-secondary text-xs sm:text-sm h-8 sm:h-9"
                  >
                    <RefreshCw className={`h-3.5 w-3.5 sm:h-4 sm:w-4 mr-1.5 ${isGeneratingOutfit ? 'animate-spin' : ''}`} />
                    Regenerate
                  </Button>
                  <Button 
                    onClick={wearTodaysOutfit}
                    disabled={isWearingOutfit || generatedOutfit.isWorn}
                    size="sm"
                    className={`${
                      generatedOutfit.isWorn 
                        ? 'bg-[var(--copper-mid)] hover:bg-[var(--copper-mid)]/90 text-white' 
                        : 'bg-gradient-to-r from-[var(--copper-mid)] to-[var(--copper-mid)] hover:from-[var(--copper-mid)] hover:to-accent text-white shadow-lg shadow-[var(--copper-mid)]/25'
                    } text-xs sm:text-sm h-8 sm:h-9`}
                  >
                    {isWearingOutfit ? (
                      <>
                        <RefreshCw className="h-3.5 w-3.5 sm:h-4 sm:w-4 mr-1.5 animate-spin" />
                        Wearing...
                      </>
                    ) : generatedOutfit.isWorn ? (
                      <>
                        <CheckCircle className="h-3.5 w-3.5 sm:h-4 sm:w-4 mr-1.5" />
                        Worn Today
                      </>
                    ) : (
                      <>
                        <Heart className="h-3.5 w-3.5 sm:h-4 sm:w-4 mr-1.5" />
                        Wear This Outfit
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="card-surface backdrop-blur-xl rounded-2xl p-6 sm:p-8 text-center border border-border/60 dark:border-border/70">
              {outfitError ? (
                <div className="space-y-3">
                  <AlertCircle className="h-10 w-10 text-red-500 mx-auto" />
                  <p className="text-red-600 dark:text-red-400 font-medium">{outfitError}</p>
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
                    <p className="text-card-foreground font-medium mb-1">Preparing today&apos;s outfit</p>
                    <p className="text-sm text-muted-foreground">Auto-generating based on current weather</p>
                  </div>
                </div>
              )}
              
              {!user && (
                <p className="text-xs text-muted-foreground mt-4">
                  Sign in to get your daily weather outfit
                </p>
              )}
            </div>
          )}
        </div>

        {/* Weather Display - Compact & Modern - Moved Below Outfit */}
          {weatherLoading && !weather ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin text-[var(--copper-mid)] mx-auto mb-3" />
              <p className="text-muted-foreground">Getting your weather...</p>
            </div>
            </div>
          ) : weather ? (
          <div className={`card-surface backdrop-blur-xl rounded-2xl p-2.5 sm:p-4 lg:p-5 border border-border/60 dark:border-border/70 transition-all ${weatherIsStale ? 'opacity-60' : ''}`}>
            {/* Compact Weather Display - Always Visible */}
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-[#D4A574]/30 to-[#C9956F]/30 dark:from-[#D4A574]/20 dark:to-[#C9956F]/20 rounded-xl sm:rounded-2xl flex items-center justify-center flex-shrink-0">
                  {getWeatherIcon()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-[#D4A574] to-[#C9956F] bg-clip-text text-transparent">
                    {formattedWeather?.temperature}
                  </div>
                  <p className="text-xs sm:text-sm text-muted-foreground truncate">
                    {formattedWeather?.condition}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsWeatherExpanded(!isWeatherExpanded)}
                className="flex-shrink-0 h-8 w-8 p-0 sm:hidden"
              >
                <ChevronDown className={`h-4 w-4 transition-transform ${isWeatherExpanded ? 'rotate-180' : ''}`} />
              </Button>
            </div>

            {/* Expanded Weather Details - Collapsible on Mobile, Always Visible on Desktop */}
            <div className={`mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-border/60 dark:border-border/60 space-y-1.5 sm:space-y-2 ${isWeatherExpanded ? 'block' : 'hidden sm:block'}`}>
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
          </div>
          ) : (
          <div className="card-surface backdrop-blur-xl rounded-2xl p-6 border border-red-200 dark:border-red-800/50 text-center">
            <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-3" />
            <p className="text-red-600 dark:text-red-400 mb-4 font-medium">Weather data unavailable</p>
            <Button 
              onClick={fetchWeatherByLocation} 
              variant="outline" 
              size="sm"
              className="border-border/70 dark:border-border/80 text-muted-foreground hover:bg-secondary"
            >
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </div>
          )}

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

