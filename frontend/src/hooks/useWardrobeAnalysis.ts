import { useState, useEffect } from 'react';

interface WardrobeGap {
  id: string;
  type: 'essential' | 'occasion' | 'style' | 'season' | 'validation';
  category: string;
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  suggestedItems: string[];
  priority: number;
  data?: any;
}

interface GapAnalysis {
  gaps: WardrobeGap[];
  coverage: {
    essentials: number;
    occasions: number;
    styles: number;
    seasons: number;
  };
  recommendations: string[];
  analysis_timestamp: string;
}

interface UseWardrobeAnalysisReturn {
  gapAnalysis: GapAnalysis | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useWardrobeAnalysis(): UseWardrobeAnalysisReturn {
  const [gapAnalysis, setGapAnalysis] = useState<GapAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchGapAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/wardrobe/gaps', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setGapAnalysis(result.data);
      } else {
        throw new Error(result.message || 'Failed to fetch wardrobe analysis');
      }
    } catch (err) {
      console.error('Error fetching wardrobe analysis:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch wardrobe analysis');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGapAnalysis();
  }, []);

  const refetch = async () => {
    await fetchGapAnalysis();
  };

  return {
    gapAnalysis,
    loading,
    error,
    refetch
  };
}

// Hook for just coverage metrics
export function useWardrobeCoverage() {
  const [coverage, setCoverage] = useState<{
    coverage: {
      essentials: number;
      occasions: number;
      styles: number;
      seasons: number;
    };
    total_items: number;
    high_priority_gaps: number;
    medium_priority_gaps: number;
    low_priority_gaps: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCoverage = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch('/api/wardrobe/coverage', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
          setCoverage(result.data);
        } else {
          throw new Error(result.message || 'Failed to fetch wardrobe coverage');
        }
      } catch (err) {
        console.error('Error fetching wardrobe coverage:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch wardrobe coverage');
      } finally {
        setLoading(false);
      }
    };

    fetchCoverage();
  }, []);

  return { coverage, loading, error };
}

// Hook for recommendations
export function useWardrobeRecommendations() {
  const [recommendations, setRecommendations] = useState<{
    recommendations: string[];
    suggested_items: string[];
    priority_gaps: WardrobeGap[];
    total_gaps: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch('/api/wardrobe/recommendations', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
          setRecommendations(result.data);
        } else {
          throw new Error(result.message || 'Failed to fetch wardrobe recommendations');
        }
      } catch (err) {
        console.error('Error fetching wardrobe recommendations:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch wardrobe recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  return { recommendations, loading, error };
} 