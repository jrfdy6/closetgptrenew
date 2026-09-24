import { useEffect, useRef } from 'react';
import { WARDROBE_ACTIVITY_EVENT } from '@/lib/wardrobeActivity';

export const GAMIFICATION_ACTIVITY_EVENT = 'gamificationActivityChanged';

/** Refresh existing views after confirmed wear changes and when returning to the tab. */
export function useWardrobeActivityRefresh(uid: string | undefined, refresh: () => unknown) {
  const callback = useRef(refresh);
  callback.current = refresh;
  useEffect(() => {
    if (!uid) return;
    const changed = (event: Event) => {
      const owner = (event as CustomEvent).detail?.uid;
      if (!owner || owner === uid) void callback.current();
    };
    const returned = () => { if (document.visibilityState === 'visible') void callback.current(); };
    window.addEventListener(WARDROBE_ACTIVITY_EVENT, changed);
    window.addEventListener(GAMIFICATION_ACTIVITY_EVENT, changed);
    document.addEventListener('visibilitychange', returned);
    return () => {
      window.removeEventListener(WARDROBE_ACTIVITY_EVENT, changed);
      window.removeEventListener(GAMIFICATION_ACTIVITY_EVENT, changed);
      document.removeEventListener('visibilitychange', returned);
    };
  }, [uid]);
}
