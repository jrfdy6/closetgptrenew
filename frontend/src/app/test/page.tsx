'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useFirebase } from '@/lib/firebase-context';
import { performanceService } from '@/lib/services/performanceService';
import { usageService } from '@/lib/services/usageService';
import { privacyService } from '@/lib/services/privacyService';
import PersonalizationStatusCard from '@/components/PersonalizationStatusCard';
import UsageIndicator from '@/components/UsageIndicator';
import MonthlyStyleReport from '@/components/MonthlyStyleReport';
import StyleTrendsVisualization from '@/components/StyleTrendsVisualization';
import PerformanceMonitor from '@/components/PerformanceMonitor';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  RefreshCw,
  Activity,
  Database,
  Shield,
  BarChart3,
  Zap
} from 'lucide-react';

interface TestResult {
  name: string;
  status: 'pass' | 'fail' | 'pending';
  message: string;
  details?: any;
}

export default function TestPage() {
  const { user } = useFirebase();
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);
  const [privacySettings, setPrivacySettings] = useState<any>(null);
  const [styleReport, setStyleReport] = useState<any>(null);

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      // Load performance metrics
      setPerformanceMetrics(performanceService.getMetrics());
      
      // Load privacy settings
      if (user) {
        try {
          const summary = await privacyService.getPrivacySummary(user);
          setPrivacySettings(summary);
        } catch (error) {
          console.error('Error loading privacy summary:', error);
        }
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const runTests = async () => {
    setIsRunning(true);
    setTestResults([]);
    
    const results: TestResult[] = [];
    
    // Test 1: User Authentication
    try {
      if (!user) {
        results.push({
          name: 'User Authentication',
          status: 'fail',
          message: 'User not authenticated'
        });
      } else {
        results.push({
          name: 'User Authentication',
          status: 'pass',
          message: `Authenticated as ${user.email}`,
          details: { uid: user.uid }
        });
      }
    } catch (error) {
      results.push({
        name: 'User Authentication',
        status: 'fail',
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }
    
    // Test 2: Performance Service
    try {
      const metrics = performanceService.getMetrics();
      results.push({
        name: 'Performance Service',
        status: 'pass',
        message: 'Performance service is working',
        details: metrics
      });
      setPerformanceMetrics(metrics);
    } catch (error) {
      results.push({
        name: 'Performance Service',
        status: 'fail',
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }
    
    // Test 3: Usage Service
    try {
      if (user) {
        const usage = await usageService.getCurrentUsage(user);
        results.push({
          name: 'Usage Service',
          status: 'pass',
          message: 'Usage data loaded successfully',
          details: usage
        });
      } else {
        results.push({
          name: 'Usage Service',
          status: 'fail',
          message: 'User not authenticated'
        });
      }
    } catch (error) {
      results.push({
        name: 'Usage Service',
        status: 'fail',
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }
    
      // Test 4: Style Report API
      try {
        if (user) {
          const token = await user.getIdToken();
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-production.up.railway.app';
          const response = await fetch(`${apiUrl}/api/style-report`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
        
        if (response.ok) {
          const data = await response.json();
          results.push({
            name: 'Style Report API',
            status: 'pass',
            message: 'Style report generated successfully',
            details: data
          });
          setStyleReport(data);
        } else {
          const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
          results.push({
            name: 'Style Report API',
            status: 'fail',
            message: `API Error: ${error.detail || response.statusText}`
          });
        }
      } else {
        results.push({
          name: 'Style Report API',
          status: 'fail',
          message: 'User not authenticated'
        });
      }
    } catch (error) {
      results.push({
        name: 'Style Report API',
        status: 'fail',
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }
    
    // Test 5: Privacy Settings API
      try {
        if (user) {
          const data = await privacyService.getPrivacySummary(user);
          results.push({
            name: 'Privacy Settings API',
            status: 'pass',
            message: 'Privacy settings loaded successfully',
            details: data
          });
          setPrivacySettings(data);
        } else {
          results.push({
            name: 'Privacy Settings API',
            status: 'fail',
            message: 'User not authenticated'
          });
        }
      } catch (error) {
        results.push({
          name: 'Privacy Settings API',
          status: 'fail',
          message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
        });
      }
    
    // Test 6: Cache Functionality
      try {
        const testKey = 'test-cache-key';
        const testData = { test: 'data', timestamp: Date.now() };
        performanceService.set(testKey, testData, 60000);
        const retrieved = performanceService.get<{ test: string; timestamp: number }>(testKey);
        
        if (retrieved && retrieved.test === testData.test) {
          results.push({
            name: 'Cache Functionality',
            status: 'pass',
            message: 'Cache read/write working correctly'
          });
        } else {
          results.push({
            name: 'Cache Functionality',
            status: 'fail',
            message: 'Cache retrieval failed'
          });
        }
      } catch (error) {
        results.push({
          name: 'Cache Functionality',
          status: 'fail',
          message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
        });
      }
    
    setTestResults(results);
    setIsRunning(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'fail':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pass':
        return <Badge variant="default" className="bg-green-500">Pass</Badge>;
      case 'fail':
        return <Badge variant="destructive">Fail</Badge>;
      default:
        return <Badge variant="secondary">Pending</Badge>;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">System Test Page</h1>
          <p className="text-muted-foreground mt-2">
            Test all Phase 4 features and data propagation
          </p>
        </div>
        <Button onClick={runTests} disabled={isRunning}>
          {isRunning ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              Running Tests...
            </>
          ) : (
            <>
              <Activity className="h-4 w-4 mr-2" />
              Run All Tests
            </>
          )}
        </Button>
      </div>

      <Tabs defaultValue="tests" className="w-full">
        <TabsList>
          <TabsTrigger value="tests">Test Results</TabsTrigger>
          <TabsTrigger value="components">Components</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="privacy">Privacy</TabsTrigger>
        </TabsList>

        <TabsContent value="tests" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Test Results</CardTitle>
              <CardDescription>
                {testResults.length > 0 
                  ? `${testResults.filter(r => r.status === 'pass').length} of ${testResults.length} tests passed`
                  : 'Run tests to see results'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              {testResults.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  Click "Run All Tests" to start testing
                </div>
              ) : (
                <div className="space-y-3">
                  {testResults.map((result, index) => (
                    <div
                      key={index}
                      className="p-4 border rounded-lg space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(result.status)}
                          <span className="font-medium">{result.name}</span>
                        </div>
                        {getStatusBadge(result.status)}
                      </div>
                      <p className="text-sm text-muted-foreground">{result.message}</p>
                      {result.details && (
                        <details className="mt-2">
                          <summary className="text-sm cursor-pointer text-blue-600">
                            View Details
                          </summary>
                          <pre className="mt-2 p-2 bg-gray-100 dark:bg-gray-800 rounded text-xs overflow-auto">
                            {JSON.stringify(result.details, null, 2)}
                          </pre>
                        </details>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="components" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <PersonalizationStatusCard />
            <UsageIndicator />
          </div>
          <MonthlyStyleReport />
          <StyleTrendsVisualization />
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <PerformanceMonitor showDetails={true} />
          {performanceMetrics && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Performance Metrics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="p-4 bg-gray-100 dark:bg-gray-800 rounded text-xs overflow-auto">
                  {JSON.stringify(performanceMetrics, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="privacy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Privacy Settings
              </CardTitle>
            </CardHeader>
            <CardContent>
              {privacySettings ? (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Data Summary</h3>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded">
                        <div className="text-2xl font-bold">{privacySettings.data_summary?.outfits || 0}</div>
                        <div className="text-sm text-muted-foreground">Outfits</div>
                      </div>
                      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded">
                        <div className="text-2xl font-bold">{privacySettings.data_summary?.wardrobe_items || 0}</div>
                        <div className="text-sm text-muted-foreground">Wardrobe Items</div>
                      </div>
                      <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded">
                        <div className="text-2xl font-bold">{privacySettings.data_summary?.analytics_entries || 0}</div>
                        <div className="text-sm text-muted-foreground">Analytics</div>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">Privacy Settings</h3>
                    <div className="space-y-2">
                      {Object.entries(privacySettings.privacy_settings || {}).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                          <span className="text-sm capitalize">{key.replace(/_/g, ' ')}</span>
                          <Badge variant={value ? "default" : "secondary"}>
                            {value ? "Enabled" : "Disabled"}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Loading privacy settings...
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

