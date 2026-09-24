import { initializeApp } from 'firebase/app';
import { getAuth, connectAuthEmulator } from 'firebase/auth';
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';

// Suppress harmless Cross-Origin-Opener-Policy warnings from Firebase OAuth popup
if (typeof window !== 'undefined') {
  // Only set up filter once
  if (!(window as any).__firebaseConsoleFilterSet) {
    const originalError = console.error;
    const originalWarn = console.warn;
    
    console.error = (...args: any[]) => {
      // Check all arguments for the message
      const message = args.map(arg => 
        typeof arg === 'string' ? arg : 
        typeof arg === 'object' && arg !== null ? JSON.stringify(arg) : 
        String(arg)
      ).join(' ');
      
      // Filter out Cross-Origin-Opener-Policy warnings from Firebase
      if (message.includes('Cross-Origin-Opener-Policy') || 
          message.includes('window.closed call')) {
        return; // Suppress this error
      }
      originalError.apply(console, args);
    };
    
    console.warn = (...args: any[]) => {
      // Check all arguments for the message
      const message = args.map(arg => 
        typeof arg === 'string' ? arg : 
        typeof arg === 'object' && arg !== null ? JSON.stringify(arg) : 
        String(arg)
      ).join(' ');
      
      // Filter out Cross-Origin-Opener-Policy warnings from Firebase
      if (message.includes('Cross-Origin-Opener-Policy') || 
          message.includes('window.closed call')) {
        return; // Suppress this warning
      }
      originalWarn.apply(console, args);
    };
    
    (window as any).__firebaseConsoleFilterSet = true;
  }
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

// Local acceptance only: never direct a production build or real project to emulators.
if (process.env.NEXT_PUBLIC_USE_FIREBASE_EMULATORS === 'true' && typeof window !== 'undefined') {
  if (process.env.NODE_ENV !== 'development' || !firebaseConfig.projectId.startsWith('demo-') ||
      !['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname)) {
    throw new Error('Firebase emulators require a local development server and a demo- project.');
  }
  connectAuthEmulator(auth, 'http://127.0.0.1:9099', { disableWarnings: true });
  connectFirestoreEmulator(db, '127.0.0.1', 8202);
}

export default app;
