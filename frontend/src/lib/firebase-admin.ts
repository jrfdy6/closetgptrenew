import type { Firestore } from 'firebase-admin/firestore';
import { getFirebaseAdminDb, initFirebaseAdminApp } from '@/lib/server/firebaseAdmin';

export const initializeFirebaseAdmin = () => initFirebaseAdminApp();
export const getFirebaseAdmin = () => initFirebaseAdminApp();

function loadAdminDb(): Firestore | null {
  try {
    return getFirebaseAdminDb();
  } catch {
    return null;
  }
}

export const adminDb = loadAdminDb();
