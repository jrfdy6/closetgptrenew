'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  TestTube, 
  ArrowLeft,
  RefreshCw, 
  CheckCircle,
  AlertCircle,
  Info,
  Shield,
  Eye,
  Bug
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';

export default function PersonalizationDemoDebugPage() {
  const router = useRouter();
  const { user } = useFirebase();
  const [debugInfo, setDebugInfo] = useState<any>({});
  const [isLoading, setIsLoading] = useState(false);
  const [testResults, setTestResults] = useState<string[]>([]);

  const addTestResult = (result: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${result}`]);
  };

  const runDebugTests = async () => {
    if (!user) {
      addTestResult('❌ No user authenticated');
      return;
    }

    setIsLoading(true);
    setTestResults([]);
    addTestResult('🔍 Starting debug tests...');

    try {
      // Test 1: Check user object
      addTestResult(`✅ User object: ${user.uid}`);
      addTestResult(`✅ User email: ${user.email || 'No email'}`);
      addTestResult(`✅ User displayName: ${user.displayName || 'No display name'}`);

      // Test 2: Check token generation
      try {
        const token = await user.getIdToken();
        addTestResult(`✅ Token generated: ${token.substring(0, 20)}...`);
        addTestResult(`✅ Token length: ${token.length}`);
      } catch (tokenError) {
        addTestResult(`❌ Token generation failed: ${tokenError}`);
      }

      // Test 3: Test API connectivity
      try {
        const response = await fetch('/api/outfits-existing-data/health');
        if (response.ok) {
          const data = await response.json();
          addTestResult(`✅ Health check passed: ${data.status}`);
        } else {
          addTestResult(`❌ Health check failed: ${response.status}`);
        }
      } catch (healthError) {
        addTestResult(`❌ Health check error: ${healthError}`);
      }

      // Test 4: Test authentication with token
      try {
        const token = await user.getIdToken();
        const response = await fetch('/api/outfits-existing-data/personalization-status', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        addTestResult(`📡 Response status: ${response.status}`);
        addTestResult(`📡 Response headers: ${JSON.stringify(Object.fromEntries(response.headers.entries()))}`);

        if (response.ok) {
          const data = await response.json();
          addTestResult(`✅ Personalization status retrieved successfully`);
          addTestResult(`📊 User ID: ${data.user_id}`);
          addTestResult(`📊 Personalization enabled: ${data.personalization_enabled}`);
          addTestResult(`📊 Has existing data: ${data.has_existing_data}`);
          addTestResult(`📊 Total interactions: ${data.total_interactions}`);
        } else {
          const errorText = await response.text();
          addTestResult(`❌ Personalization status failed: ${response.status} - ${errorText}`);
        }
      } catch (authError) {
        addTestResult(`❌ Authentication test failed: ${authError}`);
      }

      // Test 5: Check environment variables
      addTestResult(`🔍 NEXT_PUBLIC_BACKEND_URL: ${process.env.NEXT_PUBLIC_BACKEND_URL || 'Not set'}`);
      addTestResult(`🔍 API_BASE: https://closetgptrenew-production.up.railway.app`);

    } catch (error) {
      addTestResult(`❌ Debug test failed: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      setDebugInfo({
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        emailVerified: user.emailVerified,
        metadata: {
          creationTime: user.metadata.creationTime,
          lastSignInTime: user.metadata.lastSignInTime
        }
      });
    }
  }, [user]);

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="container mx-auto p-6">
          <div className="text-center">
            <Bug className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Authentication Required</h2>
            <p className="text-muted-foreground mb-4">Please sign in to run debug tests</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-stone-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      <div className="container mx-auto p-8">
        {/* Header */}
        <div className="flex items-center gap-6 mb-12">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => router.push('/personalization-demo')}
            className="flex items-center gap-3 border-2 border-stone-300 hover:border-stone-400 text-stone-700 hover:text-stone-900 hover:bg-stone-50 px-6 py-3 rounded-full font-medium transition-all duration-300 hover:scale-105"
          >
            <ArrowLeft className="h-5 w-5" />
            Back to Demo
          </Button>
          <div>
            <h1 className="text-4xl font-serif font-bold flex items-center gap-4 text-stone-900 dark:text-stone-100">
              <Bug className="h-10 w-10 text-red-500" />
              Debug Personalization
            </h1>
            <p className="text-stone-600 dark:text-stone-400 font-light text-lg mt-2">
              Debug authentication and connectivity issues
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: User Info */}
          <div className="space-y-6">
            {/* User Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="h-5 w-5 text-blue-500" />
                  User Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm font-medium">User ID</span>
                    <Badge variant="outline">{debugInfo.uid || 'Loading...'}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm font-medium">Email</span>
                    <Badge variant="outline">{debugInfo.email || 'No email'}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm font-medium">Display Name</span>
                    <Badge variant="outline">{debugInfo.displayName || 'No name'}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm font-medium">Email Verified</span>
                    <Badge variant={debugInfo.emailVerified ? "default" : "secondary"}>
                      {debugInfo.emailVerified ? "Yes" : "No"}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Environment Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-green-500" />
                  Environment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm font-medium">Backend URL</span>
                    <Badge variant="outline">
                      {process.env.NEXT_PUBLIC_BACKEND_URL || 'Default Railway URL'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm font-medium">API Base</span>
                    <Badge variant="outline">https://closetgptrenew-production.up.railway.app</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Debug Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TestTube className="h-5 w-5 text-purple-500" />
                  Debug Tests
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={runDebugTests}
                  disabled={isLoading}
                  className="w-full"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Running Debug Tests...
                    </>
                  ) : (
                    <>
                      <Bug className="h-4 w-4 mr-2" />
                      Run Debug Tests
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Test Results */}
          <div className="space-y-6">
            {/* Test Results */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-500" />
                  Debug Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                {testResults.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Bug className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No debug tests run yet. Click "Run Debug Tests" to start.</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {testResults.map((result, index) => (
                      <div key={index} className="p-2 bg-gray-50 dark:bg-gray-800 rounded text-sm">
                        {result}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Debug Info */}
        <Card className="mt-8 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
          <CardContent className="p-6">
            <h3 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
              🐛 Debug Information
            </h3>
            <div className="text-sm text-yellow-700 dark:text-yellow-300">
              <p className="mb-2">This debug page helps identify authentication and connectivity issues:</p>
              <ul className="space-y-1 text-xs">
                <li>• Checks Firebase user object and token generation</li>
                <li>• Tests API connectivity and authentication</li>
                <li>• Verifies environment variables</li>
                <li>• Shows detailed error information</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
