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
      // Call backend directly to avoid Vercel API route timeout (10s limit)
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
      const isMobile = typeof navigator !== 'undefined' && /Mobile|Android|iPhone|iPad/i.test(navigator.userAgent);
      const timeout = isMobile ? 60000 : 30000; // 60s on mobile (matching wardrobe), 30s on desktop
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.warn(`⏱️ DEBUG: Gamification stats request timing out after ${timeout/1000}s...`);
        controller.abort();
      }, timeout);
      
      try {
        const response = await fetch(`${backendUrl}/api/gamification/stats`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Failed to fetch gamification stats: ${response.status}`);
      }

      const data = await response.json();
      
        if (data.success) {
          setStats(data.data);
        } else {
          throw new Error(data.error || 'Failed to fetch stats');
        }
      } catch (fetchError) {
        clearTimeout(timeoutId);
        throw fetchError;
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        const isMobile = typeof navigator !== 'undefined' && /Mobile|Android|iPhone|iPad/i.test(navigator.userAgent);
        const timeoutSeconds = isMobile ? 60 : 30;
        console.error(`⏱️ DEBUG: Gamification stats timed out after ${timeoutSeconds}s (non-critical, continuing...)`);
        // Don't set error for timeout - allow dashboard to continue without stats
        setStats(null);
      } else {
        console.error('Error fetching gamification stats:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      }
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
      
      // Call backend directly to avoid Vercel API route timeout
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
      const isMobile = typeof navigator !== 'undefined' && /Mobile|Android|iPhone|iPad/i.test(navigator.userAgent);
      const timeout = isMobile ? 60000 : 30000; // 60s on mobile (matching wardrobe), 30s on desktop
      
      // Fetch active and available challenges in parallel
      const [activeResponse, availableResponse] = await Promise.all([
        (async () => {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), timeout);
          try {
            const res = await fetch(`${backendUrl}/api/challenges/active`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              signal: controller.signal
            });
            clearTimeout(timeoutId);
            return res;
          } catch (err) {
            clearTimeout(timeoutId);
            throw err;
          }
        })(),
        (async () => {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), timeout);
          try {
            const res = await fetch(`${backendUrl}/api/challenges/available`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              signal: controller.signal
            });
            clearTimeout(timeoutId);
            return res;
          } catch (err) {
            clearTimeout(timeoutId);
            throw err;
          }
        })()
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

