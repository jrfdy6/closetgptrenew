import type { Outfit, OutfitCreate, OutfitUpdate, OutfitFilters as BaseOutfitFilters } from '@/lib/services/outfitService';

type OutfitFilters = BaseOutfitFilters & { season?: string };
function editableOutfitFields(outfit: OutfitCreate | OutfitUpdate, create = false) {
  const fields = ['name', 'occasion', 'style', 'mood', 'description', 'notes', 'items', ...(create ? ['id'] : ['isFavorite'])];
  return Object.fromEntries(fields.filter(key => (outfit as any)[key] !== undefined).map(key => [key, (outfit as any)[key]]));
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
      body: JSON.stringify(editableOutfitFields(outfit, true)),
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
    const response = await this.makeRequest(`/outfits/${id}`, {
      method: 'PUT',
      body: JSON.stringify(editableOutfitFields(outfit)),
      headers: { Authorization: `Bearer ${token}` },
    });
    const saved = response?.outfit ?? response?.data ?? response;
    if (response?.success === false) throw new Error('Your outfit could not be updated.');
    // Older API responses confirm the update without the document.
    return saved?.id ? saved as Outfit : this.getOutfitById(id, token);
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
