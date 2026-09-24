import { GAMIFICATION_ACTIVITY_EVENT, useWardrobeActivityRefresh } from '@/hooks/useWardrobeActivityRefresh';
import { useState, useEffect, useCallback, useRef } from 'react';
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
  progress: number | {
    total_outfits?: number;
    weeks_completed?: number;
    current_week_outfits?: number;
    current_week_start?: string;
  };
  target: number;
  status: string;
  rewards: {
    xp: number;
    badge?: string;
    tokens?: number;
  };
  icon?: string;
  started_at?: string;
  expires_at?: string;
  featured?: boolean;
  instance_id?: string;
  completed_at?: string;
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
  const owner = useRef(user?.uid);
  const sequence = useRef(0);
  if (owner.current !== user?.uid) { owner.current = user?.uid; sequence.current++; }
  const [stats, setStats] = useState<GamificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    const requestId = ++sequence.current;
    const current = () => owner.current === user?.uid && sequence.current === requestId;
    if (!user) {
      setStats(null);
      setError(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const token = await user.getIdToken();
      if (!current()) return;
      const isMobile = typeof navigator !== 'undefined' && /Mobile|Android|iPhone|iPad/i.test(navigator.userAgent);
      const timeout = isMobile ? 60000 : 30000; // 60s on mobile (matching wardrobe), 30s on desktop
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.warn(`⏱️ DEBUG: Gamification stats request timing out after ${timeout/1000}s...`);
        controller.abort();
      }, timeout);
      
      try {
        const response = await fetch('/api/gamification/stats', {
          cache: 'no-store',
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
      if (!current()) return;
      
        if (data.success) {
          const value = data.data;
          if (!value || !Number.isFinite(value.xp) || value.xp < 0 ||
              !Number.isInteger(value.level?.level) || value.level.level < 1 ||
              !Number.isFinite(value.level?.xp_for_next_level) || !Number.isFinite(value.level?.progress_percentage) ||
              !Array.isArray(value.badges) || !Number.isInteger(value.active_challenges_count) || value.active_challenges_count < 0) {
            throw new Error('Your progress could not be loaded. Please try again.');
          }
          setStats(value);
        } else {
          throw new Error(data.error || 'Failed to fetch stats');
        }
      } catch (fetchError) {
        clearTimeout(timeoutId);
        throw fetchError;
      }
    } catch (err) {
      if (!current()) return;
      if (err instanceof Error && err.name === 'AbortError') {
        const isMobile = typeof navigator !== 'undefined' && /Mobile|Android|iPhone|iPad/i.test(navigator.userAgent);
        const timeoutSeconds = isMobile ? 60 : 30;
        console.error(`⏱️ DEBUG: Gamification stats timed out after ${timeoutSeconds}s (non-critical, continuing...)`);
        setError('Your progress could not be refreshed. Please try again.');
      } else {
        console.error('Error fetching gamification stats:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      }
    } finally {
      if (current()) setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    setStats(null);
    fetchStats();
  }, [fetchStats]);

  // Badge evaluation may commit an unlock during its read; avoid listening to
  // both legacy rating and canonical activity events for the same action.
  useEffect(() => {
    const handleBadgesUpdated = (event: Event) => {
      if ((event as CustomEvent).detail?.uid === user?.uid) void fetchStats();
    };
    window.addEventListener('badgesUpdated', handleBadgesUpdated);
    return () => window.removeEventListener('badgesUpdated', handleBadgesUpdated);
  }, [fetchStats, user?.uid]);

  useWardrobeActivityRefresh(user?.uid, fetchStats);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats
  };
}

