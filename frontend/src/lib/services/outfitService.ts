import { db } from '@/lib/firebase/config';
import { collection, query, where, orderBy, limit, getDocs, doc, getDoc, addDoc, updateDoc, deleteDoc, Timestamp } from 'firebase/firestore';
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
  createdAt: Timestamp;
  updatedAt: Timestamp;
  userId: string;
  isFavorite?: boolean;
  wearCount?: number;
  lastWorn?: Timestamp;
}

export interface OutfitFilters {
  occasion?: string;
  style?: string;
  mood?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
  limit?: number;
  offset?: number;
}

export interface OutfitResponse {
  success: boolean;
  data?: Outfit | Outfit[];
  error?: string;
  message?: string;
}

// ===== CORE SERVICE CLASS =====
export class OutfitService {
  private static readonly COLLECTION_NAME = 'outfits';
  private static readonly WARDROBE_COLLECTION = 'wardrobe';

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

  // ===== DIRECT FIRESTORE OPERATIONS =====
  
  /**
   * Get user's outfits directly from Firestore
   * This bypasses the broken backend routing and queries the actual data location
   */
  static async getUserOutfits(user: User, filters: OutfitFilters = {}): Promise<Outfit[]> {
    try {
      console.log('🔍 [OutfitService] Getting user outfits directly from Firestore');
      
      // Build query
      let outfitsQuery = query(
        collection(db, this.COLLECTION_NAME),
        where('userId', '==', user.uid)
      );

      // Apply filters
      if (filters.occasion) {
        outfitsQuery = query(outfitsQuery, where('occasion', '==', filters.occasion));
      }
      
      if (filters.style) {
        outfitsQuery = query(outfitsQuery, where('style', '==', filters.style));
      }

      // Apply ordering and pagination
      outfitsQuery = query(
        outfitsQuery,
        orderBy('createdAt', 'desc'),
        limit(filters.limit || 50)
      );

      // Execute query
      const querySnapshot = await getDocs(outfitsQuery);
      const outfits: Outfit[] = [];

      querySnapshot.forEach((doc) => {
        const outfitData = doc.data();
        outfits.push({
          id: doc.id,
          ...outfitData,
          createdAt: outfitData.createdAt || Timestamp.now(),
          updatedAt: outfitData.updatedAt || Timestamp.now(),
        } as Outfit);
      });

      console.log(`✅ [OutfitService] Found ${outfits.length} outfits for user ${user.uid}`);
      return outfits;

    } catch (error) {
      console.error('❌ [OutfitService] Error getting user outfits:', error);
      throw new Error('Failed to fetch outfits from database');
    }
  }

  /**
   * Get a specific outfit by ID
   */
  static async getOutfitById(user: User, outfitId: string): Promise<Outfit | null> {
    try {
      console.log(`🔍 [OutfitService] Getting outfit ${outfitId}`);
      
      const outfitDoc = await getDoc(doc(db, this.COLLECTION_NAME, outfitId));
      
      if (!outfitDoc.exists()) {
        console.log(`⚠️ [OutfitService] Outfit ${outfitId} not found`);
        return null;
      }

      const outfitData = outfitDoc.data();
      
      // Verify ownership
      if (outfitData.userId !== user.uid) {
        console.warn(`🚫 [OutfitService] User ${user.uid} attempted to access outfit ${outfitId} owned by ${outfitData.userId}`);
        throw new Error('Access denied: Outfit does not belong to user');
      }

      const outfit: Outfit = {
        id: outfitDoc.id,
        ...outfitData,
        createdAt: outfitData.createdAt || Timestamp.now(),
        updatedAt: outfitData.updatedAt || Timestamp.now(),
      } as Outfit;

      console.log(`✅ [OutfitService] Successfully retrieved outfit ${outfitId}`);
      return outfit;

    } catch (error) {
      console.error(`❌ [OutfitService] Error getting outfit ${outfitId}:`, error);
      throw error;
    }
  }

  /**
   * Create a new outfit
   */
  static async createOutfit(user: User, outfitData: Omit<Outfit, 'id' | 'createdAt' | 'updatedAt' | 'userId'>): Promise<Outfit> {
    try {
      console.log('🔍 [OutfitService] Creating new outfit');
      
      const newOutfit = {
        ...outfitData,
        userId: user.uid,
        createdAt: Timestamp.now(),
        updatedAt: Timestamp.now(),
        wearCount: 0,
        isFavorite: false,
      };

      const docRef = await addDoc(collection(db, this.COLLECTION_NAME), newOutfit);
      
      const createdOutfit: Outfit = {
        id: docRef.id,
        ...newOutfit,
      };

      console.log(`✅ [OutfitService] Successfully created outfit ${docRef.id}`);
      return createdOutfit;

    } catch (error) {
      console.error('❌ [OutfitService] Error creating outfit:', error);
      throw new Error('Failed to create outfit');
    }
  }

