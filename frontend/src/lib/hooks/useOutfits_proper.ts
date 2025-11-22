import { useState, useEffect, useCallback } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import OutfitService from '@/lib/services/outfitService_proper';
import { 
  Outfit, 
  OutfitFilters, 
  OutfitCreate,
  OutfitUpdate, 
  OutfitStats 
} from '@/lib/services/outfitService';

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
  
  // ===== ACTIONS =====
  fetchOutfits: (filters?: OutfitFilters) => Promise<void>;
  fetchOutfit: (id: string) => Promise<void>;
  loadMoreOutfits: () => Promise<void>;
  addNewOutfit: (outfit: Outfit) => void;
  createOutfit: (data: OutfitCreate) => Promise<Outfit | null>;
  updateOutfit: (id: string, updates: OutfitUpdate) => Promise<Outfit | null>;
  deleteOutfit: (id: string) => Promise<boolean>;
  markAsWorn: (id: string) => Promise<boolean>;
  toggleFavorite: (id: string) => Promise<boolean>;
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
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  const [currentFilters, setCurrentFilters] = useState<OutfitFilters>({});
  const [error, setError] = useState<string | null>(null);

  // Pagination constants
  const INITIAL_PAGE_SIZE = 50; // Load 20 outfits initially
  const PAGE_SIZE = 12; // Load 12 more each time

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

  // ===== CORE ACTIONS =====
  
  /**
   * Fetch user's outfits with optional filtering (resets pagination)
   * Follows the established wardrobe service pattern
   */
  const fetchOutfits = useCallback(async (filters: OutfitFilters = {}) => {
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      setLoading(true);
      clearError();
      
      // Start fresh with initial page size
      const finalFilters = {
        limit: INITIAL_PAGE_SIZE,
        offset: 0,
        ...filters, // Allow filters to override if needed
      };
      
      setCurrentFilters(filters); // Store for loadMore
      
      console.log('🔍 [useOutfits] Fetching initial outfits with filters:', finalFilters);
      
      // Call Next.js API route instead of backend directly
      const token = await user.getIdToken();
      
      // Build query parameters
      const params = new URLSearchParams();
      if (finalFilters.limit) params.append('limit', finalFilters.limit.toString());
      if (finalFilters.offset) params.append('offset', finalFilters.offset.toString());
      if (finalFilters.occasion) params.append('occasion', finalFilters.occasion);
      if (finalFilters.style) params.append('style', finalFilters.style);
      
      const queryString = params.toString();
      const url = queryString ? `/api/outfits?${queryString}` : '/api/outfits';
      
      console.log('🔍 [useOutfits] Fetching from URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch outfits: ${response.status}`);
      }
      
      const responseData = await response.json();
      console.log('🔍 [useOutfits] Raw response data:', {
        isArray: Array.isArray(responseData),
        hasOutfits: !!(responseData.outfits),
        hasData: !!(responseData.data),
        keys: Object.keys(responseData),
        length: Array.isArray(responseData) ? responseData.length : 'N/A'
      });
      
      // Handle different response formats
      let fetchedOutfits;
      if (Array.isArray(responseData)) {
        // Backend returns array directly
        fetchedOutfits = responseData;
        console.log('🔍 [useOutfits] Using array format, length:', fetchedOutfits.length);
      } else if (responseData.outfits && Array.isArray(responseData.outfits)) {
        // Backend returns object with outfits array
        fetchedOutfits = responseData.outfits;
        console.log('🔍 [useOutfits] Using outfits format, length:', fetchedOutfits.length);
      } else if (responseData.data && Array.isArray(responseData.data)) {
        // Backend returns object with data array
        fetchedOutfits = responseData.data;
        console.log('🔍 [useOutfits] Using data format, length:', fetchedOutfits.length);
      } else {
        console.warn('🔍 [useOutfits] Unexpected response format:', responseData);
        fetchedOutfits = [];
      }
      
      const normalizedOutfits = fetchedOutfits.map(normalizeOutfitData);
      setOutfits(normalizedOutfits);
      
      // Check if there are more to load
      // If we got fewer items than requested, there are no more
      setHasMore(normalizedOutfits.length > 0 && normalizedOutfits.length === INITIAL_PAGE_SIZE);
      
      console.log(`✅ [useOutfits] Successfully fetched ${fetchedOutfits.length} initial outfits`);
      
      // Reset retry count on success
      setRetryCount(0);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ [useOutfits] Error fetching outfits:', errorMessage);
      
      // Prevent infinite retry loops
      if (retryCount < 3) {
        console.warn(`⚠️ [useOutfits] Retry ${retryCount + 1}/3 in 2 seconds...`);
        setRetryCount(prev => prev + 1);
        setTimeout(() => fetchOutfits(filters), 2000);
      } else {
        console.error('🚫 [useOutfits] Max retries reached, stopping fetch attempts');
        handleError(error as Error);
        setRetryCount(0); // Reset for next manual retry
      }
    } finally {
      setLoading(false);
    }
  }, [user, clearError, handleError, INITIAL_PAGE_SIZE, retryCount]);

  /**
   * Load more outfits (pagination)
   */
  const loadMoreOutfits = useCallback(async () => {
    if (!user || !hasMore || loadingMore) {
      return;
    }

    try {
      setLoadingMore(true);
      clearError();
      
      const finalFilters = {
        limit: PAGE_SIZE,
        offset: outfits.length, // Use current length as offset
        ...currentFilters,
      };
      
      console.log('🔍 [useOutfits] Loading more outfits with filters:', finalFilters);
      
      const token = await user.getIdToken();
      
      // Build query parameters
      const params = new URLSearchParams();
      if (finalFilters.limit) params.append('limit', finalFilters.limit.toString());
      if (finalFilters.offset) params.append('offset', finalFilters.offset.toString());
      if (finalFilters.occasion) params.append('occasion', finalFilters.occasion);
      if (finalFilters.style) params.append('style', finalFilters.style);
      
      const queryString = params.toString();
      const url = queryString ? `/api/outfits?${queryString}` : '/api/outfits';
      
      console.log('🔍 [useOutfits] Loading more from URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Failed to load more outfits: ${response.status}`);
      }
      
      const responseData = await response.json();
      
      // Handle structured response format
      const moreOutfitsRaw = responseData.outfits || responseData;
      const moreOutfits = Array.isArray(moreOutfitsRaw)
        ? moreOutfitsRaw.map(normalizeOutfitData)
        : [];
      
      // Filter out duplicates (in case backend returns same outfits) and update state
      let actualNewCount = 0;
      setOutfits(prev => {
        const existingIds = new Set(prev.map(o => o.id));
        const newOutfits = moreOutfits.filter(o => !existingIds.has(o.id));
        actualNewCount = newOutfits.length;
        return [...prev, ...newOutfits];
      });
      
      // Check if there are more to load
      // If we got fewer items than requested, or 0 items, there are no more
      setHasMore(actualNewCount > 0 && actualNewCount === PAGE_SIZE);
      
      console.log(`✅ [useOutfits] Successfully loaded ${actualNewCount} new outfits`);
      
      // If we got no new outfits, explicitly set hasMore to false
      if (actualNewCount === 0) {
        console.log('🛑 [useOutfits] No new outfits returned, setting hasMore to false');
        setHasMore(false);
      }
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoadingMore(false);
    }
  }, [user, hasMore, loadingMore, outfits.length, currentFilters, clearError, handleError, PAGE_SIZE]);

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
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      setLoading(true);
      clearError();
      
      console.log(`🔍 [useOutfits] Fetching outfit ${id}`);
      
      const token = await user.getIdToken();
      const fetchedOutfit = await OutfitService.getOutfitById(id, token);
      setOutfit(fetchedOutfit ? normalizeOutfitData(fetchedOutfit) : null);
      
      if (fetchedOutfit) {
        console.log(`✅ [useOutfits] Successfully fetched outfit ${id}`);
      } else {
        console.log(`⚠️ [useOutfits] Outfit ${id} not found`);
      }
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  }, [user, clearError, handleError]);

  /**
   * Create a new outfit
   */
  const createOutfit = useCallback(async (data: OutfitCreate): Promise<Outfit | null> => {
    if (!user) {
      setError('User not authenticated');
      return null;
    }

    try {
      setLoading(true);
      clearError();
      
      console.log('🎨 [useOutfits] Creating new outfit:', data);
      
      const token = await user.getIdToken();
      const newOutfit = await OutfitService.createOutfit(data, token);
      
      if (newOutfit) {
        const normalized = normalizeOutfitData(newOutfit);
        // Add to local state
        setOutfits(prev => [normalized, ...prev]);
        console.log(`✅ [useOutfits] Successfully created outfit ${newOutfit.id}`);
      }
      
      return newOutfit;
      
    } catch (error) {
      handleError(error as Error);
      return null;
    } finally {
      setLoading(false);
    }
  }, [user, clearError, handleError]);

  /**
   * Update an existing outfit
   */
  const updateOutfit = useCallback(async (id: string, updates: OutfitUpdate): Promise<Outfit | null> => {
    if (!user) {
      setError('User not authenticated');
      return null;
    }

    try {
      setLoading(true);
      clearError();
      
      console.log(`🔄 [useOutfits] Updating outfit ${id}:`, updates);
      
      const token = await user.getIdToken();
      const updatedOutfit = await OutfitService.updateOutfit(id, updates, token);
      
      if (updatedOutfit) {
        // Update local state
        const normalized = normalizeOutfitData(updatedOutfit);
        setOutfits(prev => prev.map(o => o.id === id ? normalized : o));
        if (outfit?.id === id) {
          setOutfit(normalized);
        }
        console.log(`✅ [useOutfits] Successfully updated outfit ${id}`);
      }
      
      return updatedOutfit;
      
    } catch (error) {
      handleError(error as Error);
      return null;
    } finally {
      setLoading(false);
    }
  }, [user, outfit, clearError, handleError]);

  /**
   * Delete an outfit
   */
  const deleteOutfit = useCallback(async (id: string): Promise<boolean> => {
    if (!user) {
      setError('User not authenticated');
      return false;
    }

    try {
      setLoading(true);
      clearError();
      
      console.log(`🗑️ [useOutfits] Deleting outfit ${id}`);
      
      const token = await user.getIdToken();
      await OutfitService.deleteOutfit(id, token);
      
      // Remove from local state
      setOutfits(prev => prev.filter(o => o.id !== id));
      if (outfit?.id === id) {
        setOutfit(null);
      }
      
      console.log(`✅ [useOutfits] Successfully deleted outfit ${id}`);
      return true;
      
    } catch (error) {
      handleError(error as Error);
      return false;
    } finally {
      setLoading(false);
    }
  }, [user, outfit, clearError, handleError]);

  /**
   * Mark an outfit as worn
   */
  const markAsWorn = useCallback(async (id: string): Promise<boolean> => {
    if (!user) {
      setError('User not authenticated');
      return false;
    }

    try {
      setLoading(true);
      clearError();
      
      console.log(`👕 [useOutfits] Marking outfit ${id} as worn`);
      
      const token = await user.getIdToken();
      await OutfitService.markOutfitAsWorn(id, token);
      
      // Update local state
      setOutfits(prev => prev.map(o => {
        if (o.id === id) {
          return {
            ...o,
            wearCount: (o.wearCount || 0) + 1,
            lastWorn: new Date().toISOString()
          };
        }
        return o;
      }));
      
      if (outfit?.id === id) {
        setOutfit(prev => prev ? {
          ...prev,
          wearCount: (prev.wearCount || 0) + 1,
          lastWorn: new Date().toISOString()
        } : null);
      }
      
      console.log(`✅ [useOutfits] Successfully marked outfit ${id} as worn`);
      return true;
      
    } catch (error) {
      handleError(error as Error);
      return false;
    } finally {
      setLoading(false);
    }
  }, [user, outfit, clearError, handleError]);

  /**
   * Toggle outfit favorite status
   */
  const toggleFavorite = useCallback(async (id: string): Promise<boolean> => {
    if (!user) {
      setError('User not authenticated');
      return false;
    }

    try {
      setLoading(true);
      clearError();
      
      console.log(`❤️ [useOutfits] Toggling favorite for outfit ${id}`);
      
      const token = await user.getIdToken();
      await OutfitService.toggleOutfitFavorite(id, token);
      
      // Update local state
      setOutfits(prev => prev.map(o => {
        if (o.id === id) {
          return { ...o, isFavorite: !o.isFavorite };
        }
        return o;
      }));
      
      if (outfit?.id === id) {
        setOutfit(prev => prev ? { ...prev, isFavorite: !prev.isFavorite } : null);
      }
      
      console.log(`✅ [useOutfits] Successfully toggled favorite for outfit ${id}`);
      return true;
      
    } catch (error) {
      handleError(error as Error);
      return false;
    } finally {
      setLoading(false);
    }
  }, [user, outfit, clearError, handleError]);

  /**
   * Search outfits with text query
   */
  const searchOutfits = useCallback(async (query: string, filters: OutfitFilters = {}): Promise<Outfit[]> => {
    if (!user) {
      setError('User not authenticated');
      return [];
    }

    try {
      setLoading(true);
      clearError();
      
      console.log(`🔍 [useOutfits] Searching outfits with query: "${query}"`);
      
      const token = await user.getIdToken();
      const searchResults = await OutfitService.searchOutfits(query, filters, token);
      
      console.log(`✅ [useOutfits] Search returned ${searchResults.length} results`);
      return searchResults.map(normalizeOutfitData);
      
    } catch (error) {
      handleError(error as Error);
      return [];
    } finally {
      setLoading(false);
    }
  }, [user, clearError, handleError]);

  /**
   * Fetch outfit statistics
   */
  const fetchStats = useCallback(async () => {
    // RE-ENABLED - stats endpoint should be working now
    if (!user) {
      setError('User not authenticated');
      return;
    }

    console.log('📊 [useOutfits] Fetching outfit stats...');

    try {
      // Don't set main loading state for stats to avoid blocking outfit display
      clearError();
      
      console.log('📊 [useOutfits] Fetching outfit statistics');
      
      // Call Next.js API route instead of backend directly
      const token = await user.getIdToken();
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
      setStats(outfitStats?.data || outfitStats);
      
      console.log('✅ [useOutfits] Successfully fetched outfit statistics');
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.warn('⚠️ [useOutfits] Stats fetch failed (non-critical):', errorMessage);
      // Don't set error state for stats failures - just log as warning
      setStats(null);
    }
  }, [user, clearError, handleError]);

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
    return outfits.find(o => o.id === id);
  }, [outfits]);

  // ===== EFFECTS =====
  
  /**
   * Auto-fetch outfits when user changes
   */
  useEffect(() => {
    if (user && !authLoading) {
      console.log('👤 [useOutfits] User authenticated, fetching outfits');
      fetchOutfits();
      fetchStats();
    }
  }, [user?.uid, authLoading]); // Use user.uid instead of user object to prevent re-renders

  // ===== RETURN VALUE =====
  return {
    // State
    outfits,
    outfit,
    stats,
    loading,
    loadingMore,
    hasMore,
    error,
    
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
