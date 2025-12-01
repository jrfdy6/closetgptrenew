'use client';

import { useState, useEffect, useCallback } from 'react';
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
  ArrowLeft
} from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import { useRouter } from 'next/navigation';
import OutfitService from '@/lib/services/outfitService';
import BodyPositiveMessage from '@/components/BodyPositiveMessage';
import { useAutoWeather } from '@/hooks/useWeather';
import type { WeatherData } from '@/types/weather';
import { subscriptionService, SUBSCRIPTION_TIERS } from '@/lib/services/subscriptionService';

// Import new enhanced components
import OutfitGenerationForm from '@/components/ui/outfit-generation-form';
import OutfitResultsDisplay from '@/components/ui/outfit-results-display';
import { OutfitGenerating, WardrobeLoading } from '@/components/ui/outfit-loading';
import StyleEducationModule from '@/components/ui/style-education-module';
// Phase 2: Progressive Reveal Components
import OutfitRevealAnimation from '@/components/OutfitRevealAnimation';
import { useToast } from '@/components/ui/use-toast';

interface OutfitGenerationForm {
  occasion: string;
  style: string;
  mood: string;
  weather: string;
  description: string;
}

interface GeneratedOutfit {
  id: string;
  name: string;
  style: string;
  mood: string;
  occasion: string;
  confidence_score: number;
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
}

interface OutfitRating {
  rating: number;
  isLiked: boolean;
  isDisliked: boolean;
  feedback?: string;
}

interface FlatLayUsage {
  tier: string;
  limit: number | null;
  used: number;
  remaining: number | null;
}

