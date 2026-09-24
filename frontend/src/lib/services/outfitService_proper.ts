import type { Outfit, OutfitCreate, OutfitUpdate, OutfitFilters as BaseOutfitFilters } from '@/lib/services/outfitService';

type OutfitFilters = BaseOutfitFilters & { season?: string };
import { auth } from '@/lib/firebase/config';
import { wearOperationKey, clearWearOperation } from '@/lib/savedOutfit';
import { apiRequestError } from '@/lib/apiRequestError';

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
      cache: 'no-store',
      headers: defaultHeaders,
    });

    if (!response.ok) {
      throw await apiRequestError(response);
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
    return this.makeRequest(`/outfits/${encodeURIComponent(id)}`, {
      cache: 'no-store',
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
    const editable = ['name', 'description', 'notes', 'occasion', 'style', 'mood', 'season', 'items', 'isFavorite'];
    const patch = Object.fromEntries(Object.entries(outfit).filter(([field, value]) => editable.includes(field) && value !== undefined));
    const result = await this.makeRequest(`/outfits/${encodeURIComponent(id)}`, {
      method: 'PUT', body: JSON.stringify(patch), headers: { Authorization: `Bearer ${token}` },
    });
    if (result?.success !== true || result.id !== id) throw new Error('The server did not confirm your outfit update. Please retry.');
    // The backend owns garment identity and stale-preview invalidation.
    return this.getOutfitById(id, token);
  }

  async deleteOutfit(id: string, token: string): Promise<void> {
    const result = await this.makeRequest(`/outfits/${encodeURIComponent(id)}`, {
      method: 'DELETE', headers: { Authorization: `Bearer ${token}` },
    });
    if (result?.success !== true || result.id !== id || result.deleted !== true) {
      throw new Error('The server did not confirm deletion. Please retry.');
    }
  }

  async markOutfitAsWorn(id: string, token: string, operationKey?: string, timezone?: string): Promise<any> {
    const uid = auth?.currentUser?.uid || 'signed-in';
    const key = operationKey || wearOperationKey(uid, id);
    const result = await this.makeRequest('/outfits/' + encodeURIComponent(id) + '/worn', {
      method: 'POST',
      body: JSON.stringify({ idempotency_key: key, timezone: timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC' }),
      headers: { Authorization: 'Bearer ' + token },
    });
    if (result?.success !== true || result.outfit_id !== id || !result.event_id || !Number.isInteger(result.wear_count)) {
      throw new Error('We could not confirm the wear record. Retry to check the same action.');
    }
    if (!operationKey) clearWearOperation(uid, id);
    return result;
  }

  async setOutfitFavorite(id: string, isFavorite: boolean, token: string): Promise<{ isFavorite: boolean }> {
    const result = await this.makeRequest(`/outfits/${encodeURIComponent(id)}/favorite`, {
      method: 'PUT',
      body: JSON.stringify({ isFavorite }),
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (result?.success === false || result?.isFavorite !== isFavorite) throw new Error('The server did not confirm your favorite update. Please retry.');
    return result;
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
