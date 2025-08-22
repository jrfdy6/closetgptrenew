import { User } from 'firebase/auth';

// ===== DATA TYPES =====
export interface OutfitItem {
  id: string;
  name: string;
  category: string;
  style: string;
  color: string;
  imageUrl?: string;
  userId: string;
}

export interface Outfit {
  id: string;
  name: string;
  occasion: string;
  style: string;
  mood?: string;
  items: OutfitItem[];
  confidenceScore?: number;
  reasoning?: string;
  createdAt: Date;
  updatedAt: Date;
  userId: string;
  isFavorite?: boolean;
  wearCount?: number;
  lastWorn?: Date;
}

export interface OutfitCreate {
  name: string;
  occasion: string;
  style: string;
  mood?: string;
  items: OutfitItem[];
  confidenceScore?: number;
  reasoning?: string;
}

export interface OutfitUpdate {
  name?: string;
  occasion?: string;
  style?: string;
  mood?: string;
  items?: OutfitItem[];
  confidenceScore?: number;
  reasoning?: string;
}

export interface OutfitFilters {
  occasion?: string;
  style?: string;
  mood?: string;
  limit?: number;
  offset?: number;
}

export interface OutfitStats {
  totalOutfits: number;
  favoriteOutfits: number;
  totalWearCount: number;
  occasions: Record<string, number>;
  styles: Record<string, number>;
  recentActivity?: Array<{
    id: string;
    name: string;
    lastUpdated: Date;
  }>;
}

// ===== API RESPONSE TYPES =====
export interface StandardResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T = any> {
  success: boolean;
  data: T[];
  total: number;
  limit: number;
  offset: number;
  message?: string;
}

// ===== CORE SERVICE CLASS =====
export class OutfitService {
  private static readonly API_BASE = '/api/outfits';

  // ===== AUTHENTICATION HELPERS =====
  private static async getAuthHeaders(user: User): Promise<HeadersInit> {
    const token = await user.getIdToken();
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  private static async checkBackendConnection(): Promise<boolean> {
    try {
      const response = await fetch('/api/health/simple', { method: 'GET' });
      return response.ok;
    } catch {
      return false;
    }
  }

  // ===== CORE API OPERATIONS (Following Wardrobe Pattern) =====
  
  /**
   * Get user's outfits from backend API
   * This follows the established wardrobe service pattern
   */
  static async getUserOutfits(user: User, filters: OutfitFilters = {}): Promise<Outfit[]> {
    try {
      console.log('🔍 [OutfitService] Getting user outfits from backend API');
      
      // Build query parameters
      const params = new URLSearchParams();
      if (filters.occasion) params.append('occasion', filters.occasion);
      if (filters.style) params.append('style', filters.style);
      if (filters.mood) params.append('mood', filters.mood);
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.offset) params.append('offset', filters.offset.toString());
      
      const url = `${this.API_BASE}/?${params.toString()}`;
      console.log(`🔗 [OutfitService] API URL: ${url}`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: await this.getAuthHeaders(user),
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Access denied. You do not have permission to view outfits.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data: PaginatedResponse<Outfit> = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch outfits');
      }
      
      console.log(`✅ [OutfitService] Retrieved ${data.data.length} outfits from backend`);
      return data.data;
      
    } catch (error) {
      console.error('❌ [OutfitService] Error getting user outfits:', error);
      throw error;
    }
  }

