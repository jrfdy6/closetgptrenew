"use client";

import { useState, useEffect } from 'react';
import { useFirebase } from '@/lib/firebase-context';

export default function TestUserFiltering() {
  const { user, loading: authLoading } = useFirebase();
  const [debugData, setDebugData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toISOString()}: ${message}`]);
  };

  const testUserFiltering = async () => {
    if (!user) {
      setError('User not authenticated');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      addLog('Starting user filtering debug test...');
      
      // Get the user's ID token for authentication
      const idToken = await user.getIdToken();
      addLog(`User ID: ${user.uid}`);
      addLog(`ID token length: ${idToken.length}`);
      
      // First try the minimal debug endpoint
      addLog('Testing minimal debug endpoint first...');
      const minimalResponse = await fetch('http://localhost:3001/api/outfits/debug-minimal', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      addLog(`Minimal debug response status: ${minimalResponse.status}`);
      
      if (minimalResponse.ok) {
        const minimalData = await minimalResponse.json();
        addLog('Minimal debug successful!');
        addLog(`Firebase initialized: ${minimalData.firebase_initialized}`);
        addLog(`Should bypass Firestore: ${minimalData.should_bypass_firestore}`);
        addLog(`DB object: ${minimalData.db_object}`);
      } else {
        const errorText = await minimalResponse.text();
        addLog(`Minimal debug failed: ${minimalResponse.status} - ${errorText}`);
      }
      
      // Then try the simple debug endpoint
      addLog('Testing simple debug endpoint...');
      const simpleResponse = await fetch('http://localhost:3001/api/outfits/debug-simple', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      addLog(`Simple debug response status: ${simpleResponse.status}`);
      
      if (simpleResponse.ok) {
        const simpleData = await simpleResponse.json();
        addLog('Simple debug successful!');
        addLog(`Total outfits: ${simpleData.total_outfits}`);
        addLog(`Outfits with user_id: ${simpleData.outfits_with_user_id}`);
        addLog(`Outfits with userId: ${simpleData.outfits_with_userId}`);
      } else {
        const errorText = await simpleResponse.text();
        addLog(`Simple debug failed: ${simpleResponse.status} - ${errorText}`);
      }
      
      // Now try the full debug endpoint
      addLog('Testing full user filtering debug...');
      const response = await fetch('http://localhost:3001/api/outfits/debug-user-filtering', {
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json',
        },
      });
      
      addLog(`Full debug response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        addLog(`Error response: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setDebugData(data);
      addLog('Debug data received successfully');
      
      // Log summary
      addLog(`Total outfits analyzed: ${data.total_outfits_analyzed}`);
      addLog(`Direct user_id matches: ${data.outfits_with_direct_user_id_match}`);
      addLog(`Item userId matches: ${data.outfits_with_item_userId_match}`);
      addLog(`No matches: ${data.outfits_with_no_match}`);
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      addLog(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  if (authLoading) {
    return (
      <div className="container mx-auto p-8">
        <h1 className="text-2xl font-bold mb-4">User Filtering Debug Test</h1>
        <div>Loading authentication...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">User Filtering Debug Test</h1>
      
      <div className="mb-6 p-4 bg-blue-100 border border-blue-400 text-blue-700 rounded">
        <h2 className="text-lg font-bold mb-2">Authentication Status</h2>
        {user ? (
          <div>
            <p><strong>User ID:</strong> {user.uid}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Anonymous:</strong> {user.isAnonymous ? 'Yes' : 'No'}</p>
          </div>
        ) : (
          <p>Not authenticated - please sign in</p>
        )}
      </div>
      
      <div className="mb-6">
        <button
          onClick={testUserFiltering}
          disabled={loading || !user}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
        >
          {loading ? 'Testing...' : 'Test User Filtering Debug'}
        </button>
        
        <button
          onClick={clearLogs}
          className="ml-4 bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          Clear Logs
        </button>
      </div>
      
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {debugData && (
        <div className="mb-6">
          <h2 className="text-xl font-bold mb-2">Debug Results</h2>
          <div className="bg-gray-100 p-4 rounded">
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <strong>Current User ID:</strong> {debugData.current_user_id}
              </div>
              <div>
                <strong>User ID Type:</strong> {debugData.current_user_id_type}
              </div>
              <div>
                <strong>Total Outfits Analyzed:</strong> {debugData.total_outfits_analyzed}
              </div>
              <div>
                <strong>Direct User ID Matches:</strong> {debugData.outfits_with_direct_user_id_match}
              </div>
              <div>
                <strong>Item UserId Matches:</strong> {debugData.outfits_with_item_userId_match}
              </div>
              <div>
                <strong>No Matches:</strong> {debugData.outfits_with_no_match}
              </div>
            </div>
            
            <h3 className="text-lg font-bold mb-2">Detailed Analysis (First 5 Outfits)</h3>
            <div className="space-y-2">
              {debugData.detailed_analysis?.slice(0, 5).map((outfit: any, index: number) => (
                <div key={index} className="border p-3 rounded bg-white">
                  <div><strong>Outfit ID:</strong> {outfit.outfit_id}</div>
                  <div><strong>user_id:</strong> '{outfit.outfit_user_id}'</div>
                  <div><strong>userId:</strong> '{outfit.outfit_userId}'</div>
                  <div><strong>Items:</strong> {outfit.items_count}</div>
                  <div><strong>Direct Match:</strong> {outfit.direct_match ? '✅' : '❌'}</div>
                  <div><strong>Item Match:</strong> {outfit.item_match ? '✅' : '❌'}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      <div className="mb-4">
        <h2 className="text-xl font-bold mb-2">Test Logs</h2>
        <div className="bg-gray-100 p-4 rounded max-h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-gray-500">No logs yet. Click "Test User Filtering Debug" to start.</p>
          ) : (
            <div className="space-y-1">
              {logs.map((log, index) => (
                <div key={index} className="text-sm font-mono">
                  {log}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-8 p-4 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
        <h3 className="text-lg font-bold mb-2">Instructions</h3>
        <ol className="list-decimal list-inside space-y-1">
          <li>Make sure you're signed in (you should see your user ID above)</li>
          <li>Click "Test User Filtering Debug" to trigger the debug endpoint</li>
          <li>Check the backend console for detailed logs starting with "🔍 DEBUG:"</li>
          <li>The logs will show exactly how user filtering is working</li>
          <li>Look for patterns in the user_id vs userId comparisons</li>
        </ol>
      </div>
      
      <div className="mt-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
        <h3 className="text-lg font-bold mb-2">What to Look For</h3>
        <ul className="list-disc list-inside space-y-1">
          <li><strong>current_user_id:</strong> The user ID from authentication</li>
          <li><strong>outfit.user_id:</strong> The user_id field in outfit documents</li>
          <li><strong>outfit.userId:</strong> The userId field in outfit documents</li>
          <li><strong>item.userId:</strong> The userId field in item objects</li>
          <li><strong>Matching patterns:</strong> Which fields actually match the current user</li>
        </ul>
      </div>
    </div>
  );
} 