import { initializeApp, getApps, cert } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';

// Lazy initialization function
function initializeFirebaseAdmin() {
  const apps = getApps();
  if (!apps.length) {
    try {
      const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n');
      if (!privateKey) {
        throw new Error('FIREBASE_PRIVATE_KEY is not set');
      }

      initializeApp({
        credential: cert({
          projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
          clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
          privateKey: privateKey,
        }),
      });
      console.log('Firebase Admin initialized successfully');
    } catch (error) {
      console.error('Error initializing Firebase Admin:', error);
      throw error;
    }
  }
}

// Lazy getters for auth and db
let _auth: any = null;
let _db: any = null;

export function getAuthInstance() {
  if (!_auth) {
    initializeFirebaseAdmin();
    _auth = getAuth();
  }
  return _auth;
}

export function getDbInstance() {
  if (!_db) {
    initializeFirebaseAdmin();
    _db = getFirestore();
  }
  return _db;
}

// For backward compatibility
export const auth = {
  verifyIdToken: async (token: string) => {
    return getAuthInstance().verifyIdToken(token);
  }
};

export const db = {
  collection: (name: string) => {
    return getDbInstance().collection(name);
  }
}; 