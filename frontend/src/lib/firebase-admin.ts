import { initializeApp, getApps, cert } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';

let adminDb: any = null;

// Only initialize Firebase Admin if we're in a server environment and have the required env vars
if (typeof window === 'undefined' && process.env.FIREBASE_PROJECT_ID) {
  try {
    if (!process.env.FIREBASE_CLIENT_EMAIL) {
      console.warn('FIREBASE_CLIENT_EMAIL is not set');
    }

    if (!process.env.FIREBASE_PRIVATE_KEY) {
      console.warn('FIREBASE_PRIVATE_KEY is not set');
    }

    // Only initialize if all required env vars are present
    if (process.env.FIREBASE_PROJECT_ID && process.env.FIREBASE_CLIENT_EMAIL && process.env.FIREBASE_PRIVATE_KEY) {
      const firebaseAdminConfig = {
        credential: cert({
          projectId: process.env.FIREBASE_PROJECT_ID,
          clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
          privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
        }),
      };

      const apps = getApps();

      if (!apps.length) {
        initializeApp(firebaseAdminConfig);
      }

      adminDb = getFirestore();
    }
  } catch (error) {
    console.error('Failed to initialize Firebase Admin:', error);
  }
}

export { adminDb }; 