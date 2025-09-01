import { ClothingItem, WardrobeFilters } from '@/lib/hooks/useWardrobe';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001';

export interface WardrobeResponse {
  success: boolean;
  items: ClothingItem[];
  count: number;
  errors?: string[];
}

export interface WardrobeItemResponse {
  success: boolean;
  message: string;
  item?: ClothingItem;
}

export class WardrobeService {
  private static async getAuthHeaders(): Promise<HeadersInit> {
    // Get the Firebase ID token for authentication
    const auth = (await import('@/lib/firebase/config')).auth;
    const user = auth.currentUser;
    
    if (!user) {
      throw new Error('User not authenticated');
    }
    
    const token = await user.getIdToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  private static async checkBackendConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health/simple`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      return response.ok;
    } catch (error) {
      console.warn('Backend connection check failed:', error);
      return false;
    }
  }

  static async getWardrobeItems(): Promise<ClothingItem[]> {
    try {
      console.log('🔍 DEBUG: Getting wardrobe items...'); // Trigger Vercel deployment
      // Trigger Vercel deployment - Firebase auth fix
      
      const response = await fetch('/api/wardrobe/', {
        method: 'GET',
        headers: await this.getAuthHeaders(),
      });

      console.log('🔍 DEBUG: Wardrobe API response status:', response.status);
      
      if (!response.ok) {
        console.log('🔍 DEBUG: Wardrobe API response not ok:', {
          status: response.status,
          statusText: response.statusText,
          url: response.url
        });
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Access denied. You do not have permission to view this wardrobe.');
        } else if (response.status === 404) {
          throw new Error('Wardrobe not found.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }

      const data = await response.json();
      console.log('🔍 DEBUG: Wardrobe data received:', data);
      
      if (data.items && Array.isArray(data.items)) {
        return data.items;
      } else if (Array.isArray(data)) {
        return data;
      } else {
        console.warn('🔍 DEBUG: Unexpected data format:', data);
        return [];
      }
    } catch (error) {
      console.error('Error fetching wardrobe items:', error);
      throw error;
    }
  }

  static async addWardrobeItem(itemData: Omit<ClothingItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<ClothingItem> {
    try {
      const headers = await this.getAuthHeaders();
      
      // Transform frontend data to backend format
      const backendItem = {
        name: itemData.name,
        category: itemData.type, // Map type to category
        color: itemData.color,
        image_url: itemData.imageUrl, // Map imageUrl to image_url
        style: itemData.style,
        season: itemData.season,
        occasion: itemData.occasion,
        wear_count: itemData.wearCount, // Map wearCount to wear_count
        favorite: itemData.favorite,
        last_worn: itemData.lastWorn?.toISOString(),
      };
      
      const response = await fetch(`${API_BASE_URL}/api/wardrobe/add`, {
        method: 'POST',
        headers,
        body: JSON.stringify(backendItem),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to add wardrobe item');
      }

      return data.item;
    } catch (error) {
      console.error('Error adding wardrobe item:', error);
      throw error;
    }
  }

  static async updateWardrobeItem(id: string, updates: Partial<ClothingItem>): Promise<void> {
    try {
      const headers = await this.getAuthHeaders();
      
      // Transform frontend updates to backend format
      const backendUpdates: any = {};
      if (updates.name !== undefined) backendUpdates.name = updates.name;
      if (updates.type !== undefined) backendUpdates.category = updates.type; // Map type to category
      if (updates.color !== undefined) backendUpdates.color = updates.color;
      if (updates.imageUrl !== undefined) backendUpdates.image_url = updates.imageUrl; // Map imageUrl to image_url
      if (updates.style !== undefined) backendUpdates.style = updates.style;
      if (updates.season !== undefined) backendUpdates.season = updates.season;
      if (updates.occasion !== undefined) backendUpdates.occasion = updates.occasion;
      if (updates.wearCount !== undefined) backendUpdates.wear_count = updates.wearCount; // Map wearCount to wear_count
      if (updates.favorite !== undefined) backendUpdates.favorite = updates.favorite;
      if (updates.lastWorn !== undefined) backendUpdates.last_worn = updates.lastWorn?.toISOString();
      
      const response = await fetch(`${API_BASE_URL}/api/wardrobe/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(backendUpdates),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to update wardrobe item');
      }
    } catch (error) {
      console.error('Error updating wardrobe item:', error);
      throw error;
    }
  }

  static async deleteWardrobeItem(id: string): Promise<void> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${API_BASE_URL}/api/wardrobe/${id}`, {
        method: 'DELETE',
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to delete wardrobe item');
      }
    } catch (error) {
      console.error('Error deleting wardrobe item:', error);
      throw error;
    }
  }

  static async toggleFavorite(id: string, favorite: boolean): Promise<void> {
    try {
      console.log(`🔍 [WardrobeService] Toggling favorite for item ${id} to ${favorite}`);
      
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${API_BASE_URL}/api/wardrobe/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ favorite }),
      });

      console.log(`🔍 [WardrobeService] Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`🔍 [WardrobeService] Error response: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(`🔍 [WardrobeService] Response data:`, data);
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to toggle favorite');
      }
      
      console.log(`✅ [WardrobeService] Successfully toggled favorite for item ${id}`);
    } catch (error) {
      console.error('Error toggling favorite:', error);
      throw error;
    }
  }

  static async incrementWearCount(id: string): Promise<void> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${API_BASE_URL}/api/wardrobe/${id}/increment-wear`, {
        method: 'POST',
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to increment wear count');
      }
    } catch (error) {
      console.error('Error incrementing wear count:', error);
      throw error;
    }
  }

  // Method to check if the service is available
  static async isServiceAvailable(): Promise<boolean> {
    try {
      const isBackendAvailable = await this.checkBackendConnection();
      if (!isBackendAvailable) return false;
      
      // Try to access the wardrobe endpoint
      const response = await fetch(`${API_BASE_URL}/api/wardrobe/`, {
        method: 'GET',
        headers: await this.getAuthHeaders(),
      });
      
      return response.status !== 404; // 404 means endpoint not found
    } catch (error) {
      return false;
    }
  }
}
