import { useState } from 'react';
import { OutfitGeneratedOutfit, ClothingItem, UserProfile } from '@shared/types';
import { WeatherData } from '@/types/weather';
import { authenticatedFetch } from '@/lib/utils/auth';

interface GenerateOutfitParams {
  wardrobe: ClothingItem[];
  weather: WeatherData;
  occasion: string;
  userProfile: UserProfile;
  style?: string;
  mood?: string;
  baseItem?: ClothingItem;
}

export function useOutfitGenerator() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateOutfit = async (params: GenerateOutfitParams): Promise<OutfitGeneratedOutfit> => {
    setLoading(true);
    setError(null);

    try {
      // NEW: Retrieve recent outfit history for diversity with proper authentication
      let outfitHistory = [];
      try {
        console.log('🔍 DEBUG: Fetching outfit history with authentication...');
        const historyResponse = await authenticatedFetch('/api/outfits');
        console.log('🔍 DEBUG: Outfit history response status:', historyResponse.status);
        
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
        } else {
          console.warn('🔍 DEBUG: Failed to get outfit history, status:', historyResponse.status);
          const errorText = await historyResponse.text();
          console.warn('🔍 DEBUG: Outfit history error:', errorText);
        }
      } catch (error) {
        console.warn('Failed to retrieve outfit history for diversity:', error);
        // Continue without history if retrieval fails
      }

      const payload = {
        occasion: params.occasion,
        weather: params.weather,
        wardrobe: params.wardrobe,
        user_profile: {
          id: params.userProfile.id,
          name: params.userProfile.name,
          email: params.userProfile.email,
          gender: params.userProfile.gender,
          bodyType: params.userProfile.bodyType || 'athletic',
          skinTone: params.userProfile.skinTone || 'medium',
          height: params.userProfile.measurements?.height || 175,
          weight: params.userProfile.measurements?.weight || 70,
          preferences: {
            style: params.userProfile.preferences?.style || ['classic'],
            colors: params.userProfile.preferences?.colors || ['blue', 'white', 'black'],
            occasions: params.userProfile.preferences?.occasions || ['casual']
          },
          stylePreferences: params.userProfile.stylePreferences || [],
          fitPreference: params.userProfile.fitPreference || 'fitted',
          
          // Enhanced measurements
          measurements: {
            ...params.userProfile.measurements,
            heightFeetInches: params.userProfile.heightFeetInches || '',
            topSize: params.userProfile.topSize || '',
            bottomSize: params.userProfile.bottomSize || '',
            shoeSize: params.userProfile.shoeSize || '',
            dressSize: params.userProfile.dressSize || '',
            jeanWaist: params.userProfile.jeanWaist || '',
            braSize: params.userProfile.braSize || '',
            inseam: params.userProfile.inseam || '',
            waist: params.userProfile.waist || '',
            chest: params.userProfile.chest || '',
            shoulderWidth: params.userProfile.shoulderWidth || 0,
            waistWidth: params.userProfile.waistWidth || 0,
            hipWidth: params.userProfile.hipWidth || 0,
            armLength: params.userProfile.armLength || 0,
            neckCircumference: params.userProfile.neckCircumference || 0,
            thighCircumference: params.userProfile.thighCircumference || 0,
            calfCircumference: params.userProfile.calfCircumference || 0
          },
          
          // Size preferences
          sizePreference: params.userProfile.sizePreference,
          
          // Color palette
          colorPalette: params.userProfile.colorPalette || {
            primary: [],
            secondary: [],
            accent: [],
            neutral: [],
            avoid: []
          },
          
          // Style personality scores
          stylePersonality: params.userProfile.stylePersonality || {
            classic: 0.5,
            modern: 0.5,
            creative: 0.5,
            minimal: 0.5,
            bold: 0.5
          },
          
          // Material preferences
          materialPreferences: params.userProfile.materialPreferences || {
            preferred: [],
            avoid: [],
            seasonal: {
              spring: [],
              summer: [],
              fall: [],
              winter: []
            }
          },
          
          // Fit preferences
          fitPreferences: params.userProfile.fitPreferences || {
            tops: 'regular',
            bottoms: 'regular',
            dresses: 'regular'
          },
          
          // Comfort levels
          comfortLevel: params.userProfile.comfortLevel || {
            tight: 0.5,
            loose: 0.5,
            structured: 0.5,
            relaxed: 0.5
          },
          
          // Brand preferences
          preferredBrands: params.userProfile.preferredBrands || [],
          
          // Budget preference
          budget: params.userProfile.budget,
          
          createdAt: params.userProfile.createdAt,
          updatedAt: params.userProfile.updatedAt
        },
        likedOutfits: [],
        trendingStyles: [],
        outfitHistory: outfitHistory,  // NEW: Add outfit history for diversity
        style: params.style,
        mood: params.mood,
        baseItem: params.baseItem
      };

      const response = await authenticatedFetch("/api/outfit/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        console.error('Outfit Generation Error:', data);
        throw new Error(data.details || data.error || "Failed to generate outfit");
      }

      return data;
    } catch (error) {
      console.error('Outfit Generation Error:', error);
      const errorMessage = error instanceof Error ? error.message : "Failed to generate outfit";
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    generateOutfit,
    loading,
    error,
  };
} 