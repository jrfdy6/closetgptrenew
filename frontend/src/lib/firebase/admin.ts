import type { Auth } from 'firebase-admin/auth';
import type { Firestore } from 'firebase-admin/firestore';
import {
  getFirebaseAdminAuth,
  getFirebaseAdminDb,
  initFirebaseAdminApp,
} from '@/lib/server/firebaseAdmin';

export const initializeFirebaseAdmin = () => initFirebaseAdminApp();
export const getFirebaseAdmin = () => initFirebaseAdminApp();

function loadAdminAuth(): Auth | null {
  try {
    return getFirebaseAdminAuth();
  } catch {
    return null;
  }
}

function loadAdminDb(): Firestore | null {
  try {
    return getFirebaseAdminDb();
  } catch {
    return null;
  }
}

export const auth = loadAdminAuth();
export const db = loadAdminDb();
