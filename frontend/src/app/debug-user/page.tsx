"use client";

import { useAuth } from "@/hooks/useAuth";
import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DebugUserPage() {
  const { user, loading } = useAuth();

  useEffect(() => {
    if (user) {
      console.log("🔍 USER ID FOR MIGRATION:", user.uid);
      console.log("🔍 Copy this ID and use it in the migration script");
      console.log("🔍 User details:", {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName
      });
    }
  }, [user]);

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">Loading...</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-red-500">Not authenticated</p>
              <p className="text-sm text-muted-foreground mt-2">
                Please sign in to view your user ID
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Debug User Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">
                User ID (Firebase UID):
              </p>
              <code className="bg-gray-100 px-3 py-2 rounded text-sm font-mono break-all block">
                {user.uid}
              </code>
            </div>
            
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">
                User Email:
              </p>
              <p className="text-sm">{user.email}</p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">
                Display Name:
              </p>
              <p className="text-sm">{user.displayName || "Not set"}</p>
            </div>
            
            <div className="mt-6 p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-green-800">
                <strong>✅ Check your browser console!</strong>
              </p>
              <p className="text-sm text-green-700 mt-2">
                Your user ID has been logged to the console. Copy it and use it in the migration script.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
