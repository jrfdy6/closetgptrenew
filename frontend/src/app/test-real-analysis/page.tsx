"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getFirebaseIdToken } from "@/lib/utils/auth";

export default function TestRealAnalysis() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testRealAnalysis = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const token = await getFirebaseIdToken();
      const response = await fetch('/api/analyze-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          image: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=400&fit=crop&crop=center"
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to analyze image');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Test Real GPT-4o Analysis</h1>
      
      <Card className="p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Backend Connection Test</h2>
        <p className="text-muted-foreground mb-4">
          This test will verify that the frontend can connect to the real backend and get GPT-4o analysis results.
        </p>
        
        <Button 
          onClick={testRealAnalysis} 
          disabled={loading}
          className="mb-4"
        >
          {loading ? "Testing..." : "Test Real Analysis"}
        </Button>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
            <h3 className="text-red-800 font-semibold">Error:</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {result && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <h3 className="text-green-800 font-semibold">Success! Analysis Result:</h3>
            <pre className="text-sm text-green-700 mt-2 overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">What This Tests:</h2>
        <ul className="list-disc list-inside space-y-2 text-muted-foreground">
          <li>Frontend API route connectivity</li>
          <li>Backend endpoint accessibility</li>
          <li>GPT-4o model integration</li>
          <li>Response parsing and formatting</li>
        </ul>
      </Card>
    </div>
  );
} 