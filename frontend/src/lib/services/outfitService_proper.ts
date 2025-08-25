import { Outfit, OutfitCreate, OutfitUpdate, OutfitFilters } from '@/custom_types/outfit';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

class OutfitService {
  private async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}/api${endpoint}`;
    
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
    return this.makeRequest('/outfits', {
      method: 'POST',
      body: JSON.stringify(outfit),
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async updateOutfit(id: string, outfit: OutfitUpdate, token: string): Promise<Outfit> {
    return this.makeRequest(`/outfits/${id}`, {
      method: 'PUT',
      body: JSON.stringify(outfit),
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async deleteOutfit(id: string, token: string): Promise<void> {
    return this.makeRequest(`/outfits/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async markOutfitAsWorn(id: string, token: string): Promise<Outfit> {
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
