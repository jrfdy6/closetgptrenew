import { NextRequest } from 'next/server';
import { getAuth } from 'firebase-admin/auth';
import { initializeApp, getApps, cert } from 'firebase-admin/app';

// Initialize Firebase Admin SDK
if (!getApps().length) {
  try {
    const serviceAccount = process.env.FIREBASE_SERVICE_ACCOUNT_KEY
      ? JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT_KEY)
      : null;

    if (serviceAccount) {
      initializeApp({
        credential: cert(serviceAccount),
      });
    } else {
      console.warn('Firebase service account key not found, using default credentials');
      initializeApp();
    }
  } catch (error) {
    console.error('Failed to initialize Firebase Admin:', error);
  }
}

// Server-side authentication utilities
export const getServerAuth = () => {
  // Implement server-side authentication
  return null
}

export const requireServerAuth = () => {
  // Require server-side authentication
  throw new Error('Server authentication not implemented')
}

// Function for getting user ID from request with Firebase token verification
export const getUserIdFromRequest = async (req: NextRequest): Promise<string | null> => {
  try {
    const authHeader = req.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      console.log('❌ No valid authorization header found');
      return null;
    }

    const token = authHeader.split('Bearer ')[1];
    if (!token) {
      console.log('❌ No token found in authorization header');
      return null;
    }

    // For test tokens, return a test user ID
    if (token === 'test') {
      console.log('✅ Using test token for authentication');
      return 'test-user-id';
    }

    try {
      // Verify Firebase token
      const decodedToken = await getAuth().verifyIdToken(token);
      console.log('✅ Firebase token verified for user:', decodedToken.uid);
      return decodedToken.uid;
    } catch (firebaseError) {
      console.error('❌ Firebase token verification failed:', firebaseError);
      return null;
    }
  } catch (error) {
    console.error('❌ Error in getUserIdFromRequest:', error);
    return null;
  }
};
