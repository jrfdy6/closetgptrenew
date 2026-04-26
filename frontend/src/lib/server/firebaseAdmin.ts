import { cert, getApps, initializeApp, type App } from 'firebase-admin/app';
import { getAuth, type Auth } from 'firebase-admin/auth';
import { getFirestore, type Firestore } from 'firebase-admin/firestore';
import { getStorage, type Storage } from 'firebase-admin/storage';
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';

const SERVICE_ACCOUNT_CANDIDATES = [
  join(process.cwd(), 'serviceAccountKey.local.json'),
  join(process.cwd(), 'frontend', 'serviceAccountKey.local.json'),
  join(process.cwd(), 'backend', 'serviceAccountKey.local.json'),
];

function getStorageBucket() {
  return process.env.FIREBASE_STORAGE_BUCKET || process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET;
}

function loadLocalServiceAccount() {
  for (const candidate of SERVICE_ACCOUNT_CANDIDATES) {
    if (!existsSync(candidate)) {
      continue;
    }

    const raw = readFileSync(candidate, 'utf8');
    return JSON.parse(raw);
  }

  return null;
}

export function initFirebaseAdminApp(): App {
  const existingApp = getApps()[0];
  if (existingApp) {
    return existingApp;
  }

  const projectId = process.env.FIREBASE_PROJECT_ID;
  const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;
  const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n');
  const storageBucket = getStorageBucket();

  if (projectId && clientEmail && privateKey) {
    return initializeApp({
      credential: cert({
        projectId,
        clientEmail,
        privateKey,
      }),
      ...(storageBucket ? { storageBucket } : {}),
    });
  }

  const serviceAccount = loadLocalServiceAccount();
  if (serviceAccount) {
    return initializeApp({
      credential: cert(serviceAccount),
      ...(storageBucket ? { storageBucket } : {}),
    });
  }

  throw new Error(
    'Firebase Admin not configured (missing env vars and no serviceAccountKey.local.json found)'
  );
}

export function getFirebaseAdminAuth(): Auth {
  return getAuth(initFirebaseAdminApp());
}

export function getFirebaseAdminDb(): Firestore {
  return getFirestore(initFirebaseAdminApp());
}

export function getFirebaseAdminStorage(): Storage {
  return getStorage(initFirebaseAdminApp());
}
