/**
 * Optimistic Update Hook
 * Provides optimistic UI updates for common actions
 */

import { useState, useCallback } from 'react';

interface OptimisticUpdateOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  rollbackOnError?: boolean;
}

export function useOptimisticUpdate<T>(
  initialData: T,
  updateFn: (data: T) => Promise<T>
) {
  const [data, setData] = useState<T>(initialData);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [previousData, setPreviousData] = useState<T | null>(null);

  const update = useCallback(async (
    optimisticUpdate: (current: T) => T,
    options?: OptimisticUpdateOptions<T>
  ) => {
    // Save current state for rollback
    setPreviousData(data);
    
    // Apply optimistic update immediately
    const optimisticData = optimisticUpdate(data);
    setData(optimisticData);
    setIsUpdating(true);
    setError(null);

    try {
      // Perform actual update
      const result = await updateFn(optimisticData);
      setData(result);
      options?.onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Update failed');
      setError(error);
      
      // Rollback on error if enabled
      if (options?.rollbackOnError !== false && previousData !== null) {
        setData(previousData);
      }
      
      options?.onError?.(error);
      throw error;
    } finally {
      setIsUpdating(false);
      setPreviousData(null);
    }
  }, [data, updateFn, previousData]);

  const reset = useCallback(() => {
    if (previousData !== null) {
      setData(previousData);
      setPreviousData(null);
    }
    setError(null);
    setIsUpdating(false);
  }, [previousData]);

  return {
    data,
    isUpdating,
    error,
    update,
    reset,
    setData
  };
}

/**
 * Hook for optimistic favorite toggle
 */
export function useOptimisticFavorite() {
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [updating, setUpdating] = useState<Set<string>>(new Set());

  const toggleFavorite = useCallback(async (
    itemId: string,
    currentState: boolean,
    updateFn: (itemId: string, favorite: boolean) => Promise<void>
  ) => {
    // Optimistically update UI
    const newFavorites = new Set(favorites);
    if (currentState) {
      newFavorites.delete(itemId);
    } else {
      newFavorites.add(itemId);
    }
    setFavorites(newFavorites);
    setUpdating(prev => new Set(prev).add(itemId));

    try {
      await updateFn(itemId, !currentState);
    } catch (error) {
      // Rollback on error
      setFavorites(favorites);
      throw error;
    } finally {
      setUpdating(prev => {
        const next = new Set(prev);
        next.delete(itemId);
        return next;
      });
    }
  }, [favorites]);

  return {
    favorites,
    updating,
    toggleFavorite,
    isFavorite: (itemId: string) => favorites.has(itemId),
    isUpdating: (itemId: string) => updating.has(itemId)
  };
}

/**
 * Hook for optimistic wear count update
 */
export function useOptimisticWearCount() {
  const [wearCounts, setWearCounts] = useState<Map<string, number>>(new Map());
  const [updating, setUpdating] = useState<Set<string>>(new Set());

  const incrementWearCount = useCallback(async (
    itemId: string,
    currentCount: number,
    updateFn: (itemId: string, count: number) => Promise<void>
  ) => {
    // Optimistically update UI
    const newCount = currentCount + 1;
    setWearCounts(prev => new Map(prev).set(itemId, newCount));
    setUpdating(prev => new Set(prev).add(itemId));

    try {
      await updateFn(itemId, newCount);
    } catch (error) {
      // Rollback on error
      setWearCounts(prev => {
        const next = new Map(prev);
        next.set(itemId, currentCount);
        return next;
      });
      throw error;
    } finally {
      setUpdating(prev => {
        const next = new Set(prev);
        next.delete(itemId);
        return next;
      });
    }
  }, []);

  return {
    wearCounts,
    updating,
    incrementWearCount,
    getWearCount: (itemId: string) => wearCounts.get(itemId),
    isUpdating: (itemId: string) => updating.has(itemId)
  };
}

