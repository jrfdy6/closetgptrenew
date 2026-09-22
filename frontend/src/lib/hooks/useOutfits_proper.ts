import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import OutfitService from '@/lib/services/outfitService_proper';
import { clearWearOperation, wearOperationKey } from '@/lib/savedOutfit';
import {
  Outfit,
  OutfitFilters,
  OutfitCreate,
  OutfitUpdate
} from '@/lib/services/outfitService';
import type { OutfitStats } from '@/lib/types/outfit';

  // ===== HOOK RETURN INTERFACE =====
interface UseOutfitsReturn {
  // ===== STATE =====
  outfits: Outfit[];
  outfit: Outfit | null;
  stats: OutfitStats | null;
  loading: boolean;
  loadingMore: boolean;
  hasMore: boolean;
  error: string | null;
  mutationErrors: Record<string, string>;
  pendingMutations: string[];

  // ===== ACTIONS =====
  fetchOutfits: (filters?: OutfitFilters) => Promise<void>;
  fetchOutfit: (id: string) => Promise<void>;
  loadMoreOutfits: () => Promise<void>;
  addNewOutfit: (outfit: Outfit) => void;
  createOutfit: (data: OutfitCreate) => Promise<Outfit | null>;
  updateOutfit: (id: string, updates: OutfitUpdate) => Promise<Outfit | null>;
  deleteOutfit: (id: string) => Promise<boolean>;
  markAsWorn: (id: string) => Promise<boolean>;
  toggleFavorite: (id: string, isFavorite?: boolean) => Promise<boolean>;
  searchOutfits: (query: string, filters?: OutfitFilters) => Promise<Outfit[]>;
  fetchStats: () => Promise<void>;

  // ===== UTILITIES =====
  clearError: () => void;
  refresh: () => Promise<void>;
  getOutfitById: (id: string) => Outfit | undefined;
}

const normalizeOutfitData = (raw: any): Outfit => {
  if (!raw) {
    return raw;
  }

  const normalizedItems = Array.isArray(raw.items)
    ? raw.items.map((item: any) => ({
        ...item,
        id: item.id ?? item.item_id ?? item._id ?? item.uuid ?? item.name ?? '',
        imageUrl: item.imageUrl ?? item.image_url ?? item.thumbnailUrl ?? item.thumbnail_url ?? null,
        originalImageUrl: item.originalImageUrl ?? item.original_image_url ?? undefined,
        thumbnailUrl: item.thumbnailUrl ?? item.thumbnail_url ?? item.imageUrl ?? item.image_url ?? null,
        backgroundRemovedUrl:
          item.backgroundRemovedUrl ??
          item.background_removed_url ??
          item.processedImageUrl ??
          item.processed_image_url ??
          undefined,
        favorite: item.favorite ?? item.isFavorite ?? item.is_favorite ?? item.favorite ?? false,
      }))
    : raw.items ?? [];

  const normalized: Outfit = {
    ...raw,
    id: raw.id ?? raw._id ?? raw.outfit_id ?? raw.uuid,
    items: normalizedItems,
    isFavorite: raw.isFavorite ?? raw.favorite ?? raw.is_favorite ?? false,
    wearCount:
      raw.wearCount ??
      raw.wear_count ??
      raw.totalWearCount ??
      raw.total_wear_count ??
      0,
    lastWorn:
      raw.lastWorn ??
      raw.last_worn ??
      raw.lastWornAt ??
      raw.last_worn_at ??
      raw.lastWornTimestamp ??
      null,
    createdAt: raw.createdAt ?? raw.created_at ?? raw.created_at ?? raw.createdAt,
    updatedAt: raw.updatedAt ?? raw.updated_at ?? raw.updated_at ?? raw.updatedAt,
  } as Outfit;

  return normalized;
};

