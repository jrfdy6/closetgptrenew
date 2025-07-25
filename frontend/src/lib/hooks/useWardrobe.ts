import { useState, useCallback, useEffect } from 'react';
import { useAuth } from './useAuth';
import { 
  getWardrobeItems, 
  addWardrobeItem, 
  updateWardrobeItem, 
  deleteWardrobeItem,
  processAndAddImages
} from '../firebase/wardrobeService';
import type { ClothingItem } from '@/types/wardrobe';
import type { ProcessImagesResponse } from '@/types/wardrobe';

export function useWardrobe() {
  const { user, loading: authLoading, isAuthenticated } = useAuth();
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadItems = useCallback(async () => {
    if (!user?.uid) {
      console.log('No user ID available, skipping load');
      setLoading(false);
      return;
    }
    
    console.log('Starting to load items for user:', user.uid);
    setLoading(true);
    setError(null);
    
    try {
      console.log('Calling getWardrobeItems...');
      const result = await getWardrobeItems(user.uid);
      console.log('getWardrobeItems result:', {
        success: result.success,
        itemCount: result.data?.length,
        firstItem: result.data?.[0] ? {
          id: result.data[0].id,
          name: result.data[0].name,
          type: result.data[0].type
        } : null
      });

      if (result.success && result.data) {
        setItems(result.data);
      } else {
        console.error('Failed to load items:', result.error);
        setError(result.error || 'Failed to load items');
        setItems([]);
      }
    } catch (err) {
      console.error('Error in loadItems:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to load items';
      console.error('Setting error state:', errorMessage);
      setError(errorMessage);
      setItems([]);
    } finally {
      console.log('Finished loading items');
      setLoading(false);
    }
  }, [user]);

  // Load items when user changes
  useEffect(() => {
    console.log('useWardrobe effect triggered:', {
      user: user?.uid,
      authLoading,
      isAuthenticated
    });

    if (authLoading) {
      console.log('Auth is still loading, waiting...');
      return;
    }

    if (user && !authLoading) {
      console.log('Loading items for user:', user.uid);
      loadItems();
    } else if (!authLoading && !user) {
      console.log('No user, clearing items');
      setItems([]);
      setError(null);
      setLoading(false);
    }
  }, [user, authLoading, loadItems]);

  const addItem = useCallback(async (item: Omit<ClothingItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => {
    if (!user?.uid) throw new Error('Not authenticated');
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await addWardrobeItem(item);
      if (result.success && result.data) {
        await loadItems();
        return result.data;
      } else {
        throw new Error(result.error || 'Failed to add item');
      }
    } catch (err) {
      console.error('Error adding item:', err);
      const error = err instanceof Error ? err.message : 'Failed to add item';
      setError(error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [user, loadItems]);

  const updateItem = useCallback(async (itemId: string, updates: Partial<ClothingItem>) => {
    if (!user?.uid) throw new Error('Not authenticated');
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await updateWardrobeItem(itemId, updates);
      if (result.success && result.data) {
        setItems(prev => prev.map(item => 
          item.id === itemId ? result.data! : item
        ));
        return result.data;
      } else {
        throw new Error(result.error || 'Failed to update item');
      }
    } catch (err) {
      console.error('Error updating item:', err);
      const error = err instanceof Error ? err.message : 'Failed to update item';
      setError(error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [user]);

  const removeItem = useCallback(async (itemId: string) => {
    if (!user?.uid) throw new Error('Not authenticated');
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await deleteWardrobeItem(itemId);
      if (result.success) {
        setItems(prev => prev.filter(item => item.id !== itemId));
      } else {
        throw new Error(result.error || 'Failed to remove item');
      }
    } catch (err) {
      console.error('Error removing item:', err);
      const error = err instanceof Error ? err.message : 'Failed to remove item';
      setError(error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [user]);

  const processImages = useCallback(async (files: File[]): Promise<ProcessImagesResponse> => {
    if (authLoading) {
      return {
        success: false,
        data: null,
        error: 'Authentication is still loading'
      };
    }

    if (!isAuthenticated || !user?.uid) {
      return {
        success: false,
        data: null,
        error: 'Not authenticated'
      };
    }
    
    if (!files || files.length === 0) {
      return {
        success: false,
        data: null,
        error: 'No files provided'
      };
    }
    
    setLoading(true);
    setError(null);
    
    try {
      console.log('Processing images with userId:', user.uid);
      const result = await processAndAddImages({
        userId: user.uid,
        files,
        onProgress: (progress: number) => {
          console.log(`Processing progress: ${progress}%`);
        }
      });

      if (result.success && result.data) {
        setItems(prev => [...prev, ...result.data!.newItems]);
        return result;
      } else {
        return {
          success: false,
          data: null,
          error: result.error || 'No items were processed'
        };
      }
    } catch (err) {
      console.error('Error in processImages:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to process images';
      setError(errorMessage);
      return {
        success: false,
        data: null,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  }, [user, isAuthenticated, authLoading]);

  return {
    items,
    loading: loading || authLoading,
    error,
    loadItems,
    addItem,
    updateItem,
    removeItem,
    processImages
  };
} 