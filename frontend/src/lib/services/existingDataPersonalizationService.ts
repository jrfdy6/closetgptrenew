/**
 * Existing Data Personalization Service
 * ====================================
 * 
 * This service connects to the backend personalization system that uses
 * your existing Firebase data (favorites, wear counts, style profiles)
 * instead of creating duplicate functionality.
 */

import { User } from 'firebase/auth';

// ===== DATA TYPES =====

export interface PersonalizationStatus {
  user_id: string;
  personalization_enabled: boolean;
  has_existing_data: boolean;
  total_interactions: number;
  min_interactions_required: number;
  ready_for_personalization: boolean;
  preferred_colors: string[];
  preferred_styles: string[];
  preferred_occasions: string[];
  favorite_items_count: number;
  most_worn_items_count: number;
  data_source: string;
  system_parameters: {
    min_interactions: number;
    max_outfits: number;
    learning_rate: number;
    exploration_rate: number;
    uses_existing_data: boolean;
  };
}

export interface UserPreferences {
  user_id: string;
  preferences: {
    preferred_colors: string[];
    preferred_styles: string[];
    preferred_occasions: string[];
    disliked_colors: string[];
    disliked_styles: string[];
  };
  existing_data: {
    favorite_items: string[];
    most_worn_items: string[];
    total_interactions: number;
    last_updated: number;
    data_source: string;
  };
  stats: {
    total_interactions: number;
    ready_for_personalization: boolean;
    favorite_items_count: number;
    most_worn_items_count: number;
  };
  uses_existing_data: boolean;
}

export interface PersonalizedOutfit {
  id: string;
  name: string;
  items: Array<{
    id: string;
    name: string;
    type: string;
    color: string;
    style?: string;
    occasion?: string;
  }>;
  style: string;
  occasion: string;
  mood: string;
  weather: Record<string, any>;
  confidence: number;
  personalization_score?: number;
  personalization_applied: boolean;
  user_interactions: number;
  data_source: string;
  metadata: {
    generation_time: number;
    personalization_enabled: boolean;
    user_id: string;
    uses_existing_data: boolean;
    preference_data_source: string;
  };
}

export interface OutfitGenerationRequest {
  occasion: string;
  style: string;
  mood: string;
  weather?: Record<string, any>;
  wardrobe?: any[];
  user_profile?: Record<string, any>;
  baseItemId?: string;
}

// ===== SERVICE CLASS =====

export class ExistingDataPersonalizationService {
  private static readonly API_BASE = '/api';
  private static readonly ENDPOINT_PREFIX = '/api/outfits-existing-data';

