"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, onAuthStateChanged } from "firebase/auth";
import { auth, debugAuth } from "./firebase/config";

interface FirebaseContextType {
  user: User | null;
  loading: boolean;
  error: Error | null;
}

const FirebaseContext = createContext<FirebaseContextType>({
  user: null,
  loading: true,
  error: null,
});

export const useFirebase = () => useContext(FirebaseContext);

export const FirebaseProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    console.log('🔍 Firebase context useEffect - auth object:', auth);
    debugAuth();
    
    if (!auth) {
      console.warn("Firebase Auth is not initialized - this is normal during SSR");
      setLoading(false);
      return;
    }

    console.log('🔍 Setting up auth state listener...');
    
    // Add a timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      console.log('🔍 Auth state listener timeout - assuming no user');
      setLoading(false);
    }, 5000); // 5 second timeout
    
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      console.log('🔍 Auth state changed - user:', user ? user.uid : 'null');
      clearTimeout(timeoutId);
      setUser(user);
      setLoading(false);
    }, (error) => {
      console.error("Firebase auth error:", error);
      clearTimeout(timeoutId);
      setError(error);
      setLoading(false);
    });

    return () => {
      console.log('🔍 Cleaning up auth state listener');
      unsubscribe();
    };
  }, []);

  return (
    <FirebaseContext.Provider value={{ user, loading, error }}>
      {children}
    </FirebaseContext.Provider>
  );
}; 