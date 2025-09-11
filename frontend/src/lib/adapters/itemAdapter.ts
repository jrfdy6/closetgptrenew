/**
 * Item Adapter - Centralized conversion between OutfitItem and ClothingItem
 * 
 * This adapter provides a single source of truth for converting between
 * the two different item representations used in the application:
 * - OutfitItem: Backend/API format (category, style, color)
 * - ClothingItem: Frontend wardrobe format (type, brand, season)
 */

import { OutfitItem } from '@/lib/services/outfitService';
import { ClothingItem } from '@/lib/services/outfitService';

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
    brand: '', // OutfitItem doesn't have brand
    imageUrl: outfitItem.imageUrl,
    user_id: outfitItem.user_id,
    season: 'all', // Default season
    isFavorite: false, // OutfitItem doesn't have isFavorite
    wearCount: 0, // OutfitItem doesn't have wearCount
    lastWorn: null, // OutfitItem doesn't have lastWorn
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    // Additional required ClothingItem fields with sensible defaults
    size: '', // Default size
    material: '', // Default material
    condition: 'good', // Default condition
    price: 0, // Default price
    purchaseDate: null, // Default purchase date
    tags: [], // Default tags
    notes: '' // Default notes
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
    style: '', // ClothingItem doesn't have style field
    color: clothingItem.color,
    imageUrl: clothingItem.imageUrl,
    user_id: clothingItem.user_id
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
