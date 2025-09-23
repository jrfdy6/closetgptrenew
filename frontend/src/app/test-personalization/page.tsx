'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Brain, 
  TestTube, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Info,
  Heart,
  TrendingUp,
  Palette,
  Shirt,
  Calendar,
  Database,
  Zap,
  Eye,
  Download
} from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import { useExistingDataPersonalization } from '@/lib/hooks/useExistingDataPersonalization';
import { PersonalizedOutfit } from '@/lib/services/existingDataPersonalizationService';
import Navigation from '@/components/Navigation';

interface TestResult {
  testName: string;
  status: 'success' | 'error' | 'warning' | 'info';
  message: string;
  data?: any;
  timestamp: string;
}

export default function TestPersonalizationPage() {
  const { user } = useFirebase();
  const {
    personalizationStatus,
    userPreferences,
    isLoading,
    error,
    isReadyForPersonalization,
    hasExistingData,
    totalInteractions,
    topColors,
    topStyles,
    topOccasions,
    favoriteItemsCount,
    mostWornItemsCount,
    generatePersonalizedOutfit,
    refreshPersonalizationData,
    checkHealth,
    dataSource,
    usesExistingData
  } = useExistingDataPersonalization();

  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunningTests, setIsRunningTests] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<PersonalizedOutfit | null>(null);
  const [testRequest, setTestRequest] = useState({
    occasion: 'Business',
    style: 'Classic',
    mood: 'Confident'
  });

  const addTestResult = (testName: string, status: TestResult['status'], message: string, data?: any) => {
    const result: TestResult = {
      testName,
      status,
      message,
      data,
      timestamp: new Date().toLocaleTimeString()
    };
    setTestResults(prev => [...prev, result]);
  };

  const runComprehensiveTests = async () => {
    if (!user) {
      addTestResult('Authentication', 'error', 'User not authenticated');
      return;
    }

    setIsRunningTests(true);
    setTestResults([]);

    try {
      // Test 1: Health Check
      addTestResult('Health Check', 'info', 'Testing system health...');
      const isHealthy = await checkHealth();
      addTestResult('Health Check', isHealthy ? 'success' : 'error', 
        isHealthy ? 'System is healthy' : 'System health check failed');

      // Test 2: Personalization Status
      addTestResult('Personalization Status', 'info', 'Checking personalization status...');
      if (personalizationStatus) {
        addTestResult('Personalization Status', 'success', 
          `Status loaded: ${totalInteractions} interactions, ${isReadyForPersonalization ? 'Ready' : 'Learning'}`,
          personalizationStatus);
      } else {
        addTestResult('Personalization Status', 'error', 'Failed to load personalization status');
      }

      // Test 3: User Preferences
      addTestResult('User Preferences', 'info', 'Loading user preferences...');
      if (userPreferences) {
        addTestResult('User Preferences', 'success', 
          `Preferences loaded: ${topColors.length} colors, ${topStyles.length} styles, ${topOccasions.length} occasions`,
          userPreferences);
      } else {
        addTestResult('User Preferences', 'error', 'Failed to load user preferences');
      }

      // Test 4: Data Source Analysis
      addTestResult('Data Source Analysis', 'info', 'Analyzing data sources...');
      if (hasExistingData) {
        addTestResult('Data Source Analysis', 'success', 
          `Found existing data: ${favoriteItemsCount} favorites, ${mostWornItemsCount} most worn items`,
          { dataSource, usesExistingData, favoriteItemsCount, mostWornItemsCount });
      } else {
        addTestResult('Data Source Analysis', 'warning', 'No existing data found - personalization will be limited');
      }

      // Test 5: Outfit Generation
      addTestResult('Outfit Generation', 'info', 'Testing personalized outfit generation...');
      try {
        const outfit = await generatePersonalizedOutfit({
          occasion: testRequest.occasion,
          style: testRequest.style,
          mood: testRequest.mood,
          weather: {
            temperature: 72,
            condition: 'Clear',
            humidity: 50,
            wind_speed: 5,
            location: 'Test Location'
          }
        });

        if (outfit) {
          setGeneratedOutfit(outfit);
          addTestResult('Outfit Generation', 'success', 
            `Outfit generated: ${outfit.items.length} items, personalization ${outfit.personalization_applied ? 'applied' : 'not applied'}`,
            outfit);
        } else {
          addTestResult('Outfit Generation', 'error', 'Failed to generate outfit');
        }
      } catch (err) {
        addTestResult('Outfit Generation', 'error', `Generation failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }

      // Test 6: Data Refresh
      addTestResult('Data Refresh', 'info', 'Testing data refresh...');
      try {
        await refreshPersonalizationData();
        addTestResult('Data Refresh', 'success', 'Data refreshed successfully');
      } catch (err) {
        addTestResult('Data Refresh', 'error', `Refresh failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }

    } catch (err) {
      addTestResult('Test Suite', 'error', `Test suite failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsRunningTests(false);
    }
  };

  const exportTestResults = () => {
    const data = {
      timestamp: new Date().toISOString(),
      user: user?.uid || 'anonymous',
      testResults,
      personalizationStatus,
      userPreferences,
      generatedOutfit
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `personalization-test-results-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'success': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'warning': return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'info': return <Info className="h-4 w-4 text-blue-500" />;
    }
  };

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'success': return 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800';
      case 'error': return 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800';
      case 'info': return 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800';
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="container mx-auto p-6">
          <div className="text-center">
            <TestTube className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Authentication Required</h2>
            <p className="text-muted-foreground mb-4">Please sign in to test personalization with your data</p>
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
          <div>
            <h1 className="text-4xl font-serif font-bold flex items-center gap-4 text-stone-900 dark:text-stone-100">
              <TestTube className="h-10 w-10 text-blue-500" />
              Personalization Testing
            </h1>
            <p className="text-stone-600 dark:text-stone-400 font-light text-lg mt-2">
              Test the existing data personalization system with your real Firebase data
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Test Controls */}
          <div className="space-y-6">
            {/* Test Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-blue-500" />
                  Test Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Occasion</label>
                  <Select value={testRequest.occasion} onValueChange={(value) => setTestRequest(prev => ({ ...prev, occasion: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Casual">Casual</SelectItem>
                      <SelectItem value="Business">Business</SelectItem>
                      <SelectItem value="Party">Party</SelectItem>
                      <SelectItem value="Date">Date</SelectItem>
                      <SelectItem value="Interview">Interview</SelectItem>
                      <SelectItem value="Weekend">Weekend</SelectItem>
                      <SelectItem value="Loungewear">Loungewear</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Style</label>
                  <Select value={testRequest.style} onValueChange={(value) => setTestRequest(prev => ({ ...prev, style: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Classic">Classic</SelectItem>
                      <SelectItem value="Modern">Modern</SelectItem>
                      <SelectItem value="Preppy">Preppy</SelectItem>
                      <SelectItem value="Minimalist">Minimalist</SelectItem>
                      <SelectItem value="Streetwear">Streetwear</SelectItem>
                      <SelectItem value="Business Casual">Business Casual</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Mood</label>
                  <Select value={testRequest.mood} onValueChange={(value) => setTestRequest(prev => ({ ...prev, mood: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Confident">Confident</SelectItem>
                      <SelectItem value="Relaxed">Relaxed</SelectItem>
                      <SelectItem value="Professional">Professional</SelectItem>
                      <SelectItem value="Playful">Playful</SelectItem>
                      <SelectItem value="Elegant">Elegant</SelectItem>
                      <SelectItem value="Bold">Bold</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button 
                  onClick={runComprehensiveTests}
                  disabled={isRunningTests}
                  className="w-full"
                >
                  {isRunningTests ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Running Tests...
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4 mr-2" />
                      Run Comprehensive Tests
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Current Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-green-500" />
                  Current Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                      {totalInteractions}
                    </div>
                    <div className="text-sm text-blue-600 dark:text-blue-400">Interactions</div>
                  </div>
                  
                  <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="text-xl font-bold text-green-600 dark:text-green-400">
                      {favoriteItemsCount + mostWornItemsCount}
                    </div>
                    <div className="text-sm text-green-600 dark:text-green-400">Engaged Items</div>
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <span className="font-medium">Personalization Ready</span>
                  <Badge variant={isReadyForPersonalization ? "default" : "secondary"}>
                    {isReadyForPersonalization ? "Yes" : "Not Yet"}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <span className="font-medium">Data Source</span>
                  <Badge variant="outline">
                    {usesExistingData ? "Existing Firebase Data" : "Unknown"}
                  </Badge>
                </div>

                {/* Top Preferences */}
                {topColors.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Palette className="h-4 w-4 text-purple-500" />
                      <span className="text-sm font-medium">Your Top Colors</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {topColors.slice(0, 5).map((color, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {color}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {topStyles.length > 0 && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Shirt className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-medium">Your Top Styles</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {topStyles.slice(0, 5).map((style, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {style}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Test Results */}
          <div className="space-y-6">
            {/* Test Results */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="h-5 w-5 text-purple-500" />
                    Test Results
                  </CardTitle>
                  {testResults.length > 0 && (
                    <Button onClick={exportTestResults} variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Export
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {testResults.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <TestTube className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No tests run yet. Click "Run Comprehensive Tests" to start.</p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {testResults.map((result, index) => (
                      <div 
                        key={index} 
                        className={`p-3 rounded-lg border ${getStatusColor(result.status)}`}
                      >
                        <div className="flex items-start gap-3">
                          {getStatusIcon(result.status)}
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium">{result.testName}</span>
                              <span className="text-xs text-muted-foreground">{result.timestamp}</span>
                            </div>
                            <p className="text-sm">{result.message}</p>
                            {result.data && (
                              <details className="mt-2">
                                <summary className="text-xs cursor-pointer text-muted-foreground">
                                  View Data
                                </summary>
                                <pre className="text-xs mt-2 p-2 bg-gray-100 dark:bg-gray-800 rounded overflow-x-auto">
                                  {JSON.stringify(result.data, null, 2)}
                                </pre>
                              </details>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Generated Outfit */}
            {generatedOutfit && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Heart className="h-5 w-5 text-red-500" />
                    Generated Outfit
                    {generatedOutfit.personalization_applied && (
                      <Badge variant="default" className="ml-2">
                        Personalized
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Style</div>
                        <div className="font-semibold">{generatedOutfit.style}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Occasion</div>
                        <div className="font-semibold">{generatedOutfit.occasion}</div>
                      </div>
                    </div>

                    {generatedOutfit.personalization_applied && (
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <div className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-2">
                          Personalization Applied
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">Score:</span>
                            <span className="ml-2 font-medium">
                              {generatedOutfit.personalization_score?.toFixed(2) || 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Interactions:</span>
                            <span className="ml-2 font-medium">{generatedOutfit.user_interactions}</span>
                          </div>
                        </div>
                      </div>
                    )}

                    <div>
                      <div className="text-sm font-medium text-muted-foreground mb-2">
                        Items ({generatedOutfit.items.length})
                      </div>
                      <div className="space-y-2">
                        {generatedOutfit.items.map((item, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                            <div>
                              <div className="font-medium">{item.name}</div>
                              <div className="text-sm text-muted-foreground">{item.type} • {item.color}</div>
                            </div>
                            <Badge variant="outline">{item.color}</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <Card className="mt-8 border-red-200 bg-red-50 dark:bg-red-900/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-red-600">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Testing Info */}
        <Card className="mt-8 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <CardContent className="p-6">
            <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
              🧪 Testing Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-700 dark:text-blue-300">
              <div>
                <div className="font-medium mb-1">What This Tests:</div>
                <ul className="space-y-1 text-xs">
                  <li>• System health and connectivity</li>
                  <li>• Personalization data loading</li>
                  <li>• User preference extraction</li>
                  <li>• Outfit generation with personalization</li>
                  <li>• Data refresh functionality</li>
                </ul>
              </div>
              <div>
                <div className="font-medium mb-1">Your Data Sources:</div>
                <ul className="space-y-1 text-xs">
                  <li>• Wardrobe item favorites</li>
                  <li>• Item wear counts</li>
                  <li>• Outfit favorites</li>
                  <li>• Style profile preferences</li>
                  <li>• User interaction history</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