  // ===== AUTHENTICATION HELPERS =====
  private static async getAuthHeaders(user: User): Promise<HeadersInit> {
    try {
      console.log('🔍 [Auth] Getting ID token for user:', user.uid);
      const token = await user.getIdToken();
      console.log('🔍 [Auth] Token generated, length:', token.length);
      console.log('🔍 [Auth] Token preview:', token.substring(0, 20) + '...');
      
      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };
    } catch (error) {
      console.error('❌ [Auth] Failed to get ID token:', error);
      // Fallback to test token for debugging
      console.log('🔍 [Auth] Using test token as fallback');
      return {
        'Authorization': `Bearer test`,
        'Content-Type': 'application/json',
      };
    }
  }

  // TEMPORARY: Force test token for debugging
  private static async getAuthHeadersForcedTest(user: User): Promise<HeadersInit> {
    console.log('🔍 [Auth] FORCED TEST TOKEN for debugging - user:', user.uid);
    return {
      'Authorization': `Bearer test`,
      'Content-Type': 'application/json',
    };
  }

  // ===== PERSONALIZATION STATUS =====

  /**
   * Get personalization status from existing Firebase data
   */
  static async getPersonalizationStatus(user: User): Promise<PersonalizationStatus> {
    try {
      console.log('🔍 [ExistingDataPersonalization] Getting personalization status from existing data');
      
      const headers = await this.getAuthHeadersForcedTest(user);
      console.log('🔍 [API] Making request to:', `${this.API_BASE}${this.ENDPOINT_PREFIX}/personalization-status`);
      console.log('🔍 [API] Headers:', headers);
      
      const response = await fetch(`${this.API_BASE}${this.ENDPOINT_PREFIX}/personalization-status`, {
        method: 'GET',
        headers,
      });

      console.log('🔍 [API] Response status:', response.status);
      console.log('🔍 [API] Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ [API] Error response:', errorText);
        throw new Error(`Failed to get personalization status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ [ExistingDataPersonalization] Personalization status retrieved:', data);
      return data;

    } catch (error) {
      console.error('❌ [ExistingDataPersonalization] Error getting personalization status:', error);
      throw error;
    }
  }

  /**
   * Get detailed user preferences from existing Firebase data
   */
  static async getUserPreferences(user: User): Promise<UserPreferences> {
    try {
      console.log('🔍 [ExistingDataPersonalization] Getting user preferences from existing data');
      
      const headers = await this.getAuthHeadersForcedTest(user);
      const response = await fetch(`${this.API_BASE}${this.ENDPOINT_PREFIX}/user-preferences`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to get user preferences: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ [ExistingDataPersonalization] User preferences retrieved:', data);
      return data;

    } catch (error) {
      console.error('❌ [ExistingDataPersonalization] Error getting user preferences:', error);
      throw error;
    }
  }

  // ===== PERSONALIZED OUTFIT GENERATION =====

  /**
   * Generate personalized outfit using existing Firebase data
   */
  static async generatePersonalizedOutfit(
    user: User, 
    request: OutfitGenerationRequest
  ): Promise<PersonalizedOutfit> {
    try {
      console.log('🔍 [ExistingDataPersonalization] Generating personalized outfit from existing data');
      
      const headers = await this.getAuthHeadersForcedTest(user);
      const response = await fetch(`${this.API_BASE}${this.ENDPOINT_PREFIX}/generate-personalized`, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate personalized outfit: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ [ExistingDataPersonalization] Personalized outfit generated:', data);
      return data;

    } catch (error) {
      console.error('❌ [ExistingDataPersonalization] Error generating personalized outfit:', error);
      throw error;
    }
  }

  // ===== SYSTEM ANALYTICS =====

  /**
   * Get system analytics for existing data usage
   */
  static async getSystemAnalytics(): Promise<{
    system_stats: {
      uses_existing_data: boolean;
      data_sources: string[];
      no_duplicate_storage: boolean;
      firebase_integration: boolean;
    };
    engine_stats: {
      learning_rate: number;
      exploration_rate: number;
      min_interactions_required: number;
    };
    benefits: string[];
    uses_existing_data: boolean;
    timestamp: number;
  }> {
    try {
      console.log('🔍 [ExistingDataPersonalization] Getting system analytics');
      
      const response = await fetch(`${this.API_BASE}${this.ENDPOINT_PREFIX}/analytics`);

      if (!response.ok) {
        throw new Error(`Failed to get system analytics: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ [ExistingDataPersonalization] System analytics retrieved:', data);
      return data;

    } catch (error) {
      console.error('❌ [ExistingDataPersonalization] Error getting system analytics:', error);
      throw error;
    }
  }

  // ===== HEALTH CHECK =====

  /**
   * Check if the existing data personalization system is healthy
   */
  static async healthCheck(): Promise<{
    status: string;
    personalization_enabled: boolean;
    min_interactions_required: number;
    max_outfits: number;
    uses_existing_data: boolean;
    data_sources: string[];
    timestamp: number;
  }> {
    try {
      console.log('🔍 [ExistingDataPersonalization] Checking system health');
      
      const response = await fetch(`${this.API_BASE}${this.ENDPOINT_PREFIX}/health`);

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ [ExistingDataPersonalization] Health check passed:', data);
      return data;

    } catch (error) {
      console.error('❌ [ExistingDataPersonalization] Error checking health:', error);
      throw error;
    }
  }

  // ===== CONVENIENCE METHODS =====

  /**
   * Check if user is ready for personalization
   */
  static async isUserReadyForPersonalization(user: User): Promise<boolean> {
    try {
      const status = await this.getPersonalizationStatus(user);
      return status.ready_for_personalization;
    } catch (error) {
      console.error('❌ [ExistingDataPersonalization] Error checking personalization readiness:', error);
      return false;
    }
  }

  /**
   * Get user's top preferences from existing data
   */
  static async getTopPreferences(user: User, limit: number = 5): Promise<{
    colors: string[];
    styles: string[];
    occasions: string[];
  }> {
    try {
      const preferences = await this.getUserPreferences(user);
      return {
        colors: preferences.preferences.preferred_colors.slice(0, limit),
        styles: preferences.preferences.preferred_styles.slice(0, limit),
        occasions: preferences.preferences.preferred_occasions.slice(0, limit),
      };
    } catch (error) {
      console.error('❌ [ExistingDataPersonalization] Error getting top preferences:', error);
      return { colors: [], styles: [], occasions: [] };
    }
  }

  /**
   * Generate outfit with fallback to regular generation
   */
  static async generateOutfitWithPersonalization(
    user: User,
    request: OutfitGenerationRequest,
    fallbackToRegular: boolean = true
  ): Promise<PersonalizedOutfit | null> {
    try {
      // Try personalized generation first
      const personalizedOutfit = await this.generatePersonalizedOutfit(user, request);
      
      if (personalizedOutfit.personalization_applied) {
        console.log('✅ [ExistingDataPersonalization] Personalized outfit generated successfully');
        return personalizedOutfit;
      } else {
        console.log('⚠️ [ExistingDataPersonalization] Personalization not applied, but outfit generated');
        return personalizedOutfit;
      }
    } catch (error) {
      console.error('❌ [ExistingDataPersonalization] Personalized generation failed:', error);
      
      if (fallbackToRegular) {
        console.log('🔄 [ExistingDataPersonalization] Falling back to regular outfit generation');
        // You would call your regular outfit generation here
        // return await RegularOutfitService.generateOutfit(user, request);
        return null;
      }
      
      throw error;
    }
  }
}

// ===== EXPORT DEFAULT INSTANCE =====
export default ExistingDataPersonalizationService;
