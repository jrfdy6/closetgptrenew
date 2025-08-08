"use client";

import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Copy } from "lucide-react";
import { useState } from "react";

export default function TestUserIdPage() {
  const { user, loading } = useAuth();
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    if (user?.uid) {
      await navigator.clipboard.writeText(user.uid);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

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
          <CardTitle>Your Firebase User ID</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">
                User ID (Firebase UID):
              </p>
              <div className="flex items-center gap-2">
                <code className="bg-gray-100 px-3 py-2 rounded text-sm font-mono break-all">
                  {user.uid}
                </code>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyToClipboard}
                  className="flex-shrink-0"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  {copied ? "Copied!" : "Copy"}
                </Button>
              </div>
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
            
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Instructions:</strong>
              </p>
              <ol className="text-sm text-blue-700 mt-2 space-y-1">
                <li>1. Copy your User ID above</li>
                <li>2. Go to the backend directory</li>
                <li>3. Run: <code className="bg-blue-100 px-1 rounded">python3 migrate_outfits_user_id.py</code></li>
                <li>4. Paste your User ID when prompted</li>
                <li>5. Check your outfits page - they should now appear!</li>
              </ol>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
