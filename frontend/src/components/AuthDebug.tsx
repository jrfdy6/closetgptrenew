"use client";

import { useFirebase } from "@/lib/firebase-context";
import { auth } from "@/lib/firebase/config";
import { useState, useEffect } from "react";

export default function AuthDebug() {
  const { user, loading, error } = useFirebase();
  const [authToken, setAuthToken] = useState<string | null>(null);

  useEffect(() => {
    const getToken = async () => {
      if (auth?.currentUser) {
        try {
          const token = await auth.currentUser.getIdToken();
          setAuthToken(token ? "Present" : "Empty");
        } catch (error) {
          setAuthToken("Error getting token");
        }
      } else {
        setAuthToken("No user");
      }
    };

    getToken();
  }, [user]);

  return (
    <div className="fixed bottom-4 right-4 bg-black text-white p-4 rounded-lg text-xs max-w-sm z-50">
      <h3 className="font-bold mb-2">🔍 Auth Debug</h3>
      <div className="space-y-1">
        <div>Loading: {loading ? "Yes" : "No"}</div>
        <div>User: {user ? user.uid : "None"}</div>
        <div>Auth Object: {auth ? "Exists" : "Missing"}</div>
        <div>Current User: {auth?.currentUser ? "Yes" : "No"}</div>
        <div>Token: {authToken}</div>
        {error && <div className="text-red-400">Error: {error.message}</div>}
      </div>
    </div>
  );
}
