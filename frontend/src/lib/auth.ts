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
  fetchSignInMethodsForEmail,
  EmailAuthProvider,
  reauthenticateWithCredential
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
    // DEBUG: Log raw error details
    console.log("[signIn] Raw error:", error);
    const errorCode = error.code || "unknown";
    const firebaseErrorMessage = error.message || "No message provided";
    console.log(`[signIn] Firebase error code: ${errorCode}, message: ${firebaseErrorMessage}`);
    
    // DEBUG: Fetch and log sign-in methods
    let methodsResult;
    try {
      methodsResult = await getSignInMethods(email);
      console.log(`[signIn] getSignInMethods result for ${email}:`, methodsResult);
      if (methodsResult.success && methodsResult.methods) {
        console.log(`[signIn] Available sign-in methods:`, methodsResult.methods);
      } else {
        console.log(`[signIn] getSignInMethods failed or returned no methods:`, methodsResult.error);
      }
    } catch (fetchError) {
      console.log("[signIn] Error fetching sign-in methods:", fetchError);
    }
    
    // Convert Firebase error codes to user-friendly messages
    let errorMessage = 'Sign in failed';
    
    if (error.code === 'auth/invalid-credential' || error.code === 'auth/wrong-password' || error.code === 'auth/user-not-found') {
      // Check if there's a Google account with this email
      try {
        // methodsResult already fetched above for logging
        if (!methodsResult) {
          methodsResult = await getSignInMethods(email);
        }
        if (methodsResult.success && methodsResult.methods && methodsResult.methods.length > 0) {
          if (methodsResult.methods.includes('google.com')) {
            // Check if user is currently signed in with Google
            const currentUser = auth.currentUser;
            if (currentUser && currentUser.email === email) {
              const linkedProviders = currentUser.providerData.map(p => p.providerId);
              if (linkedProviders.includes('google.com')) {
                // User is signed in with Google - try to link the password
                try {
                  const linkResult = await linkEmailPassword(email, password);
                  if (linkResult.success) {
                    return { 
                      success: true, 
                      user: currentUser,
                      message: 'Password successfully linked to your account!'
                    };
                  } else {
                    errorMessage = `Password linking failed: ${linkResult.error}. Please sign in with Google and link your password in account settings.`;
                  }
                } catch (linkError: any) {
                  errorMessage = 'Unable to link password. Please sign in with Google and link your password in account settings.';
                }
              } else {
                errorMessage = 'This email is associated with a Google account. Please use "Sign in with Google" instead. After signing in with Google, you can link your password in account settings.';
              }
            } else {
              errorMessage = 'This email is associated with a Google account. Please use "Sign in with Google" instead. After signing in with Google, you can link your password in account settings.';
            }
          } else {
            errorMessage = 'Invalid email or password. Please check your credentials and try again.';
          }
        } else {
          errorMessage = 'Invalid email or password. Please check your credentials and try again.';
        }
      } catch (checkError) {
        // If we can't check methods, use generic message
        errorMessage = 'Invalid email or password. Please check your credentials and try again.';
      }
    } else if (error.code === 'auth/invalid-email') {
      errorMessage = 'Please enter a valid email address.';
    } else if (error.code === 'auth/user-disabled') {
      errorMessage = 'This account has been disabled. Please contact support.';
    } else if (error.code === 'auth/too-many-requests') {
      errorMessage = 'Too many failed attempts. Please try again later.';
    } else if (error.code === 'auth/account-exists-with-different-credential') {
      errorMessage = 'An account with this email already exists with a different sign-in method. Please use "Sign in with Google" to link your accounts.';
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

// Link email/password to current Google-authenticated account
export const linkEmailPassword = async (email: string, password: string) => {
  try {
    const currentUser = auth.currentUser;
    if (!currentUser) {
      return { 
        success: false, 
        error: 'You must be signed in to link an email/password' 
      };
    }

    // Create email credential
    const credential = EmailAuthProvider.credential(email, password);
    
    // Link the credential to the current user
    await linkWithCredential(currentUser, credential);
    
    return { success: true };
  } catch (error: any) {
    console.error('Link email/password error:', error);
    
    if (error.code === 'auth/credential-already-in-use') {
      return {
        success: false,
        error: 'This email/password is already linked to another account.'
      };
    } else if (error.code === 'auth/email-already-in-use') {
      return {
        success: false,
        error: 'This email is already in use by another account.'
      };
    } else if (error.code === 'auth/invalid-credential') {
      return {
        success: false,
        error: 'Invalid email or password. Please check your credentials.'
      };
    }
    
    return { 
      success: false, 
      error: error.message || 'Failed to link email/password' 
    };
  }
};

// Check what sign-in methods are available for an email
export const getSignInMethods = async (email: string) => {
  try {
    const methods = await fetchSignInMethodsForEmail(auth, email);
    return { success: true, methods };
  } catch (error: any) {
    return { 
      success: false, 
      error: error.message || 'Failed to check sign-in methods' 
    };
  }
};

// Get linked providers for current user
export const getLinkedProviders = (): string[] => {
  const user = auth.currentUser;
  if (!user) return [];
  
  return user.providerData.map(provider => provider.providerId);
};

// Check if password is linked to current account
export const hasPasswordLinked = (): boolean => {
  const providers = getLinkedProviders();
  return providers.includes('password');
};