  /**
   * Get a specific outfit by ID from backend API
   */
  static async getOutfitById(user: User, outfitId: string): Promise<Outfit | null> {
    try {
      console.log(`🔍 [OutfitService] Getting outfit ${outfitId} from backend API`);
      
      const response = await fetch(`${this.API_BASE}/${outfitId}`, {
        method: 'GET',
        headers: await this.getAuthHeaders(user),
      });
      
      if (response.status === 404) {
        console.log(`⚠️ [OutfitService] Outfit ${outfitId} not found`);
        return null;
      }
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Access denied. You do not have permission to view this outfit.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data: StandardResponse<Outfit> = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch outfit');
      }
      
      console.log(`✅ [OutfitService] Successfully retrieved outfit ${outfitId}`);
      return data.data!;
      
    } catch (error) {
      console.error(`❌ [OutfitService] Error getting outfit ${outfitId}:`, error);
      throw error;
    }
  }

  /**
   * Create a new outfit through backend API
   */
  static async createOutfit(user: User, outfitData: OutfitCreate): Promise<Outfit> {
    try {
      console.log('🔍 [OutfitService] Creating new outfit through backend API');
      
      const response = await fetch(`${this.API_BASE}/`, {
        method: 'POST',
        headers: await this.getAuthHeaders(user),
        body: JSON.stringify(outfitData),
      });
      
      if (!response.ok) {
        if (response.status === 400) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Invalid outfit data');
        } else if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data: StandardResponse<Outfit> = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to create outfit');
      }
      
      console.log(`✅ [OutfitService] Successfully created outfit ${data.data!.id}`);
      return data.data!;
      
    } catch (error) {
      console.error('❌ [OutfitService] Error creating outfit:', error);
      throw error;
    }
  }

  /**
   * Update an existing outfit through backend API
   */
  static async updateOutfit(user: User, outfitId: string, updates: OutfitUpdate): Promise<Outfit> {
    try {
      console.log(`🔍 [OutfitService] Updating outfit ${outfitId} through backend API`);
      
      const response = await fetch(`${this.API_BASE}/${outfitId}`, {
        method: 'PUT',
        headers: await this.getAuthHeaders(user),
        body: JSON.stringify(updates),
      });
      
      if (response.status === 404) {
        throw new Error('Outfit not found');
      }
      
      if (!response.ok) {
        if (response.status === 400) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Invalid update data');
        } else if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data: StandardResponse<Outfit> = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to update outfit');
      }
      
      console.log(`✅ [OutfitService] Successfully updated outfit ${outfitId}`);
      return data.data!;
      
    } catch (error) {
      console.error(`❌ [OutfitService] Error updating outfit ${outfitId}:`, error);
      throw error;
    }
  }

  /**
   * Delete an outfit through backend API
   */
  static async deleteOutfit(user: User, outfitId: string): Promise<void> {
    try {
      console.log(`🔍 [OutfitService] Deleting outfit ${outfitId} through backend API`);
      
      const response = await fetch(`${this.API_BASE}/${outfitId}`, {
        method: 'DELETE',
        headers: await this.getAuthHeaders(user),
      });
      
      if (response.status === 404) {
        throw new Error('Outfit not found');
      }
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data: StandardResponse = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to delete outfit');
      }
      
      console.log(`✅ [OutfitService] Successfully deleted outfit ${outfitId}`);
      
    } catch (error) {
      console.error(`❌ [OutfitService] Error deleting outfit ${outfitId}:`, error);
      throw error;
    }
  }

  /**
   * Mark outfit as worn through backend API
   */
  static async markOutfitAsWorn(user: User, outfitId: string): Promise<void> {
    try {
      console.log(`🔍 [OutfitService] Marking outfit ${outfitId} as worn through backend API`);
      
      const response = await fetch(`${this.API_BASE}/${outfitId}/mark-worn`, {
        method: 'POST',
        headers: await this.getAuthHeaders(user),
      });
      
      if (response.status === 404) {
        throw new Error('Outfit not found');
      }
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data: StandardResponse = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to mark outfit as worn');
      }
      
      console.log(`✅ [OutfitService] Successfully marked outfit ${outfitId} as worn`);
      
    } catch (error) {
      console.error(`❌ [OutfitService] Error marking outfit ${outfitId} as worn:`, error);
      throw error;
    }
  }

  /**
   * Toggle outfit favorite status through backend API
   */
  static async toggleOutfitFavorite(user: User, outfitId: string): Promise<void> {
    try {
      console.log(`🔍 [OutfitService] Toggling favorite for outfit ${outfitId} through backend API`);
      
      const response = await fetch(`${this.API_BASE}/${outfitId}/toggle-favorite`, {
        method: 'POST',
        headers: await this.getAuthHeaders(user),
      });
      
      if (response.status === 404) {
        throw new Error('Outfit not found');
      }
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data: StandardResponse = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to toggle outfit favorite');
      }
      
      console.log(`✅ [OutfitService] Successfully toggled favorite for outfit ${outfitId}`);
      
    } catch (error) {
      console.error(`❌ [OutfitService] Error toggling favorite for outfit ${outfitId}:`, error);
      throw error;
    }
  }

  /**
   * Get outfit statistics through backend API
   */
  static async getOutfitStats(user: User): Promise<OutfitStats> {
    try {
      console.log('🔍 [OutfitService] Getting outfit statistics from backend API');
      
      const response = await fetch(`${this.API_BASE}/stats/summary`, {
        method: 'GET',
        headers: await this.getAuthHeaders(user),
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data: StandardResponse<OutfitStats> = await response.json();
      
      if (!data.success) {
        throw new Error(data.error || 'Failed to get outfit statistics');
      }
      
      console.log('✅ [OutfitService] Successfully retrieved outfit statistics');
      return data.data!;
      
    } catch (error) {
      console.error('❌ [OutfitService] Error getting outfit statistics:', error);
      throw error;
    }
  }

  /**
   * Search outfits with text query through backend API
   */
  static async searchOutfits(user: User, query: string, filters: OutfitFilters = {}): Promise<Outfit[]> {
    try {
      console.log(`🔍 [OutfitService] Searching outfits with query: "${query}"`);
      
      // For now, implement client-side search using the existing get_user_outfits
      // In the future, this could be enhanced with a dedicated search endpoint
      const allOutfits = await this.getUserOutfits(user, { ...filters, limit: 1000 });
      
      if (!query || !query.trim()) {
        return allOutfits;
      }
      
      const queryLower = query.toLowerCase();
      const searchResults = allOutfits.filter(outfit => {
        const searchableText = `${outfit.name} ${outfit.occasion} ${outfit.style} ${outfit.mood || ''}`.toLowerCase();
        return queryLower in searchableText;
      });
      
      // Sort by relevance
      searchResults.sort((a, b) => {
        const aScore = this.calculateRelevanceScore(a, queryLower);
        const bScore = this.calculateRelevanceScore(b, queryLower);
        return bScore - aScore;
      });
      
      console.log(`✅ [OutfitService] Search returned ${searchResults.length} results`);
      return searchResults;
      
    } catch (error) {
      console.error('❌ [OutfitService] Error searching outfits:', error);
      throw error;
    }
  }

  // ===== UTILITY METHODS =====
  
  private static calculateRelevanceScore(outfit: Outfit, query: string): number {
    let score = 0;
    
    // Name matches get highest score
    if (query in outfit.name.toLowerCase()) score += 10;
    
    // Occasion matches
    if (query in outfit.occasion.toLowerCase()) score += 5;
    
    // Style matches
    if (query in outfit.style.toLowerCase()) score += 5;
    
    // Mood matches
    if (outfit.mood && query in outfit.mood.toLowerCase()) score += 3;
    
    // Recency bonus
    const daysSinceUpdate = (Date.now() - outfit.updatedAt.getTime()) / (1000 * 60 * 60 * 24);
    if (daysSinceUpdate < 7) score += 2;
    else if (daysSinceUpdate < 30) score += 1;
    
    return score;
  }
}

// ===== EXPORT DEFAULT INSTANCE =====
export default OutfitService;
