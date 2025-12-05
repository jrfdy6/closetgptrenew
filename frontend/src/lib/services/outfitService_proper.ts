import { Outfit, OutfitCreate, OutfitUpdate, OutfitFilters } from '@/lib/types/outfit';
import { db } from '@/lib/firebase/config';
import { doc, updateDoc, getDoc } from 'firebase/firestore';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

class OutfitService {
  private async makeRequest(endpoint: string, options: RequestInit = {}) {
    // Use Next.js API routes instead of calling backend directly
    const url = `/api${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers: defaultHeaders,
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    return response.json();
  }

  async getUserOutfits(filters: OutfitFilters = {}, token: string): Promise<Outfit[]> {
    const queryParams = new URLSearchParams();
    if (filters.style) queryParams.append('style', filters.style);
    if (filters.occasion) queryParams.append('occasion', filters.occasion);
    if (filters.season) queryParams.append('season', filters.season);
    
    const endpoint = `/outfits?${queryParams.toString()}`;
    return this.makeRequest(endpoint, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async getOutfitById(id: string, token: string): Promise<Outfit> {
    return this.makeRequest(`/outfits/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async createOutfit(outfit: OutfitCreate, token: string): Promise<Outfit> {
    const response = await this.makeRequest('/outfits', {
      method: 'POST',
      body: JSON.stringify(outfit),
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response?.outfit) {
      return response.outfit as Outfit;
    }

    return response as Outfit;
  }

  async updateOutfit(id: string, outfit: OutfitUpdate, token: string): Promise<Outfit> {
    try {
      console.log(`🔍 [OutfitService] Updating outfit ${id} directly in Firestore`);
      
      // Get the current outfit to verify it exists
      const outfitRef = doc(db, 'outfits', id);
      const outfitDoc = await getDoc(outfitRef);
      
      if (!outfitDoc.exists()) {
        throw new Error('Outfit not found');
      }
      
      // Update the outfit in Firestore
      // Filter out undefined values as Firestore doesn't accept them
      const updateData = Object.fromEntries(
        Object.entries({
          ...outfit,
          updatedAt: new Date(),
        }).filter(([_, value]) => value !== undefined)
      );
      
      // Also filter undefined values from nested objects in items array
      if (updateData.items && Array.isArray(updateData.items)) {
        updateData.items = updateData.items.map(item => {
          if (typeof item === 'object' && item !== null) {
            return Object.fromEntries(
              Object.entries(item).filter(([_, value]) => value !== undefined)
            );
          }
          return item;
        });
      }
      
      console.log('🔍 [OutfitService] Filtered update data:', updateData);
      
      await updateDoc(outfitRef, updateData);
      
      // Get the updated outfit
      const updatedDoc = await getDoc(outfitRef);
      const updatedOutfit = {
        id: updatedDoc.id,
        ...updatedDoc.data(),
      } as Outfit;
      
      console.log(`✅ [OutfitService] Successfully updated outfit ${id} in Firestore`);
      return updatedOutfit;
      
    } catch (error) {
      console.error(`❌ [OutfitService] Error updating outfit ${id}:`, error);
      throw error;
    }
  }

  async deleteOutfit(id: string, token: string): Promise<void> {
    return this.makeRequest(`/outfits/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async markOutfitAsWorn(id: string, token: string): Promise<any> {
    // Returns: { success, message, outfit_id, wear_count, xp_earned, level_up, new_level }
    return this.makeRequest(`/outfits/${id}/worn`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async toggleOutfitFavorite(id: string, token: string): Promise<Outfit> {
    return this.makeRequest(`/outfits/${id}/favorite`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async getOutfitStats(token: string): Promise<any> {
    return this.makeRequest('/outfits/stats/summary', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async searchOutfits(query: string, filters: OutfitFilters = {}, token: string): Promise<Outfit[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('q', query);
    if (filters.style) queryParams.append('style', filters.style);
    if (filters.occasion) queryParams.append('occasion', filters.occasion);
    if (filters.season) queryParams.append('season', filters.season);
    
    const endpoint = `/outfits/search?${queryParams.toString()}`;
    return this.makeRequest(endpoint, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  // Helper method to calculate relevance score for search results
  calculateRelevanceScore(outfit: Outfit, query: string): number {
    let score = 0;
    const lowerQuery = query.toLowerCase();
    
    // Check if query matches outfit name
    if (outfit.name.toLowerCase().includes(lowerQuery)) {
      score += 10;
    }
    
    // Check if query matches style
    if (outfit.style && outfit.style.toLowerCase().includes(lowerQuery)) {
      score += 8;
    }
    
    // Check if query matches occasion
    if (outfit.occasion && outfit.occasion.toLowerCase().includes(lowerQuery)) {
      score += 6;
    }
    
    // Check if query matches description
    if (outfit.description && outfit.description.toLowerCase().includes(lowerQuery)) {
      score += 4;
    }
    
    // Bonus for favorite outfits
    if (outfit.isFavorite) {
      score += 2;
    }
    
    // Bonus for recently worn outfits
    if (outfit.lastWorn) {
      score += 1;
    }
    
    return score;
  }
}

export const outfitService = new OutfitService();
export default outfitService;
