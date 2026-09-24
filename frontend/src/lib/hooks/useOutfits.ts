import { useState, useEffect, useCallback } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import OutfitService, { Outfit, OutfitFilters } from '@/lib/services/outfitService';

// ===== HOOK INTERFACE =====
interface UseOutfitsReturn {
  // Data
  outfits: Outfit[];
  outfit: Outfit | null;
  
  // Loading states
  loading: boolean;
  loadingOutfit: boolean;
  creating: boolean;
  updating: boolean;
  deleting: boolean;
  
  // Error states
  error: string | null;
  
  // Actions
  fetchOutfits: (filters?: OutfitFilters) => Promise<void>;
  fetchOutfit: (id: string) => Promise<void>;
  createOutfit: (outfitData: Omit<Outfit, 'id' | 'createdAt' | 'updatedAt' | 'userId'>) => Promise<Outfit | null>;
  updateOutfit: (id: string, updates: Partial<Outfit>) => Promise<void>;
  deleteOutfit: (id: string) => Promise<void>;
  markAsWorn: (id: string) => Promise<void>;
  toggleFavorite: (id: string) => Promise<void>;
  searchOutfits: (filters: OutfitFilters) => Promise<Outfit[]>;
  
  // Utilities
  clearError: () => void;
  refresh: () => Promise<void>;
}