export function useBadges() {
  const { user } = useAuthContext();
  const owner = useRef(user?.uid);
  const sequence = useRef(0);
  if (owner.current !== user?.uid) { owner.current = user?.uid; sequence.current++; }
  const [badges, setBadges] = useState<BadgeInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBadges = useCallback(async () => {
    const requestId = ++sequence.current;
    const current = () => owner.current === user?.uid && sequence.current === requestId;
    if (!user) {
      setBadges([]);
      setError(null);
      setLoading(false);
      return;
    }

    let timeoutId: ReturnType<typeof setTimeout> | undefined;
    try {
      setLoading(true);
      setError(null);
      
      const token = await user.getIdToken();
      if (!current()) return;
      const controller = new AbortController();
      timeoutId = setTimeout(() => controller.abort(), 30000);
      const response = await fetch('/api/gamification/badges', {
        signal: controller.signal,
        cache: 'no-store',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch badges: ${response.status}`);
      }

      const data = await response.json();
      if (!current()) return;
      
      if (data.success) {
        if (!Array.isArray(data.data?.badges)) throw new Error('Your badges could not be loaded.');
        setBadges(data.data.badges);
        // Badge evaluation can commit rewards during this read. Refresh summary readers,
        // without recursively re-reading the badge endpoint.
        if (data.data.newly_unlocked?.length) window.dispatchEvent(new CustomEvent('badgesUpdated', { detail: { uid: user.uid } }));
      } else {
        throw new Error(data.error || 'Failed to fetch badges');
      }
    } catch (err) {
      if (!current()) return;
      console.error('Error fetching badges:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      clearTimeout(timeoutId);
      if (current()) setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    setBadges([]);
    fetchBadges();
  }, [fetchBadges]);

  useWardrobeActivityRefresh(user?.uid, fetchBadges);

  return {
    badges,
    loading,
    error,
    refetch: fetchBadges
  };
}

export function useChallenges() {
  const { user } = useAuthContext();
  const owner = useRef(user?.uid);
  const sequence = useRef(0);
  if (owner.current !== user?.uid) { owner.current = user?.uid; sequence.current++; }
  const [activeChallenges, setActiveChallenges] = useState<Challenge[]>([]);
  const [availableChallenges, setAvailableChallenges] = useState<Challenge[]>([]);
  const [completedChallenges, setCompletedChallenges] = useState<Challenge[]>([]);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchChallenges = useCallback(async () => {
    const requestId = ++sequence.current;
    const current = () => owner.current === user?.uid && sequence.current === requestId;
    if (!user) {
      setActiveChallenges([]);
      setAvailableChallenges([]);
      setCompletedChallenges([]);
      setError(null);
      setHistoryError(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setHistoryError(null);
      const token = await user.getIdToken();
      if (!current()) return;
      const timeout = /Mobile|Android|iPhone|iPad/i.test(navigator.userAgent) ? 60000 : 30000;
      const readChallenges = async (path: string): Promise<Challenge[]> => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        try {
          const response = await fetch(`/api/challenges/${path}`, {
            cache: 'no-store',
            headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
            signal: controller.signal,
          });
          if (!response.ok) throw new Error('Your challenges could not be loaded. Please try again.');
          const data = await response.json();
          if (data.success === false || !Array.isArray(data.data?.challenges)) {
            throw new Error('Your challenges could not be loaded. Please try again.');
          }
          return data.data.challenges;
        } finally { clearTimeout(timeoutId); }
      };
      const [active, available, history] = await Promise.allSettled([
        readChallenges('active'), readChallenges('available'), readChallenges('history'),
      ]);
      if (!current()) return;
      if (active.status === 'fulfilled' && available.status === 'fulfilled') {
        setActiveChallenges(active.value);
        setAvailableChallenges(available.value);
      } else {
        setError('Your challenges could not be loaded. Please try again.');
      }
      if (history.status === 'fulfilled') {
        setCompletedChallenges(history.value.filter(challenge => challenge.status === 'completed'));
      } else {
        setHistoryError('Your completed challenges could not be loaded. Please try again.');
      }
    } catch (err) {
      if (!current()) return;
      setError('Your challenges could not be loaded. Please try again.');
      setHistoryError('Your completed challenges could not be loaded. Please try again.');
    } finally {
      if (current()) setLoading(false);
    }
  }, [user]);

  const startChallenge = useCallback(async (challengeId: string) => {
    if (!user) return;

    let timeoutId: ReturnType<typeof setTimeout> | undefined;
    try {
      const token = await user.getIdToken();
      if (owner.current !== user.uid) return false;
      const controller = new AbortController();
      timeoutId = setTimeout(() => controller.abort(), 30000);
      const response = await fetch(`/api/challenges/${encodeURIComponent(challengeId)}/start`, {
        method: 'POST',
        signal: controller.signal,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const result = await response.json();
      if (response.ok && result.success === true) {
        if (owner.current !== user.uid) return false;
        // Refresh both the challenge list and the summary from committed state.
        window.dispatchEvent(new CustomEvent(GAMIFICATION_ACTIVITY_EVENT, { detail: { uid: user.uid } }));
        return true;
      }
      return false;
    } catch (err) {
      console.error('Error starting challenge:', err);
      return false;
    } finally {
      clearTimeout(timeoutId);
    }
  }, [user, fetchChallenges]);

  useEffect(() => {
    setActiveChallenges([]);
    setAvailableChallenges([]);
    setCompletedChallenges([]);
    fetchChallenges();
  }, [fetchChallenges]);

  useWardrobeActivityRefresh(user?.uid, fetchChallenges);

  return {
    activeChallenges,
    availableChallenges,
    completedChallenges,
    historyError,
    loading,
    error,
    refetch: fetchChallenges,
    startChallenge
  };
}
