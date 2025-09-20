/**
 * Fast Outfit Service
 * 
 * Lightning-fast outfit loading using pre-aggregated stats and metadata.
 * Replaces slow pagination with instant loading for better UX.
 */

import { User } from 'firebase/auth';

// ===== TYPES =====
export interface OutfitMetadata {
  id: string;
  name: string;
  occasion: string;
  style: string;
  mood: string;
  isFavorite: boolean;
  isWorn: boolean;
  wearCount: number;
  rating?: number;
  createdAt: any;
  updatedAt: any;
  thumbnailUrl: string;
  itemCount: number;
  itemPreviews: Array<{
    id: string;
    name: string;
    imageUrl: string;
    type: string;
  }>;
}

export interface OutfitSummary {
  total_outfits: number;
  outfits_this_week: number;
  recent_outfits: Array<{
    id: string;
    name: string;
    thumbnailUrl: string;
    occasion: string;
    createdAt: any;
  }>;
  last_updated: any;
}

export interface FilterOptions {
  occasions: string[];
  styles: string[];
  moods: string[];
  sort_options: Array<{
    value: string;
    label: string;
  }>;
}

export interface OutfitFilters {
  occasion?: string;
  style?: string;
  is_favorite?: boolean;
  sort_by?: string;
}

export interface PaginationInfo {
  limit: number;
  offset: number;
  total: number;
  has_more: boolean;
}

export interface OutfitMetadataResponse {
  success: boolean;
  outfits: OutfitMetadata[];
  pagination: PaginationInfo;
  filters: OutfitFilters;
}

class FastOutfitService {
  private async makeAuthenticatedRequest(user: User | null, endpoint: string, options: RequestInit = {}): Promise<any> {
    if (!user) {
      throw new Error('User not authenticated');
    }

    // Get authentication token
    const token = await user.getIdToken();
    if (!token) {
      throw new Error('Failed to get authentication token');
    }

    // Use Next.js API route as proxy
    const fullUrl = endpoint.startsWith('http') ? endpoint : `/api${endpoint}`;

    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unable to read error');
      console.error('🔍 Fast Outfit API request failed:', response.status, errorText);
      
      let errorData = {};
      try {
        errorData = JSON.parse(errorText);
      } catch (e) {
        // If JSON parsing fails, use the text error
      }
      
      throw new Error(`API request failed: ${response.status} ${JSON.stringify(errorData)}`);
    }

    return response.json();
  }

  /**
   * Get outfit summary for instant loading
   */
  async getOutfitSummary(user: User | null): Promise<OutfitSummary> {
    try {
      console.log('🚀 [FastOutfitService] Fetching outfit summary...');
      
      const response = await this.makeAuthenticatedRequest(user, '/outfits-fast/summary');
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch outfit summary');
      }

      console.log('✅ [FastOutfitService] Outfit summary loaded:', response.summary);
      return response.summary;
    } catch (error) {
      console.error('❌ [FastOutfitService] Error fetching outfit summary:', error);
      throw error;
    }
  }

  /**
   * Get outfit metadata for fast grid loading
   */
  async getOutfitMetadata(
    user: User | null, 
    filters: OutfitFilters = {}, 
    limit: number = 100, 
    offset: number = 0
  ): Promise<OutfitMetadataResponse> {
    try {
      console.log('🚀 [FastOutfitService] Fetching outfit metadata...', { filters, limit, offset });
      
      // Build query parameters
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
        sort_by: filters.sort_by || 'date-newest'
      });

      if (filters.occasion) params.append('occasion', filters.occasion);
      if (filters.style) params.append('style', filters.style);
      if (filters.is_favorite !== undefined) params.append('is_favorite', filters.is_favorite.toString());

      const response = await this.makeAuthenticatedRequest(
        user, 
        `/outfits-fast/metadata?${params.toString()}`
      );
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch outfit metadata');
      }

      console.log('✅ [FastOutfitService] Outfit metadata loaded:', {
        count: response.outfits.length,
        total: response.pagination.total,
        has_more: response.pagination.has_more
      });

      return response;
    } catch (error) {
      console.error('❌ [FastOutfitService] Error fetching outfit metadata:', error);
      throw error;
    }
  }

  /**
   * Get available filter options
   */
  async getFilterOptions(user: User | null): Promise<FilterOptions> {
    try {
      console.log('🚀 [FastOutfitService] Fetching filter options...');
      
      const response = await this.makeAuthenticatedRequest(user, '/outfits-fast/filter-options');
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch filter options');
      }

      console.log('✅ [FastOutfitService] Filter options loaded:', response.filter_options);
      return response.filter_options;
    } catch (error) {
      console.error('❌ [FastOutfitService] Error fetching filter options:', error);
      throw error;
    }
  }

  /**
   * Search outfits by text query (client-side filtering for now)
   */
  searchOutfits(outfits: OutfitMetadata[], query: string): OutfitMetadata[] {
    if (!query.trim()) {
      return outfits;
    }

    const lowerQuery = query.toLowerCase();
    return outfits.filter(outfit => 
      outfit.name.toLowerCase().includes(lowerQuery) ||
      outfit.occasion.toLowerCase().includes(lowerQuery) ||
      outfit.style.toLowerCase().includes(lowerQuery) ||
      outfit.mood.toLowerCase().includes(lowerQuery) ||
      outfit.itemPreviews.some(item => 
        item.name.toLowerCase().includes(lowerQuery) ||
        item.type.toLowerCase().includes(lowerQuery)
      )
    );
  }
}

// Export singleton instance
export const fastOutfitService = new FastOutfitService();
export default fastOutfitService;
