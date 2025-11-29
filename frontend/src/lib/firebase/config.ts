import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Suppress harmless Cross-Origin-Opener-Policy warnings from Firebase OAuth popup
if (typeof window !== 'undefined') {
  const originalError = console.error;
  const originalWarn = console.warn;
  
  console.error = (...args: any[]) => {
    const message = args[0]?.toString() || '';
    // Filter out Cross-Origin-Opener-Policy warnings from Firebase
    if (message.includes('Cross-Origin-Opener-Policy')) {
      return; // Suppress this error
    }
    originalError.apply(console, args);
  };
  
  console.warn = (...args: any[]) => {
    const message = args[0]?.toString() || '';
    // Filter out Cross-Origin-Opener-Policy warnings from Firebase
    if (message.includes('Cross-Origin-Opener-Policy')) {
      return; // Suppress this warning
    }
    originalWarn.apply(console, args);
  };
}

// Firebase configuration
export const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || '',
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || '',
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || '',
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || ''
}

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Cloud Firestore and get a reference to the service
export const db = getFirestore(app);

export default app;
