import { useState } from 'react';
import { Outfit, ClothingItem } from '../types';
import { ApiClient } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';

export const useAIRecommendations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getStyleAdvice = async (outfit: Outfit) => {
    try {
      setLoading(true);
      setError(null);
      const response = await ApiClient.getInstance().post<{
        advice: string;
        improvements: string[];
        score: number;
      }>(API_ENDPOINTS.AI.STYLE_ADVICE, { outfit });
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get style advice');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getOutfitRecommendations = async (occasion?: string, season?: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await ApiClient.getInstance().get<Outfit[]>(
        API_ENDPOINTS.AI.OUTFIT_RECOMMENDATIONS,
        { params: { occasion, season } }
      );
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get outfit recommendations');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getColorAnalysis = async (items: ClothingItem[]) => {
    try {
      setLoading(true);
      setError(null);
      const response = await ApiClient.getInstance().post<{
        colorPalette: string[];
        complementaryColors: string[];
        recommendations: string[];
      }>(API_ENDPOINTS.AI.COLOR_ANALYSIS, { items });
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get color analysis');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getPersonalizedRecommendations = async (preferences: {
    style?: string[];
    colors?: string[];
    occasions?: string[];
    seasons?: string[];
  }) => {
    try {
      setLoading(true);
      setError(null);
      const response = await ApiClient.getInstance().post<{
        outfits: Outfit[];
        suggestions: string[];
        trends: string[];
      }>(API_ENDPOINTS.AI.OUTFIT_RECOMMENDATIONS, preferences);
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get personalized recommendations');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    getStyleAdvice,
    getOutfitRecommendations,
    getColorAnalysis,
    getPersonalizedRecommendations,
  };
}; 