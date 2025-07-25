import { db } from './config';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { UserProfile } from '@/types/wardrobe';

export const userProfileService = {
  async updateProfile(userId: string, profileData: Partial<UserProfile>): Promise<void> {
    if (!db) {
      throw new Error("Firestore is not initialized");
    }
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);

    if (!userDoc.exists()) {
      // Create new profile
      await setDoc(userRef, {
        ...profileData,
        id: userId,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      });
    } else {
      // Update existing profile
      await setDoc(userRef, {
        ...profileData,
        updatedAt: Date.now(),
      }, { merge: true });
    }
  },

  async getProfile(userId: string): Promise<UserProfile | null> {
    if (!db) {
      throw new Error("Firestore is not initialized");
    }
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);

    if (!userDoc.exists()) {
      return null;
    }

    return userDoc.data() as UserProfile;
  },
}; 