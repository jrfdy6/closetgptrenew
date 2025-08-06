"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { collection, query, where, getDocs, onSnapshot } from 'firebase/firestore';
import { db } from '@/lib/firebase/config';

export default function TestWardrobeQuery() {
  const { user } = useAuth();
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const testSimpleQuery = async () => {
    if (!user?.uid) {
      setError('No user authenticated');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log('Testing simple query for user:', user.uid);
      
      // Test 1: Simple collection query
      const wardrobeRef = collection(db, 'wardrobe');
      console.log('Collection reference created');
      
      // Test 2: Query with where clause
      const q = query(wardrobeRef, where('userId', '==', user.uid));
      console.log('Query created:', q);
      
      // Test 3: Execute query
      const snapshot = await getDocs(q);
      console.log('Query executed, found documents:', snapshot.docs.length);
      
      const items = snapshot.docs.map(doc => ({
        id: doc.id,
        data: doc.data()
      }));
      
      setResults({
        method: 'getDocs',
        documentCount: snapshot.docs.length,
        items: items.slice(0, 3) // Show first 3 items
      });
      
    } catch (err) {
      console.error('Error in simple query:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const testRealtimeQuery = async () => {
    if (!user?.uid) {
      setError('No user authenticated');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log('Testing realtime query for user:', user.uid);
      
      const wardrobeRef = collection(db, 'wardrobe');
      const q = query(wardrobeRef, where('userId', '==', user.uid));
      
      // Test realtime listener
      const unsubscribe = onSnapshot(q, (snapshot) => {
        console.log('Realtime listener triggered, documents:', snapshot.docs.length);
        const items = snapshot.docs.map(doc => ({
          id: doc.id,
          data: doc.data()
        }));
        
        setResults({
          method: 'onSnapshot',
          documentCount: snapshot.docs.length,
          items: items.slice(0, 3)
        });
      }, (error) => {
        console.error('Realtime listener error:', error);
        setError(`Realtime listener error: ${error.message}`);
      });
      
      // Cleanup after 5 seconds
      setTimeout(() => {
        unsubscribe();
        console.log('Realtime listener unsubscribed');
      }, 5000);
      
    } catch (err) {
      console.error('Error in realtime query:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const testCollectionExists = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log('Testing if wardrobe collection exists');
      
      const wardrobeRef = collection(db, 'wardrobe');
      const q = query(wardrobeRef);
      const snapshot = await getDocs(q);
      
      setResults({
        method: 'collectionExists',
        documentCount: snapshot.docs.length,
        message: 'Collection exists and is accessible'
      });
      
    } catch (err) {
      console.error('Error testing collection:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Test Wardrobe Query</h1>
      
      <div className="mb-6">
        <p className="text-sm text-gray-600 mb-4">
          User ID: {user?.uid || 'Not authenticated'}
        </p>
      </div>

      <div className="space-y-4 mb-6">
        <button
          onClick={testCollectionExists}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          Test Collection Exists
        </button>
        
        <button
          onClick={testSimpleQuery}
          disabled={loading || !user?.uid}
          className="px-4 py-2 bg-green-500 text-white rounded disabled:opacity-50 ml-2"
        >
          Test Simple Query
        </button>
        
        <button
          onClick={testRealtimeQuery}
          disabled={loading || !user?.uid}
          className="px-4 py-2 bg-purple-500 text-white rounded disabled:opacity-50 ml-2"
        >
          Test Realtime Query
        </button>
      </div>

      {loading && (
        <div className="mb-4 p-4 bg-yellow-100 border border-yellow-400 rounded">
          Loading...
        </div>
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 rounded">
          <h3 className="font-bold">Error:</h3>
          <pre className="text-sm mt-2">{error}</pre>
        </div>
      )}

      {results && (
        <div className="mb-4 p-4 bg-green-100 border border-green-400 rounded">
          <h3 className="font-bold">Results:</h3>
          <pre className="text-sm mt-2 whitespace-pre-wrap">
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
} 