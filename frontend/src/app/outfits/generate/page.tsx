'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { 
  Sparkles, 
  Palette, 
  Calendar, 
  MapPin, 
  Clock, 
  Zap,
  Shirt,
  Heart,
  RefreshCw,
  ArrowLeft,
  Shuffle
} from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import { useRouter } from 'next/navigation';
import { useAutoWeather } from '@/hooks/useWeather';
import type { WeatherData } from '@/types/weather';
import { type FlatLaySource } from '@/lib/flatLayState';
import {
  assertRequiredBaseItem,
  buildOutfitGenerationUserProfile,
} from '@/lib/outfitGenerationContract';
import { randomOutfitConfiguration } from '@/lib/randomOutfitConfiguration';
import OnboardingProgress from '@/components/onboarding/OnboardingProgress';
import FirstLookSetup from '@/components/onboarding/FirstLookSetup';

// Import new enhanced components
import OutfitGenerationBottomSheet from '@/components/outfits/OutfitGenerationBottomSheet';
import { OutfitGenerating, WardrobeLoading } from '@/components/ui/outfit-loading';
// Phase 2: Progressive Reveal Components
import OutfitRevealAnimation from '@/components/OutfitRevealAnimation';
import { useToast } from '@/components/ui/use-toast';
import { motion } from 'framer-motion';

interface OutfitGenerationForm {
  occasion: string;
  style: string;
  mood: string;
  weather: string;
  description: string;
}

interface GeneratedOutfit extends FlatLaySource {
  id: string;
  baseItemId?: string | null;
  name: string;
  style: string;
  mood: string;
  occasion: string;
  confidence_score: number | null;
  score_breakdown?: any;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
    color: string;
    reason?: string;
  }>;
  reasoning: string;
  createdAt: string;
  metadata?: {
    generation_strategy?: string;
    [key: string]: any;
  };
  outfitAnalysis?: {
    textureAnalysis?: any;
    patternBalance?: any;
    colorStrategy?: any;
    styleSynergy?: any;
  };
  flat_lay_status?: string;
  flatLayStatus?: string;
  flat_lay_url?: string | null;
  flatLayUrl?: string | null;
  flat_lay_error?: string | null;
  flatLayError?: string | null;
  flat_lay_requested?: boolean;
  flatLayRequested?: boolean;
  weather?: WeatherData;
  isWorn?: boolean;
}

