import { useState, useCallback, useEffect } from "react";
import { useFirebase } from "@/lib/firebase-context";
import {
  getUserProfile,
  setUserProfile,
  updateUserProfile,
  updateUserPreferences,
  updateUserMeasurements,
  updateUserStylePreferences,
} from "@/lib/firebase/userService";
import { UserProfileSchema } from "@shared/types";
import type { UserProfile } from "@shared/types";

export function useUserProfile() {
  const { user } = useFirebase();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch user profile
  const fetchProfile = useCallback(async () => {
    if (!user) return;

    try {
      setIsLoading(true);
      setError(null);
      const validatedProfile = await getUserProfile(user.uid);
      
      if (!validatedProfile) {
        // Create a new profile if one doesn't exist
        const newProfile = {
          id: user.uid,
          name: user.displayName || "",
          email: user.email || "",
          gender: "male" as const,
          preferences: {
            style: [],
            colors: [],
            occasions: []
          },
          measurements: {
            height: 0,
            weight: 0,
            bodyType: "average",
            skinTone: "medium"
          },
          stylePreferences: [],
          bodyType: "average",
          skinTone: "medium",
          fitPreference: "fitted" as const,
          createdAt: Date.now(),
          updatedAt: Date.now()
        };
        
        await setUserProfile(user.uid, newProfile);
        setProfile(newProfile);
      } else {
        setProfile(validatedProfile);
      }
    } catch (err) {
      setError("Failed to fetch user profile");
      console.error("Profile error:", err);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  // Create or update user profile
  const updateProfile = useCallback(async (updates: Partial<UserProfile>) => {
    if (!user) return;

    try {
      setIsLoading(true);
      setError(null);
      await setUserProfile(user.uid, updates);
      await fetchProfile(); // Refresh profile after update
    } catch (err) {
      setError("Failed to update profile");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [user, fetchProfile]);

  // Update user preferences
  const updatePreferences = useCallback(async (preferences: Partial<UserProfile["preferences"]>) => {
    if (!user) return;

    try {
      setIsLoading(true);
      setError(null);
      await updateUserPreferences(user.uid, preferences);
      await fetchProfile(); // Refresh profile after update
    } catch (err) {
      setError("Failed to update preferences");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [user, fetchProfile]);

  // Update user measurements
  const updateMeasurements = useCallback(async (measurements: Partial<UserProfile["measurements"]>) => {
    if (!user) return;

    try {
      setIsLoading(true);
      setError(null);
      await updateUserMeasurements(user.uid, measurements);
      await fetchProfile(); // Refresh profile after update
    } catch (err) {
      setError("Failed to update measurements");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [user, fetchProfile]);

  // Update style preferences
  const updateStylePreferences = useCallback(async (stylePreferences: string[]) => {
    if (!user) return;

    try {
      setIsLoading(true);
      setError(null);
      await updateUserStylePreferences(user.uid, stylePreferences);
      await fetchProfile(); // Refresh profile after update
    } catch (err) {
      setError("Failed to update style preferences");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [user, fetchProfile]);

  // Initial fetch
  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return {
    profile,
    isLoading,
    error,
    updateProfile,
    updatePreferences,
    updateMeasurements,
    updateStylePreferences,
    refreshProfile: fetchProfile,
  };
} 