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
      // Check if backend is accessible
      const isBackendAvailable = await this.checkBackendConnection();
      if (!isBackendAvailable) {
        throw new Error('Backend service is not available. Please try again later or contact support.');
      }

      const headers = await this.getAuthHeaders();
      const authHeader = (headers as Record<string, string>).Authorization;
      console.log('🔍 DEBUG: Auth headers - hasAuth:', !!authHeader);
      console.log('🔍 DEBUG: Auth headers - authType:', authHeader?.split(' ')[0]);
      console.log('🔍 DEBUG: Auth headers - tokenLength:', authHeader?.split(' ')[1]?.length || 0);
      console.log('🔍 DEBUG: Full headers object:', headers);
      
      console.log('🔍 DEBUG: About to fetch from:', `${API_BASE_URL}/api/wardrobe`);
      let response;
      try {
        response = await fetch(`${API_BASE_URL}/api/wardrobe`, {
          method: 'GET',
          headers,
        });
        console.log('🔍 DEBUG: Fetch completed successfully, status:', response.status);
        console.log('🔍 DEBUG: Response headers:', Object.fromEntries(response.headers.entries()));
      } catch (fetchError) {
        console.error('🔍 DEBUG: Fetch failed with error:', fetchError);
        throw new Error(`Network error: ${fetchError instanceof Error ? fetchError.message : 'Unknown fetch error'}`);
      }

      if (!response.ok) {
        console.error('🔍 DEBUG: Wardrobe API response not ok:', {
          status: response.status,
          statusText: response.statusText,
          url: response.url
        });
        
        if (response.status === 404) {
          throw new Error('Wardrobe service not found. The backend may need to be updated.');
        } else if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Access denied. You may not have permission to view this wardrobe.');
        } else if (response.status === 500) {
          throw new Error('Backend server error. Please try again later.');
        }
        
        throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
      }

      console.log('🔍 DEBUG: About to parse response as JSON...');
      const data: WardrobeResponse = await response.json();
      console.log('🔍 DEBUG: Parsed response data:', data);
      console.log('🔍 DEBUG: Response data keys:', Object.keys(data));
      console.log('🔍 DEBUG: Response data type:', typeof data);
      console.log('🔍 DEBUG: Actual key names:', JSON.stringify(Object.keys(data)));
      console.log('🔍 DEBUG: Success value:', (data as any).success);
      console.log('🔍 DEBUG: Error value:', (data as any).error);
      
      // Check if backend returned an error response
      if (data.success === false) {
        const errorMessage = (data as any).error || 'Backend returned an error';
        console.error('🔍 DEBUG: Backend error response:', errorMessage);
        throw new Error(`Backend error: ${errorMessage}`);
      }
      
      // Check if we have the expected data structure
      if (!data.items || !Array.isArray(data.items)) {
        console.error('🔍 DEBUG: Response data does not have items array');
        console.error('🔍 DEBUG: Available keys:', Object.keys(data));
        console.error('🔍 DEBUG: Actual key names:', JSON.stringify(Object.keys(data)));
        throw new Error('Invalid response format from backend');
      }
      
      console.log('🔍 DEBUG: Successfully parsed wardrobe response with', data.items.length, 'items');

      // Transform the backend data to match frontend ClothingItem interface
      return data.items.map(item => ({
        id: item.id,
        name: item.name || 'Unknown Item',
        type: item.type || 'unknown',
        color: item.color || 'unknown',
        imageUrl: item.imageUrl || '/placeholder.png',
        wearCount: item.wearCount || 0,
        favorite: item.favorite || false,
        style: Array.isArray(item.style) ? item.style : [],
        season: Array.isArray(item.season) ? item.season : [],
        occasion: Array.isArray(item.occasion) ? item.occasion : [],
        lastWorn: item.lastWorn ? new Date(item.lastWorn) : undefined,
        userId: item.userId,
        createdAt: new Date(item.createdAt),
        updatedAt: new Date(item.updatedAt),
      }));
    } catch (error) {
      console.error('Error fetching wardrobe items:', error);
      
      // Provide more helpful error messages
      if (error instanceof Error) {
        if (error.message.includes('Backend service is not available')) {
          throw new Error('Unable to connect to wardrobe service. Please check your internet connection and try again.');
        } else if (error.message.includes('Wardrobe service not found')) {
          throw new Error('Wardrobe service is currently being updated. Please try again in a few minutes.');
        } else if (error.message.includes('User not authenticated')) {
          throw new Error('Please sign in to view your wardrobe.');
        }
      }
      
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
      const headers = await this.getAuthHeaders();
      const response = await fetch(`${API_BASE_URL}/api/wardrobe/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ favorite }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to toggle favorite');
      }
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
        headers: { 'Authorization': 'Bearer test' }, // Use test token for availability check
      });
      
      return response.status !== 404; // 404 means endpoint not found
    } catch (error) {
      return false;
    }
  }
}
