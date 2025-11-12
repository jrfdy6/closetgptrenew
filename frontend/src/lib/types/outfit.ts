// ===== OUTFIT TYPES =====
// Centralized type definitions for the Easy Outfit App system

export interface Outfit {
  id: string;
  name: string;
  user_id: string; // Changed from userId to user_id to match backend
  items: string[]; // array of clothing item IDs
  style: string;
  season?: string;
  temperature?: number;
  occasion?: string;
  notes?: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  isFavorite?: boolean;
  lastWorn?: string;
  wearCount?: number;
}

export interface OutfitCreate {
  user_id: string; // Changed from userId to user_id to match backend
  items: string[];
  style: string;
  season?: string;
  temperature?: number;
  occasion?: string;
  notes?: string;
}

export interface OutfitUpdate {
  id: string;
  items?: string[];
  style?: string;
  season?: string;
  temperature?: number;
  occasion?: string;
  notes?: string;
  updatedAt?: string;
}

export interface OutfitStats {
  totalOutfits: number;
  favoriteStyles: Record<string, number>; // style → count
  mostUsedItems: Record<string, number>;  // itemId → count
  seasonalDistribution: Record<string, number>; // season → count
  lastWorn?: string; // ISO timestamp
}

export interface OutfitFilters {
  occasion?: string;
  style?: string;
  season?: string;
  mood?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
  limit?: number;
  offset?: number;
}
