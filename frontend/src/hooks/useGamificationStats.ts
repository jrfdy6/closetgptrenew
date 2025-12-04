import { useState, useEffect, useCallback } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';

export interface LevelInfo {
  level: number;
  tier: string;
  current_xp: number;
  xp_for_next_level: number;
  progress_percentage: number;
}

export interface AIFitScoreComponent {
  score: number;
  max: number;
  count?: number;
  percentage?: number;
}

export interface AIFitScoreExplanation {
  total_score: number;
  components: {
    feedback: AIFitScoreComponent;
    consistency: AIFitScoreComponent;
    confidence: AIFitScoreComponent;
  };
  explanations: string[];
  next_milestone: {
    type: string;
    target: number;
    current: number;
    message: string;
  } | null;
}

export interface TVEStats {
  total_tve: number;
  total_wardrobe_cost: number;
  percent_recouped: number;
  annual_potential_range: {
    low: number;
    high: number;
  };
  tve_by_category: {
    [category: string]: {
      tve: number;
      cost: number;
      percent: number;
    };
  };
  lowest_progress_category: {
    category: string;
    percent: number;
  } | null;
}

export interface Challenge {
  challenge_id: string;
  title: string;
  description: string;
  progress: number;
  target: number;
  status: string;
  rewards: {
    xp: number;
    badge?: string;
  };
  icon?: string;
  started_at?: string;
  expires_at?: string;
}

export interface GamificationStats {
  xp: number;
  level: LevelInfo;
  ai_fit_score: AIFitScoreExplanation;
  tve: TVEStats;
  badges: string[];
  active_challenges: Challenge[];
  active_challenges_count: number;
}

export interface BadgeInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlock_condition: string;
  rarity: string;
}

export function useGamificationStats() {
  const { user } = useAuthContext();
  const [stats, setStats] = useState<GamificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const token = await user.getIdToken();
      const response = await fetch('/api/gamification/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch gamification stats: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setStats(data.data);
      } else {
        throw new Error(data.error || 'Failed to fetch stats');
      }
    } catch (err) {
      console.error('Error fetching gamification stats:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Listen for outfit rated events to refresh stats
  useEffect(() => {
    const handleOutfitRated = () => {
      console.log('🔄 Gamification stats: Outfit rated, refreshing stats...');
      fetchStats();
    };

    window.addEventListener('outfitRated', handleOutfitRated);
    
    return () => {
      window.removeEventListener('outfitRated', handleOutfitRated);
    };
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats
  };
}

export function useBadges() {
  const { user } = useAuthContext();
  const [badges, setBadges] = useState<BadgeInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBadges = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const token = await user.getIdToken();
      const response = await fetch('/api/gamification/badges', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch badges: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setBadges(data.data.badges || []);
      } else {
        throw new Error(data.error || 'Failed to fetch badges');
      }
    } catch (err) {
      console.error('Error fetching badges:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchBadges();
  }, [fetchBadges]);

  return {
    badges,
    loading,
    error,
    refetch: fetchBadges
  };
}

export function useChallenges() {
  const { user } = useAuthContext();
  const [activeChallenges, setActiveChallenges] = useState<Challenge[]>([]);
  const [availableChallenges, setAvailableChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchChallenges = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const token = await user.getIdToken();
      
      // Fetch active and available challenges in parallel
      const [activeResponse, availableResponse] = await Promise.all([
        fetch('/api/challenges/active', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }),
        fetch('/api/challenges/available', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
      ]);

      if (activeResponse.ok && availableResponse.ok) {
        const activeData = await activeResponse.json();
        const availableData = await availableResponse.json();
        
        setActiveChallenges(activeData.data?.challenges || []);
        setAvailableChallenges(availableData.data?.challenges || []);
      }
    } catch (err) {
      console.error('Error fetching challenges:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const startChallenge = useCallback(async (challengeId: string) => {
    if (!user) return;

    try {
      const token = await user.getIdToken();
      const response = await fetch(`/api/challenges/${challengeId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // Refresh challenges
        await fetchChallenges();
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error starting challenge:', err);
      return false;
    }
  }, [user, fetchChallenges]);

  useEffect(() => {
    fetchChallenges();
  }, [fetchChallenges]);

  return {
    activeChallenges,
    availableChallenges,
    loading,
    error,
    refetch: fetchChallenges,
    startChallenge
  };
}

