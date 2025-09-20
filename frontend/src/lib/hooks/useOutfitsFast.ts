/**
 * Fast Outfits Hook
 * 
 * Lightning-fast outfit loading using pre-aggregated stats.
 * Replaces slow pagination with instant loading and virtual scrolling.
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import fastOutfitService, { 
  OutfitMetadata, 
  OutfitSummary, 
  FilterOptions, 
  OutfitFilters,
  OutfitMetadataResponse 
} from '@/lib/services/outfitServiceFast';

interface UseOutfitsFastReturn {
  // Summary data (loads instantly)
  summary: OutfitSummary | null;
  summaryLoading: boolean;
  
  // Outfit metadata (for grid display)
  outfits: OutfitMetadata[];
  loading: boolean;
  loadingMore: boolean;
  hasMore: boolean;
  
  // Filter options
  filterOptions: FilterOptions | null;
  filtersLoading: boolean;
  
  // Current state
  currentFilters: OutfitFilters;
  searchQuery: string;
  filteredOutfits: OutfitMetadata[];
  
  // Error handling
  error: string | null;
  
  // Actions
  loadSummary: () => Promise<void>;
  loadOutfits: (filters?: OutfitFilters, reset?: boolean) => Promise<void>;
  loadMoreOutfits: () => Promise<void>;
  loadFilterOptions: () => Promise<void>;
  setFilters: (filters: OutfitFilters) => void;
  setSearchQuery: (query: string) => void;
  clearError: () => void;
  refresh: () => Promise<void>;
}

export function useOutfitsFast(): UseOutfitsFastReturn {
  // ===== STATE =====
  const { user, loading: authLoading } = useAuthContext();
  
  // Summary data
  const [summary, setSummary] = useState<OutfitSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  
  // Outfit data
  const [outfits, setOutfits] = useState<OutfitMetadata[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  
  // Filter data
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [filtersLoading, setFiltersLoading] = useState(false);
  
  // Current state
  const [currentFilters, setCurrentFilters] = useState<OutfitFilters>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [currentOffset, setCurrentOffset] = useState(0);
  
  // Error handling
  const [error, setError] = useState<string | null>(null);

  // ===== CONSTANTS =====
  const PAGE_SIZE = 50; // Load 50 outfits at a time

  // ===== ERROR HANDLING =====
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleError = useCallback((error: Error | string) => {
    const errorMessage = typeof error === 'string' ? error : error.message;
    console.error('❌ [useOutfitsFast] Error:', errorMessage);
    setError(errorMessage);
  }, []);

  // ===== COMPUTED VALUES =====
  // Apply search filter to outfits
  const filteredOutfits = fastOutfitService.searchOutfits(outfits, searchQuery);

  // ===== CORE ACTIONS =====

  /**
   * Load outfit summary (instant loading)
   */
  const loadSummary = useCallback(async () => {
    if (!user || authLoading) return;

    try {
      setSummaryLoading(true);
      clearError();
      
      const summaryData = await fastOutfitService.getOutfitSummary(user);
      setSummary(summaryData);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setSummaryLoading(false);
    }
  }, [user, authLoading, clearError, handleError]);

  /**
   * Load outfit metadata
   */
  const loadOutfits = useCallback(async (filters: OutfitFilters = {}, reset: boolean = true) => {
    if (!user || authLoading) return;

    try {
      if (reset) {
        setLoading(true);
        setOutfits([]);
        setCurrentOffset(0);
      } else {
        setLoadingMore(true);
      }
      
      clearError();
      
      const offset = reset ? 0 : currentOffset;
      const response = await fastOutfitService.getOutfitMetadata(user, filters, PAGE_SIZE, offset);
      
      if (reset) {
        setOutfits(response.outfits);
        setCurrentFilters(filters);
      } else {
        setOutfits(prev => [...prev, ...response.outfits]);
      }
      
      setCurrentOffset(offset + response.outfits.length);
      setHasMore(response.pagination.has_more);
      
    } catch (error) {
      handleError(error as Error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [user, authLoading, currentOffset, clearError, handleError]);

  /**
   * Load more outfits (pagination)
   */
  const loadMoreOutfits = useCallback(async () => {
    if (!hasMore || loadingMore || loading) return;
    
    await loadOutfits(currentFilters, false);
  }, [hasMore, loadingMore, loading, loadOutfits, currentFilters]);

  /**
   * Load filter options
   */
  const loadFilterOptions = useCallback(async () => {
    if (!user || authLoading) return;

    try {
      setFiltersLoading(true);
      clearError();
      
      const options = await fastOutfitService.getFilterOptions(user);
      setFilterOptions(options);
    } catch (error) {
      handleError(error as Error);
    } finally {
      setFiltersLoading(false);
    }
  }, [user, authLoading, clearError, handleError]);

  /**
   * Set filters and reload outfits
   */
  const setFilters = useCallback((filters: OutfitFilters) => {
    setCurrentFilters(filters);
    loadOutfits(filters, true);
  }, [loadOutfits]);

  /**
   * Refresh all data
   */
  const refresh = useCallback(async () => {
    await Promise.all([
      loadSummary(),
      loadOutfits(currentFilters, true),
      loadFilterOptions()
    ]);
  }, [loadSummary, loadOutfits, loadFilterOptions, currentFilters]);

  // ===== EFFECTS =====

  /**
   * Load initial data when user is available
   */
  useEffect(() => {
    if (user && !authLoading) {
      console.log('🚀 [useOutfitsFast] Loading initial data...');
      refresh();
    }
  }, [user, authLoading]); // Don't include refresh in deps to avoid loops

  /**
   * Load summary immediately when user is available (fastest loading)
   */
  useEffect(() => {
    if (user && !authLoading && !summary) {
      loadSummary();
    }
  }, [user, authLoading, summary, loadSummary]);

  return {
    // Summary data
    summary,
    summaryLoading,
    
    // Outfit data
    outfits,
    loading,
    loadingMore,
    hasMore,
    
    // Filter data
    filterOptions,
    filtersLoading,
    
    // Current state
    currentFilters,
    searchQuery,
    filteredOutfits,
    
    // Error handling
    error,
    
    // Actions
    loadSummary,
    loadOutfits,
    loadMoreOutfits,
    loadFilterOptions,
    setFilters,
    setSearchQuery,
    clearError,
    refresh,
  };
}

export default useOutfitsFast;