export default function OutfitGenerationPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useFirebase();
  const { weather, loading: weatherLoading, fetchWeatherByLocation } = useAutoWeather();
  const { toast } = useToast();
  const [baseItem, setBaseItem] = useState<any>(null);
  const [wardrobeItems, setWardrobeItems] = useState<any[]>([]);
  const [wardrobeLoading, setWardrobeLoading] = useState(false);
  const [freshWeatherData, setFreshWeatherData] = useState<WeatherData | null>(null);
  const [flatLayUsage, setFlatLayUsage] = useState<FlatLayUsage | null>(null);
  const [flatLayLoading, setFlatLayLoading] = useState(false);
  const [flatLayError, setFlatLayError] = useState<string | null>(null);
  const [flatLayActionLoading, setFlatLayActionLoading] = useState(false);
  
  const loadFlatLayUsage = useCallback(async () => {
    if (!user) {
      setFlatLayUsage(null);
      return;
    }

    setFlatLayLoading(true);
    setFlatLayError(null);

    try {
      // Use subscription service to get current subscription from payment system
      const subscription = await subscriptionService.getCurrentSubscription(user);
      const tier = subscription.role || 'tier1';
      
      // Get tier info to get the limit
      const tierInfo = subscriptionService.getTierInfo(tier);
      const limitStr = tierInfo?.limit || '1 flat lay/week';
      const limit = parseInt(limitStr.split('/')[0]) || 1;
      
      // Get remaining from subscription (already calculated by backend)
      const remaining = subscription.flatlays_remaining ?? 0;
      
      // Calculate used
      const used = Math.max(0, limit - remaining);

      setFlatLayUsage({ tier, limit, used, remaining });
    } catch (error) {
      console.error('Error loading flat lay usage:', error);
      setFlatLayError('Unable to load your flat lay balance right now.');
      setFlatLayUsage(null);
    } finally {
      setFlatLayLoading(false);
    }
  }, [user]);
  
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
          console.error('🔍 Failed to fetch wardrobe items:', response.status);
        }
      } catch (error) {
        console.error('🔍 Error fetching wardrobe items:', error);
      } finally {
        setWardrobeLoading(false);
      }
    };

    if (user) {
      fetchWardrobeItems();
    }
  }, [user]);
  
  // Use Next.js API routes instead of direct backend calls
  const API_BASE = '/api';
  const [formData, setFormData] = useState<OutfitGenerationForm>({
    occasion: '',
    style: '',
    mood: '',
    weather: '',
    description: ''
  });
  const [generating, setGenerating] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<GeneratedOutfit | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRevealAnimation, setShowRevealAnimation] = useState(false);
  const [outfitRating, setOutfitRating] = useState<OutfitRating>({
    rating: 0,
    isLiked: false,
    isDisliked: false,
    feedback: ''
  });
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [filteredStyles, setFilteredStyles] = useState<string[]>([]);

  useEffect(() => {
    if (generatedOutfit && user?.uid) {
      loadFlatLayUsage();
    }

    if (!generatedOutfit) {
      setFlatLayUsage(null);
    }
  }, [generatedOutfit?.id, user?.uid, loadFlatLayUsage]);

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
        return;
      }
      
      console.log('🔍 Fetching profile for user:', user.uid);
      try {
        const profileToken = await user.getIdToken();
        const response = await fetch('/api/user/profile', {
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
          if (formData.style && !filtered.includes(formData.style)) {
            console.log('🔍 Resetting incompatible style:', formData.style);
            setFormData(prev => ({ ...prev, style: '' }));
          }
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


  const handleGenerateOutfit = async () => {
    if (!user) {
      setError('Please sign in to generate outfits');
      return;
    }

    if (!formData.occasion || !formData.style || !formData.mood) {
      setError('Please fill in all required fields');
      return;
    }

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
        occasion: formData.occasion,
        style: formData.style,
        mood: formData.mood,
        weather: weatherData,
        wardrobe: Array.isArray(wardrobeItems) ? wardrobeItems : (wardrobeItems as any)?.items || [],
        user_profile: {
          id: user.uid,
          name: user.displayName || "User",
          email: user.email || "",
          gender: userProfile?.gender || "male",
          age: userProfile?.age || 25,
          style_preferences: userProfile?.style_preferences || [],
          size_preferences: userProfile?.size_preferences || [],
          color_preferences: userProfile?.color_preferences || []
        },
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
      const response = await generateOutfit(requestWithMode, authToken);
      const data = response.data;
      console.log('🔍 DEBUG: Generated outfit data:', data);
      console.log('🔍 DEBUG: Items with images:', data.items?.map(item => ({ name: item.name, imageUrl: item.imageUrl })));
      console.log('🎨 DEBUG: Metadata:', data.metadata);
      console.log('🎨 DEBUG: Flat lay URL:', data.metadata?.flat_lay_url);

      const enrichedMetadata = {
        ...(data.metadata ?? {}),
        flat_lay_status: data.metadata?.flat_lay_status ?? data.flat_lay_status ?? 'awaiting_consent',
        flatLayStatus: data.metadata?.flatLayStatus ?? data.flatLayStatus ?? 'awaiting_consent',
        flat_lay_url: data.metadata?.flat_lay_url ?? data.flat_lay_url ?? null,
        flatLayUrl: data.metadata?.flatLayUrl ?? data.flatLayUrl ?? null,
        flat_lay_error: data.metadata?.flat_lay_error ?? data.flat_lay_error ?? null,
        flatLayError: data.metadata?.flatLayError ?? data.flatLayError ?? null,
        flat_lay_requested: data.metadata?.flat_lay_requested ?? data.flat_lay_requested ?? false,
        flatLayRequested: data.metadata?.flatLayRequested ?? data.flatLayRequested ?? false,
      };

      const enrichedData = {
        ...data,
        metadata: enrichedMetadata,
        flat_lay_status: data.flat_lay_status ?? enrichedMetadata.flat_lay_status,
        flatLayStatus: data.flatLayStatus ?? enrichedMetadata.flatLayStatus,
        flat_lay_url: data.flat_lay_url ?? enrichedMetadata.flat_lay_url,
        flatLayUrl: data.flatLayUrl ?? enrichedMetadata.flatLayUrl,
        flat_lay_error: data.flat_lay_error ?? enrichedMetadata.flat_lay_error,
        flatLayError: data.flatLayError ?? enrichedMetadata.flatLayError,
        flat_lay_requested: data.flat_lay_requested ?? enrichedMetadata.flat_lay_requested ?? false,
        flatLayRequested: data.flatLayRequested ?? enrichedMetadata.flatLayRequested ?? false,
      };

      setGeneratedOutfit(enrichedData);
      
      // Check for slow request and show user-friendly message
      if (enrichedData.metadata?.is_slow) {
        const duration = enrichedData.metadata?.generation_duration || 0;
        console.log(`⚠️ Slow generation detected: ${duration}s`);
        // Note: User-facing message can be displayed in UI component
      }
      
      // Auto-save the generated outfit directly to Firestore
      if (user) {
        try {
          // Validate minimum items before saving
          if (!data.items || data.items.length < 3) {
            console.warn('🔍 DEBUG: Skipping auto-save - need at least 3 items to save outfit');
            return;
          }
          
          console.log('💾 Auto-saving outfit to Firestore...');
          
          // Import Firebase directly to save
          const { db } = await import('@/lib/firebase/config');
          const { collection, doc, setDoc } = await import('firebase/firestore');
          
          // Prepare outfit data for Firestore
          const outfitId = enrichedData.id || `outfit_${Date.now()}`;
          const now = new Date().toISOString();
          const outfitData = {
            id: outfitId,
            name: enrichedData.name,
            occasion: enrichedData.occasion || formData.occasion,
            style: enrichedData.style,
            mood: enrichedData.mood || 'neutral',
            description: enrichedData.reasoning || enrichedData.description || '',
            items: enrichedData.items.map((item: any) => ({
              id: item.id,
              name: item.name,
              category: item.category || item.type,
              type: item.type || item.category,
              color: item.color,
              imageUrl: item.imageUrl || "",
              user_id: user.uid
            })),
            user_id: user.uid,
            createdAt: now,
            updatedAt: now,
            wearCount: 0,
            isFavorite: false,
            confidence_score: enrichedData.confidence_score || 0.8,
            generation_strategy: enrichedData.generation_strategy || 'hybrid',
            metadata: enrichedMetadata,
            flat_lay_status: enrichedMetadata.flat_lay_status,
            flatLayStatus: enrichedMetadata.flatLayStatus,
            flat_lay_url: enrichedMetadata.flat_lay_url,
            flatLayUrl: enrichedMetadata.flatLayUrl,
            flat_lay_error: enrichedMetadata.flat_lay_error,
            flatLayError: enrichedMetadata.flatLayError,
            flat_lay_requested: enrichedMetadata.flat_lay_requested ?? false,
            flatLayRequested: enrichedMetadata.flatLayRequested ?? false,
          };
          
          // Save directly to Firestore
          const outfitRef = doc(collection(db, 'outfits'), outfitId);
          await setDoc(outfitRef, outfitData);
          
          console.log('✅ Outfit auto-saved successfully to Firestore with ID:', outfitId);
          
          // Update the outfit with the confirmed ID
          setGeneratedOutfit(prev => prev ? {
            ...prev,
            id: outfitId,
            metadata: {
              ...(prev.metadata ?? {}),
              ...enrichedMetadata,
            }
          } : null);
        } catch (err) {
          console.log('🔍 DEBUG: Auto-save failed, but outfit generation succeeded');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate outfit');
    } finally {
      setGenerating(false);
      setShowRevealAnimation(false);
    }
  };

  const hasFlatLayCredits = flatLayUsage
    ? flatLayUsage.remaining === null || (flatLayUsage.remaining ?? 0) > 0
    : false;

  const handleFlatLayRequest = useCallback(async () => {
    if (!generatedOutfit?.id || !user) {
      return;
    }

    if (
      flatLayUsage &&
      flatLayUsage.remaining !== null &&
      flatLayUsage.remaining <= 0
    ) {
      toast({
        title: "No credits available",
        description: "Upgrade your plan to unlock more flat lay credits.",
        variant: "destructive"
      });
      return;
    }

    setFlatLayActionLoading(true);

    try {
      // Consume quota immediately when user requests flat lay
      await subscriptionService.consumeFlatLayQuota(user);
      
      const [{ db }, firestore] = await Promise.all([
        import('@/lib/firebase/config'),
        import('firebase/firestore'),
      ]);

      const outfitRef = firestore.doc(db, 'outfits', generatedOutfit.id);

      await firestore.updateDoc(outfitRef, {
        flat_lay_status: 'pending',
        flatLayStatus: 'pending',
        'metadata.flat_lay_status': 'pending',
        'metadata.flatLayStatus': 'pending',
        flat_lay_requested: true,
        flatLayRequested: true,
        'metadata.flat_lay_requested': true,
        'metadata.flatLayRequested': true,
        flat_lay_error: null,
        flatLayError: null,
        'metadata.flat_lay_error': null,
        'metadata.flatLayError': null,
        'metadata.flat_lay_worker': 'premium_v1',
        'metadata.flatLayWorker': 'premium_v1',
      });

      setGeneratedOutfit(prev =>
        prev
          ? {
              ...prev,
              flat_lay_status: 'pending',
              flatLayStatus: 'pending',
              flat_lay_url: null,
              flatLayUrl: null,
              flat_lay_error: null,
              flatLayError: null,
              flat_lay_requested: true,
              flatLayRequested: true,
              metadata: {
                ...(prev.metadata ?? {}),
                flat_lay_status: 'pending',
                flatLayStatus: 'pending',
                flat_lay_url: null,
                flatLayUrl: null,
                flat_lay_error: null,
                flatLayError: null,
                flat_lay_requested: true,
                flatLayRequested: true,
                flat_lay_worker: 'premium_v1',
                flatLayWorker: 'premium_v1',
              },
            }
          : prev
      );

      toast({
        title: "Flat lay on the way!",
        description: "We'll craft your premium flat lay and notify you once it's ready.",
      });

      // Refresh quota display to show updated count
      loadFlatLayUsage();
    } catch (error) {
      console.error('Error requesting flat lay:', error);
      toast({
        title: "Unable to request flat lay",
        description: "Please try again from your outfits list.",
        variant: "destructive"
      });
    } finally {
      setFlatLayActionLoading(false);
    }
  }, [generatedOutfit?.id, user, flatLayUsage, toast, loadFlatLayUsage]);

  const handleFlatLaySkip = useCallback(async () => {
    if (!generatedOutfit) {
      return;
    }

    if (flatLayActionLoading) {
      return;
    }

    const outfitId = generatedOutfit.id;

    // Optimistically update local state so the grid is visible immediately
    setGeneratedOutfit(prev =>
      prev
        ? {
            ...prev,
            flat_lay_status: 'declined',
            flatLayStatus: 'declined',
            flat_lay_requested: false,
            flatLayRequested: false,
            metadata: {
              ...(prev.metadata ?? {}),
              flat_lay_status: 'declined',
              flatLayStatus: 'declined',
              flat_lay_requested: false,
              flatLayRequested: false,
            },
          }
        : prev
    );

    // If we don't have an outfit ID yet (e.g. before autosave completes), just exit after the optimistic update
    if (!user || !outfitId) {
      toast({
        title: "Flat lay skipped",
        description: "You can always generate a flat lay later from My Outfits.",
      });
      return;
    }

    setFlatLayActionLoading(true);

    try {
      const [{ db }, firestore] = await Promise.all([
        import('@/lib/firebase/config'),
        import('firebase/firestore'),
      ]);

      const outfitRef = firestore.doc(db, 'outfits', outfitId);

      await firestore.updateDoc(outfitRef, {
        flat_lay_status: 'declined',
        flatLayStatus: 'declined',
        'metadata.flat_lay_status': 'declined',
        'metadata.flatLayStatus': 'declined',
        flat_lay_requested: false,
        flatLayRequested: false,
        'metadata.flat_lay_requested': false,
        'metadata.flatLayRequested': false,
      });

      toast({
        title: "Flat lay skipped",
        description: "You can always generate a flat lay later from My Outfits.",
      });

      loadFlatLayUsage();
    } catch (error) {
      console.error('Error updating flat lay status:', error);
      toast({
        title: "Unable to update flat lay",
        description: "Please try again.",
        variant: "destructive"
      });
    } finally {
      setFlatLayActionLoading(false);
    }
  }, [generatedOutfit, user, flatLayActionLoading, toast, loadFlatLayUsage]);

  const handleWearOutfit = async () => {
    if (!generatedOutfit || !user) return;
    
    // Validate minimum items before wearing
    if (!generatedOutfit.items || generatedOutfit.items.length < 3) {
      setError('Need at least 3 items to wear an outfit');
      return;
    }
    
    try {
      const currentTimestamp = Date.now();
      const currentDate = new Date(currentTimestamp);
      console.log(`📅 [Generate] Sending timestamp: ${currentTimestamp} (${currentDate.toLocaleString()})`);
      
      // Use API route to mark as worn - this updates backend stats for dashboard counter
      const wornToken = await user.getIdToken();
      const response = await fetch(`/api/outfit-history/mark-worn`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${wornToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          outfitId: generatedOutfit.id,
          outfitName: generatedOutfit.name,
          dateWorn: currentTimestamp, // Send current timestamp in milliseconds to avoid timezone issues
          occasion: generatedOutfit.occasion || 'Casual',
          mood: generatedOutfit.mood || 'Confident',
          weather: generatedOutfit.weather || {},
          notes: `Generated outfit: ${generatedOutfit.name}`,
          tags: ['generated'],
          items: generatedOutfit.items // Include items for wear count updates
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to mark outfit as worn: ${response.status}`);
      }
      
      const result = await response.json();
      console.log(`✅ [Generate] Successfully marked outfit as worn via API:`, result);
      
      // Dispatch event to notify dashboard of outfit being marked as worn
      const event = new CustomEvent('outfitMarkedAsWorn', {
        detail: {
          outfitId: generatedOutfit.id,
          outfitName: generatedOutfit.name,
          timestamp: new Date().toISOString()
        }
      });
      window.dispatchEvent(event);
      console.log('🔄 [Generate] Dispatched outfitMarkedAsWorn event for dashboard refresh');
      
      // Show success message and navigate to outfits page
      setError(null);
      // Show success message briefly before navigating
      setGeneratedOutfit(prev => prev ? {
        ...prev,
        isWorn: true,
        lastWorn: new Date().toISOString()
      } : null);
      
      // Navigate after a short delay to show success
      setTimeout(() => {
        // Add timestamp to force refresh of outfits page
        const timestamp = Date.now();
        console.log('🔄 [Generate] Navigating to outfits page with forced refresh');
        router.push(`/outfits?refresh=${timestamp}`);
      }, 1500);
    } catch (err) {
      console.error('Error wearing outfit:', err);
      setError('Failed to wear outfit');
    }
  };

  const handleRegenerate = () => {
    setGeneratedOutfit(null);
    setError(null);
    setOutfitRating({ rating: 0, isLiked: false, isDisliked: false, feedback: '' });
    setRatingSubmitted(false);
  };

  const handleRatingChange = (rating: number) => {
    setOutfitRating(prev => ({ ...prev, rating }));
    // Auto-submit after a short delay to allow user to see their selection
    setTimeout(() => {
      if (rating > 0) {
        handleSubmitRating();
      }
    }, 500);
  };

  const handleLikeToggle = () => {
    setOutfitRating(prev => ({ 
      ...prev, 
      isLiked: !prev.isLiked, 
      isDisliked: false 
    }));
    // Auto-submit like/dislike changes
    setTimeout(() => {
      handleSubmitRating();
    }, 300);
  };

  const handleDislikeToggle = () => {
    setOutfitRating(prev => ({ 
      ...prev, 
      isDisliked: !prev.isDisliked, 
      isLiked: false 
    }));
    // Auto-submit like/dislike changes
    setTimeout(() => {
      handleSubmitRating();
    }, 300);
  };

  const handleFeedbackChange = (feedback: string) => {
    setOutfitRating(prev => ({ ...prev, feedback }));
    // Auto-submit feedback after user stops typing (debounced)
    clearTimeout((window as any).feedbackTimeout);
    (window as any).feedbackTimeout = setTimeout(() => {
      if (feedback.trim() && outfitRating.rating > 0) {
        handleSubmitRating();
      }
    }, 1000);
  };

  const handleSubmitRating = async () => {
    if (!generatedOutfit || !user) return;
    
    // Only submit if there's actual rating data
    if (outfitRating.rating === 0 && !outfitRating.isLiked && !outfitRating.isDisliked && !outfitRating.feedback.trim()) {
      console.log('🔍 DEBUG: No rating data to submit, skipping');
      return;
    }
    
    try {
      const ratingToken = await user.getIdToken();
      
      // If outfit doesn't have an ID yet, save it first
      let outfitId = generatedOutfit.id;
      console.log('🔍 DEBUG: Checking outfit ID for rating:', { 
        outfitId, 
        hasId: !!outfitId,
        outfitName: generatedOutfit.name 
      });
      
      if (!outfitId) {
        console.log('🔍 DEBUG: No outfit ID found, will save outfit first');
        // Validate minimum items before saving for rating
        if (!generatedOutfit.items || generatedOutfit.items.length < 3) {
          setError('Need at least 3 items to save and rate an outfit');
          return;
        }
        
        const outfitPayload = {
          name: generatedOutfit.name,
          occasion: generatedOutfit.occasion || formData.occasion,
          style: generatedOutfit.style,
          description: generatedOutfit.reasoning,
          items: generatedOutfit.items.map((item: any) => ({
            ...item,
            userId: user.uid,  // Required: inject from Firebase auth
            subType: item.subType || item.category || item.type || "item",  // Required: fallback chain
            style: [generatedOutfit.style] || ["casual"],  // Required: List[str] from parent outfit
            occasion: [generatedOutfit.occasion || formData.occasion] || ["casual"],  // Required: List[str] from parent
            imageUrl: item.imageUrl || item.image_url || item.image || "",  // Normalize image field
            color: item.color || "unknown",  // Ensure color is provided
            type: item.type || "item",  // Ensure type is provided
            
            // Required ClothingItem fields that were missing:
            season: ["All"],                               // fallback if no season logic yet
            tags: [],                                      // default empty array
            dominantColors: [],                            // default empty array
            matchingColors: [],                            // default empty array
            createdAt: Math.floor(Date.now() / 1000),      // timestamp in seconds
            updatedAt: Math.floor(Date.now() / 1000),      // timestamp in seconds
          })),
          createdAt: Math.floor(Date.now() / 1000),
          metadata: {
            ...(generatedOutfit.metadata ?? {}),
            flat_lay_status: 'awaiting_consent',
            flatLayStatus: 'awaiting_consent',
            flat_lay_requested: false,
            flatLayRequested: false,
          },
          flat_lay_status: 'awaiting_consent',
          flatLayStatus: 'awaiting_consent',
          flat_lay_url: null,
          flatLayUrl: null,
          flat_lay_error: null,
          flatLayError: null,
          flat_lay_requested: false,
          flatLayRequested: false,
        };
        
        console.log('🔍 DEBUG: Outfit creation payload:', JSON.stringify(outfitPayload, null, 2));
        
        const saveResponse = await fetch('/api/outfits', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${ratingToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(outfitPayload),
        });
        
        if (saveResponse.ok) {
          const savedOutfit = await saveResponse.json();
          outfitId = savedOutfit.id || savedOutfit.outfitId;
          
          console.log('✅ [Generate] Outfit saved successfully:', savedOutfit);
          
          // Update the generated outfit with the new ID
          setGeneratedOutfit(prev => prev ? {
            ...prev,
            id: outfitId
          } : null);
        } else {
          console.error('❌ [Generate] Failed to save outfit:', saveResponse.status, await saveResponse.text());
          setError('Failed to save outfit for rating');
          return;
        }
      }
      
      // Prepare rating payload - only include rating if stars were selected
      const ratingPayload: any = {
        outfitId: outfitId,
        isLiked: outfitRating.isLiked,
        isDisliked: outfitRating.isDisliked,
        feedback: outfitRating.feedback
      };
      
      // Only include rating if stars were actually selected (1-5)
      if (outfitRating.rating > 0) {
        ratingPayload.rating = outfitRating.rating;
      }
      
      console.log('🔍 DEBUG: Submitting rating payload:', ratingPayload);
      
      // Submit rating to backend
      const response = await fetch('/api/outfits/rate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${ratingToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(ratingPayload),
      });
      
      if (response.ok) {
        setRatingSubmitted(true);
        // Update the generated outfit with rating data
        setGeneratedOutfit(prev => prev ? {
          ...prev,
          rating: outfitRating.rating,
          isLiked: outfitRating.isLiked,
          isDisliked: outfitRating.isDisliked
        } : null);
        console.log('✅ Rating submitted successfully');
        console.log('🔄 [Generate] Rating submitted - outfit should now be available in outfits list');
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Rating submission failed:', errorData);
        setError(`Failed to submit rating: ${errorData.detail || errorData.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('❌ Error submitting rating:', err);
      setError('Failed to submit rating');
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
        {/* Header */}
        <div className="space-y-4 sm:space-y-0 sm:flex sm:items-center sm:gap-6 mb-8 sm:mb-12">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => router.push('/outfits')}
            className="flex items-center gap-2 glass-button-secondary text-stone-700 dark:text-stone-300 hover:text-stone-900 dark:hover:text-stone-100 px-4 sm:px-6 py-2 sm:py-3 rounded-full text-sm sm:text-base font-medium glass-transition hover:scale-105"
          >
            <ArrowLeft className="h-4 w-4 sm:h-5 sm:w-5" />
            Back to My Looks
          </Button>
          <div className="space-y-2">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold flex items-center gap-3 text-stone-900 dark:text-stone-100">
              <Sparkles className="h-8 w-8 sm:h-10 sm:w-10 text-stone-600 dark:text-stone-400 flex-shrink-0" />
              <span>Generate New Outfit</span>
            </h1>
            <p className="text-stone-600 dark:text-stone-400 font-light text-base sm:text-lg">AI-powered outfit creation based on your preferences</p>
          </div>
        </div>


        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
          {/* Enhanced Outfit Generation Form */}
          <OutfitGenerationForm
            formData={formData}
            onFormChange={(field, value) => handleInputChange(field, value)}
            onGenerate={handleGenerateOutfit}
            generating={generating}
            wardrobeLoading={wardrobeLoading}
            occasions={occasions}
            styles={filteredStyles.length > 0 ? filteredStyles : styles}
            moods={moods}
            weatherOptions={weatherOptions}
            baseItem={baseItem}
            freshWeatherData={freshWeatherData}
            onRemoveBaseItem={() => {
              setBaseItem(null);
              const url = new URL(window.location.href);
              url.searchParams.delete('baseItem');
              window.history.replaceState({}, '', url.toString());
            }}
          />

          {/* Enhanced Generated Outfit Display */}
          <div className="space-y-6">
            {generatedOutfit ? (
              <>
                {/* Slow request notification */}
                {generatedOutfit.metadata?.is_slow && (
                  <Card className="border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/50">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <Clock className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-amber-900 dark:text-amber-100">
                            This is taking longer than usual...
                          </p>
                          <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
                            We're still working on it. Your outfit will be ready shortly.
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
                <BodyPositiveMessage variant="outfit" />
                <OutfitResultsDisplay
                outfit={generatedOutfit}
                rating={outfitRating}
                onRatingChange={handleRatingChange}
                onLikeToggle={handleLikeToggle}
                onDislikeToggle={handleDislikeToggle}
                onFeedbackChange={handleFeedbackChange}
                onWearOutfit={handleWearOutfit}
                onRegenerate={handleRegenerate}
                onViewOutfits={() => router.push(`/outfits?refresh=${Date.now()}`)}
                ratingSubmitted={ratingSubmitted}
                isWorn={generatedOutfit?.isWorn}
                flatLayUsage={flatLayUsage}
                flatLayLoading={flatLayLoading}
                flatLayError={flatLayError}
                onRequestFlatLay={handleFlatLayRequest}
                onSkipFlatLay={handleFlatLaySkip}
                flatLayActionLoading={flatLayActionLoading}
                hasFlatLayCredits={hasFlatLayCredits}
              />
              </>
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
            ) : (
              <Card className="border-dashed">
                <CardContent className="p-6 sm:p-8 lg:p-12 text-center">
                  <Sparkles className="h-12 w-12 sm:h-14 sm:w-14 lg:h-16 lg:w-16 text-muted-foreground mx-auto mb-3 sm:mb-4" />
                  <h3 className="text-base sm:text-lg font-semibold mb-2">Ready to Generate</h3>
                  <p className="text-sm sm:text-base text-muted-foreground">
                    Fill out the form and click "Generate Outfit" to create your AI-powered style combination
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>

      <ClientOnlyNav />
    </div>
  );
}
