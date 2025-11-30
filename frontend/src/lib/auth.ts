import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User,
  sendPasswordResetEmail,
  signInWithPopup,
  GoogleAuthProvider,
  linkWithCredential,
  fetchSignInMethodsForEmail
} from 'firebase/auth';
import { auth } from './firebase/config';

// Helper function to clear outfit-related localStorage data
// This prevents data leakage between users
const clearOutfitCache = () => {
  if (typeof window === 'undefined') return;
  
  try {
    // Find and remove all outfit-related localStorage keys
    const keysToRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && (
        key.includes('daily-outfit') || 
        key.includes('outfit-cache') ||
        key.includes('weather-outfit') ||
        key.includes('generated-outfit')
      )) {
        keysToRemove.push(key);
      }
    }
    
    // Remove all found keys
    keysToRemove.forEach(key => localStorage.removeItem(key));
    
    console.log(`🧹 Cleared ${keysToRemove.length} cached outfit items from localStorage`);
  } catch (error) {
    console.error('Error clearing outfit cache:', error);
  }
};

// Sign in with email and password
export const signIn = async (email: string, password: string) => {
  try {
    // Clear any cached outfit data from previous user sessions
    clearOutfitCache();
    
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    return { success: true, user: userCredential.user };
  } catch (error: any) {
    // Convert Firebase error codes to user-friendly messages
    let errorMessage = 'Sign in failed';
    if (error.code === 'auth/invalid-credential' || error.code === 'auth/wrong-password' || error.code === 'auth/user-not-found') {
      // Generic message - could be wrong password OR account created with different method
      errorMessage = 'Invalid email or password. Please check your credentials and try again. If you created your account with Google, use "Sign in with Google" instead.';
    } else if (error.code === 'auth/invalid-email') {
      errorMessage = 'Please enter a valid email address.';
    } else if (error.code === 'auth/user-disabled') {
      errorMessage = 'This account has been disabled. Please contact support.';
    } else if (error.code === 'auth/too-many-requests') {
      errorMessage = 'Too many failed attempts. Please try again later.';
    } else if (error.code === 'auth/account-exists-with-different-credential') {
      errorMessage = 'An account with this email already exists. Please sign in with Google to link your accounts.';
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    return { 
      success: false, 
      error: errorMessage
    };
  }
};

// Sign up with email and password
export const signUp = async (email: string, password: string) => {
  try {
    // Clear any cached outfit data before creating new account
    clearOutfitCache();
    
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    return { success: true, user: userCredential.user };
  } catch (error: any) {
    return { 
      success: false, 
      error: error.message || 'Sign up failed' 
    };
  }
};

// Sign in with Google
export const signInWithGoogle = async () => {
  try {
    // Clear any cached outfit data from previous user sessions
    clearOutfitCache();
    
    const provider = new GoogleAuthProvider();
    // Request additional scopes if needed
    provider.addScope('profile');
    provider.addScope('email');
    
    const userCredential = await signInWithPopup(auth, provider);
    
    // Firebase automatically links accounts with the same email
    // If linking was needed, it happens automatically
    return { success: true, user: userCredential.user };
  } catch (error: any) {
    console.error('Google sign in error:', error);
    
    // Handle account linking errors
    if (error.code === 'auth/account-exists-with-different-credential') {
      return {
        success: false,
        error: 'An account already exists with this email. Please sign in with your password first, then you can link your Google account.'
      };
    }
    
    return { 
      success: false, 
      error: error.message || 'Google sign in failed' 
    };
  }
};

// Sign out
export const signOutUser = async () => {
  try {
    // Clear cached outfit data when signing out
    clearOutfitCache();
    
    await signOut(auth);
    return { success: true };
  } catch (error: any) {
    return { 
      success: false, 
      error: error.message || 'Sign out failed' 
    };
  }
};

// Send password reset email
export const resetPassword = async (email: string) => {
  try {
    await sendPasswordResetEmail(auth, email);
    return { success: true };
  } catch (error: any) {
    return { 
      success: false, 
      error: error.message || 'Password reset failed' 
    };
  }
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return !!auth.currentUser;
};

// Get current user
export const getCurrentUser = (): User | null => {
  return auth.currentUser;
};

// Require authentication
export const requireAuth = () => {
  if (!isAuthenticated()) {
    throw new Error('Authentication required');
  }
};

// Auth state listener
export const onAuthStateChange = (callback: (user: User | null) => void) => {
  return onAuthStateChanged(auth, callback);
};
