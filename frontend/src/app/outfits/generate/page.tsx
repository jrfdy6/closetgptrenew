"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useWardrobe } from "@/hooks/useWardrobe";
import { useUserProfile } from "@/hooks/useUserProfile";
import { useWeather } from "@/hooks/useWeather";
import { authenticatedFetch } from "@/lib/utils/auth";
import { ClothingItem } from "../../shared/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { WeatherDisplay } from "@/components/WeatherDisplay";
import { Shuffle, X, RefreshCw, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import Image from "next/image";
import { OutfitWarnings } from '@/components/ui/OutfitWarnings';

const OCCASIONS = [
  "Casual",
  "Business Casual",
  "Formal",
  "Gala",
  "Party",
  "Date Night",
  "Work",
  "Interview",
  "Brunch",
  "Wedding Guest",
  "Cocktail",
  "Travel",
  "Airport",
  "Loungewear",
  "Beach",
  "Vacation",
  "Festival",
  "Rainy Day",
  "Snow Day",
  "Hot Weather",
  "Cold Weather",
  "Night Out",
  "Athletic / Gym",
  "School",
  "Holiday",
  "Concert",
  "Errands",
  "Chilly Evening",
  "Museum / Gallery",
  "First Date",
  "Business Formal",
  "Funeral / Memorial",
  "Fashion Event",
  "Outdoor Gathering"
];
const MOODS = ["energetic", "relaxed", "confident", "playful", "elegant"];
const STYLES = [
  "Dark Academia",
  "Old Money",
  "Streetwear",
  "Y2K",
  "Minimalist",
  "Boho",
  "Preppy",
  "Grunge",
  "Classic",
  "Techwear",
  "Androgynous",
  "Coastal Chic",
  "Business Casual",
  "Avant-Garde",
  "Cottagecore",
  "Edgy",
  "Athleisure",
  "Casual Cool",
  "Romantic",
  "Artsy"
];

export default function GenerateOutfitPage() {
  const router = useRouter();
  const { wardrobe, loading: wardrobeLoading } = useWardrobe();
  const { profile, isLoading: profileLoading } = useUserProfile();
  const { weather, loading: weatherLoading } = useWeather();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [baseItem, setBaseItem] = useState<ClothingItem | null>(null);
  const [formData, setFormData] = useState({
    occasion: "",
    mood: "",
    style: "",
    description: "",
  });

  // Check for base item and form data from sessionStorage on component mount
  useEffect(() => {
    console.log('🔍 DEBUG: GenerateOutfitPage useEffect triggered');
    
    const storedBaseItem = sessionStorage.getItem('baseItem');
    const storedFormData = sessionStorage.getItem('outfitFormData');
    
    console.log('🔍 DEBUG: sessionStorage contents:');
    console.log('  - baseItem exists:', !!storedBaseItem);
    console.log('  - formData exists:', !!storedFormData);
    
    if (storedBaseItem) {
      try {
        const parsedItem = JSON.parse(storedBaseItem);
        console.log('✅ DEBUG: Successfully parsed base item:', {
          id: parsedItem.id,
          name: parsedItem.name,
          type: parsedItem.type,
          color: parsedItem.color
        });
        setBaseItem(parsedItem);
        // Clear from sessionStorage after retrieving
        sessionStorage.removeItem('baseItem');
        console.log('✅ DEBUG: Cleared baseItem from sessionStorage');
      } catch (error) {
        console.error('❌ DEBUG: Error parsing base item from sessionStorage:', error);
        console.log('🔍 DEBUG: Raw baseItem string:', storedBaseItem);
      }
    } else {
      console.log('ℹ️ DEBUG: No baseItem found in sessionStorage');
    }
    
    if (storedFormData) {
      try {
        const parsedFormData = JSON.parse(storedFormData);
        console.log('✅ DEBUG: Successfully parsed form data:', parsedFormData);
        setFormData(parsedFormData);
        // Clear from sessionStorage after retrieving
        sessionStorage.removeItem('outfitFormData');
        console.log('✅ DEBUG: Cleared outfitFormData from sessionStorage');
      } catch (error) {
        console.error('❌ DEBUG: Error parsing form data from sessionStorage:', error);
        console.log('🔍 DEBUG: Raw formData string:', storedFormData);
      }
    } else {
      console.log('ℹ️ DEBUG: No outfitFormData found in sessionStorage');
    }
  }, []);

  const clearBaseItem = () => {
    setBaseItem(null);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setError(null);

    if (!wardrobe || wardrobe.length === 0) {
      setError("Please add some items to your wardrobe first");
      setIsRefreshing(false);
      return;
    }

    if (!profile) {
      setError("Please complete your profile first");
      setIsRefreshing(false);
      return;
    }

    const weatherData = weather || {
      temperature: 75,
      condition: "sunny",
      location: "default",
      humidity: 50,
      wind_speed: 5,
      precipitation: 0
    };

    try {
      let outfitHistory = [];
      try {
        const historyResponse = await authenticatedFetch('/api/outfits');
        if (historyResponse.ok) {
          const historyData = await historyResponse.json();
          outfitHistory = historyData.slice(0, 10).map((outfit: any) => ({
            id: outfit.id,
            items: outfit.items || [],
            createdAt: outfit.createdAt || Date.now(),
            occasion: outfit.occasion,
            style: outfit.style
          }));
        }
      } catch (error) {
        console.warn('Failed to retrieve outfit history for diversity:', error);
      }

      const payload = {
        ...formData,
        wardrobe: wardrobe,
        weather: weatherData,
        user_profile: {
          id: profile.id,
          name: profile.name,
          email: profile.email,
          preferences: profile.preferences,
          measurements: profile.measurements,
          stylePreferences: profile.stylePreferences,
          bodyType: profile.bodyType || 'athletic',
          skinTone: profile.measurements.skinTone,
          createdAt: profile.createdAt,
          updatedAt: profile.updatedAt
        },
        likedOutfits: [],
        trendingStyles: [],
        outfitHistory: outfitHistory,
        baseItem: baseItem
      };

      const response = await authenticatedFetch("/api/outfit/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.details || data.error || "Failed to generate outfit");
      }

      router.push(`/outfits/${data.id}`);
    } catch (err) {
      console.error('Outfit Generation Error:', err);
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsRefreshing(false);
    }
  };

  const randomizeFields = () => {
    const randomOccasion = OCCASIONS[Math.floor(Math.random() * OCCASIONS.length)];
    const randomMood = MOODS[Math.floor(Math.random() * MOODS.length)];
    const randomStyle = STYLES[Math.floor(Math.random() * STYLES.length)];
    const userGender = profile?.gender || 'male';

    setFormData(prev => ({
      ...prev,
      occasion: randomOccasion,
      mood: randomMood,
      style: randomStyle,
      gender: userGender,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    console.log('🔍 DEBUG: handleSubmit called');
    e.preventDefault();
    setLoading(true);
    setError(null);

    console.log('🔍 DEBUG: Form validation:');
    console.log('  - wardrobe exists:', !!wardrobe);
    console.log('  - wardrobe length:', wardrobe?.length || 0);
    console.log('  - profile exists:', !!profile);
    console.log('  - formData:', formData);
    console.log('  - baseItem:', baseItem);

    if (!wardrobe || wardrobe.length === 0) {
      console.error('❌ DEBUG: No wardrobe items found');
      setError("Please add some items to your wardrobe first");
      setLoading(false);
      return;
    }

    if (!profile) {
      console.error('❌ DEBUG: No user profile found');
      setError("Please complete your profile first");
      setLoading(false);
      return;
    }

    // Use actual weather data if available, fallback to default if not
    const weatherData = weather || {
      temperature: 75, // Changed from 70 to 75 as a more reasonable fallback
      condition: "sunny",
      location: "default",
      humidity: 50,
      wind_speed: 5,
      precipitation: 0
    };

    // Log weather data for debugging
    console.log('Weather data for outfit generation:', {
      actualWeather: weather,
      fallbackWeather: weatherData,
      usingActualWeather: !!weather
    });

    try {
      // NEW: Retrieve recent outfit history for diversity
      let outfitHistory = [];
      try {
        const historyResponse = await authenticatedFetch('/api/outfits');
        if (historyResponse.ok) {
          const historyData = await historyResponse.json();
          // Get the last 10 outfits for diversity filtering
          outfitHistory = historyData.slice(0, 10).map((outfit: any) => ({
            id: outfit.id,
            items: outfit.items || [],
            createdAt: outfit.createdAt || Date.now(),
            occasion: outfit.occasion,
            style: outfit.style
          }));
          console.log(`📚 Retrieved ${outfitHistory.length} recent outfits for diversity`);
        }
      } catch (error) {
        console.warn('Failed to retrieve outfit history for diversity:', error);
        // Continue without history if retrieval fails
      }

      // Transform baseItem from WardrobeItem to ClothingItem format if it exists
      let transformedBaseItem = null;
      if (baseItem) {
        console.log('🔍 DEBUG: Transforming baseItem from WardrobeItem to ClothingItem format');
        transformedBaseItem = {
          id: baseItem.id,
          name: baseItem.name,
          type: baseItem.type,
          color: baseItem.color,
          season: baseItem.season || [],
          imageUrl: baseItem.imageUrl,
          tags: baseItem.tags || [],
          style: baseItem.style || [],
          userId: profile.id, // Use current user's ID
          dominantColors: baseItem.metadata?.colorAnalysis?.dominant || [],
          matchingColors: baseItem.metadata?.colorAnalysis?.matching || [],
          occasion: (baseItem.metadata as any)?.occasionTags || [],
          brand: (baseItem.metadata as any)?.brand || null,
          createdAt: baseItem.createdAt,
          updatedAt: baseItem.updatedAt,
          subType: null, // Not available in WardrobeItem
          colorName: null, // Not available in WardrobeItem
          backgroundRemoved: null, // Not available in WardrobeItem
          embedding: null, // Not available in WardrobeItem
          metadata: {
            analysisTimestamp: baseItem.createdAt || Date.now(),
            originalType: baseItem.type,
            colorAnalysis: {
              dominant: baseItem.metadata?.colorAnalysis?.dominant || [],
              matching: baseItem.metadata?.colorAnalysis?.matching || []
            },
            styleTags: baseItem.style || [],
            occasionTags: (baseItem.metadata as any)?.occasionTags || [],
            brand: (baseItem.metadata as any)?.brand || null,
            imageHash: null,
            basicMetadata: null,
            visualAttributes: null,
            itemMetadata: null,
            naturalDescription: null,
            temperatureCompatibility: null,
            materialCompatibility: null,
            bodyTypeCompatibility: null,
            skinToneCompatibility: null,
            outfitScoring: null
          },
          wearCount: 0,
          lastWorn: 0.0,
          favorite_score: 0.0
        };
        console.log('✅ DEBUG: Base item transformed successfully:', {
          id: transformedBaseItem.id,
          name: transformedBaseItem.name,
          hasTags: !!transformedBaseItem.tags,
          hasUserId: !!transformedBaseItem.userId,
          hasDominantColors: !!transformedBaseItem.dominantColors,
          hasMatchingColors: !!transformedBaseItem.matchingColors,
          hasOccasion: !!transformedBaseItem.occasion
        });
      }

      const payload = {
        ...formData,
        wardrobe: wardrobe,
        weather: weatherData,
        user_profile: {
          id: profile.id,
          name: profile.name,
          email: profile.email,
          preferences: profile.preferences,
          measurements: profile.measurements,
          stylePreferences: profile.stylePreferences,
          bodyType: profile.bodyType || 'athletic',
          skinTone: profile.measurements.skinTone,
          createdAt: profile.createdAt,
          updatedAt: profile.updatedAt
        },
        likedOutfits: [],
        trendingStyles: [],
        outfitHistory: outfitHistory,  // NEW: Add outfit history for diversity
        baseItem: transformedBaseItem // Use the transformed base item
      };

      console.log('🔍 DEBUG: Payload structure:');
      console.log('  - occasion:', formData.occasion);
      console.log('  - mood:', formData.mood);
      console.log('  - style:', formData.style);
      console.log('  - wardrobeSize:', wardrobe.length);
      console.log('  - baseItem:', baseItem ? {
        id: baseItem.id,
        name: baseItem.name,
        type: baseItem.type,
        color: baseItem.color
      } : 'None');
      console.log('  - weather:', weatherData);
      console.log('  - userProfile.id:', profile.id);
      console.log('  - outfitHistoryCount:', outfitHistory.length);
      
      console.log('🔍 DEBUG: Full payload:', payload);

      console.log('🔍 DEBUG: Making API call to /api/outfit/generate');
      
      const response = await authenticatedFetch("/api/outfit/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      console.log('🔍 DEBUG: API response received:');
      console.log('  - status:', response.status);
      console.log('  - ok:', response.ok);
      console.log('  - statusText:', response.statusText);

      const data = await response.json();
      console.log('🔍 DEBUG: API response data:', data);

      if (!response.ok) {
        console.error('❌ DEBUG: API call failed:', data);
        throw new Error(data.details || data.error || "Failed to generate outfit");
      }

      console.log('✅ DEBUG: API call successful!');
      console.log('🔍 DEBUG: Generated outfit details:', {
        id: data.id,
        name: data.name,
        occasion: data.occasion,
        style: data.style,
        itemsCount: data.items?.length || 0,
        items: data.items?.map((item: any) => ({
          name: item.name,
          type: item.type,
          style: item.style
        }))
      });

      console.log('🔍 DEBUG: Redirecting to outfit details page:', `/outfits/${data.id}`);
      // Redirect to the outfit details page
      router.push(`/outfits/${data.id}`);
    } catch (err) {
      console.error('❌ DEBUG: Error in handleSubmit:', err);
      console.log('🔍 DEBUG: Error details:', {
        message: err instanceof Error ? err.message : 'Unknown error',
        stack: err instanceof Error ? err.stack : undefined
      });
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      console.log('🔍 DEBUG: handleSubmit completed, setting loading to false');
      setLoading(false);
    }
  };

  if (wardrobeLoading || profileLoading) {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">Loading...</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      <WeatherDisplay />
      
      {/* Base Item Display */}
      {baseItem && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 relative rounded-lg overflow-hidden bg-gray-200">
                  {baseItem.imageUrl && (
                    <Image
                      src={baseItem.imageUrl}
                      alt={baseItem.name}
                      fill
                      className="object-cover"
                    />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-blue-900">Starting with: {baseItem.name}</h3>
                  <p className="text-sm text-blue-700">This item will be included in your generated outfit</p>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={clearBaseItem}
                className="text-blue-700 border-blue-300 hover:bg-blue-100"
              >
                <X className="w-4 h-4 mr-2" />
                Remove
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      
      <Card>
        <CardHeader>
          <CardTitle>Generate Outfit</CardTitle>
          <CardDescription>
            {baseItem 
              ? `Create a new outfit starting with your ${baseItem.name}`
              : "Create a new outfit based on your preferences and wardrobe"
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="occasion">Occasion</Label>
                <Select
                  value={formData.occasion}
                  onValueChange={(value) =>
                    setFormData((prev) => ({ ...prev, occasion: value }))
                  }
                >
                  <SelectTrigger id="occasion">
                    <SelectValue placeholder="Select occasion" />
                  </SelectTrigger>
                  <SelectContent>
                    {OCCASIONS.map((occasion) => (
                      <SelectItem key={occasion} value={occasion}>
                        {occasion.charAt(0).toUpperCase() + occasion.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="mood">Mood</Label>
                <Select
                  value={formData.mood}
                  onValueChange={(value) =>
                    setFormData((prev) => ({ ...prev, mood: value }))
                  }
                >
                  <SelectTrigger id="mood">
                    <SelectValue placeholder="Select mood" />
                  </SelectTrigger>
                  <SelectContent>
                    {MOODS.map((mood) => (
                      <SelectItem key={mood} value={mood}>
                        {mood.charAt(0).toUpperCase() + mood.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="style">Style</Label>
                <Select
                  value={formData.style}
                  onValueChange={(value) =>
                    setFormData((prev) => ({ ...prev, style: value }))
                  }
                >
                  <SelectTrigger id="style">
                    <SelectValue placeholder="Select style" />
                  </SelectTrigger>
                  <SelectContent>
                    {STYLES.map((style) => (
                      <SelectItem key={style} value={style}>
                        {style.charAt(0).toUpperCase() + style.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, description: e.target.value }))
                  }
                  placeholder="Add any additional details about your desired outfit..."
                />
              </div>
            </div>

            {error && (
              <div className="text-red-500 text-sm">{error}</div>
            )}

            <div className="flex justify-between">
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={randomizeFields}
                  disabled={loading}
                >
                  <Shuffle className="w-4 h-4 mr-2" />
                  Randomize
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleRefresh}
                  disabled={isRefreshing || loading}
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                  {isRefreshing ? 'Generating...' : 'Generate New'}
                </Button>
              </div>
              <Button type="submit" disabled={loading}>
                {loading ? "Generating..." : "Generate Outfit"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
} 