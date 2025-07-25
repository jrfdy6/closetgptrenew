import { useState, useEffect } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { userProfileService } from '@/lib/firebase/userProfileService';
import { UserProfile } from '@/types/wardrobe';

export function useUserProfile() {
  const { user } = useFirebase();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function loadProfile() {
      if (!user) {
        setProfile(null);
        setIsLoading(false);
        return;
      }

      try {
        const userProfile = await userProfileService.getProfile(user.uid);
        setProfile(userProfile);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load profile'));
      } finally {
        setIsLoading(false);
      }
    }

    loadProfile();
  }, [user]);

  const updateProfile = async (profileData: Partial<UserProfile>) => {
    if (!user) {
      throw new Error('User must be logged in to update profile');
    }

    try {
      await userProfileService.updateProfile(user.uid, profileData);
      const updatedProfile = await userProfileService.getProfile(user.uid);
      setProfile(updatedProfile);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to update profile'));
      throw err;
    }
  };

  return {
    profile,
    isLoading,
    error,
    updateProfile,
  };
} 