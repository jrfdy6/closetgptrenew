import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { WardrobeService } from '@/lib/services/wardrobeService';
import { safeToDate } from '@/lib/utils/dateUtils';

// The wardrobe API preserves nested analysis alongside flattened editing fields.
interface WardrobeSourceMetadata {
  visualAttributes?: { material?: string | string[] | null; [key: string]: unknown } | null;
  [key: string]: unknown;
}
export interface ClothingItem {
  metadata?: WardrobeSourceMetadata | null;
  analysis?: { metadata?: WardrobeSourceMetadata | null; material?: string | string[] | null; [key: string]: unknown } | null;
  id: string;
  name: string;
  type: string;
  color: string;
  imageUrl: string;
  wearCount: number;
  favorite: boolean;
  style?: string[];
  season?: string[];
  occasion?: string[];
  lastWorn?: Date;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
  // Additional fields for comprehensive item details
  description?: string;
  brand?: string;
  size?: string;
  material?: string[];
  sleeveLength?: string;
  fit?: string;
  neckline?: string;
  length?: string;
  purchaseDate?: Date;
  purchasePrice?: number;
  // Phase 1 new fields - gender-inclusive outfit generation
  transparency?: string;
  collarType?: string;
  embellishments?: string;
  printSpecificity?: string;
  rise?: string;
  legOpening?: string;
  heelHeight?: string;
  statementLevel?: number;
}

export interface WardrobeFilters {
  type?: string;
  color?: string;
  season?: string;
  style?: string;
  occasion?: string;
  search?: string;
}

