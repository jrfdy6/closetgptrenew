import type { GeneratedOutfit } from '@/components/ui/outfit-results-display';

export interface SavedOutfit extends GeneratedOutfit {
  user_id: string;
  isFavorite?: boolean;
  wearCount?: number;
  lastWorn?: unknown;
  lastWearDate?: string;
  lastWearTimezone?: string;
  rating?: number;
  isLiked?: boolean;
  isDisliked?: boolean;
  feedback?: string;
  items_available?: boolean;
}

export class SavedOutfitError extends Error {
  constructor(message: string, public status: number) { super(message); }
}

export async function savedOutfitRequest(path: string, token: string, options: RequestInit = {}) {
  const response = await fetch('/api/outfits/' + path, {
    ...options, cache: 'no-store',
    headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json', ...options.headers },
  });
  const body = await response.json().catch(() => null);
  if (!response.ok || body?.success === false) {
    throw new SavedOutfitError(typeof body?.error === 'string' ? body.error :
      response.status === 404 ? 'This saved outfit is unavailable.' : 'We could not confirm the update. Please try again.', response.status);
  }
  return body;
}

export async function readSavedOutfit(id: string, uid: string, token: string, signal?: AbortSignal): Promise<SavedOutfit> {
  const body = await savedOutfitRequest(encodeURIComponent(id), token, { signal });
  if (body?.id !== id || body?.user_id !== uid || !Array.isArray(body.items)) {
    throw new SavedOutfitError('The server could not confirm this saved outfit.', 502);
  }
  return body;
}

export function savedDate(value: unknown): Date | null {
  let date: Date;
  if (typeof value === 'number') date = new Date(value < 1e11 ? value * 1000 : value);
  else if (typeof value === 'string') date = new Date(value);
  else if (value && typeof value === 'object' && 'seconds' in value) date = new Date(Number(value.seconds) * 1000);
  else return null;
  return Number.isFinite(date.getTime()) ? date : null;
}

export function localDay(value: unknown = Date.now()): string | null {
  const date = savedDate(value);
  return date ? [date.getFullYear(), String(date.getMonth() + 1).padStart(2, '0'), String(date.getDate()).padStart(2, '0')].join('-') : null;
}

const pendingWear = new Map<string, string>();
export function wearOperationKey(uid: string, outfitId: string): string {
  const storageKey = 'easyoutfit:pending-wear:v1:' + uid + ':' + outfitId;
  let key = pendingWear.get(storageKey);
  try { key = sessionStorage.getItem(storageKey) || key; } catch { /* day dedupe remains server-owned */ }
  if (!key) {
    key = typeof crypto.randomUUID === 'function' ? crypto.randomUUID() :
      Array.from(crypto.getRandomValues(new Uint8Array(24)), value => value.toString(16).padStart(2, '0')).join('');
    pendingWear.set(storageKey, key);
    try { sessionStorage.setItem(storageKey, key); } catch { /* retain in this session */ }
  }
  return key;
}
export function clearWearOperation(uid: string, outfitId: string) {
  const storageKey = 'easyoutfit:pending-wear:v1:' + uid + ':' + outfitId;
  pendingWear.delete(storageKey);
  try { sessionStorage.removeItem(storageKey); } catch { /* no persisted browser copy */ }
}