// ===== CUSTOM HOOK IMPLEMENTATION =====
export function useOutfits(): UseOutfitsReturn {
  // ===== STATE MANAGEMENT =====
  const { user, loading: authLoading } = useAuthContext();

  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [outfit, setOutfit] = useState<Outfit | null>(null);
  const [stats, setStats] = useState<OutfitStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [currentFilters, setCurrentFilters] = useState<OutfitFilters>({});
  const [error, setError] = useState<string | null>(null);
  const [mutationErrors, setMutationErrors] = useState<Record<string, string>>({});
  const [pendingMutations, setPendingMutations] = useState<string[]>([]);
  const pendingMutationIds = useRef(new Set<string>());

  // Pagination constants
  const INITIAL_PAGE_SIZE = 50;
  const PAGE_SIZE = 12; // Load 12 more each time
  const MAX_OUTFITS = 1000; // Maximum outfits to load to prevent infinite loops

  // Account revision changes synchronously, before effects, so an old request
  // cannot reveal another account's rows or acknowledge its pending mutation.
  const account = useRef({ uid: user?.uid ?? null, authLoading, revision: 0 });
  if (account.current.uid !== (user?.uid ?? null) || account.current.authLoading !== authLoading) {
    account.current = { uid: user?.uid ?? null, authLoading, revision: account.current.revision + 1 };
  }
  const mounted = useRef(true);
  const [stateOwner, setStateOwner] = useState(user?.uid ?? null);
  const listSequence = useRef(0);
  const detailSequence = useRef(0);
  const statsSequence = useRef(0);
  const searchSequence = useRef(0);
  const loadMoreInFlight = useRef(false);
  const current = useCallback((revision: number, uid: string) => mounted.current &&
    !account.current.authLoading && account.current.uid === uid && account.current.revision === revision, []);

  // ===== ERROR HANDLING =====
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleError = useCallback((error: Error | string) => {
    const errorMessage = typeof error === 'string' ? error : error.message;
    console.error('❌ [useOutfits] Error:', errorMessage);
    setError(errorMessage);
    setLoading(false);
  }, []);

  // Mutations have local errors and pending state; they must not replace the grid.
  const beginMutation = useCallback((id: string) => {
    if (pendingMutationIds.current.has(id)) return false;
    pendingMutationIds.current.add(id);
    setPendingMutations(Array.from(pendingMutationIds.current));
    setMutationErrors(prev => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
    return true;
  }, []);

  const finishMutation = useCallback((id: string) => {
    pendingMutationIds.current.delete(id);
    setPendingMutations(Array.from(pendingMutationIds.current));
  }, []);

  const handleMutationError = useCallback((id: string, error: unknown) => {
    const message = error instanceof Error ? error.message : 'Unable to save this change. Please try again.';
    setMutationErrors(prev => ({ ...prev, [id]: message }));
  }, []);

  // ===== CORE ACTIONS =====

  /**
   * Fetch user's outfits with optional filtering (resets pagination)
   * Follows the established wardrobe service pattern
   */
  const fetchOutfits = useCallback(async (filters: OutfitFilters = {}) => {
    const revision = account.current.revision;
    if (!user || !current(revision, user.uid)) return;
    const sequence = ++listSequence.current;
    loadMoreInFlight.current = false;
    setLoadingMore(false);
    setLoading(true);
    clearError();
    const pageSize = Math.min(MAX_OUTFITS, Math.max(1, filters.limit ?? INITIAL_PAGE_SIZE));
    const active = () => current(revision, user.uid) && sequence === listSequence.current;
    try {
      setCurrentFilters(filters);
      const token = await user.getIdToken();
      if (!active()) return;
      const params = new URLSearchParams({ limit: String(pageSize), offset: String(filters.offset ?? 0) });
      if (filters.occasion) params.set('occasion', filters.occasion);
      if (filters.style) params.set('style', filters.style);
      const response = await fetch(`/api/outfits?${params}`, {
        method: 'GET', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, cache: 'no-store',
      });
      if (!response.ok) throw new Error('Your saved outfits could not be loaded. Please try again.');
      const payload = await response.json();
      const rows = Array.isArray(payload) ? payload : Array.isArray(payload.outfits) ? payload.outfits : payload.data;
      if (!Array.isArray(rows)) throw new Error('Your saved outfits could not be loaded. Please try again.');
      if (!active()) return;
      const normalized = rows.map(normalizeOutfitData);
      setOutfits(normalized);
      setHasMore(normalized.length === pageSize && normalized.length < MAX_OUTFITS);
    } catch (failure) {
      if (active()) handleError(failure as Error);
    } finally {
      if (active()) setLoading(false);
    }
  }, [user, current, clearError, handleError]);

  /** A failed next page keeps already loaded outfits and requires explicit retry. */
  const loadMoreOutfits = useCallback(async () => {
    const revision = account.current.revision;
    if (!user || !current(revision, user.uid) || !hasMore || loading || loadMoreInFlight.current) return;
    loadMoreInFlight.current = true;
    setLoadingMore(true);
    clearError();
    const sequence = listSequence.current;
    const active = () => current(revision, user.uid) && sequence === listSequence.current;
    try {
      const token = await user.getIdToken();
      if (!active()) return;
      const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(outfits.length) });
      if (currentFilters.occasion) params.set('occasion', currentFilters.occasion);
      if (currentFilters.style) params.set('style', currentFilters.style);
      const response = await fetch(`/api/outfits?${params}`, {
        method: 'GET', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }, cache: 'no-store',
      });
      if (!response.ok) throw new Error('More saved outfits could not be loaded. Please try again.');
      const payload = await response.json();
      const rows = Array.isArray(payload) ? payload : Array.isArray(payload.outfits) ? payload.outfits : payload.data;
      if (!Array.isArray(rows)) throw new Error('More saved outfits could not be loaded. Please try again.');
      if (!active()) return;
      const existing = new Set(outfits.map(row => row.id));
      const additions = rows.map(normalizeOutfitData).filter(row => !existing.has(row.id));
      const available = Math.max(0, MAX_OUTFITS - outfits.length);
      setOutfits(previous => {
        const ids = new Set(previous.map(row => row.id));
        return [...previous, ...additions.filter(row => !ids.has(row.id)).slice(0, available)];
      });
      setHasMore(rows.length === PAGE_SIZE && additions.length > 0 && outfits.length + additions.length < MAX_OUTFITS);
    } catch (failure) {
      if (active()) handleError(failure as Error);
    } finally {
      if (active()) { loadMoreInFlight.current = false; setLoadingMore(false); }
    }
  }, [user, current, hasMore, loading, outfits, currentFilters, clearError, handleError]);

  /**
   * Add a new outfit to the beginning of the list (for newly generated outfits)
   */
  const addNewOutfit = useCallback((newOutfit: Outfit) => {
    const normalized = normalizeOutfitData(newOutfit);
    setOutfits(prev => {
      // Check if outfit already exists to avoid duplicates
      const exists = prev.some(outfit => outfit.id === normalized.id);
      if (exists) {
        console.log('🔍 [useOutfits] Outfit already exists, not adding duplicate');
        return prev;
      }

      console.log('🔍 [useOutfits] Adding new outfit to the beginning of list:', normalized.name);
      return [normalized, ...prev];
    });
  }, []);

  /**
   * Fetch a specific outfit by ID
   */
  const fetchOutfit = useCallback(async (id: string) => {
    const revision = account.current.revision;
    if (user && !current(revision, user.uid)) { return; }
    if (!user) {
      setError('User not authenticated');
      return;
    }

    const sequence = ++detailSequence.current;
    const active = () => current(revision, user.uid) && sequence === detailSequence.current;
    try {
      setLoading(true);
      clearError();

      console.log(`🔍 [useOutfits] Fetching outfit ${id}`);

      const token = await user.getIdToken();
      if (!active()) { return; }
      const fetchedOutfit = await OutfitService.getOutfitById(id, token);
      if (!active()) { return; }
      setOutfit(fetchedOutfit ? normalizeOutfitData(fetchedOutfit) : null);

      if (fetchedOutfit) {
        console.log(`✅ [useOutfits] Successfully fetched outfit ${id}`);
      } else {
        console.log(`⚠️ [useOutfits] Outfit ${id} not found`);
      }

    } catch (error) {
      if (active()) handleError(error as Error);
    } finally {
      if (active()) setLoading(false);
    }
  }, [user, current, clearError, handleError]);

  /**
   * Create a new outfit
   */
  const createOutfit = useCallback(async (data: OutfitCreate): Promise<Outfit | null> => {
    const revision = account.current.revision;
    if (user && !current(revision, user.uid)) { return null; }
    if (!user) {
      handleMutationError('create', new Error('Please sign in to save changes.'));
      return null;
    }

    const active = () => current(revision, user.uid);
    if (!beginMutation('create')) return null;
    try {

      console.log('🎨 [useOutfits] Creating new outfit:', data);

      const token = await user.getIdToken();
      if (!active()) { return null; }
      const newOutfit = await OutfitService.createOutfit(data, token);
      if (!active()) { return null; }

      const normalized = normalizeOutfitData(newOutfit);
      if (!normalized?.id) throw new Error('The server did not confirm that your outfit was saved.');
      setOutfits(prev => [normalized, ...prev.filter(o => o.id !== normalized.id)]);
      return normalized;

    } catch (error) {
      if (active()) handleMutationError('create', error);
      return null;
    } finally {
      if (active()) finishMutation('create');
    }
  }, [user, current, beginMutation, finishMutation, handleMutationError]);

  /**
   * Update an existing outfit
   */
  const updateOutfit = useCallback(async (id: string, updates: OutfitUpdate): Promise<Outfit | null> => {
    const revision = account.current.revision;
    if (user && !current(revision, user.uid)) { return null; }
    if (!user) {
      handleMutationError(id, new Error('Please sign in to save changes.'));
      return null;
    }

    const active = () => current(revision, user.uid);
    if (!beginMutation(id)) return null;
    try {

      console.log(`🔄 [useOutfits] Updating outfit ${id}:`, updates);

      const token = await user.getIdToken();
      if (!active()) { return null; }
      const updatedOutfit = await OutfitService.updateOutfit(id, updates, token);
      if (!active()) { return null; }

      if (updatedOutfit) {
        // Update local state
        const normalized = normalizeOutfitData(updatedOutfit);
        setOutfits(prev => prev.map(o => o.id === id ? normalized : o));
        setOutfit(previous => previous?.id === id ? normalized : previous);
        console.log(`✅ [useOutfits] Successfully updated outfit ${id}`);
      }

      return updatedOutfit;

    } catch (error) {
      if (active()) handleMutationError(id, error);
      return null;
    } finally {
      if (active()) finishMutation(id);
    }
  }, [user, current, outfit, beginMutation, finishMutation, handleMutationError]);

  /**
   * Delete an outfit
   */
  const deleteOutfit = useCallback(async (id: string): Promise<boolean> => {
    const revision = account.current.revision;
    if (user && !current(revision, user.uid)) { return false; }
    if (!user) {
      handleMutationError(id, new Error('Please sign in to save changes.'));
      return false;
    }

    const active = () => current(revision, user.uid);
    if (!beginMutation(id)) return false;
    try {

      console.log(`🗑️ [useOutfits] Deleting outfit ${id}`);

      const token = await user.getIdToken();
      if (!active()) { return false; }
      await OutfitService.deleteOutfit(id, token);
      if (!active()) { return false; }

      // Remove from local state
      setOutfits(prev => prev.filter(o => o.id !== id));
      setOutfit(previous => previous?.id === id ? null : previous);

      console.log(`✅ [useOutfits] Successfully deleted outfit ${id}`);
      return true;

    } catch (error) {
      if (active()) handleMutationError(id, error);
      return false;
    } finally {
      if (active()) finishMutation(id);
    }
  }, [user, current, outfit, beginMutation, finishMutation, handleMutationError]);

  /**
   * Mark an outfit as worn
   */
  const markAsWorn = useCallback(async (id: string): Promise<boolean> => {
    const revision = account.current.revision;
    if (user && !current(revision, user.uid)) { return false; }
    if (!user) {
      handleMutationError(id, new Error('Please sign in to save changes.'));
      return false;
    }

    const active = () => current(revision, user.uid);
    if (!beginMutation(id)) return false;
    try {

      console.log(`👕 [useOutfits] Marking outfit ${id} as worn`);

      const token = await user.getIdToken();
      if (!active()) { return false; }
      const result = await OutfitService.markOutfitAsWorn(id, token, wearOperationKey(user.uid, id), Intl.DateTimeFormat().resolvedOptions().timeZone);
      if (result?.success !== true || !Number.isInteger(result.wear_count) || result.wear_count < 0 ||
        typeof result.last_worn !== 'number' || !Number.isFinite(result.last_worn)) {
        throw new Error('The server did not confirm the wear record. Please try again.');
      }
      if (!active()) { return false; }

      clearWearOperation(user.uid, id);

      // Show XP notification only after the current account receives confirmation.
      if (result && result.xp_earned && result.xp_earned > 0) {
        console.log('✅ XP awarded from wearing outfit (grid):', result.xp_earned, 'Dispatching xpAwarded event...');
        window.dispatchEvent(new CustomEvent('xpAwarded', {
          detail: {
            xp: result.xp_earned,
            reason: 'Outfit worn',
            level_up: result.level_up || false,
            new_level: result.new_level
          }
        }));
      }

      // Update local state
      setOutfits(prev => prev.map(o => {
        if (o.id === id) {
          return {
            ...o,
            wearCount: result.wear_count,
            lastWorn: result.last_worn
          };
        }
        return o;
      }));

      setOutfit(previous => previous?.id === id ? {
        ...previous, wearCount: result.wear_count, lastWorn: result.last_worn,
      } : previous);

      console.log(`✅ [useOutfits] Successfully marked outfit ${id} as worn`);
      return true;

    } catch (error) {
      if (active()) handleMutationError(id, error);
      return false;
    } finally {
      if (active()) finishMutation(id);
    }
  }, [user, current, outfit, beginMutation, finishMutation, handleMutationError]);

  /**
   * Toggle outfit favorite status
   */
  const toggleFavorite = useCallback(async (id: string, isFavorite?: boolean): Promise<boolean> => {
    const revision = account.current.revision;
    if (user && !current(revision, user.uid)) { return false; }
    if (!user) {
      handleMutationError(id, new Error('Please sign in to save changes.'));
      return false;
    }

    const active = () => current(revision, user.uid);
    if (!beginMutation(id)) return false;
    try {

      console.log(`❤️ [useOutfits] Toggling favorite for outfit ${id}`);

      const token = await user.getIdToken();
      if (!active()) { return false; }
      const currentOutfit = outfits.find(o => o.id === id) ?? (outfit?.id === id ? outfit : undefined);
      if (isFavorite === undefined && !currentOutfit) throw new Error('Outfit not found. Please refresh and try again.');
      const desiredState = isFavorite ?? !currentOutfit?.isFavorite;
      const result = await OutfitService.setOutfitFavorite(id, desiredState, token);
      if (!active()) { return false; }
      if (typeof result?.isFavorite !== 'boolean') throw new Error('The server did not confirm the favorite update.');

      // Update local state
      setOutfits(prev => prev.map(o => {
        if (o.id === id) {
          return { ...o, isFavorite: result.isFavorite };
        }
        return o;
      }));

      setOutfit(previous => previous?.id === id ? { ...previous, isFavorite: result.isFavorite } : previous);

      console.log(`✅ [useOutfits] Successfully toggled favorite for outfit ${id}`);
      return true;

    } catch (error) {
      if (active()) handleMutationError(id, error);
      return false;
    } finally {
      if (active()) finishMutation(id);
    }
  }, [user, current, outfits, outfit, beginMutation, finishMutation, handleMutationError]);

  /**
   * Search outfits with text query
   */
  const searchOutfits = useCallback(async (query: string, filters: OutfitFilters = {}): Promise<Outfit[]> => {
    const revision = account.current.revision;
    if (user && !current(revision, user.uid)) { return []; }
    if (!user) {
      setError('User not authenticated');
      return [];
    }

    const sequence = ++searchSequence.current;
    const active = () => current(revision, user.uid) && sequence === searchSequence.current;
    try {
      setLoading(true);
      clearError();

      console.log(`🔍 [useOutfits] Searching outfits with query: "${query}"`);

      const token = await user.getIdToken();
      if (!active()) { return []; }
      const searchResults = await OutfitService.searchOutfits(query, filters, token);
      if (!active()) { return []; }

      console.log(`✅ [useOutfits] Search returned ${searchResults.length} results`);
      return searchResults.map(normalizeOutfitData);

    } catch (error) {
      if (active()) handleError(error as Error);
      return [];
    } finally {
      if (active()) setLoading(false);
    }
  }, [user, current, clearError, handleError]);

  /**
   * Fetch outfit statistics
   */
  const fetchStats = useCallback(async () => {
    const revision = account.current.revision;
    if (user && !current(revision, user.uid)) { return; }
    // RE-ENABLED - stats endpoint should be working now
    if (!user) {
      setError('User not authenticated');
      return;
    }

    console.log('📊 [useOutfits] Fetching outfit stats...');

    const sequence = ++statsSequence.current;
    const active = () => current(revision, user.uid) && sequence === statsSequence.current;
    try {
      // Don't set main loading state for stats to avoid blocking outfit display

      console.log('📊 [useOutfits] Fetching outfit statistics');

      // Call Next.js API route instead of backend directly
      const token = await user.getIdToken();
      if (!active()) { return; }
      const response = await fetch('/api/outfit-stats/stats', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch stats: ${response.status}`);
      }

      const outfitStats = await response.json();
      if (!active()) return;
      setStats(outfitStats?.data || outfitStats);

      console.log('✅ [useOutfits] Successfully fetched outfit statistics');

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.warn('⚠️ [useOutfits] Stats fetch failed (non-critical):', errorMessage);
      // Don't set error state for stats failures - just log as warning
      if (active()) setStats(null);
    }
  }, [user, current, clearError, handleError]);

  /**
   * Refresh all data
   */
  const refresh = useCallback(async () => {
    console.log('🔄 [useOutfits] Refreshing all data');

    // Reset pagination state
    setHasMore(true);

    await Promise.all([
      fetchOutfits(currentFilters),
      fetchStats()
    ]);
  }, [fetchOutfits, fetchStats, currentFilters]);

  /**
   * Get outfit by ID from local state
   */
  const getOutfitById = useCallback((id: string): Outfit | undefined => {
    return stateOwner === account.current.uid && !account.current.authLoading ? outfits.find(o => o.id === id) : undefined;
  }, [outfits, stateOwner]);

  // ===== EFFECTS =====
  useEffect(() => {
    mounted.current = true;
    setStateOwner(user?.uid ?? null);
    setOutfits([]); setOutfit(null); setStats(null);
    setError(null); setMutationErrors({}); setPendingMutations([]);
    pendingMutationIds.current.clear();
    loadMoreInFlight.current = false;
    setLoadingMore(false); setHasMore(false); setCurrentFilters({});
    if (user && !authLoading) {
      void fetchOutfits();
      void fetchStats();
    } else setLoading(Boolean(authLoading));
    return () => { mounted.current = false; account.current.revision += 1; };
  }, [user?.uid, authLoading]);

  const visible = !authLoading && stateOwner === (user?.uid ?? null);

  // ===== RETURN VALUE =====
  return {
    // State
    outfits: visible ? outfits : [],
    outfit: visible ? outfit : null,
    stats: visible ? stats : null,
    loading: visible ? loading : true,
    loadingMore: visible ? loadingMore : false,
    hasMore: visible ? hasMore : false,
    error: visible ? error : null,
    mutationErrors: visible ? mutationErrors : {},
    pendingMutations: visible ? pendingMutations : [],

    // Actions
    fetchOutfits,
    fetchOutfit,
    loadMoreOutfits,
    addNewOutfit,
    createOutfit,
    updateOutfit,
    deleteOutfit,
    markAsWorn,
    toggleFavorite,
    searchOutfits,
    fetchStats,

    // Utilities
    clearError,
    refresh,
    getOutfitById,
  };
}

// ===== EXPORT DEFAULT =====
export default useOutfits;
