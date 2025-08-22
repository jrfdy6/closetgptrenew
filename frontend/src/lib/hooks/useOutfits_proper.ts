import { useState, useEffect, useCallback } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import OutfitService, { 
  Outfit, 
  OutfitFilters, 
  OutfitCreate, 
  OutfitUpdate, 
  OutfitStats 
} from '@/lib/services/outfitService_proper';

// ===== HOOK RETURN INTERFACE =====
interface UseOutfitsReturn {
  // ===== STATE =====
  outfits: Outfit[];
  outfit: Outfit | null;
  stats: OutfitStats | null;
  loading: boolean;
  error: string | null;
  
  // ===== ACTIONS =====
  fetchOutfits: (filters?: OutfitFilters) => Promise<void>;
  fetchOutfit: (id: string) => Promise<void>;
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

// ===== CUSTOM HOOK IMPLEMENTATION =====
export function useOutfits(): UseOutfitsReturn {
  // ===== STATE MANAGEMENT =====
  const { user, loading: authLoading } = useAuthContext();
  
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [outfit, setOutfit] = useState<Outfit | null>(null);
  const [stats, setStats] = useState<OutfitStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
   * Fetch user's outfits with optional filtering
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
      
      console.log('🔍 [useOutfits] Fetching outfits with filters:', filters);
      
      const fetchedOutfits = await OutfitService.getUserOutfits(user, filters);
      setOutfits(fetchedOutfits);
      
      console.log(`✅ [useOutfits] Successfully fetched ${fetchedOutfits.length} outfits`);
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  }, [user, clearError, handleError]);

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
      
      const fetchedOutfit = await OutfitService.getOutfitById(user, id);
      setOutfit(fetchedOutfit);
      
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
      
      const newOutfit = await OutfitService.createOutfit(user, data);
      
      if (newOutfit) {
        // Add to local state
        setOutfits(prev => [newOutfit, ...prev]);
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
      
      const updatedOutfit = await OutfitService.updateOutfit(user, id, updates);
      
      if (updatedOutfit) {
        // Update local state
        setOutfits(prev => prev.map(o => o.id === id ? updatedOutfit : o));
        if (outfit?.id === id) {
          setOutfit(updatedOutfit);
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
      
      await OutfitService.deleteOutfit(user, id);
      
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
      
      await OutfitService.markOutfitAsWorn(user, id);
      
      // Update local state
      setOutfits(prev => prev.map(o => {
        if (o.id === id) {
          return {
            ...o,
            wearCount: (o.wearCount || 0) + 1,
            lastWorn: new Date()
          };
        }
        return o;
      }));
      
      if (outfit?.id === id) {
        setOutfit(prev => prev ? {
          ...prev,
          wearCount: (prev.wearCount || 0) + 1,
          lastWorn: new Date()
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
      
      await OutfitService.toggleOutfitFavorite(user, id);
      
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
      
      const searchResults = await OutfitService.searchOutfits(user, query, filters);
      
      console.log(`✅ [useOutfits] Search returned ${searchResults.length} results`);
      return searchResults;
      
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
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      setLoading(true);
      clearError();
      
      console.log('📊 [useOutfits] Fetching outfit statistics');
      
      const outfitStats = await OutfitService.getOutfitStats(user);
      setStats(outfitStats);
      
      console.log('✅ [useOutfits] Successfully fetched outfit statistics');
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
    }
  }, [user, clearError, handleError]);

  /**
   * Refresh all data
   */
  const refresh = useCallback(async () => {
    console.log('🔄 [useOutfits] Refreshing all data');
    await Promise.all([
      fetchOutfits(),
      fetchStats()
    ]);
  }, [fetchOutfits, fetchStats]);

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
  }, [user, authLoading, fetchOutfits, fetchStats]);

  // ===== RETURN VALUE =====
  return {
    // State
    outfits,
    outfit,
    stats,
    loading,
    error,
    
    // Actions
    fetchOutfits,
    fetchOutfit,
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