  /**
   * Update an existing outfit
   */
  static async updateOutfit(user: User, outfitId: string, updates: Partial<Outfit>): Promise<void> {
    try {
      console.log(`🔍 [OutfitService] Updating outfit ${outfitId}`);
      
      // Verify ownership first
      const existingOutfit = await this.getOutfitById(user, outfitId);
      if (!existingOutfit) {
        throw new Error('Outfit not found');
      }

      const updateData = {
        ...updates,
        updatedAt: Timestamp.now(),
      };

      await updateDoc(doc(db, this.COLLECTION_NAME, outfitId), updateData);
      
      console.log(`✅ [OutfitService] Successfully updated outfit ${outfitId}`);

    } catch (error) {
      console.error(`❌ [OutfitService] Error updating outfit ${outfitId}:`, error);
      throw error;
    }
  }

  /**
   * Delete an outfit
   */
  static async deleteOutfit(user: User, outfitId: string): Promise<void> {
    try {
      console.log(`🔍 [OutfitService] Deleting outfit ${outfitId}`);
      
      // Get Firebase ID token for authentication
      const token = await user.getIdToken();
      
      // Use Next.js API route as proxy to avoid Railway HTTPS redirect issues
      const fullUrl = `/api/outfits/${outfitId}`;
      console.log('🔍 DEBUG: Using Next.js API route as proxy:', fullUrl);
      
      const response = await fetch(fullUrl, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      console.log('🔍 DEBUG: Outfit DELETE API response status:', response.status);
      
      if (!response.ok) {
        console.log('🔍 DEBUG: Outfit DELETE API response not ok:', {
          status: response.status,
          statusText: response.statusText,
          url: response.url
        });
        
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Not authorized to delete this outfit.');
        } else if (response.status === 404) {
          throw new Error('Outfit not found.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }

      const data = await response.json();
      console.log('🔍 DEBUG: Outfit DELETE response received:', data);
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to delete outfit');
      }
      
      console.log(`✅ [OutfitService] Successfully deleted outfit ${outfitId}`);

    } catch (error) {
      console.error(`❌ [OutfitService] Error deleting outfit ${outfitId}:`, error);
      throw error;
    }
  }

  /**
   * Mark outfit as worn
   */
  static async markOutfitAsWorn(user: User, outfitId: string): Promise<void> {
    try {
      console.log(`🔍 [OutfitService] Marking outfit ${outfitId} as worn`);
      
      const existingOutfit = await this.getOutfitById(user, outfitId);
      if (!existingOutfit) {
        throw new Error('Outfit not found');
      }

      // 1. Update the outfit document with wear count
      const updates = {
        wearCount: (existingOutfit.wearCount || 0) + 1,
        lastWorn: Timestamp.now(),
        updatedAt: Timestamp.now(),
      };

      await updateDoc(doc(db, this.COLLECTION_NAME, outfitId), updates);
      
      // 2. Update individual wardrobe items wear counts
      if (existingOutfit.items && Array.isArray(existingOutfit.items)) {
        console.log(`🔍 [OutfitService] Updating wear counts for ${existingOutfit.items.length} wardrobe items`);
        
        const wardrobeUpdates = existingOutfit.items.map(async (item: any) => {
          if (item.id) {
            try {
              const itemRef = doc(db, 'wardrobe', item.id);
              const itemDoc = await getDoc(itemRef);
              
              if (itemDoc.exists()) {
                const itemData = itemDoc.data();
                // Verify ownership
                if (itemData.userId === user.uid) {
                  const currentWearCount = itemData.wearCount || 0;
                  await updateDoc(itemRef, {
                    wearCount: currentWearCount + 1,
                    lastWorn: currentTimestamp,
                    updatedAt: currentTimestamp
                  });
                  console.log(`✅ [OutfitService] Updated wear count for item: ${item.name || item.id}`);
                } else {
                  console.warn(`⚠️ [OutfitService] Skipping item ${item.id} - not owned by user`);
                }
              } else {
                console.warn(`⚠️ [OutfitService] Item ${item.id} not found in wardrobe`);
              }
            } catch (itemError) {
              console.error(`❌ [OutfitService] Error updating item ${item.id}:`, itemError);
              // Don't fail the whole operation if one item fails
            }
          }
        });
        
        // Wait for all wardrobe item updates to complete
        await Promise.all(wardrobeUpdates);
        console.log(`✅ [OutfitService] Completed wardrobe item wear count updates`);
      }

      // 3. Create outfit history entry for dashboard synchronization
      const historyEntry = {
        user_id: user.uid,
        outfit_id: outfitId,
        outfit_name: existingOutfit.name || 'Outfit',
        outfit_image: existingOutfit.imageUrl || '',
        date_worn: currentTimestamp,
        occasion: existingOutfit.occasion || 'Casual',
        mood: 'Comfortable', // Default mood
        weather: {},
        notes: '',
        tags: [],
        created_at: currentTimestamp,
        updated_at: currentTimestamp
      };

      // Add to outfit_history collection for dashboard sync
      await addDoc(collection(db, 'outfit_history'), historyEntry);
      
      // 4. Trigger dashboard refresh event
      window.dispatchEvent(new CustomEvent('outfitMarkedAsWorn', { 
        detail: { outfitId, outfitName: existingOutfit.name } 
      }));
      
      console.log(`✅ [OutfitService] Successfully marked outfit ${outfitId} as worn and synced with dashboard and wardrobe items`);

    } catch (error) {
      console.error(`❌ [OutfitService] Error marking outfit ${outfitId} as worn:`, error);
      throw error;
    }
  }

  /**
   * Toggle outfit favorite status
   */
  static async toggleOutfitFavorite(user: User, outfitId: string): Promise<void> {
    try {
      console.log(`🔍 [OutfitService] Toggling favorite for outfit ${outfitId}`);
      
      const existingOutfit = await this.getOutfitById(user, outfitId);
      if (!existingOutfit) {
        throw new Error('Outfit not found');
      }

      const newFavoriteStatus = !existingOutfit.isFavorite;
      
      await updateDoc(doc(db, this.COLLECTION_NAME, outfitId), {
        isFavorite: newFavoriteStatus,
        updatedAt: Timestamp.now(),
      });
      
      console.log(`✅ [OutfitService] Successfully ${newFavoriteStatus ? 'favorited' : 'unfavorited'} outfit ${outfitId}`);

    } catch (error) {
      console.error(`❌ [OutfitService] Error toggling favorite for outfit ${outfitId}:`, error);
      throw error;
    }
  }

  /**
   * Search outfits with advanced filters
   */
  static async searchOutfits(user: User, filters: OutfitFilters): Promise<Outfit[]> {
    try {
      console.log('🔍 [OutfitService] Searching outfits with filters:', filters);
      
      // Start with basic user filter
      let outfitsQuery = query(
        collection(db, this.COLLECTION_NAME),
        where('userId', '==', user.uid)
      );

      // Apply filters
      if (filters.occasion) {
        outfitsQuery = query(outfitsQuery, where('occasion', '==', filters.occasion));
      }
      
      if (filters.style) {
        outfitsQuery = query(outfitsQuery, where('style', '==', filters.style));
      }

      if (filters.mood) {
        outfitsQuery = query(outfitsQuery, where('mood', '==', filters.mood));
      }

      // Apply ordering and pagination
      outfitsQuery = query(
        outfitsQuery,
        orderBy('createdAt', 'desc'),
        limit(filters.limit || 100)
      );

      const querySnapshot = await getDocs(outfitsQuery);
      const outfits: Outfit[] = [];

      querySnapshot.forEach((doc) => {
        const outfitData = doc.data();
        outfits.push({
          id: doc.id,
          ...outfitData,
          createdAt: outfitData.createdAt || Timestamp.now(),
          updatedAt: outfitData.updatedAt || Timestamp.now(),
        } as Outfit);
      });

      // Apply date range filter if specified (client-side for now)
      let filteredOutfits = outfits;
      if (filters.dateRange) {
        filteredOutfits = outfits.filter(outfit => {
          const outfitDate = outfit.createdAt.toDate();
          return outfitDate >= filters.dateRange!.start && outfitDate <= filters.dateRange!.end;
        });
      }

      console.log(`✅ [OutfitService] Search returned ${filteredOutfits.length} outfits`);
      return filteredOutfits;

    } catch (error) {
      console.error('❌ [OutfitService] Error searching outfits:', error);
      throw new Error('Failed to search outfits');
    }
  }

  /**
   * Get outfit statistics for user
   */
  static async getOutfitStats(user: User): Promise<{
    totalOutfits: number;
    favoriteOutfits: number;
    totalWearCount: number;
    occasions: Record<string, number>;
    styles: Record<string, number>;
  }> {
    try {
      console.log('🔍 [OutfitService] Getting outfit statistics');
      
      const allOutfits = await this.getUserOutfits(user, { limit: 1000 });
      
      const stats = {
        totalOutfits: allOutfits.length,
        favoriteOutfits: allOutfits.filter(o => o.isFavorite).length,
        totalWearCount: allOutfits.reduce((sum, o) => sum + (o.wearCount || 0), 0),
        occasions: {} as Record<string, number>,
        styles: {} as Record<string, number>,
      };

      // Count occasions and styles
      allOutfits.forEach(outfit => {
        stats.occasions[outfit.occasion] = (stats.occasions[outfit.occasion] || 0) + 1;
        stats.styles[outfit.style] = (stats.styles[outfit.style] || 0) + 1;
      });

      console.log(`✅ [OutfitService] Retrieved statistics for ${stats.totalOutfits} outfits`);
      return stats;

    } catch (error) {
      console.error('❌ [OutfitService] Error getting outfit statistics:', error);
      throw new Error('Failed to get outfit statistics');
    }
  }
}

// ===== EXPORT DEFAULT INSTANCE =====
export default OutfitService;



