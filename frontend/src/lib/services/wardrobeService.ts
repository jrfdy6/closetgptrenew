import { ClothingItem, WardrobeFilters } from '@/lib/hooks/useWardrobe';

// Use Next.js API routes instead of direct backend calls
const API_BASE_URL = '/api';

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
  /**
   * Transform backend item structure (nested metadata) to frontend structure (flat fields)
   * Backend: item.metadata.visualAttributes.material
   * Frontend: item.material
   */
  private static transformBackendItem(backendItem: any): ClothingItem {
    const metadata = backendItem.metadata || {};
    const visualAttributes = metadata.visualAttributes || {};
    
    return {
      ...backendItem,
      // Extract nested fields to root level for frontend display
      description: metadata.naturalDescription || backendItem.description || '',
      material: visualAttributes.material ? [visualAttributes.material] : (backendItem.material || []),
      sleeveLength: visualAttributes.sleeveLength || backendItem.sleeveLength || '',
      fit: visualAttributes.fit || backendItem.fit || '',
      neckline: visualAttributes.neckline || backendItem.neckline || '',
      length: visualAttributes.length || backendItem.length || '',
      // New fields from Phase 1
      transparency: visualAttributes.transparency || '',
      collarType: visualAttributes.collarType || '',
      embellishments: visualAttributes.embellishments || '',
      printSpecificity: visualAttributes.printSpecificity || '',
      rise: visualAttributes.rise || '',
      legOpening: visualAttributes.legOpening || '',
      heelHeight: visualAttributes.heelHeight || '',
      statementLevel: visualAttributes.statementLevel || 0,
      // Keep the original metadata for backend updates
      metadata: backendItem.metadata,
    };
  }

  /**
   * Transform frontend updates (flat fields) to backend structure (nested metadata)
   * Frontend: { material: ['cotton'], description: 'A nice shirt' }
   * Backend: { metadata: { visualAttributes: { material: 'cotton' }, naturalDescription: 'A nice shirt' } }
   */
  private static transformFrontendUpdates(frontendUpdates: Partial<ClothingItem>): any {
    const backendUpdates: any = {};
    
    // Regular fields that map directly
    if (frontendUpdates.name !== undefined) backendUpdates.name = frontendUpdates.name;
    if (frontendUpdates.type !== undefined) backendUpdates.type = frontendUpdates.type;
    if (frontendUpdates.color !== undefined) backendUpdates.color = frontendUpdates.color;
    if (frontendUpdates.style !== undefined) backendUpdates.style = frontendUpdates.style;
    if (frontendUpdates.season !== undefined) backendUpdates.season = frontendUpdates.season;
    if (frontendUpdates.occasion !== undefined) backendUpdates.occasion = frontendUpdates.occasion;
    if (frontendUpdates.brand !== undefined) backendUpdates.brand = frontendUpdates.brand;
    if (frontendUpdates.size !== undefined) backendUpdates.size = frontendUpdates.size;
    
    // Metadata fields that need to be nested
    const hasMetadataUpdates = 
      frontendUpdates.description !== undefined ||
      frontendUpdates.material !== undefined ||
      frontendUpdates.sleeveLength !== undefined ||
      frontendUpdates.fit !== undefined ||
      frontendUpdates.neckline !== undefined ||
      frontendUpdates.length !== undefined ||
      frontendUpdates.transparency !== undefined ||
      frontendUpdates.collarType !== undefined ||
      frontendUpdates.embellishments !== undefined ||
      frontendUpdates.printSpecificity !== undefined ||
      frontendUpdates.rise !== undefined ||
      frontendUpdates.legOpening !== undefined ||
      frontendUpdates.heelHeight !== undefined ||
      frontendUpdates.statementLevel !== undefined;
    
    if (hasMetadataUpdates) {
      backendUpdates.metadata = backendUpdates.metadata || {};
      
      // Natural description
      if (frontendUpdates.description !== undefined) {
        backendUpdates.metadata.naturalDescription = frontendUpdates.description;
      }
      
      // Visual attributes
      if (frontendUpdates.material !== undefined ||
          frontendUpdates.sleeveLength !== undefined ||
          frontendUpdates.fit !== undefined ||
          frontendUpdates.neckline !== undefined ||
          frontendUpdates.length !== undefined ||
          frontendUpdates.transparency !== undefined ||
          frontendUpdates.collarType !== undefined ||
          frontendUpdates.embellishments !== undefined ||
          frontendUpdates.printSpecificity !== undefined ||
          frontendUpdates.rise !== undefined ||
          frontendUpdates.legOpening !== undefined ||
          frontendUpdates.heelHeight !== undefined ||
          frontendUpdates.statementLevel !== undefined) {
        
        backendUpdates.metadata.visualAttributes = backendUpdates.metadata.visualAttributes || {};
        
        if (frontendUpdates.material !== undefined) {
          // Convert array to single string (backend expects string)
          backendUpdates.metadata.visualAttributes.material = 
            Array.isArray(frontendUpdates.material) ? frontendUpdates.material[0] : frontendUpdates.material;
        }
        if (frontendUpdates.sleeveLength !== undefined) {
          backendUpdates.metadata.visualAttributes.sleeveLength = frontendUpdates.sleeveLength;
        }
        if (frontendUpdates.fit !== undefined) {
          backendUpdates.metadata.visualAttributes.fit = frontendUpdates.fit;
        }
        if (frontendUpdates.neckline !== undefined) {
          backendUpdates.metadata.visualAttributes.neckline = frontendUpdates.neckline;
        }
        if (frontendUpdates.length !== undefined) {
          backendUpdates.metadata.visualAttributes.length = frontendUpdates.length;
        }
        // New fields from Phase 1
        if (frontendUpdates.transparency !== undefined) {
          backendUpdates.metadata.visualAttributes.transparency = frontendUpdates.transparency;
        }
        if (frontendUpdates.collarType !== undefined) {
          backendUpdates.metadata.visualAttributes.collarType = frontendUpdates.collarType;
        }
        if (frontendUpdates.embellishments !== undefined) {
          backendUpdates.metadata.visualAttributes.embellishments = frontendUpdates.embellishments;
        }
        if (frontendUpdates.printSpecificity !== undefined) {
          backendUpdates.metadata.visualAttributes.printSpecificity = frontendUpdates.printSpecificity;
        }
        if (frontendUpdates.rise !== undefined) {
          backendUpdates.metadata.visualAttributes.rise = frontendUpdates.rise;
        }
        if (frontendUpdates.legOpening !== undefined) {
          backendUpdates.metadata.visualAttributes.legOpening = frontendUpdates.legOpening;
        }
        if (frontendUpdates.heelHeight !== undefined) {
          backendUpdates.metadata.visualAttributes.heelHeight = frontendUpdates.heelHeight;
        }
        if (frontendUpdates.statementLevel !== undefined) {
          backendUpdates.metadata.visualAttributes.statementLevel = frontendUpdates.statementLevel;
        }
      }
    }
    
    return backendUpdates;
  }

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
      // Trigger Vercel deployment - Firebase auth fix - Force rebuild
      
      // Use Next.js API route as proxy to avoid Railway HTTPS redirect issues
      const fullUrl = '/api/wardrobe';
      console.log('🔍 DEBUG: Using Next.js API route as proxy:', fullUrl);
      console.log('🔍 DEBUG: This avoids Railway HTTPS->HTTP redirect issues');
      
      const response = await fetch(fullUrl, {
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
      
      let items: any[] = [];
      if (data.items && Array.isArray(data.items)) {
        items = data.items;
      } else if (Array.isArray(data)) {
        items = data;
      } else {
        console.warn('🔍 DEBUG: Unexpected data format:', data);
        return [];
      }
      
      // Transform backend items to frontend structure (flatten nested metadata)
      const transformedItems = items.map(item => this.transformBackendItem(item));
      console.log('🔍 DEBUG: Transformed items with flattened metadata:', transformedItems.slice(0, 2));
      
      // VERIFICATION - Check first item has material and description
      if (transformedItems.length > 0) {
        const firstItem = transformedItems[0];
        console.log('✅ TRANSFORMATION VERIFICATION (first item):');
        console.log(`  material: ${firstItem.material}`);
        console.log(`  description: ${firstItem.description}`);
        console.log(`  neckline: ${firstItem.neckline}`);
        console.log(`  Source: metadata.visualAttributes.material = ${firstItem.metadata?.visualAttributes?.material}`);
      }
      
      return transformedItems;
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
      
      // Transform frontend updates (flat fields) to backend format (nested metadata)
      const backendUpdates = this.transformFrontendUpdates(updates);
      
      console.log('🔄 Transforming frontend updates to backend format:', {
        frontendUpdates: updates,
        backendUpdates: backendUpdates
      });
      
      const response = await fetch(`${API_BASE_URL}/wardrobe/${id}`, {
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
      console.log(`🔍 [WardrobeService] Deleting wardrobe item ${id}`);
      
      // Use Next.js API route as proxy to avoid Railway HTTPS redirect issues
      const fullUrl = `/api/wardrobe/${id}`;
      console.log('🔍 DEBUG: Using Next.js API route as proxy:', fullUrl);
      
      const response = await fetch(fullUrl, {
        method: 'DELETE',
        headers: await this.getAuthHeaders(),
      });

      console.log('🔍 DEBUG: Wardrobe DELETE API response status:', response.status);
      
      if (!response.ok) {
        console.log('🔍 DEBUG: Wardrobe DELETE API response not ok:', {
          status: response.status,
          statusText: response.statusText,
          url: response.url
        });
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Not authorized to delete this item.');
        } else if (response.status === 404) {
          throw new Error('Wardrobe item not found.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }

      const data = await response.json();
      console.log('🔍 DEBUG: Wardrobe DELETE response received:', data);
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to delete wardrobe item');
      }
      
      console.log(`✅ [WardrobeService] Successfully deleted wardrobe item ${id}`);
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
