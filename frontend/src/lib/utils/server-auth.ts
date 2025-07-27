import { getAuth } from 'firebase-admin/auth';
import { getApps, initializeApp, cert } from 'firebase-admin/app';

// Initialize Firebase Admin if not already initialized
if (!getApps().length) {
  try {
    let firebaseAdminConfig;
    
    // Try to use environment variables first
    if (process.env.FIREBASE_PROJECT_ID && process.env.FIREBASE_CLIENT_EMAIL && process.env.FIREBASE_PRIVATE_KEY) {
      firebaseAdminConfig = {
        credential: cert({
          projectId: process.env.FIREBASE_PROJECT_ID,
          clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
          privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
        }),
      };
    } else {
      // Fall back to service account key file
      const serviceAccount = require('../../serviceAccountKey.json');
      firebaseAdminConfig = {
        credential: cert(serviceAccount),
      };
    }
    
    initializeApp(firebaseAdminConfig);
    console.log('✅ Firebase Admin initialized successfully');
  } catch (error) {
    console.error('Failed to initialize Firebase Admin:', error);
  }
}

/**
 * Verify Firebase ID token on the server side
 * @param authHeader - The Authorization header from the request
 * @returns Promise<string | null> - The user ID if token is valid, null otherwise
 */
export async function verifyFirebaseToken(authHeader: string | null): Promise<string | null> {
  try {
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return null;
    }

    const token = authHeader.split('Bearer ')[1];
    const decodedToken = await getAuth().verifyIdToken(token);
    return decodedToken.uid;
  } catch (error) {
    console.error('Error verifying Firebase token:', error);
    return null;
  }
}

/**
 * Get user ID from request headers
 * @param request - NextRequest object
 * @returns Promise<string | null> - The user ID if authenticated, null otherwise
 */
export async function getUserIdFromRequest(request: any): Promise<string | null> {
  const authHeader = request.headers.get('authorization');
  return await verifyFirebaseToken(authHeader);
} 