export default function OutfitGenerationPage() {
  const router = useRouter();
  const generationInFlight = useRef(false);
  const activeUser = useRef<string | undefined>();
  const [firstLookFlow, setFirstLookFlow] = useState(false);
  useEffect(() => {
    setFirstLookFlow(new URLSearchParams(window.location.search).get('onboarding') === '1');
  }, []);
  const { user, loading: authLoading } = useFirebase();
  activeUser.current = user?.uid;
  useEffect(() => () => { activeUser.current = undefined; }, []);
  const { weather, loading: weatherLoading, fetchWeatherByLocation } = useAutoWeather();
  const { toast } = useToast();
  const [baseItem, setBaseItem] = useState<any>(null);
  const [wardrobeItems, setWardrobeItems] = useState<any[]>([]);
  const [wardrobeLoading, setWardrobeLoading] = useState(false);
  const [wardrobeLoadError, setWardrobeLoadError] = useState<string | null>(null);
  const [wardrobeLoadAttempt, setWardrobeLoadAttempt] = useState(0);
  const [freshWeatherData, setFreshWeatherData] = useState<WeatherData | null>(null);
  // Extract base item ID from URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const baseItemId = urlParams.get('baseItemId');
    
    if (baseItemId) {
      console.log('🔍 Base item ID from URL:', baseItemId);
      // We'll find the full item when wardrobe loads
      setBaseItem({ id: baseItemId });
    }
  }, []);

  // Fetch wardrobe items when user is available
  useEffect(() => {
    const fetchWardrobeItems = async () => {
      if (!user) return;
      
      try {
        setWardrobeLoading(true);
        setWardrobeLoadError(null);
        const wardrobeToken = await user.getIdToken();
        const response = await fetch('/api/wardrobe', {
          headers: {
            'Authorization': `Bearer ${wardrobeToken}`,
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          // Handle the wardrobe API response structure
          const items = data.items || data;
          if (!Array.isArray(items)) throw new Error('Invalid wardrobe response');
          setWardrobeItems(items);
          console.log('🔍 Wardrobe items loaded:', items.length);
          
          // Get base item ID from URL params directly (in case state hasn't been set yet)
          const urlParams = new URLSearchParams(window.location.search);
          const baseItemId = urlParams.get('baseItemId');
          
          // If we have a baseItem ID, find the full item in wardrobe
          if (baseItemId) {
            const fullItem = items.find((item: any) => item.id === baseItemId);
            if (fullItem) {
              console.log('🔍 Found base item in wardrobe with full metadata:', fullItem.name);
              console.log('🔍 Rich metadata includes:', {
                dominantColors: fullItem.dominantColors?.length || 0,
                matchingColors: fullItem.matchingColors?.length || 0,
                metadata: fullItem.metadata ? 'present' : 'missing',
                material: fullItem.metadata?.visualAttributes?.material,
                texture: fullItem.metadata?.visualAttributes?.textureStyle,
                silhouette: fullItem.metadata?.visualAttributes?.silhouette,
                fit: fullItem.metadata?.visualAttributes?.fit
              });
              console.log('🔍 Setting base item to:', {
                id: fullItem.id,
                name: fullItem.name,
                imageUrl: fullItem.imageUrl || fullItem.image_url,
                type: fullItem.type
              });
              
              // METADATA REPAIR: Inject defaults for missing metadata to pass validation
              const repairedBaseItem = {
                ...fullItem,
                material: fullItem.material ?? "unspecified",
                texture: fullItem.texture ?? "unspecified", 
                dominantColors: fullItem.dominantColors ?? [],
                matchingColors: fullItem.matchingColors ?? [],
                season: fullItem.season ?? ["all"],
                userId: fullItem.userId ?? user?.uid ?? "unknown",
                createdAt: fullItem.createdAt ?? Date.now(),
                updatedAt: fullItem.updatedAt ?? Date.now()
              };
              
              console.log('🔧 METADATA REPAIR: Added defaults for base item:', {
                material: repairedBaseItem.material,
                texture: repairedBaseItem.texture,
                dominantColors: repairedBaseItem.dominantColors.length,
                matchingColors: repairedBaseItem.matchingColors.length,
                season: repairedBaseItem.season,
                userId: repairedBaseItem.userId ? 'present' : 'missing',
                timestamps: { createdAt: repairedBaseItem.createdAt, updatedAt: repairedBaseItem.updatedAt }
              });
              
              setBaseItem(repairedBaseItem);
            } else {
              console.warn('🔍 Base item not found in wardrobe:', baseItemId);
              setBaseItem(null);
            }
          }
        } else {
          throw new Error('Wardrobe request failed');
        }
      } catch (error) {
        console.error('🔍 Error fetching wardrobe items:', error);
        setWardrobeLoadError('Your saved wardrobe could not be loaded. Please retry before creating an outfit.');
      } finally {
        setWardrobeLoading(false);
      }
    };

    if (user) {
      fetchWardrobeItems();
    }
  }, [user, wardrobeLoadAttempt]);
  
  // Use Next.js API routes instead of direct backend calls
  const API_BASE = '/api';
  const [formData, setFormData] = useState<OutfitGenerationForm>({
    occasion: '',
    style: '',
    mood: '',
    weather: '',
    description: ''
  });
  const shuffleOverrideRef = useRef<{ occasion: string; style: string; mood: string } | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<GeneratedOutfit | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRevealAnimation, setShowRevealAnimation] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [filteredStyles, setFilteredStyles] = useState<string[]>([]);

  const occasions = [
    // Simple occasion values (matching backend validation error)
    'Casual', 'Business', 'Party', 'Date', 'Interview', 'Weekend', 'Loungewear', 'Gym'
  ];

  const styles = [
    // Academic & Intellectual
    'Dark Academia', 'Light Academia', 'Old Money',
    // Trendy & Modern
    'Y2K', 'Coastal Grandmother', 'Clean Girl', 'Cottagecore',
    // Artistic & Creative
    'Avant-Garde', 'Artsy', 'Maximalist', 'Colorblock',
    // Professional & Classic
    'Business Casual', 'Classic', 'Preppy', 'Urban Professional',
    // Urban & Street
    'Streetwear', 'Techwear', 'Grunge', 'Hipster',
    // Feminine & Romantic
    'Romantic', 'Boho', 'French Girl', 'Pinup',
    // Modern & Minimal
    'Minimalist', 'Modern', 'Scandinavian', 'Monochrome',
    // Alternative & Edgy
    'Gothic', 'Punk', 'Cyberpunk', 'Edgy',
    // Seasonal & Lifestyle
    'Coastal Chic', 'Athleisure', 'Casual Cool', 'Loungewear', 'Workout'
  ];

  const moods = [
    // Backend-supported moods (from validation error message)
    'Romantic', 'Playful', 'Serene', 'Dynamic', 'Bold', 'Subtle'
  ];

  const weatherOptions = [
    'sunny', 'rainy', 'cloudy', 'cold', 'warm', 'hot', 'mild'
  ];

  // Smart gender-aware style filtering - filters only obviously gender-specific styles
  // Styles that can work for both genders (like Romantic, Boho) are kept available
  const filterStylesByGender = (styles: string[], gender: string) => {
    const effectiveGender = gender || 'male';
    
    // Only filter styles that are VERY obviously gender-specific
    // These styles have strong gender associations that don't translate well
    const obviouslyFeminineStyles = [
      'Coastal Grandmother',  // Very feminine aesthetic (linen dresses, straw accessories)
      'French Girl',          // Parisian women's fashion
      'Pinup',                // 1950s women's pinup style
      'Clean Girl'            // TikTok women's aesthetic
    ];
    
    const obviouslyMasculineStyles = [
      'Techwear'              // Very masculine tech/utility aesthetic
    ];
    
    // Styles like Romantic, Boho, Cottagecore can work for both genders with adjustments
    // So we keep them available - backend will handle appropriate item selection
    
    if (effectiveGender.toLowerCase() === 'male') {
      return styles.filter(style => !obviouslyFeminineStyles.includes(style));
    } else if (effectiveGender.toLowerCase() === 'female') {
      return styles.filter(style => !obviouslyMasculineStyles.includes(style));
    }
    
    return styles;
  };

  // Fetch user profile and filter styles
  useEffect(() => {
    const fetchUserProfile = async () => {
      if (!user) {
        console.log('🔍 No user authenticated, skipping profile fetch');
        setProfileLoading(false);
        return;
      }
      
      console.log('🔍 Fetching profile for user:', user.uid);
      setProfileLoading(true);
      try {
        const profileToken = await user.getIdToken();
        const response = await fetch('/api/user/profile?fresh=1', {
          headers: {
            'Authorization': `Bearer ${profileToken}`,
          },
        });
        
        if (response.ok) {
          const profile = await response.json();
          console.log('🔍 User profile fetched:', profile);
          setUserProfile(profile);
          
          // Filter styles based on gender
          const filtered = filterStylesByGender(styles, profile.gender);
          console.log('🔍 Filtered styles for gender:', profile.gender, ':', filtered);
          setFilteredStyles(filtered);
          
          // If current style is not compatible, reset it
          setFormData(previousFormData => {
            if (previousFormData.style && !filtered.includes(previousFormData.style)) {
              console.log('🔍 Resetting incompatible style:', previousFormData.style);
              return { ...previousFormData, style: '' };
            }
            return previousFormData;
          });
        } else {
          console.error('🔍 Profile fetch failed:', response.status, response.statusText);
          // Fallback to male-appropriate styles for 502 errors
          if (response.status === 502) {
            console.log('🔍 Backend error (502), using male-appropriate styles as fallback');
            const maleStyles = filterStylesByGender(styles, 'male');
            setFilteredStyles(maleStyles);
          } else {
            // For other errors, use all styles
            setFilteredStyles(styles);
          }
        }
      } catch (error) {
        console.error('🔍 Error fetching user profile:', error);
        // Fallback to filtered styles for male users (since you're male)
        console.log('🔍 Falling back to male-appropriate styles due to profile fetch error');
        const maleStyles = filterStylesByGender(styles, 'male');
        setFilteredStyles(maleStyles);
      } finally {
        setProfileLoading(false);
      }
    };

    fetchUserProfile();
  }, [user]);


  const handleInputChange = (field: keyof OutfitGenerationForm, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // ✅ Direct shuffle handler - uses ref to bypass state delay
  const handleShuffleAndGenerate = (shuffledData?: { occasion: string; style: string; mood: string }) => {
    // If no data provided, auto-generate random values
    if (!shuffledData) {
      const availableStyles = filteredStyles.length > 0 ? filteredStyles : styles;
      const configuration = randomOutfitConfiguration({ occasions, styles: availableStyles, moods });
      if (!configuration) {
        setError('No suitable random combination is available. Please choose your outfit settings.');
        return;
      }
      shuffledData = configuration;
    }
    
    console.log('🎲 [Direct Shuffle] Received shuffled values:', shuffledData);
    
    // Store in ref for immediate access
    shuffleOverrideRef.current = shuffledData;
    
    // Update state for UI display
    setFormData(prev => ({
      ...prev,
      ...shuffledData!
    }));
    
    console.log('🎲 [Direct Shuffle] Stored in ref, triggering generation...');
    
    // Close sheet if open
    setSheetOpen(false);
    
    // Call generation immediately - it will use ref values
    handleGenerateOutfit();
  };
  
  const handleGenerateFromSheet = (options: { occasion: string; style: string; mood: string }) => {
    console.log('🎨 [Bottom Sheet] Received values:', options);
    
    // Store in ref for immediate access
    shuffleOverrideRef.current = options;
    
    // Update state for UI display
    setFormData(prev => ({
      ...prev,
      ...options
    }));
    
    // Close sheet
    setSheetOpen(false);
    
    // Call generation immediately
    handleGenerateOutfit();
  };

  const handleGenerateOutfit = async () => {
    if (generationInFlight.current) return;
    if (!user) {
      setError('Please sign in to generate outfits');
      return;
    }

    // ✅ Use shuffle override if available (for one-click shuffle)
    const activeFormData = shuffleOverrideRef.current || formData;
    
    // Clear shuffle override after use
    if (shuffleOverrideRef.current) {
      console.log('🎲 Using shuffle override values:', shuffleOverrideRef.current);
      shuffleOverrideRef.current = null;
    }

    if (!activeFormData.occasion || !activeFormData.style || !activeFormData.mood) {
      setError('Please fill in all required fields');
      return;
    }

    const requestUserId = user.uid;
    generationInFlight.current = true;
    try {
      setGenerating(true);
      setShowRevealAnimation(true);
      setError(null);
      
      // Get Firebase ID token for authentication
      const authToken = await user.getIdToken();
      
      // Enhanced weather data fetching with better error handling
      let weatherData: WeatherData;
      
      console.log('🌤️ Starting weather data preparation for outfit generation');
      
      // Priority 1: Check for manual weather override
      if (formData.weather && formData.weather !== "Auto") {
        console.log('🌤️ Using manual weather override:', formData.weather);
        weatherData = {
          temperature: formData.weather === "Hot" ? 85 : 
                      formData.weather === "Cold" ? 35 :
                      formData.weather === "Rainy" ? 60 : 72,
          condition: formData.weather === "Hot" ? "Clear" :
                    formData.weather === "Cold" ? "Clear" :
                    formData.weather === "Rainy" ? "Rain" :
                    formData.weather === "Windy" ? "Windy" : "Clear",
          humidity: formData.weather === "Rainy" ? 90 : 65,
          wind_speed: formData.weather === "Windy" ? 15 : 5,
          location: "Manual Override",
          precipitation: formData.weather === "Rainy" ? 80 : 0,
          fallback: true,
          isManualOverride: true
        };
      }
      // Priority 2: Check if we have recent, real weather data
      else if (weather && !weather.fallback && weather.location !== "Default Location" && weather.location !== "Unknown Location") {
        console.log('🌤️ Using existing real weather data:', weather);
        weatherData = { ...weather, isManualOverride: false, isRealWeather: true };
      } else {
        // Try to fetch fresh weather data using the hook's method
        console.log('🌤️ Fetching fresh weather data for outfit generation...');
        try {
          // First try to get saved location from localStorage
          const savedLocation = localStorage.getItem('user-location');
          let locationToUse = "Unknown Location";
          
          if (savedLocation) {
            locationToUse = savedLocation;
            console.log('🌤️ Using saved location:', savedLocation);
          } else {
            // Try geolocation
            try {
              const position = await new Promise<GeolocationPosition>((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                  timeout: 10000,
                  maximumAge: 5 * 60 * 1000,
                  enableHighAccuracy: false
                });
              });
              const { latitude, longitude } = position.coords;
              locationToUse = `${latitude},${longitude}`;
              console.log('🌤️ Using GPS coordinates:', locationToUse);
            } catch (geoError) {
              console.warn('🌤️ Geolocation failed:', geoError);
            }
          }
          
          // Fetch weather with the determined location
          const response = await fetch('/api/weather', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ location: locationToUse }),
          });

          if (!response.ok) {
            throw new Error(`Weather API error: ${response.status}`);
          }

          const freshWeatherData = await response.json();
          console.log('✅ Fresh weather data fetched successfully:', freshWeatherData);
          
          if (!freshWeatherData.fallback && freshWeatherData.location !== "Unknown Location" && freshWeatherData.location !== "Default Location") {
            weatherData = { ...freshWeatherData, isManualOverride: false, isRealWeather: true };
            // Store fresh weather data for UI display
            setFreshWeatherData(freshWeatherData);
            console.log('✅ Using real weather data from API');
          } else {
            throw new Error('Weather fetch returned fallback data');
          }
        } catch (err) {
          console.warn("Could not fetch weather, using enhanced fallback:", err);
          
          // Enhanced fallback that considers manual weather override
          weatherData = {
            temperature: formData.weather === "Hot" ? 85 : 
                        formData.weather === "Cold" ? 35 :
                        formData.weather === "Rainy" ? 60 : 72,
            condition: formData.weather || "Clear",
            humidity: formData.weather === "Rainy" ? 90 : 65,
            wind_speed: formData.weather === "Windy" ? 15 : 5,
            location: "Fallback Location",
            precipitation: formData.weather === "Rainy" ? 80 : 0,
            fallback: true,
            isManualOverride: false,
            isRealWeather: false,
            isFallbackWeather: true
          };
          console.log('⚠️ Using fallback weather data - API unavailable');
        }
      }

      // Log weather data being used for outfit generation
      console.log('🎯 Final weather data for outfit generation:', {
        temperature: weatherData.temperature,
        condition: weatherData.condition,
        location: weatherData.location,
        fallback: weatherData.fallback,
        isManualOverride: weatherData.isManualOverride,
        isRealWeather: weatherData.isRealWeather,
        isFallbackWeather: weatherData.isFallbackWeather
      });

      // Prepare request data with all required fields
      const requestData = {
        occasion: activeFormData.occasion,
        style: activeFormData.style,
        mood: activeFormData.mood,
        weather: weatherData,
        wardrobe: Array.isArray(wardrobeItems) ? wardrobeItems : (wardrobeItems as any)?.items || [],
        user_profile: buildOutfitGenerationUserProfile(userProfile, user),
        likedOutfits: [],
        trendingStyles: [],
        ...(baseItem && { baseItemId: baseItem.id })
      };
      
      console.log('🔍 DEBUG: Request data being sent:', {
        occasion: requestData.occasion,
        style: requestData.style,
        mood: requestData.mood,
        wardrobeCount: requestData.wardrobe?.length,
        wardrobeType: typeof requestData.wardrobe,
        wardrobeKeys: requestData.wardrobe ? Object.keys(requestData.wardrobe) : null,
        baseItem: baseItem ? { id: baseItem.id, name: baseItem.name, type: baseItem.type } : null,
        baseItemId: baseItem ? baseItem.id : null,
        baseItemName: baseItem ? baseItem.name : null
      });
      
      // Additional debug to show the full request data
      console.log('🔍 DEBUG: Full request data:', requestData);
      console.log('🔍 DEBUG: baseItemId in request:', requestData.baseItemId);
      
      // Convert frontend data to Pydantic-compatible format
      const { convertToPydanticShape, validateConvertedData } = await import('@/lib/outfitDataConverter');
      const { generateOutfit } = await import('@/lib/robustApiClient');
      
      const convertedData = convertToPydanticShape(requestData);
      
      // DEBUG: Check if converted wardrobe actually has metadata
      if (convertedData.wardrobe && convertedData.wardrobe.length > 0) {
        const firstConverted = convertedData.wardrobe[0];
        console.log('🔍 AFTER CONVERSION: First item keys:', Object.keys(firstConverted));
        console.log('🔍 AFTER CONVERSION: metadata present?', 'metadata' in firstConverted);
        if ('metadata' in firstConverted) {
          console.log('🔍 AFTER CONVERSION: metadata keys:', Object.keys(firstConverted.metadata));
          console.log('🔍 AFTER CONVERSION: visualAttributes?', firstConverted.metadata.visualAttributes);
        }
      }
      
      if (!validateConvertedData(convertedData)) {
        throw new Error('Data validation failed');
      }
      
      console.log('🔍 DEBUG: Making MAIN HYBRID API call to /api/outfits/generate endpoint with converted data');
      
      // Add generation_mode to default to robust for main outfit generation
      const requestWithMode = {
        ...convertedData,
        generation_mode: 'robust'
      };
      
      // Use robust API client with comprehensive error handling
      if (activeUser.current !== requestUserId) return;
      const response = await generateOutfit(requestWithMode, authToken);
      const data = response.data;
      assertRequiredBaseItem(data, baseItem?.id);
      console.log('🔍 DEBUG: Generated outfit data:', data);
      console.log('🔍 DEBUG: Items with images:', data.items?.map(item => ({ name: item.name, imageUrl: item.imageUrl })));
      console.log('🎨 DEBUG: Metadata:', data.metadata);
      console.log('🎨 DEBUG: Flat lay URL:', data.metadata?.flat_lay_url);

      if (typeof data.id !== 'string' || !data.id.trim()) {
        throw new Error('The server did not confirm that your outfit was saved.');
      }
      if (activeUser.current !== requestUserId) return;
      setGeneratedOutfit(data);
      router.push('/outfits/' + encodeURIComponent(data.id));
    } catch (err) {
      if (activeUser.current === requestUserId) setError(err instanceof Error ? err.message : 'Failed to generate outfit');
    } finally {
      generationInFlight.current = false;
      setGenerating(false);
      setShowRevealAnimation(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
        <Navigation />
        <div className="container mx-auto p-6">
          <WardrobeLoading />
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
        <Navigation />
        <div className="container mx-auto p-6">
          <div className="text-center">
            <Palette className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Authentication Required</h2>
            <p className="text-muted-foreground mb-4">Please sign in to generate outfits</p>
        </div>
      </div>
      

    </div>
  );
}

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
      <Navigation />
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 pb-24">
        {firstLookFlow && !generatedOutfit && <OnboardingProgress stage="first-look" />}
        {/* Header */}
        <div className="space-y-4 sm:space-y-0 sm:flex sm:items-center sm:gap-6 mb-8 sm:mb-12">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => router.push(firstLookFlow && !generatedOutfit ? '/onboarding' : '/outfits')}
            className="flex items-center gap-2 glass-button-secondary text-stone-700 dark:text-stone-300 hover:text-stone-900 dark:hover:text-stone-100 px-4 sm:px-6 py-2 sm:py-3 rounded-full text-sm sm:text-base font-medium glass-transition hover:scale-105"
          >
            <ArrowLeft className="h-4 w-4 sm:h-5 sm:w-5" />
            {firstLookFlow && !generatedOutfit ? 'Back to my capsule' : 'Back to My Looks'}
          </Button>
          <div className="space-y-2">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold flex items-center gap-3 text-stone-900 dark:text-stone-100">
              <Sparkles className="h-8 w-8 sm:h-10 sm:w-10 text-stone-600 dark:text-stone-400 flex-shrink-0" />
              <span>{firstLookFlow && !generatedOutfit ? 'Your first look starts here' : 'Generate New Outfit'}</span>
            </h1>
            <p className="text-stone-600 dark:text-stone-400 font-light text-base sm:text-lg">{firstLookFlow && !generatedOutfit ? 'Make your saved capsule work for your day.' : 'AI-powered outfit creation based on your preferences'}</p>
          </div>
        </div>

        {error && (
          <div
            role="alert"
            aria-live="assertive"
            className="max-w-md mx-auto mb-6 rounded-2xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-800 dark:bg-red-950/40 dark:text-red-200"
          >
            {error}
          </div>
        )}

        {/* Action Buttons - Modern Mobile-First */}
        {wardrobeLoadError && <div role="alert" className="mx-auto mb-6 max-w-3xl rounded-2xl border border-red-200 bg-red-50 p-5 text-red-900 dark:border-red-900 dark:bg-red-950 dark:text-red-100">
          <p>{wardrobeLoadError}</p><Button variant="outline" className="mt-3" onClick={() => setWardrobeLoadAttempt(value => value + 1)}>Retry wardrobe</Button>
        </div>}
        {firstLookFlow && !generatedOutfit && !generating && <div className="mx-auto mb-8 max-w-3xl">
          <FirstLookSetup
            onGenerate={handleGenerateFromSheet} onShuffle={() => handleShuffleAndGenerate()}
            disabled={wardrobeLoading || profileLoading || !!wardrobeLoadError} generating={generating}
            initialOptions={formData}
            weather={freshWeatherData || weather} weatherChoice={formData.weather || 'Auto'}
            onWeatherChange={value => setFormData(previous => ({ ...previous, weather: value }))}
            occasions={occasions} styles={filteredStyles.length ? filteredStyles : styles} moods={moods}
            baseItem={baseItem}
          />
        </div>}
        {!firstLookFlow && !generatedOutfit && !generating && (
          <div className="max-w-md mx-auto mb-8 space-y-4">
            <Button
              onClick={() => setSheetOpen(true)}
              disabled={wardrobeLoading || profileLoading || !!wardrobeLoadError}
              className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-primary to-accent text-primary-foreground hover:shadow-lg hover:shadow-primary/30 transition-all rounded-2xl"
            >
              <Sparkles className="h-5 w-5 mr-2" />
              Generate Outfit
            </Button>

            <motion.div
              whileTap={{ scale: 0.98 }}
              whileHover={{ scale: 1.01 }}
            >
              <Button 
                onClick={() => handleShuffleAndGenerate()}
                disabled={wardrobeLoading || profileLoading || !!wardrobeLoadError}
                variant="outline"
                className="w-full h-12 text-base font-semibold border-2 border-amber-500/50 hover:border-amber-500 hover:bg-amber-50 dark:hover:bg-amber-950/30 transition-all duration-200 relative overflow-hidden group rounded-2xl"
                size="lg"
              >
                <Shuffle className="h-5 w-5 mr-2 flex-shrink-0" />
                <span>Surprise Me! (Shuffle)</span>
                <Sparkles className="h-4 w-4 ml-2 text-amber-500 group-hover:text-amber-600" />
                
                {/* Shimmer effect */}
                {!wardrobeLoading && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-amber-400/20 to-transparent"
                    animate={{
                      x: ['-100%', '200%']
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "linear",
                      repeatDelay: 1.5
                    }}
                  />
                )}
              </Button>
            </motion.div>

            {wardrobeLoading && (
              <p className="text-sm text-amber-600 dark:text-amber-400 text-center">
                Loading your wardrobe...
              </p>
            )}
          </div>
        )}

        {/* Generated Outfit Display */}
        <div className="max-w-4xl mx-auto">
          <div className="space-y-6">
            {generatedOutfit ? (
              <div role="status" className="rounded-3xl border bg-card p-8 text-center">
                <p>Your outfit is saved. Opening your look…</p>
                <Button className="mt-4" onClick={() => router.push('/outfits/' + encodeURIComponent(generatedOutfit.id))}>Open saved outfit</Button>
              </div>
            ) : generating ? (
              <>
                {/* Phase 2: Progressive Reveal Animation */}
                {showRevealAnimation && (
                  <OutfitRevealAnimation
                    isGenerating={generating}
                    onComplete={() => {
                      setShowRevealAnimation(false);
                    }}
                  />
                )}
                {/* Fallback: Old loading component */}
                {!showRevealAnimation && <OutfitGenerating />}
              </>
            ) : !firstLookFlow ? (
              <Card className="border-dashed">
                <CardContent className="p-6 sm:p-8 lg:p-12 text-center">
                  <Sparkles className="h-12 w-12 sm:h-14 sm:w-14 lg:h-16 lg:w-16 text-muted-foreground mx-auto mb-3 sm:mb-4" />
                  <h3 className="text-base sm:text-lg font-semibold mb-2">Ready to Generate</h3>
                  <p className="text-sm sm:text-base text-muted-foreground">
                    Fill out the form and click "Generate Outfit" to create your AI-powered style combination
                  </p>
                </CardContent>
              </Card>
            ) : null}
          </div>
        </div>
      </div>

      {/* Modern Bottom Sheet for Generation */}
      <OutfitGenerationBottomSheet
        open={sheetOpen}
        onClose={() => setSheetOpen(false)}
        onGenerate={handleGenerateFromSheet}
        onShuffle={() => handleShuffleAndGenerate()}
        generating={generating}
        weather={freshWeatherData || weather}
        weatherChoice={formData.weather || 'Auto'}
        onWeatherChange={value => setFormData(previous => ({ ...previous, weather: value }))}
        disabled={wardrobeLoading || profileLoading || !!wardrobeLoadError}
        occasions={occasions}
        styles={filteredStyles.length > 0 ? filteredStyles : styles}
        moods={moods}
        baseItem={baseItem}
        onRemoveBaseItem={() => {
          setBaseItem(null);
          const url = new URL(window.location.href);
          url.searchParams.delete('baseItemId');
          window.history.replaceState({}, '', url.toString());
        }}
        userGender={userProfile?.gender}
      />

      <ClientOnlyNav />
      

    </div>
  );
}
