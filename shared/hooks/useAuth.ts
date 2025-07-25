import { useState, useEffect } from 'react';
import { UserProfile } from '../types';
import { STORAGE_KEYS } from '../constants/index';
import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../api/endpoints';

export const useAuth = () => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    if (token) {
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await apiClient.get<UserProfile>(API_ENDPOINTS.USER.PROFILE);
      if (response.data) {
        setUser(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch user profile');
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.post<{ token: string; user: UserProfile }>(
        API_ENDPOINTS.AUTH.LOGIN,
        { email, password }
      );
      
      if (response.data) {
        localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.data.token);
        setUser(response.data.user);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, password: string, displayName: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.post<{ token: string; user: UserProfile }>(
        API_ENDPOINTS.AUTH.REGISTER,
        { email, password, displayName }
      );
      
      if (response.data) {
        localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.data.token);
        setUser(response.data.user);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT, {});
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      setUser(null);
    }
  };

  const updateProfile = async (updates: Partial<UserProfile>) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.put<UserProfile>(
        API_ENDPOINTS.USER.UPDATE_PROFILE,
        updates
      );
      
      if (response.data) {
        setUser(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateProfile,
  };
}; 