import { classifyGarment } from '@/lib/onboarding/state';

// Remounts and StrictMode effects share one claim. Session storage also protects
// reloads; failure to access browser storage must never produce a request loop.
const attempts = new Set<string>();

export function dailyOutfitKey(userId: string, day: string): string {
  return `daily-outfit-v2:${userId}:${day}`;
}

export function claimDailyOutfitAttempt(key: string): boolean {
  if (attempts.has(key)) return false;
  const attemptKey = `${key}:attempted`;
  try {
    if (sessionStorage.getItem(attemptKey)) {
      attempts.add(key);
      return false;
    }
    sessionStorage.setItem(attemptKey, 'true');
  } catch {
    // The in-memory claim still protects this application lifetime.
  }
  attempts.add(key);
  return true;
}

export function hasCompleteDailyOutfit(items: Array<Record<string, unknown>> | undefined): boolean {
  if (!items?.length) return false;
  const ids = items.map(item => typeof item.id === 'string' ? item.id.trim() : '');
  if (ids.some(id => !id) || new Set(ids).size !== ids.length) return false;
  const categories = new Set(items.map(classifyGarment));
  return categories.has('shoes') && (categories.has('one-piece') || (categories.has('top') && categories.has('bottom')));
}
