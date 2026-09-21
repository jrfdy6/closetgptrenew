import type { Outfit, OutfitCreate, OutfitUpdate, OutfitFilters as BaseOutfitFilters } from '@/lib/services/outfitService';

type OutfitFilters = BaseOutfitFilters & { season?: string };
import { db } from '@/lib/firebase/config';
import { doc, updateDoc, getDoc } from 'firebase/firestore';
import { extractFlatLayState } from '@/lib/flatLayState';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

function omitUndefined<T extends object>(value: T): T {
  const result = { ...value };
  for (const key of Object.keys(result) as Array<keyof T>) {
    if (result[key] === undefined) delete result[key];
  }
  return result;
}

function itemIdentity(items: unknown): string {
  if (!Array.isArray(items)) return '';
  return JSON.stringify(Array.from(new Set(items.map(item => {
    if (typeof item === 'string') return item;
    return item && typeof item === 'object' ? item.id ?? item.itemId ?? item.item_id : null;
  }).filter(id => typeof id === 'string'))).sort());
}

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
      const error = await response.json().catch(() => null);
      const message = error?.error ?? error?.detail;
      throw new Error(typeof message === 'string' ? message : `Request failed with status ${response.status}`);
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

    const saved = response?.outfit ?? response?.data ?? response;
    const id = saved?.id ?? saved?.outfit_id ?? response?.id ?? response?.outfit_id;
    if (response?.success === false || typeof id !== 'string' || !id.trim()) {
      throw new Error('The server did not confirm that your outfit was saved.');
    }

    // Older responses only contain outfit_id; keep the submitted draft fields.
    return { ...outfit, ...saved, id } as Outfit;
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
      const updateData: Record<string, unknown> = omitUndefined({
        ...outfit,
        updatedAt: new Date(),
      });
      
      // Also filter undefined values from nested objects in items array
      if (updateData.items && Array.isArray(updateData.items)) {
        updateData.items = updateData.items.map(item => {
          if (typeof item === 'object' && item !== null) {
            return omitUndefined(item);
          }
          return item;
        });
      }

      const currentOutfit = outfitDoc.data();
      if (Array.isArray(updateData.items) && itemIdentity(updateData.items) !== itemIdentity(currentOutfit?.items)) {
        // Clear the old visual in the same write as its changed pieces. The
        // private server ledger still controls consent, charges and in-flight work.
        const previous = extractFlatLayState(currentOutfit ?? {});
        const presentation: Record<string, unknown> = { flat_lay_url: null, flatLayUrl: null };
        if (previous.status === 'done') {
          Object.assign(presentation, {
            flat_lay_status: 'awaiting_consent', flatLayStatus: 'awaiting_consent',
            flat_lay_error: null, flatLayError: null, flat_lay_request_allowed: true,
          });
        }
        Object.assign(updateData, presentation);
        for (const [key, value] of Object.entries(presentation)) updateData[`metadata.${key}`] = value;
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

  async setOutfitFavorite(id: string, isFavorite: boolean, token: string): Promise<{ isFavorite: boolean }> {
    return this.makeRequest(`/outfits/${id}/favorite`, {
      method: 'PUT',
      body: JSON.stringify({ isFavorite }),
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
