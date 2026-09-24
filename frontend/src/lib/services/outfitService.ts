import { db } from '@/lib/firebase/config';
import { collection, query, where, orderBy, limit, getDocs, doc, getDoc, Timestamp } from 'firebase/firestore';
import { User } from 'firebase/auth';

// ===== DATA TYPES =====
export interface OutfitItem {
  id: string;
  name: string;
  category: string;
  style: string;
  color: string;
  imageUrl?: string;
  user_id: string; // Changed from userId to user_id to match backend
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
  description?: string;
  notes?: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  user_id: string; // Changed from userId to user_id to match backend
  isFavorite?: boolean;
  wearCount?: number;
  lastWorn?: Timestamp;
}

export interface OutfitCreate {
  name: string;
  occasion: string;
  style: string;
  mood?: string;
  items: OutfitItem[];
  description?: string;
  notes?: string;
  user_id: string;
}

export interface OutfitUpdate {
  name?: string;
  occasion?: string;
  style?: string;
  mood?: string;
  items?: OutfitItem[];
  description?: string;
  notes?: string;
  isFavorite?: boolean;
  updatedAt?: Timestamp;
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
      
      // Build query - check both possible user ID field names
      let outfitsQuery = query(
        collection(db, this.COLLECTION_NAME),
        where('user_id', '==', user.uid)
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
      
      // Verify ownership - check both userId and user_id for compatibility
      const ownerId = outfitData.userId || outfitData.user_id;
      if (ownerId !== user.uid) {
        console.warn(`🚫 [OutfitService] User ${user.uid} attempted to access outfit ${outfitId} owned by ${ownerId}`);
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
  static async createOutfit(user: User, outfitData: Omit<Outfit, 'id' | 'createdAt' | 'updatedAt' | 'user_id'>): Promise<Outfit> {
    const { default: service } = await import('./outfitService_proper');
    return service.createOutfit({ ...outfitData, user_id: user.uid }, await user.getIdToken());
  }

  static async updateOutfit(user: User, outfitId: string, updates: Partial<Outfit>): Promise<void> {
    const { default: service } = await import('./outfitService_proper');
    await service.updateOutfit(outfitId, updates, await user.getIdToken());
  }

  static async deleteOutfit(user: User, outfitId: string): Promise<void> {
    const { default: service } = await import('./outfitService_proper');
    await service.deleteOutfit(outfitId, await user.getIdToken());
  }

  static async markOutfitAsWorn(user: User, outfitId: string): Promise<void> {
    const [{ default: service }, { publishWearReceipt }] = await Promise.all([
      import('./outfitService_proper'), import('@/lib/wardrobeActivity'),
    ]);
    const receipt = await service.markOutfitAsWorn(outfitId, await user.getIdToken());
    publishWearReceipt(user.uid, receipt);
    if (receipt.undone) throw new Error('This wear was undone. Choose Wear again to record a new wear.');
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
      
      const { default: service } = await import('./outfitService_proper');
      await service.setOutfitFavorite(outfitId, newFavoriteStatus, await user.getIdToken());
      
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
        where('user_id', '==', user.uid)
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