export function useWardrobe() {
  const { user } = useFirebase();
  const uid = user?.uid ?? null;
  const account = useRef({ uid, revision: 0 });
  if (account.current.uid !== uid) {
    account.current = { uid, revision: account.current.revision + 1 };
  }
  const revision = account.current.revision;
  const mounted = useRef(true);
  const requestSequence = useRef(0);
  const [stateOwner, setStateOwner] = useState(revision);
  const [storedItems, setItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<WardrobeFilters>({});
  // Hide the previous account synchronously, before reset effects can run.
  const ownsState = uid !== null && stateOwner === revision;
  const items = useMemo(() => ownsState ? storedItems : [], [ownsState, storedItems]);
  const current = useCallback((ownerRevision: number, owner: string | null) =>
    mounted.current && owner !== null && account.current.uid === owner &&
    account.current.revision === ownerRevision, []);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; requestSequence.current += 1; };
  }, []);

  // A confirmed mutation supersedes reads started before its acknowledgement.
  const acknowledgeMutation = useCallback(() => {
    requestSequence.current += 1;
    setLoading(false);
  }, []);

  const fetchItems = useCallback(async () => {
    if (!current(revision, uid)) return;
    const sequence = ++requestSequence.current;
    const active = () => current(revision, uid) && sequence === requestSequence.current;
    setLoading(true);
    setError(null);
    try {
      const wardrobeItems = await WardrobeService.getWardrobeItems();
      if (active()) setItems(wardrobeItems);
    } catch (err) {
      if (active()) setError(err instanceof Error ? err.message : 'Failed to fetch wardrobe items');
    } finally {
      if (active()) setLoading(false);
    }
  }, [uid, revision, current]);

  const addItem = useCallback(async (item: Omit<ClothingItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => {
    if (!current(revision, uid)) return;
    try {
      const newItem = await WardrobeService.addWardrobeItem(item);
      if (!current(revision, uid)) return;
      acknowledgeMutation();
      setItems(prev => [...prev, newItem]);
      return newItem;
    } catch (err) {
      if (!current(revision, uid)) return;
      setError(err instanceof Error ? err.message : 'Failed to add item');
      throw err;
    }
  }, [uid, revision, current, acknowledgeMutation]);

  const updateItem = useCallback(async (id: string, updates: Partial<ClothingItem>) => {
    if (!current(revision, uid)) return;
    try {
      await WardrobeService.updateWardrobeItem(id, updates);
      if (!current(revision, uid)) return;
      acknowledgeMutation();
      setItems(prev => prev.map(item => item.id === id
        ? { ...item, ...updates, updatedAt: new Date() } : item));
    } catch (err) {
      if (!current(revision, uid)) return;
      setError(err instanceof Error ? err.message : 'Failed to update item');
      throw err;
    }
  }, [uid, revision, current, acknowledgeMutation]);

  const deleteItem = useCallback(async (id: string) => {
    if (!current(revision, uid)) return;
    try {
      await WardrobeService.deleteWardrobeItem(id);
      if (!current(revision, uid)) return;
      acknowledgeMutation();
      setItems(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      if (!current(revision, uid)) return;
      setError(err instanceof Error ? err.message : 'Failed to delete item');
      throw err;
    }
  }, [uid, revision, current, acknowledgeMutation]);

  const toggleFavorite = useCallback(async (id: string) => {
    if (!current(revision, uid)) return;
    const item = items.find(candidate => candidate.id === id);
    if (!item) return;
    const favorite = !item.favorite;
    try {
      // Keep the request outside React's replayable state updater.
      await WardrobeService.toggleFavorite(id, favorite);
      if (!current(revision, uid)) return;
      acknowledgeMutation();
      setItems(prev => prev.map(candidate => candidate.id === id
        ? { ...candidate, favorite, updatedAt: new Date() } : candidate));
    } catch (err) {
      if (!current(revision, uid)) return;
      setError(err instanceof Error ? err.message : 'Failed to toggle favorite');
      throw err;
    }
  }, [uid, revision, current, acknowledgeMutation, items]);

  const incrementWearCount = useCallback(async (id: string) => {
    if (!current(revision, uid)) return;
    try {
      const receipt = await WardrobeService.incrementWearCount(id);
      if (!current(revision, uid)) return;
      acknowledgeMutation();
      setItems(prev => prev.map(item => item.id === id ? {
        ...item,
        wearCount: receipt.newWearCount,
        lastWorn: new Date(receipt.lastWorn < 1e11 ? receipt.lastWorn * 1000 : receipt.lastWorn),
        updatedAt: new Date()
      } : item));
    } catch (err) {
      if (!current(revision, uid)) return;
      setError(err instanceof Error ? err.message : 'Failed to update wear count');
      throw err;
    }
  }, [uid, revision, current, acknowledgeMutation]);

  // Get filtered items
  const getFilteredItems = useCallback(() => {
    let filtered = [...items];

    if (filters.type && filters.type !== 'all') {
      filtered = filtered.filter(item => item.type === filters.type);
    }

    if (filters.color && filters.color !== 'all') {
      filtered = filtered.filter(item => item.color === filters.color);
    }

    if (filters.season && filters.season !== 'all') {
      filtered = filtered.filter(item =>
        item.season?.includes(filters.season!)
      );
    }

    if (filters.style && filters.style !== 'all') {
      filtered = filtered.filter(item =>
        item.style?.includes(filters.style!)
      );
    }

    if (filters.occasion && filters.occasion !== 'all') {
      filtered = filtered.filter(item =>
        item.occasion?.includes(filters.occasion!)
      );
    }

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(item =>
        item.name.toLowerCase().includes(searchLower) ||
        item.type.toLowerCase().includes(searchLower) ||
        item.color.toLowerCase().includes(searchLower)
      );
    }

    return filtered;
  }, [items, filters]);

  // Get unique values for filters
  const getUniqueValues = useCallback((key: keyof ClothingItem) => {
    const values = new Set<string>();
    items.forEach(item => {
      const value = item[key];
      if (Array.isArray(value)) {
        value.forEach(v => values.add(v));
      } else if (typeof value === 'string') {
        values.add(value);
      }
    });
    return Array.from(values).sort();
  }, [items]);

  // Get favorites
  const getFavorites = useCallback(() => {
    return items.filter(item => item.favorite);
  }, [items]);

  // Get recently worn
  const getRecentlyWorn = useCallback(() => {
    return items
      .filter(item => item.lastWorn)
      .sort((a, b) => {
        const dateA = safeToDate(a.lastWorn);
        const dateB = safeToDate(b.lastWorn);
        if (!dateA || !dateB) return 0;
        return dateB.getTime() - dateA.getTime();
      });
  }, [items]);

  // Get unworn items
  const getUnwornItems = useCallback(() => {
    return items.filter(item => item.wearCount === 0);
  }, [items]);

  // Apply filters
  const applyFilters = useCallback((newFilters: WardrobeFilters) => {
    setFilters(newFilters);
  }, []);

  // Clear filters
  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  // Reset account-owned state before starting this account's initial read.
  useEffect(() => {
    setStateOwner(revision);
    setItems([]);
    setError(null);
    setFilters({});
    setLoading(uid !== null);
    void fetchItems();
  }, [uid, revision, fetchItems]);

  return {
    items,
    loading: uid !== null && (!ownsState || loading),
    error: ownsState ? error : null,
    filters: ownsState ? filters : {},
    addItem,
    updateItem,
    deleteItem,
    toggleFavorite,
    incrementWearCount,
    getFilteredItems,
    getUniqueValues,
    getFavorites,
    getRecentlyWorn,
    getUnwornItems,
    applyFilters,
    clearFilters,
    refetch: fetchItems
  };
}
