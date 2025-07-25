import { Auth } from 'firebase/auth';
import { Firestore } from 'firebase/firestore';
import { FirebaseStorage } from 'firebase/storage';

declare module '@/lib/firebase' {
  export const auth: Auth;
  export const db: Firestore;
  export const storage: FirebaseStorage;
} 