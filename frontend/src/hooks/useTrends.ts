import { useState, useEffect } from "react";
import { useFirebase } from "@/lib/firebase-context";
import { collection, query, where, getDocs, addDoc } from "firebase/firestore";
import { db } from "@/lib/firebase/config";
import { fetchTrendingStyles, getTrendsWithAnalytics } from '@/lib/utils/trendManager';

export interface Trend {
  id: string;
  name: string;
  category: string;
  subCategories: string[];
  season: string;
  popularity: number;
  description: string;
  keyItems: string[];
  createdAt: Date;
  updatedAt: Date;
  gender: "Men" | "Women" | "Unisex";
  priceRange: string;
  sustainability: "High" | "Medium" | "Low";
  culturalInfluence?: string;
  colorPalette?: string[];
  fabricTypes?: string[];
  imageUrl: string;
}

export interface TrendAnalytics {
  totalItems: number;
  averagePrice: number;
  sustainabilityScore: number;
  popularityTrend: number;
}

export function useTrends() {
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useFirebase();

  useEffect(() => {
    const loadTrends = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch real trends from the backend
        const realTrends = await fetchTrendingStyles();
        
        // Convert to the expected format
        const convertedTrends: Trend[] = realTrends.map(trend => ({
          id: trend.id,
          name: trend.name,
          category: trend.category,
          subCategories: trend.subCategories,
          season: trend.season,
          popularity: Math.round(trend.popularity * 100), // Convert from 0-1 to 0-100
          description: trend.description,
          keyItems: trend.keyItems,
          createdAt: trend.createdAt,
          updatedAt: trend.updatedAt,
          gender: trend.gender,
          priceRange: trend.priceRange,
          sustainability: trend.sustainability ? "High" : "Medium",
          culturalInfluence: trend.culturalInfluence,
          colorPalette: trend.colorPalette,
          fabricTypes: trend.fabricTypes,
          imageUrl: trend.imageUrl,
        }));
        
        setTrends(convertedTrends);
      } catch (err) {
        console.error('Error loading trends:', err);
        setError(err instanceof Error ? err.message : 'Failed to load trends');
      } finally {
        setLoading(false);
      }
    };

    loadTrends();
  }, []);

  const addTrend = async (trend: Omit<Trend, 'id'>): Promise<Trend> => {
    const newTrend: Trend = {
      ...trend,
      id: Date.now().toString(),
      imageUrl: "",
    };
    setTrends(prev => [...prev, newTrend]);
    return newTrend;
  };

  const getTrendsByCategory = async (category: string): Promise<Trend[]> => {
    return trends.filter(trend => 
      trend.category.toLowerCase().includes(category.toLowerCase())
    );
  };

  const getTrendAnalytics = async (trendId: string): Promise<TrendAnalytics> => {
    try {
      const trend = trends.find(t => t.id === trendId);
      if (!trend) {
        throw new Error("Trend not found");
      }
      return {
        totalItems: trend.keyItems.length,
        averagePrice: 0,
        sustainabilityScore: trend.sustainability === "High" ? 90 : trend.sustainability === "Medium" ? 60 : 30,
        popularityTrend: trend.popularity
      };
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : "Failed to get trend analytics");
    }
  };

  const getTrendingItems = async (): Promise<Trend[]> => {
    return trends
      .sort((a, b) => b.popularity - a.popularity)
      .slice(0, 5);
  };

  return {
    trends,
    loading,
    error,
    getTrendsByCategory,
    getTrendAnalytics,
    getTrendingItems,
    addTrend
  };
} 