import {
  collection,
  doc,
  getDoc,
  setDoc,
  updateDoc,
  Timestamp,
} from "firebase/firestore";
import { db } from "./index";
import type { UserProfile } from "../../shared/types";
import { UserProfileSchema } from "../../shared/types";

// Collection reference
const USERS_COLLECTION = "users";

// Helper function to convert timestamp to number
function convertTimestamp(timestamp: any): number {
  if (timestamp instanceof Timestamp) {
    return timestamp.toMillis();
  }
  if (typeof timestamp === 'number') {
    return timestamp;
  }
  return Date.now();
}

// Helper function to remove undefined values from objects (Firestore doesn't allow undefined)
function removeUndefinedValues(obj: any): any {
  if (obj === null || obj === undefined) {
    return null;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(removeUndefinedValues).filter(item => item !== null);
  }
  
  if (typeof obj === 'object') {
    const cleaned: any = {};
    for (const [key, value] of Object.entries(obj)) {
      if (value !== undefined) {
        cleaned[key] = removeUndefinedValues(value);
      }
    }
    return cleaned;
  }
  
  return obj;
}

// Create initial user profile
export async function createInitialUserProfile(
  userId: string,
  email: string,
  displayName: string | null
): Promise<void> {
  const userRef = doc(db, USERS_COLLECTION, userId);
  const now = Timestamp.now();
  
  const initialProfile = {
    id: userId,
    name: displayName || email.split('@')[0],
    email: email,
    gender: null,
    preferences: {
      style: [],
      colors: [],
      occasions: []
    },
    measurements: {
      height: 0,
      weight: 0,
      bodyType: null,
      skinTone: null
    },
    stylePreferences: [],
    bodyType: null,
    skinTone: null,
    fitPreference: null,
    sizePreference: null,
    createdAt: now,
    updatedAt: now,
    onboardingCompleted: false
  };

  await setDoc(userRef, initialProfile);
}

// Get user profile
export async function getUserProfile(userId: string): Promise<UserProfile | null> {
  console.log('=== GET USER PROFILE CALLED ===');
  console.log('User ID:', userId);
  
  const userRef = doc(db, USERS_COLLECTION, userId);
  const userDoc = await getDoc(userRef);
  if (!userDoc.exists()) {
    console.log('No profile document found');
    return null;
  }
  
  const rawData = userDoc.data();
  console.log('Raw Firestore data:', rawData);
  
  // Convert Firestore Timestamp to number for createdAt/updatedAt
  const profileData = {
    ...rawData,
    id: userId,
    createdAt: convertTimestamp(rawData.createdAt),
    updatedAt: convertTimestamp(rawData.updatedAt),
  };
  
  console.log('Processed profile data:', profileData);
  
  try {
    const validatedProfile = UserProfileSchema.parse(profileData);
    console.log('Profile validation successful:', validatedProfile);
    return validatedProfile;
  } catch (error) {
    console.error("Error validating user profile:", error);
    console.error("Validation error details:", error);
    return null;
  }
}

// Create or update user profile
export async function setUserProfile(
  userId: string,
  profile: Partial<UserProfile>
): Promise<void> {
  console.log('=== SET USER PROFILE CALLED ===');
  console.log('User ID:', userId);
  console.log('Profile data to save:', profile);
  
  try {
    const userRef = doc(db, USERS_COLLECTION, userId);
    
    // Clean the profile data to remove undefined values
    const cleanedProfile = removeUndefinedValues(profile);
    console.log('Cleaned profile data:', cleanedProfile);
    
    await setDoc(
      userRef,
      {
        ...cleanedProfile,
        updatedAt: Timestamp.now(),
      },
      { merge: true }
    );
    console.log('Profile saved successfully to Firestore');
  } catch (error) {
    console.error('Error saving profile to Firestore:', error);
    throw error;
  }
}

// Update user profile
export async function updateUserProfile(
  userId: string,
  updates: Partial<UserProfile>
): Promise<void> {
  const userRef = doc(db, USERS_COLLECTION, userId);
  
  // Clean the updates data to remove undefined values
  const cleanedUpdates = removeUndefinedValues(updates);
  
  await updateDoc(userRef, {
    ...cleanedUpdates,
    updatedAt: Timestamp.now(),
  });
}

// Update user preferences
export async function updateUserPreferences(
  userId: string,
  preferences: Partial<UserProfile["preferences"]>
): Promise<void> {
  const userRef = doc(db, USERS_COLLECTION, userId);
  await updateDoc(userRef, {
    "preferences": preferences,
    updatedAt: Timestamp.now(),
  });
}

// Update user measurements
export async function updateUserMeasurements(
  userId: string,
  measurements: Partial<UserProfile["measurements"]>
): Promise<void> {
  const userRef = doc(db, USERS_COLLECTION, userId);
  await updateDoc(userRef, {
    "measurements": measurements,
    updatedAt: Timestamp.now(),
  });
}

// Update user style preferences
export async function updateUserStylePreferences(
  userId: string,
  stylePreferences: Partial<UserProfile["stylePreferences"]>
): Promise<void> {
  const userRef = doc(db, USERS_COLLECTION, userId);
  await updateDoc(userRef, {
    "stylePreferences": stylePreferences,
    updatedAt: Timestamp.now(),
  });
} 