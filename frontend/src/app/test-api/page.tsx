"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export default function TestApiPage() {
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const testAnalyzeImage = async () => {
    setLoading(true);
    setResult("Testing...");
    
    try {
      const response = await fetch('/api/analyze-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          image: { 
            url: "https://example.com/test-image.jpg" 
          } 
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
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          imageUrl: "https://example.com/test-image.jpg" 
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