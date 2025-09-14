import { useState, useEffect, useCallback } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { WardrobeService } from '@/lib/services/wardrobeService';
import { safeToDate } from '@/lib/utils/dateUtils';

export interface ClothingItem {
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
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<WardrobeFilters>({});

  // Fetch wardrobe items
  const fetchItems = useCallback(async () => {
    if (!user) {
      setItems([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Use real API call to backend directly
      const wardrobeItems = await WardrobeService.getWardrobeItems();
      setItems(wardrobeItems);
    } catch (err) {
      console.error('Error fetching wardrobe items:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch wardrobe items');
    } finally {
      setLoading(false);
    }
  }, [user?.uid]); // Use user.uid instead of user object

  // Add new item
  const addItem = useCallback(async (item: Omit<ClothingItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) => {
    if (!user) return;

    try {
      // Use real API call to backend
      const newItem = await WardrobeService.addWardrobeItem(item);
      setItems(prev => [...prev, newItem]);
      return newItem;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add item');
      throw err;
    }
  }, [user?.uid]); // Use user.uid instead of user object

  // Update item
  const updateItem = useCallback(async (id: string, updates: Partial<ClothingItem>) => {
    try {
      // Use real API call to backend
      await WardrobeService.updateWardrobeItem(id, updates);
      
      // Update local state
      setItems(prev => prev.map(item => 
        item.id === id 
          ? { ...item, ...updates, updatedAt: new Date() }
          : item
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update item');
      throw err;
    }
  }, []);

  // Delete item
  const deleteItem = useCallback(async (id: string) => {
    try {
      console.log(`🗑️ [useWardrobe] Starting delete for item ${id}`);
      
      // Use real API call to backend
      await WardrobeService.deleteWardrobeItem(id);
      
      console.log(`✅ [useWardrobe] Successfully deleted item ${id} from backend`);
      
      // Update local state
      setItems(prev => {
        const newItems = prev.filter(item => item.id !== id);
        console.log(`🔄 [useWardrobe] Updated local state. Items before: ${prev.length}, after: ${newItems.length}`);
        return newItems;
      });
      
      console.log(`✅ [useWardrobe] Item ${id} successfully deleted and removed from UI`);
    } catch (err) {
      console.error(`❌ [useWardrobe] Error deleting item ${id}:`, err);
      setError(err instanceof Error ? err.message : 'Failed to delete item');
      throw err;
    }
  }, []);

  // Toggle favorite
  const toggleFavorite = useCallback(async (id: string) => {
    try {
      console.log(`🔍 [useWardrobe] Starting toggle favorite for item ${id}`);
      
      // Use functional update to avoid dependency on items
      setItems(prev => {
        const currentItem = prev.find(item => item.id === id);
        if (!currentItem) {
          console.error(`🔍 [useWardrobe] Item ${id} not found in current items`);
          return prev;
        }
        
        const newFavoriteValue = !currentItem.favorite;
        console.log(`🔍 [useWardrobe] Current favorite: ${currentItem.favorite}, new value: ${newFavoriteValue}`);
        
        // Use real API call to backend
        WardrobeService.toggleFavorite(id, newFavoriteValue).then(() => {
          console.log(`✅ [useWardrobe] Successfully toggled favorite for item ${id}`);
        }).catch(err => {
          console.error(`❌ [useWardrobe] Error toggling favorite:`, err);
          setError(err instanceof Error ? err.message : 'Failed to toggle favorite');
        });
        
        const updated = prev.map(item => 
          item.id === id 
            ? { ...item, favorite: newFavoriteValue, updatedAt: new Date() }
            : item
        );
        console.log(`🔍 [useWardrobe] Updated items state, item ${id} favorite: ${newFavoriteValue}`);
        return updated;
      });
      
    } catch (err) {
      console.error(`❌ [useWardrobe] Error toggling favorite:`, err);
      setError(err instanceof Error ? err.message : 'Failed to toggle favorite');
      throw err;
    }
  }, []); // Remove items dependency

  // Increment wear count
  const incrementWearCount = useCallback(async (id: string) => {
    try {
      // Use real API call to backend
      await WardrobeService.incrementWearCount(id);
      
      // Update local state
      setItems(prev => prev.map(item => 
        item.id === id 
          ? { 
              ...item, 
              wearCount: item.wearCount + 1, 
              lastWorn: new Date(),
              updatedAt: new Date() 
            }
          : item
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update wear count');
      throw err;
    }
  }, []);

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

  // Initialize
  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  return {
    items,
    loading,
    error,
    filters,
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
