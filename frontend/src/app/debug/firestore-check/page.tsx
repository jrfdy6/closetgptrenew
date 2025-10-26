"use client";

import { useState } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RefreshCw, CheckCircle, XCircle } from 'lucide-react';

export default function FirestoreCheckPage() {
  const { user } = useAuthContext();
  const [testing, setTesting] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const runFirestoreTest = async () => {
    if (!user) {
      setError('Please log in first');
      return;
    }

    setTesting(true);
    setError(null);
    setResults(null);

    try {
      console.log('🧪 Running Firestore test...');
      
      // Import Firestore
      const { db } = await import('@/lib/firebase/config');
      const { collection, query, where, getDocs, getDocsFromServer } = await import('firebase/firestore');
      
      // Calculate week start (Sunday 00:00:00)
      const now = new Date();
      const dayOfWeek = now.getDay();
      const weekStart = new Date(now);
      weekStart.setDate(now.getDate() - dayOfWeek);
      weekStart.setHours(0, 0, 0, 0);
      
      console.log('📅 Week starts:', weekStart.toISOString());
      console.log('👤 User ID:', user.uid);
      console.log('📧 User email:', user.email);
      
      // Query outfit_history collection
      const historyRef = collection(db, 'outfit_history');
      const historyQuery = query(
        historyRef,
        where('user_id', '==', user.uid)
      );
      
      // Test both cached and server queries
      console.log('🔍 Testing cached query...');
      const cachedSnapshot = await getDocs(historyQuery);
      console.log(`✅ Cached query returned ${cachedSnapshot.size} entries`);
      
      console.log('🔍 Testing server query...');
      const freshSnapshot = await getDocsFromServer(historyQuery);
      console.log(`✅ Server query returned ${freshSnapshot.size} entries`);
      
      // Process entries
      const allEntries: any[] = [];
      let wornThisWeek = 0;
      
      freshSnapshot.forEach((doc) => {
        const data = doc.data();
        const dateWorn = data.date_worn;
        
        let wornDate: Date | null = null;
        if (typeof dateWorn === 'number') {
          wornDate = new Date(dateWorn);
        } else if (dateWorn && dateWorn.toDate) {
          wornDate = dateWorn.toDate();
        } else if (typeof dateWorn === 'string') {
          wornDate = new Date(dateWorn);
        }
        
        const isThisWeek = wornDate ? wornDate >= weekStart : false;
        if (isThisWeek) wornThisWeek++;
        
        allEntries.push({
          id: doc.id,
          outfit_name: data.outfit_name || 'Unknown',
          date_worn: dateWorn,
          parsed_date: wornDate?.toISOString(),
          is_this_week: isThisWeek
        });
      });
      
      setResults({
        success: true,
        user_id: user.uid,
        user_email: user.email,
        week_start: weekStart.toISOString(),
        cached_count: cachedSnapshot.size,
        fresh_count: freshSnapshot.size,
        worn_this_week: wornThisWeek,
        all_entries: allEntries,
        timestamp: new Date().toISOString()
      });
      
      console.log('✅ Test completed successfully:', {
        cached: cachedSnapshot.size,
        fresh: freshSnapshot.size,
        this_week: wornThisWeek
      });
      
    } catch (err: any) {
      console.error('❌ Test failed:', err);
      setError(err.message || 'Test failed');
    } finally {
      setTesting(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Firestore Diagnostic Test</CardTitle>
            <CardDescription>Please log in to run the test</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 dark:text-gray-400">
              You need to be logged in to test Firestore queries.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Firestore Diagnostic Test</CardTitle>
          <CardDescription>
            Test outfit_history collection queries on custom domain
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* User Info */}
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Current User</h3>
            <p className="text-sm">Email: {user.email}</p>
            <p className="text-sm">UID: {user.uid}</p>
          </div>

          {/* Test Button */}
          <Button 
            onClick={runFirestoreTest} 
            disabled={testing}
            className="w-full"
          >
            {testing ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4 mr-2" />
                Run Firestore Test
              </>
            )}
          </Button>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
              <div className="flex items-start gap-2">
                <XCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-red-900 dark:text-red-100">Test Failed</h4>
                  <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results Display */}
          {results && (
            <div className="space-y-4">
              <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                <div className="flex items-start gap-2 mb-4">
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-green-900 dark:text-green-100">Test Successful</h4>
                    <p className="text-sm text-green-700 dark:text-green-300">
                      Firestore queries are working on custom domain
                    </p>
                  </div>
                </div>

                {/* Summary Stats */}
                <div className="grid grid-cols-3 gap-4 mt-4">
                  <div className="bg-white dark:bg-gray-800 p-3 rounded-lg">
                    <div className="text-2xl font-bold">{results.cached_count}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Cached Entries</div>
                  </div>
                  <div className="bg-white dark:bg-gray-800 p-3 rounded-lg">
                    <div className="text-2xl font-bold">{results.fresh_count}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">Server Entries</div>
                  </div>
                  <div className="bg-white dark:bg-gray-800 p-3 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{results.worn_this_week}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">This Week</div>
                  </div>
                </div>
              </div>

              {/* All Entries */}
              <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
                <h4 className="font-semibold mb-3">All Outfit History Entries</h4>
                {results.all_entries.length === 0 ? (
                  <p className="text-gray-500 dark:text-gray-400 text-sm">No entries found</p>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {results.all_entries.map((entry: any, index: number) => (
                      <div 
                        key={entry.id} 
                        className={`p-3 rounded-lg text-sm ${
                          entry.is_this_week 
                            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' 
                            : 'bg-gray-50 dark:bg-gray-900'
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium">{entry.outfit_name}</div>
                            <div className="text-xs text-gray-600 dark:text-gray-400">
                              {entry.parsed_date ? new Date(entry.parsed_date).toLocaleString() : 'Invalid date'}
                            </div>
                          </div>
                          {entry.is_this_week && (
                            <span className="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded">
                              This Week
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Raw Data */}
              <details className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
                <summary className="cursor-pointer font-semibold">View Raw Data</summary>
                <pre className="mt-2 text-xs overflow-x-auto">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </details>
            </div>
          )}

          {/* Instructions */}
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <h4 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-2">Test Instructions</h4>
            <ol className="text-sm text-yellow-800 dark:text-yellow-200 space-y-1 list-decimal list-inside">
              <li>Click "Run Firestore Test" above</li>
              <li>Check if the test succeeds and shows your outfit history</li>
              <li>Note the "This Week" count</li>
              <li>Go wear an outfit from the dashboard or outfits page</li>
              <li>Come back here and run the test again</li>
              <li>The "This Week" count should increase by 1</li>
            </ol>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

