/**
 * useExistingDataPersonalization Hook
 * ===================================
 * 
 * React hook for integrating the existing data personalization system
 * with your frontend components.
 */

import { useState, useEffect, useCallback } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import ExistingDataPersonalizationService, { 
  PersonalizationStatus, 
  UserPreferences, 
  PersonalizedOutfit,
  OutfitGenerationRequest 
} from '@/lib/services/existingDataPersonalizationService';

export interface UsePersonalizationReturn {
  // Status
  personalizationStatus: PersonalizationStatus | null;
  userPreferences: UserPreferences | null;
  isLoading: boolean;
  error: string | null;
  
  // Capabilities
  isReadyForPersonalization: boolean;
  hasExistingData: boolean;
  totalInteractions: number;
  
  // Preferences
  topColors: string[];
  topStyles: string[];
  topOccasions: string[];
  favoriteItemsCount: number;
  mostWornItemsCount: number;
  
  // Actions
  generatePersonalizedOutfit: (request: OutfitGenerationRequest) => Promise<PersonalizedOutfit | null>;
  refreshPersonalizationData: () => Promise<void>;
  checkHealth: () => Promise<boolean>;
  
  // System info
  dataSource: string;
  usesExistingData: boolean;
}

export function useExistingDataPersonalization(): UsePersonalizationReturn {
  const { user } = useFirebase();
  
  // State
  const [personalizationStatus, setPersonalizationStatus] = useState<PersonalizationStatus | null>(null);
  const [userPreferences, setUserPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load personalization data when user changes
  useEffect(() => {
    if (user) {
      loadPersonalizationData();
    } else {
      // Reset state when user logs out
      setPersonalizationStatus(null);
      setUserPreferences(null);
      setError(null);
    }
  }, [user]);

  const loadPersonalizationData = useCallback(async () => {
    if (!user) return;

    try {
      setIsLoading(true);
      setError(null);

      // Load both status and preferences in parallel
      const [status, preferences] = await Promise.all([
        ExistingDataPersonalizationService.getPersonalizationStatus(user),
        ExistingDataPersonalizationService.getUserPreferences(user)
      ]);

      setPersonalizationStatus(status);
      setUserPreferences(preferences);
      
      console.log('✅ [useExistingDataPersonalization] Personalization data loaded successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load personalization data';
      setError(errorMessage);
      console.error('❌ [useExistingDataPersonalization] Error loading personalization data:', err);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const generatePersonalizedOutfit = useCallback(async (request: OutfitGenerationRequest): Promise<PersonalizedOutfit | null> => {
    if (!user) {
      setError('User not authenticated');
      return null;
    }

    try {
      setIsLoading(true);
      setError(null);

      const outfit = await ExistingDataPersonalizationService.generatePersonalizedOutfit(user, request);
      
      console.log('✅ [useExistingDataPersonalization] Personalized outfit generated:', outfit);
      return outfit;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate personalized outfit';
      setError(errorMessage);
      console.error('❌ [useExistingDataPersonalization] Error generating personalized outfit:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const refreshPersonalizationData = useCallback(async () => {
    await loadPersonalizationData();
  }, [loadPersonalizationData]);

  const checkHealth = useCallback(async (): Promise<boolean> => {
    try {
      const health = await ExistingDataPersonalizationService.healthCheck();
      return health.status === 'healthy';
    } catch (err) {
      console.error('❌ [useExistingDataPersonalization] Health check failed:', err);
      return false;
    }
  }, []);

  // Computed values
  const isReadyForPersonalization = personalizationStatus?.ready_for_personalization ?? false;
  const hasExistingData = personalizationStatus?.has_existing_data ?? false;
  const totalInteractions = personalizationStatus?.total_interactions ?? 0;
  
  const topColors = userPreferences?.preferences.preferred_colors.slice(0, 5) ?? [];
  const topStyles = userPreferences?.preferences.preferred_styles.slice(0, 5) ?? [];
  const topOccasions = userPreferences?.preferences.preferred_occasions.slice(0, 5) ?? [];
  const favoriteItemsCount = personalizationStatus?.favorite_items_count ?? 0;
  const mostWornItemsCount = personalizationStatus?.most_worn_items_count ?? 0;
  
  const dataSource = personalizationStatus?.data_source ?? 'unknown';
  const usesExistingData = personalizationStatus?.system_parameters?.uses_existing_data ?? false;

  return {
    // Status
    personalizationStatus,
    userPreferences,
    isLoading,
    error,
    
    // Capabilities
    isReadyForPersonalization,
    hasExistingData,
    totalInteractions,
    
    // Preferences
    topColors,
    topStyles,
    topOccasions,
    favoriteItemsCount,
    mostWornItemsCount,
    
    // Actions
    generatePersonalizedOutfit,
    refreshPersonalizationData,
    checkHealth,
    
    // System info
    dataSource,
    usesExistingData,
  };
}

export default useExistingDataPersonalization;
