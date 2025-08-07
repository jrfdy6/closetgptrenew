"use client";

import { useState, useEffect } from 'react';
import { db, auth } from '@/lib/firebase/config';
import { 
  collection, 
  getDocs, 
  query, 
  where, 
  onSnapshot, 
  addDoc,
  doc,
  getDoc,
  setDoc
} from 'firebase/firestore';
import { onAuthStateChanged, signInAnonymously, signInWithEmailAndPassword } from 'firebase/auth';

export default function TestFirestore() {
  const [mounted, setMounted] = useState(false);
  const [status, setStatus] = useState<string>('Loading...');
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);
  const [authStatus, setAuthStatus] = useState<string>('Checking auth...');
  const [user, setUser] = useState<any>(null);
  const [testResults, setTestResults] = useState<any>({});
  const [authMethod, setAuthMethod] = useState<'anonymous' | 'email'>('email');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  // Handle hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  // Main Firestore test effect - only run when mounted
  useEffect(() => {
    if (!mounted) return; // Don't run until mounted
    const testFirestore = async () => {
      try {
        setStatus('Testing Firestore connection...');
        
        // Test 1: Check if we're in browser
        console.log('🔍 Environment check:', {
          isBrowser: mounted,
          hasFirebaseConfig: !!process.env.NEXT_PUBLIC_FIREBASE_API_KEY
        });
        
        // Test 2: Check Firebase config
        console.log('🔍 Firebase config check:', {
          apiKey: !!process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
          projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
          authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
        });
        
        // Test 3: Check DB object
        console.log('🔍 DB object:', db);
        
        if (!db) {
          throw new Error('Firestore DB object is undefined');
        }

        // Test 4: Check authentication based on method
        setAuthStatus('Checking authentication...');
        
        // Check if user is already authenticated
        const currentUser = auth.currentUser;
        console.log('🔍 Current user on mount:', currentUser);
        
        if (currentUser) {
          console.log('🔍 User already authenticated, running tests...');
          setUser(currentUser);
          setAuthStatus(`Authenticated as: ${currentUser.uid}`);
          testFirestoreQueries();
        } else {
          console.log('🔍 No current user, setting up auth listener...');
          const unsubscribe = onAuthStateChanged(auth, (user) => {
            console.log('🔍 Auth state changed:', user);
            setUser(user);
            
            if (user) {
              setAuthStatus(`Authenticated as: ${user.uid}`);
              testFirestoreQueries();
            } else {
              setAuthStatus('Not authenticated - please sign in below');
            }
          });

          return () => unsubscribe();
        }
        
      } catch (err) {
        console.error('❌ Firestore test error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setStatus('Error occurred');
      }
    };

    testFirestore();
  }, [mounted]);

  // Don't render dynamic content until after hydration
  if (!mounted) {
    return (
      <div className="container mx-auto p-8">
        <h1 className="text-2xl font-bold mb-4">Firestore Connection Test</h1>
        <div className="mb-4">
          <strong>Status:</strong> Loading...
        </div>
        <div className="mb-4">
          <strong>Auth Status:</strong> Initializing...
        </div>
      </div>
    );
  }

  const attemptSignIn = async () => {
    try {
      setAuthStatus('Signing in...');
      if (authMethod === 'anonymous') {
        await signInAnonymously(auth);
        setAuthStatus('Signed in anonymously');
      } else if (authMethod === 'email') {
        if (!email || !password) {
          setAuthStatus('Please enter both email and password');
          return;
        }
        await signInWithEmailAndPassword(auth, email, password);
        setAuthStatus('Signed in with email');
      }
    } catch (error) {
      console.error('❌ Sign-in failed:', error);
      if (error instanceof Error && error.message.includes('admin-restricted-operation')) {
        setAuthStatus('Anonymous auth disabled - please use email/password or enable anonymous auth in Firebase Console');
      } else {
        setAuthStatus(`Auth failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
  };

  const testFirestoreQueries = async () => {
    const results: any = {};
    
    try {
      setStatus('Running comprehensive Firestore tests...');
      
      // Test 1: Basic collection reference
      console.log('🔍 Test 1: Basic collection reference');
      const wardrobeRef = collection(db, 'wardrobe');
      console.log('🔍 Wardrobe collection ref:', wardrobeRef);
      results.collectionRef = 'Success';
      
      // Test 2: getDocs query
      console.log('🔍 Test 2: getDocs query');
      try {
        const querySnapshot = await getDocs(wardrobeRef);
        console.log('🔍 Query snapshot:', querySnapshot);
        console.log('🔍 Number of documents:', querySnapshot.size);
        
        const documents = querySnapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
        
        console.log('🔍 Documents:', documents);
        setData(documents);
        results.getDocs = `Success - Found ${documents.length} documents`;
      } catch (err) {
        console.error('❌ getDocs error:', err);
        results.getDocs = `Failed - ${err instanceof Error ? err.message : 'Unknown error'}`;
      }
      
      // Test 3: Document creation test
      console.log('🔍 Test 3: Document creation test');
      try {
        const testDoc = await addDoc(collection(db, 'test'), {
          timestamp: new Date(),
          test: true,
          message: 'Test document created by Firestore test page'
        });
        console.log('🔍 Test document created:', testDoc.id);
        results.createDoc = `Success - Created doc ${testDoc.id}`;
        
        // Clean up test document
        setTimeout(async () => {
          try {
            await setDoc(doc(db, 'test', testDoc.id), { deleted: true });
            console.log('🔍 Test document marked for deletion');
          } catch (err) {
            console.error('❌ Failed to mark test doc for deletion:', err);
          }
        }, 1000);
      } catch (err) {
        console.error('❌ Document creation error:', err);
        results.createDoc = `Failed - ${err instanceof Error ? err.message : 'Unknown error'}`;
      }
      
      // Test 4: Real-time listener (this is where 400 errors occur)
      console.log('🔍 Test 4: Real-time listener test');
      try {
        const unsubscribe = onSnapshot(wardrobeRef, (snapshot) => {
          console.log('🔍 Real-time snapshot received:', snapshot);
          console.log('🔍 Real-time docs count:', snapshot.size);
          results.realtimeListener = 'Success - Real-time updates working';
        }, (error) => {
          console.error('❌ Real-time listener error:', error);
          results.realtimeListener = `Failed - ${error.message}`;
        });
        
        // Clean up after 3 seconds
        setTimeout(() => {
          unsubscribe();
          console.log('🔍 Real-time listener cleaned up');
        }, 3000);
      } catch (err) {
        console.error('❌ Real-time listener setup error:', err);
        results.realtimeListener = `Setup failed - ${err instanceof Error ? err.message : 'Unknown error'}`;
      }
      
      // Test 5: Specific document read
      console.log('🔍 Test 5: Specific document read');
      try {
        const testDocRef = doc(db, 'wardrobe', 'test-doc-id');
        const testDocSnap = await getDoc(testDocRef);
        console.log('🔍 Test doc read result:', testDocSnap.exists());
        results.specificDocRead = testDocSnap.exists() ? 'Success - Document exists' : 'Success - Document does not exist';
      } catch (err) {
        console.error('❌ Specific document read error:', err);
        results.specificDocRead = `Failed - ${err instanceof Error ? err.message : 'Unknown error'}`;
      }
      
      setTestResults(results);
      setStatus('Comprehensive tests completed');
      
    } catch (err) {
      console.error('❌ Comprehensive test error:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('Comprehensive tests failed');
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">Firestore Connection Test</h1>
      
      <div className="mb-6 p-4 bg-blue-100 border border-blue-400 text-blue-700 rounded">
        <h2 className="text-lg font-bold mb-2">Authentication</h2>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              name="authMethod"
              value="anonymous"
              checked={authMethod === 'anonymous'}
              onChange={(e) => setAuthMethod(e.target.value as 'anonymous')}
              className="mr-2"
            />
            Anonymous (requires enabling in Firebase Console)
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="authMethod"
              value="email"
              checked={authMethod === 'email'}
              onChange={(e) => setAuthMethod(e.target.value as 'email')}
              className="mr-2"
            />
            Email/Password (use your actual login credentials)
          </label>
        </div>
        
        {authMethod === 'email' && (
          <div className="mt-4 space-y-2">
            <input
              type="email"
              placeholder="Your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2 border rounded"
            />
            <input
              type="password"
              placeholder="Your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 border rounded"
            />
            <button
              onClick={attemptSignIn}
              className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
            >
              Sign In
            </button>
          </div>
        )}
        
        {authMethod === 'anonymous' && (
          <div className="mt-4">
            <button
              onClick={attemptSignIn}
              className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
            >
              Sign In Anonymously
            </button>
          </div>
        )}
      </div>
      
      <div className="mb-4">
        <strong>Status:</strong> {status}
      </div>
      
      <div className="mb-4">
        <strong>Auth Status:</strong> {authStatus}
      </div>
      
      {user && (
        <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          <strong>User:</strong> {user.uid} ({user.isAnonymous ? 'Anonymous' : 'Authenticated'})
        </div>
      )}
      
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {Object.keys(testResults).length > 0 && (
        <div className="mb-4">
          <h2 className="text-xl font-bold mb-2">Test Results:</h2>
          <div className="bg-gray-100 p-4 rounded">
            {Object.entries(testResults).map(([test, result]) => (
              <div key={test} className="mb-2">
                <strong>{test}:</strong> {String(result)}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {data && (
        <div className="mb-4">
          <strong>Data:</strong>
          <pre className="bg-gray-100 p-4 rounded mt-2 overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
      
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-2">Debug Information</h2>
        <div className="bg-gray-100 p-4 rounded">
          <p><strong>Firebase Config:</strong></p>
          <ul className="list-disc list-inside mt-2">
            <li>API Key: {process.env.NEXT_PUBLIC_FIREBASE_API_KEY ? 'Set' : 'Not Set'}</li>
            <li>Project ID: {process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'Not Set'}</li>
            <li>Auth Domain: {process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || 'Not Set'}</li>
            <li>Storage Bucket: {process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || 'Not Set'}</li>
            <li>Messaging Sender ID: {process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || 'Not Set'}</li>
            <li>App ID: {process.env.NEXT_PUBLIC_FIREBASE_APP_ID || 'Not Set'}</li>
          </ul>
          
          <p className="mt-4"><strong>Environment:</strong></p>
          <ul className="list-disc list-inside mt-2">
            <li>Is Browser: {mounted ? 'Yes' : 'No'}</li>
            <li>DB Object: {mounted && db ? 'Available' : 'Not Available'}</li>
            <li>Auth Object: {mounted && auth ? 'Available' : 'Not Available'}</li>
          </ul>
        </div>
      </div>
      
      <div className="mt-4">
        <h3 className="text-lg font-bold mb-2">Troubleshooting Steps:</h3>
        <ol className="list-decimal list-inside space-y-2">
          <li>Enter your actual login credentials above</li>
          <li>If anonymous auth is disabled, enable it in Firebase Console → Authentication → Sign-in method</li>
          <li>Check if you're signed in (should see user ID above)</li>
          <li>Look for 400 errors in browser console</li>
          <li>Check Firebase console for billing status</li>
          <li>Verify Firestore database region matches your location</li>
          <li>Check if the project has any quotas or restrictions</li>
        </ol>
      </div>
      
      <div className="mt-4 p-4 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
        <strong>Next Steps:</strong>
        <ul className="list-disc list-inside mt-2">
          <li>If you see 400 errors in console, check Firebase Console → Project Settings → Service Accounts</li>
          <li>Verify billing is enabled in Firebase Console → Usage and Billing</li>
          <li>Check if there are any quotas or restrictions in Firebase Console → Firestore Database</li>
          <li>Consider checking the Firebase project's region settings</li>
          <li><strong>Enable Anonymous Authentication:</strong> Firebase Console → Authentication → Sign-in method → Anonymous → Enable</li>
        </ul>
      </div>
    </div>
  );
} 