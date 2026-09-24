import { useEffect, useRef } from 'react';
import { GAMIFICATION_ACTIVITY_EVENT, WARDROBE_ACTIVITY_EVENT } from '@/lib/wardrobeActivity';

export { GAMIFICATION_ACTIVITY_EVENT } from '@/lib/wardrobeActivity';

/** Refresh existing views after confirmed wear changes and when returning to the tab. */
export function useWardrobeActivityRefresh(uid: string | undefined, refresh: () => unknown) {
  const callback = useRef(refresh);
  callback.current = refresh;
  useEffect(() => {
    if (!uid) return;
    let projectionRefresh: ReturnType<typeof setTimeout> | undefined;
    const changed = (event: Event) => {
      const owner = (event as CustomEvent).detail?.uid;
      if (owner && owner !== uid) return;
      void callback.current();
      if ((event as CustomEvent).detail?.projection_status === 'pending') {
        clearTimeout(projectionRefresh);
        // One bounded read after the worker's next tick; never poll indefinitely.
        projectionRefresh = setTimeout(() => void callback.current(), 5000);
      }
    };
    const returned = () => { if (document.visibilityState === 'visible') void callback.current(); };
    window.addEventListener(WARDROBE_ACTIVITY_EVENT, changed);
    window.addEventListener(GAMIFICATION_ACTIVITY_EVENT, changed);
    document.addEventListener('visibilitychange', returned);
    return () => {
      clearTimeout(projectionRefresh);
      window.removeEventListener(WARDROBE_ACTIVITY_EVENT, changed);
      window.removeEventListener(GAMIFICATION_ACTIVITY_EVENT, changed);
      document.removeEventListener('visibilitychange', returned);
    };
  }, [uid]);
}
