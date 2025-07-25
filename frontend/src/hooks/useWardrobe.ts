import { useState, useCallback, useEffect } from 'react';
import { ClothingItem, ClothingItemSchema, validateClothingItems } from '@/types/wardrobe';
import {
  getWardrobeItems,
  addWardrobeItem,
  updateWardrobeItem,
  deleteWardrobeItem,
  getWardrobeItemsByType,
  getWardrobeItemsBySeason,
  processAndAddImages
} from '@/lib/firebase/wardrobeService';
import { useFirebase } from '@/lib/firebase-context';
import { createClothingItemFromAnalysis } from '@/lib/utils/itemProcessing';
import { ApiResponse } from '../types/api';
import { WardrobeItem } from '@/types/wardrobe';

export function useWardrobe(): {
  wardrobe: WardrobeItem[];
  loading: boolean;
  error: string | null;
  loadItems: () => Promise<void>;
  addItem: (item: Omit<ClothingItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => Promise<ApiResponse<ClothingItem>>;
  updateItem: (itemId: string, updates: Partial<ClothingItem>) => Promise<ApiResponse<ClothingItem>>;
  removeItem: (itemId: string) => Promise<ApiResponse<void>>;
  getItemsByType: (type: string) => Promise<ClothingItem[]>;
  getItemsBySeason: (season: string) => Promise<ClothingItem[]>;
  processImages: (files: File[]) => Promise<ClothingItem[]>;
} {
  const [wardrobe, setWardrobe] = useState<WardrobeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useFirebase();

  const loadItems = useCallback(async () => {
    if (!user?.uid) {
      console.log('No user, skipping loadItems');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      console.log('Calling getWardrobeItems...');
      const result = await getWardrobeItems(user.uid);
      console.log('getWardrobeItems result:', {
        success: result.success,
        itemCount: result.data?.length,
        firstItem: result.data?.[0]
      });
      if (!result.success) {
        throw new Error(result.error || 'Failed to load items');
      }
      if (!result.data) {
        console.log('No data returned from getWardrobeItems');
        setWardrobe([]);
        return;
      }
      console.log('Setting wardrobe:', result.data);
      setWardrobe(result.data);
    } catch (err) {
      console.error('Error loading wardrobe:', err);
      setError(err instanceof Error ? err.message : 'Failed to load wardrobe');
    } finally {
      setLoading(false);
    }
  }, [user?.uid]);

  // Load wardrobe when component mounts and when user changes
  useEffect(() => {
    console.log('useWardrobe effect triggered:', {
      user: user?.uid,
      authLoading: !user,
      isAuthenticated: !!user?.uid
    });
    if (!user) {
      console.log('No user, clearing wardrobe');
      setWardrobe([]);
      return;
    }
    if (!user.uid) {
      console.log('Auth is still loading, waiting...');
      return;
    }
    console.log('Loading wardrobe for user:', user.uid);
    loadItems();
  }, [user?.uid, loadItems]);

  const addItem = useCallback(async (item: Omit<ClothingItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => {
    if (!user?.uid) {
      return { success: false, error: 'User not authenticated', data: null };
    }
    setLoading(true);
    setError(null);
    try {
      const result = await addWardrobeItem(item);
      if (!result.success) {
        throw new Error(result.error || 'Failed to add item');
      }
      if (!result.data) {
        throw new Error('No data returned from addWardrobeItem');
      }
      setWardrobe(prev => [...prev, result.data].filter(Boolean) as WardrobeItem[]);
      return { success: true, data: result.data };
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to add item';
      setError(error);
      return { success: false, error, data: null };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const updateItem = useCallback(async (itemId: string, updates: Partial<ClothingItem>) => {
    if (!user?.uid) {
      return { success: false, error: 'User not authenticated', data: null };
    }
    setLoading(true);
    setError(null);
    try {
      const result = await updateWardrobeItem(itemId, updates);
      if (!result.success) {
        throw new Error(result.error || 'Failed to update item');
      }
      if (!result.data) {
        throw new Error('No data returned from updateWardrobeItem');
      }
      const updatedItem = result.data;
      setWardrobe(prev => prev.map(item => item.id === itemId ? updatedItem : item).filter(Boolean) as WardrobeItem[]);
      return { success: true, data: updatedItem };
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to update item';
      setError(error);
      return { success: false, error, data: null };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const removeItem = useCallback(async (itemId: string): Promise<ApiResponse<void>> => {
    if (!user?.uid) {
      return { success: false, error: 'User not authenticated', data: null };
    }
    setLoading(true);
    setError(null);
    try {
      const result = await deleteWardrobeItem(itemId);
      if (!result.success) {
        throw new Error(result.error || 'Failed to remove item');
      }
      setWardrobe(prev => prev.filter(item => item.id !== itemId));
      return { success: true, data: null };
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to remove item';
      setError(error);
      return { success: false, error, data: null };
    } finally {
      setLoading(false);
    }
  }, [user]);

  const getItemsByType = useCallback(async (type: string) => {
    if (!user?.uid) return [];
    setLoading(true);
    setError(null);
    try {
      const typeItems = await getWardrobeItemsByType(user.uid, type);
      // Validate all items against the schema
      return validateClothingItems(typeItems);
    } catch (err) {
      console.error('Error getting items by type:', err);
      setError(err instanceof Error ? err.message : 'Failed to get items by type');
      return [];
    } finally {
      setLoading(false);
    }
  }, [user]);

  const getItemsBySeason = useCallback(async (season: string) => {
    if (!user?.uid) return [];
    setLoading(true);
    setError(null);
    try {
      const seasonItems = await getWardrobeItemsBySeason(user.uid, season);
      // Validate all items against the schema
      return validateClothingItems(seasonItems);
    } catch (err) {
      console.error('Error getting items by season:', err);
      setError(err instanceof Error ? err.message : 'Failed to get items by season');
      return [];
    } finally {
      setLoading(false);
    }
  }, [user]);

  const processImages = useCallback(async (files: File[]): Promise<ClothingItem[]> => {
    if (!user?.uid) {
      throw new Error('User not authenticated');
    }
    setLoading(true);
    setError(null);
    try {
      const result = await processAndAddImages({
        userId: user.uid,
        files,
        onProgress: (progress) => {
          console.log(`Processing progress: ${progress}%`);
        }
      });
      if (!result.success || !result.data) {
        throw new Error(result.error || 'Failed to process images');
      }
      const newItems = result.data.newItems;
      if (newItems.length > 0) {
        setWardrobe(prev => {
          const currentItems = Array.isArray(prev) ? prev : [];
          return [...currentItems, ...newItems] as WardrobeItem[];
        });
      }
      return newItems;
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to process images';
      setError(error);
      throw new Error(error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  return {
    wardrobe,
    loading,
    error,
    loadItems,
    addItem,
    updateItem,
    removeItem,
    getItemsByType,
    getItemsBySeason,
    processImages
  };
} 