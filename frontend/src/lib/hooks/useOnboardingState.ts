'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import type { OnboardingState } from '@/lib/onboarding/types';

type AccountProgress = {
  uid: string | null;
  state: OnboardingState | null;
  loading: boolean;
  error: string | null;
};

/** Shared stage hydration; a failed fetch is never an empty wardrobe. */
export function useOnboardingState() {
  const { user, loading: authLoading } = useAuthContext();
  const [progress, setProgress] = useState<AccountProgress>({ uid: user?.uid ?? null, state: null, loading: true, error: null });
  const currentUser = useRef(user);
  currentUser.current = user;
  const generation = useRef(0);

  const refresh = useCallback(async () => {
    const activeUser = currentUser.current;
    const requestGeneration = ++generation.current;
    if (!activeUser) {
      setProgress({ uid: null, state: null, loading: false, error: null });
      return null;
    }
    setProgress(previous => ({ uid: activeUser.uid, state: previous.uid === activeUser.uid ? previous.state : null, loading: true, error: null }));
    try {
      const token = await activeUser.getIdToken();
      const response = await fetch('/api/onboarding', { method: 'POST', headers: { Authorization: `Bearer ${token}` }, cache: 'no-store' });
      const result = await response.json();
      if (!response.ok || !result.success || !result.state) throw new Error('Your saved progress could not be loaded. Please retry.');
      if (requestGeneration !== generation.current || currentUser.current?.uid !== activeUser.uid) return null;
      setProgress({ uid: activeUser.uid, state: result.state, loading: false, error: null });
      return result.state as OnboardingState;
    } catch {
      if (requestGeneration === generation.current && currentUser.current?.uid === activeUser.uid) {
        setProgress(previous => ({ uid: activeUser.uid, state: previous.uid === activeUser.uid ? previous.state : null,
          loading: false, error: 'Your saved progress could not be loaded. Please retry.' }));
      }
      return null;
    } finally {
      if (requestGeneration === generation.current) setProgress(previous => ({ ...previous, loading: false }));
    }
  }, []);

  useEffect(() => {
    generation.current += 1;
    setProgress({ uid: currentUser.current?.uid ?? null, state: null, loading: true, error: null });
    if (!authLoading) void refresh();
    return () => { generation.current += 1; };
  }, [user?.uid, authLoading, refresh]);

  // Effects run after render. Mask the previous account synchronously, including
  // its failure/loading state, before any consuming page can use its readiness.
  const belongsToCurrentAccount = !authLoading && progress.uid === (user?.uid ?? null);
  return {
    state: belongsToCurrentAccount ? progress.state : null,
    loading: belongsToCurrentAccount ? progress.loading : true,
    error: belongsToCurrentAccount ? progress.error : null,
    refresh,
  };
}
