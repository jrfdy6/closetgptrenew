/**
 * Item Adapter - Centralized conversion between OutfitItem and ClothingItem
 * 
 * This adapter provides a single source of truth for converting between
 * the two different item representations used in the application:
 * - OutfitItem: Backend/API format (category, style, color)
 * - ClothingItem: Frontend wardrobe format (type, brand, season)
 */

import { OutfitItem } from '@/lib/services/outfitService';
import type { ClothingItem } from '@/lib/hooks/useWardrobe';

/**
 * Convert OutfitItem (backend format) to ClothingItem (frontend format)
 * Used when displaying outfit items in the wardrobe interface
 */
export function toClothingItem(outfitItem: OutfitItem): ClothingItem {
  return {
    id: outfitItem.id,
    name: outfitItem.name,
    type: outfitItem.category,
    color: outfitItem.color,
    brand: '',
    imageUrl: outfitItem.imageUrl || '',
    userId: outfitItem.user_id,
    style: outfitItem.style ? [outfitItem.style] : [],
    season: [],
    occasion: [],
    favorite: false,
    wearCount: 0,
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}

/**
 * Convert ClothingItem (frontend format) to OutfitItem (backend format)
 * Used when sending outfit data to the API
 */
export function toOutfitItem(clothingItem: ClothingItem): OutfitItem {
  return {
    id: clothingItem.id,
    name: clothingItem.name,
    category: clothingItem.type,
    style: clothingItem.style?.[0] || '',
    color: clothingItem.color,
    imageUrl: clothingItem.imageUrl,
    user_id: clothingItem.userId
  };
}

/**
 * Convert array of OutfitItems to ClothingItems
 * Convenience function for bulk conversion
 */
export function toClothingItems(outfitItems: OutfitItem[]): ClothingItem[] {
  return outfitItems.map(toClothingItem);
}

/**
 * Convert array of ClothingItems to OutfitItems
 * Convenience function for bulk conversion
 */
export function toOutfitItems(clothingItems: ClothingItem[]): OutfitItem[] {
  return clothingItems.map(toOutfitItem);
}

/**
 * Check if a ClothingItem exists in a wardrobe
 * Helper function for validation
 */
export function itemExistsInWardrobe(
  item: ClothingItem, 
  wardrobeItems: ClothingItem[]
): boolean {
  return wardrobeItems.some(wardrobeItem => wardrobeItem.id === item.id);
}

/**
 * Filter out items that don't exist in wardrobe
 * Helper function for validation
 */
export function filterValidItems(
  items: ClothingItem[], 
  wardrobeItems: ClothingItem[]
): ClothingItem[] {
  return items.filter(item => itemExistsInWardrobe(item, wardrobeItems));
}

/**
 * Get items that don't exist in wardrobe
 * Helper function for validation
 */
export function getInvalidItems(
  items: ClothingItem[], 
  wardrobeItems: ClothingItem[]
): ClothingItem[] {
  return items.filter(item => !itemExistsInWardrobe(item, wardrobeItems));
}
