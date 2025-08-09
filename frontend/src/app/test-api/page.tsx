"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { getFirebaseIdToken } from "@/lib/utils/auth";

export default function TestApiPage() {
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const testAnalyzeImage = async () => {
    setLoading(true);
    setResult("Testing...");
    
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

      const data = await response.json();
      setResult(`Status: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}`);
    } catch (error) {
      setResult(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const testAnalyze = async () => {
    setLoading(true);
    setResult("Testing...");
    
    try {
      const token = await getFirebaseIdToken();
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ 
          imageUrl: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=400&fit=crop&crop=center" 
        }),
      });

      const data = await response.json();
      setResult(`Status: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}`);
    } catch (error) {
      setResult(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">API Test Page</h1>
      
      <div className="space-y-4">
        <Button 
          onClick={testAnalyzeImage} 
          disabled={loading}
          className="mr-4"
        >
          Test /api/analyze-image
        </Button>
        
        <Button 
          onClick={testAnalyze} 
          disabled={loading}
        >
          Test /api/analyze
        </Button>
      </div>

      {result && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-2">Result:</h2>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto">
            {result}
          </pre>
        </div>
      )}
    </div>
  );
} 