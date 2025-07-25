import { app, db, storage, auth } from './config';
import type { FirebaseApp } from 'firebase/app';
import type { Firestore } from 'firebase/firestore';
import type { FirebaseStorage } from 'firebase/storage';
import type { Auth } from 'firebase/auth';

// Export typed instances
export const typedDb = db as Firestore;
export const typedStorage = storage as FirebaseStorage;
export const typedAuth = auth as Auth;

// Export untyped instances for backward compatibility
export { db, storage, auth };

// Export types
export type { Firestore, FirebaseStorage, Auth, FirebaseApp }; 