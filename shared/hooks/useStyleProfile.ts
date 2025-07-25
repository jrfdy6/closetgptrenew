import { useState, useEffect } from 'react';
import { StyleProfile } from '../types';
import { ApiClient } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';

export const useStyleProfile = () => {
  const [profile, setProfile] = useState<StyleProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await ApiClient.getInstance().get<StyleProfile>(
        API_ENDPOINTS.USER.STYLE_PROFILE
      );
      if (response.data) {
        setProfile(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch style profile');
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (updates: Partial<StyleProfile>) => {
    try {
      setLoading(true);
      setError(null);
      const response = await ApiClient.getInstance().put<StyleProfile>(
        API_ENDPOINTS.USER.STYLE_PROFILE,
        updates
      );

      if (response.data) {
        setProfile(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update style profile');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updatePreferences = async (preferences: StyleProfile['preferences']) => {
    try {
      setLoading(true);
      setError(null);
      const response = await ApiClient.getInstance().put<StyleProfile>(
        API_ENDPOINTS.USER.STYLE_PROFILE,
        { preferences }
      );

      if (response.data) {
        setProfile(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update style preferences');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateMeasurements = async (measurements: StyleProfile['measurements']) => {
    try {
      setLoading(true);
      setError(null);
      const response = await ApiClient.getInstance().put<StyleProfile>(
        API_ENDPOINTS.USER.STYLE_PROFILE,
        { measurements }
      );

      if (response.data) {
        setProfile(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update measurements');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const validateMeasurements = (measurements: StyleProfile['measurements']): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];

    if (measurements.height <= 0) {
      errors.push('Height must be greater than 0');
    }

    if (measurements.weight <= 0) {
      errors.push('Weight must be greater than 0');
    }

    if (!measurements.bodyType) {
      errors.push('Body type is required');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  };

  return {
    profile,
    loading,
    error,
    updateProfile,
    updatePreferences,
    updateMeasurements,
    validateMeasurements,
    refreshProfile: fetchProfile,
  };
}; 