// ===== MAIN HOOK =====
export function useOutfits(): UseOutfitsReturn {
  const { user, loading: authLoading } = useAuthContext();
  
  // ===== STATE MANAGEMENT =====
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [outfit, setOutfit] = useState<Outfit | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingOutfit, setLoadingOutfit] = useState(false);
  const [creating, setCreating] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ===== ERROR HANDLING =====
  const clearError = useCallback(() => setError(null), []);
  
  const handleError = useCallback((error: unknown, operation: string) => {
    const errorMessage = error instanceof Error ? error.message : `Failed to ${operation}`;
    console.error(`❌ [useOutfits] ${operation} error:`, error);
    setError(errorMessage);
  }, []);

  // ===== CORE OPERATIONS =====
  
  const fetchOutfits = useCallback(async (filters?: OutfitFilters) => {
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
      handleError(error, 'fetch outfits');
    } finally {
      setLoading(false);
    }
  }, [user, clearError, handleError]);

  const fetchOutfit = useCallback(async (id: string) => {
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      setLoadingOutfit(true);
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
      handleError(error, 'fetch outfit');
    } finally {
      setLoadingOutfit(false);
    }
  }, [user, clearError, handleError]);

  const createOutfit = useCallback(async (outfitData: Omit<Outfit, 'id' | 'createdAt' | 'updatedAt' | 'user_id'>): Promise<Outfit | null> => {
    if (!user) {
      setError('User not authenticated');
      return null;
    }

    try {
      setCreating(true);
      clearError();
      
      console.log('🔍 [useOutfits] Creating new outfit');
      const newOutfit = await OutfitService.createOutfit(user, outfitData);
      
      // Add to local state
      setOutfits(prev => [newOutfit, ...prev]);
      setOutfit(newOutfit);
      
      console.log(`✅ [useOutfits] Successfully created outfit ${newOutfit.id}`);
      return newOutfit;
      
    } catch (error) {
      handleError(error, 'create outfit');
      return null;
    } finally {
      setCreating(false);
    }
  }, [user, clearError, handleError]);

  const updateOutfit = useCallback(async (id: string, updates: Partial<Outfit>) => {
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      setUpdating(true);
      clearError();
      
      console.log(`🔍 [useOutfits] Updating outfit ${id}`);
      await OutfitService.updateOutfit(user, id, updates);
      
      // Update local state
      setOutfits(prev => prev.map(o => 
        o.id === id ? { ...o, ...updates, updatedAt: new Date() as any } : o
      ));
      
      if (outfit?.id === id) {
        setOutfit(prev => prev ? { ...prev, ...updates, updatedAt: new Date() as any } : null);
      }
      
      console.log(`✅ [useOutfits] Successfully updated outfit ${id}`);
      
    } catch (error) {
      handleError(error, 'update outfit');
    } finally {
      setUpdating(false);
    }
  }, [user, outfit, clearError, handleError]);

  const deleteOutfit = useCallback(async (id: string) => {
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      setDeleting(true);
      clearError();
      
      console.log(`🔍 [useOutfits] Deleting outfit ${id}`);
      await OutfitService.deleteOutfit(user, id);
      
      // Remove from local state
      setOutfits(prev => prev.filter(o => o.id !== id));
      
      if (outfit?.id === id) {
        setOutfit(null);
      }
      
      console.log(`✅ [useOutfits] Successfully deleted outfit ${id}`);
      
    } catch (error) {
      handleError(error, 'delete outfit');
    } finally {
      setDeleting(false);
    }
  }, [user, outfit, clearError, handleError]);

  const markAsWorn = useCallback(async (id: string) => {
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      clearError();
      
      console.log(`👕 [useOutfits] Marking outfit ${id} as worn`);
      
      const [{ default: service }, { publishWearReceipt }] = await Promise.all([
        import('@/lib/services/outfitService_proper'), import('@/lib/wardrobeActivity'),
      ]);
      const receipt = await service.markOutfitAsWorn(id, await user.getIdToken());
      publishWearReceipt(user.uid, receipt);
      if (receipt.undone) throw new Error('This wear was undone. Choose Wear again to record a new wear.');
      setOutfits(prev => prev.map(o => o.id === id ? { ...o, wearCount: receipt.wear_count, lastWorn: receipt.last_worn } : o));
      setOutfit(prev => prev?.id === id ? { ...prev, wearCount: receipt.wear_count, lastWorn: receipt.last_worn } : prev);

    } catch (error) {
      handleError(error, 'mark outfit as worn');
    }
  }, [user, outfit, outfits, clearError, handleError]);

  const toggleFavorite = useCallback(async (id: string) => {
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      clearError();
      
      console.log(`🔍 [useOutfits] Toggling favorite for outfit ${id}`);
      await OutfitService.toggleOutfitFavorite(user, id);
      
      // Update local state
      setOutfits(prev => prev.map(o => 
        o.id === id ? { ...o, isFavorite: !o.isFavorite } : o
      ));
      
      if (outfit?.id === id) {
        setOutfit(prev => prev ? { ...prev, isFavorite: !prev.isFavorite } : null);
      }
      
      console.log(`✅ [useOutfits] Successfully toggled favorite for outfit ${id}`);
      
    } catch (error) {
      handleError(error, 'toggle outfit favorite');
    }
  }, [user, outfit, clearError, handleError]);

  const searchOutfits = useCallback(async (filters: OutfitFilters): Promise<Outfit[]> => {
    if (!user) {
      setError('User not authenticated');
      return [];
    }

    try {
      clearError();
      
      console.log('🔍 [useOutfits] Searching outfits with filters:', filters);
      const searchResults = await OutfitService.searchOutfits(user, filters);
      
      console.log(`✅ [useOutfits] Search returned ${searchResults.length} outfits`);
      return searchResults;
      
    } catch (error) {
      handleError(error, 'search outfits');
      return [];
    }
  }, [user, clearError, handleError]);

  const refresh = useCallback(async () => {
    await fetchOutfits();
  }, [fetchOutfits]);

  // ===== EFFECTS =====
  
  // Auto-fetch outfits when user is authenticated
  useEffect(() => {
    if (user && !authLoading) {
      console.log('🔍 [useOutfits] User authenticated, fetching outfits...');
      fetchOutfits();
    }
  }, [user, authLoading, fetchOutfits]);

  // ===== RETURN INTERFACE =====
  return {
    // Data
    outfits,
    outfit,
    
    // Loading states
    loading,
    loadingOutfit,
    creating,
    updating,
    deleting,
    
    // Error states
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
    
    // Utilities
    clearError,
    refresh,
  };
}

// ===== EXPORT DEFAULT =====
export default useOutfits;
