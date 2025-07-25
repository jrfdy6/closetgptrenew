'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { FixButton } from '@/components/FixButton';

interface DiagnosticData {
  status: string;
  timestamp: number;
  system_info?: {
    python_version: string;
    platform: string;
    uptime: string;
  };
  diagnostic_data?: {
    outfits_count: number;
    traces_count: number;
    last_test_outfit_id: string;
  };
  message?: string;
  latest_outfit?: {
    id: string;
    name: string;
    generation_method: string;
    was_successful: boolean;
    items_count: number;
    created_at: number;
    validation_errors: string[];
    generation_trace: any[];
  };
  error?: string;
}

export default function AnalyticsTestPage() {
  const [healthData, setHealthData] = useState<DiagnosticData | null>(null);
  const [tracesData, setTracesData] = useState<DiagnosticData | null>(null);
  const [analytics, setAnalytics] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDiagnostics = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch health data
      const healthResponse = await fetch('/api/diagnostics/public/health');
      if (!healthResponse.ok) {
        throw new Error(`Health endpoint failed: ${healthResponse.status}`);
      }
      const healthResult = await healthResponse.json();
      setHealthData(healthResult);

      // Fetch outfit traces data
      const tracesResponse = await fetch('/api/diagnostics/public/outfit-traces');
      if (!tracesResponse.ok) {
        throw new Error(`Traces endpoint failed: ${tracesResponse.status}`);
      }
      const tracesResult = await tracesResponse.json();
      setTracesData(tracesResult);

      // Fetch analytics data (for fallback usage)
      const analyticsResponse = await fetch('/api/analytics/outfits');
      if (analyticsResponse.ok) {
        const analyticsResult = await analyticsResponse.json();
        setAnalytics(analyticsResult.data);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
  }, []);

  const formatTimestamp = (timestamp: number) => {
    try {
      return new Date(timestamp * 1000).toLocaleString();
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return 'Invalid timestamp';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Analytics Test Page</h1>
        <Button onClick={fetchDiagnostics} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </Button>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-700 font-medium">Error: {error}</p>
          </CardContent>
        </Card>
      )}

      {/* Fallback usage metric */}
      {analytics && (
        <div className="mb-4">
          <span role="img" aria-label="tools">🛠</span> {typeof analytics.fallback_usage_percentage === 'number' ? analytics.fallback_usage_percentage.toFixed(1) : '0'}% of outfits used fallback logic this week
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Health Data */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              System Health
              {healthData && (
                <Badge variant={healthData.status === 'healthy' ? 'default' : 'destructive'}>
                  {healthData.status}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {healthData ? (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Timestamp</p>
                  <p className="font-mono text-sm">{healthData.timestamp ? formatTimestamp(healthData.timestamp) : 'Unknown'}</p>
                </div>
                
                {healthData.system_info && (
                  <div>
                    <p className="text-sm text-muted-foreground">System Info</p>
                    <div className="space-y-1">
                      <p className="font-mono text-xs">Platform: {healthData.system_info.platform || 'Unknown'}</p>
                      <p className="font-mono text-xs">Python: {healthData.system_info.python_version ? healthData.system_info.python_version.split(' ')[0] : 'Unknown'}</p>
                      <p className="font-mono text-xs">Uptime: {healthData.system_info.uptime || 'Unknown'}</p>
                    </div>
                  </div>
                )}

                {healthData.diagnostic_data && (
                  <div>
                    <p className="text-sm text-muted-foreground">Diagnostic Data</p>
                    <div className="space-y-1">
                      <p className="font-mono text-xs">Outfits: {healthData.diagnostic_data.outfits_count || 0}</p>
                      <p className="font-mono text-xs">Traces: {healthData.diagnostic_data.traces_count || 0}</p>
                      <p className="font-mono text-xs">Last Test ID: {healthData.diagnostic_data.last_test_outfit_id || 'None'}</p>
                    </div>
                  </div>
                )}

                {healthData.message && (
                  <div>
                    <p className="text-sm text-muted-foreground">Message</p>
                    <p className="text-sm">{healthData.message}</p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-muted-foreground">No health data available</p>
            )}
          </CardContent>
        </Card>

        {/* Outfit Traces Data */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Latest Outfit Trace
              {tracesData && (
                <Badge variant={tracesData.status === 'success' ? 'default' : 'secondary'}>
                  {tracesData.status}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {tracesData?.latest_outfit ? (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Outfit Details</p>
                  <div className="space-y-1">
                    <p className="font-mono text-xs">ID: {tracesData.latest_outfit.id || 'Unknown'}</p>
                    <p className="font-mono text-xs">Name: {tracesData.latest_outfit.name || 'Unknown'}</p>
                    <p className="font-mono text-xs">Method: {tracesData.latest_outfit.generation_method || 'Unknown'}</p>
                    <p className="font-mono text-xs">Items: {tracesData.latest_outfit.items_count || 0}</p>
                    <p className="font-mono text-xs">Created: {tracesData.latest_outfit.created_at ? formatTimestamp(tracesData.latest_outfit.created_at) : 'Unknown'}</p>
                    <p className="font-mono text-xs">Success: {tracesData.latest_outfit.was_successful ? 'Yes' : 'No'}</p>
                  </div>
                </div>

                {Array.isArray(tracesData.latest_outfit.validation_errors) && tracesData.latest_outfit.validation_errors.length > 0 && (
                  <div>
                    <p className="text-sm text-muted-foreground">Validation Errors</p>
                    <ul className="text-xs text-red-600 space-y-2">
                      {tracesData.latest_outfit.validation_errors.map((error, index) => (
                        <li key={index} className="flex items-center justify-between">
                          <span>{error}</span>
                          <FixButton
                            errorType={error.includes("occasion appropriateness") ? "low_occasion_appropriateness" : "validation_error"}
                            errorDetails={{ 
                              error_message: error,
                              ...(error.includes("occasion appropriateness") && {
                                score: parseFloat(error.match(/0\.\d+/)?.[0] || "0"),
                                occasion: "Work" // Extract from context or error message
                              })
                            }}
                            onFixApplied={fetchDiagnostics}
                          />
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div>
                  <p className="text-sm text-muted-foreground">Generation Trace</p>
                  <p className="font-mono text-xs">Steps: {Array.isArray(tracesData.latest_outfit.generation_trace) ? tracesData.latest_outfit.generation_trace.length : 0}</p>
                  <div className="mt-2 space-y-1">
                    {Array.isArray(tracesData.latest_outfit.generation_trace) && tracesData.latest_outfit.generation_trace.slice(0, 3).map((step, index) => (
                      <div key={index} className="text-xs bg-gray-100 p-1 rounded">
                        <p className="font-medium">{step.step || 'Unknown Step'}</p>
                        <p className="text-muted-foreground">Method: {step.method || 'Unknown Method'}</p>
                        {step.duration && typeof step.duration === 'number' && (
                          <p className="text-muted-foreground">Duration: {step.duration.toFixed(3)}s</p>
                        )}
                        {step.duration && typeof step.duration !== 'number' && (
                          <p className="text-muted-foreground">Duration: {step.duration}s</p>
                        )}
                      </div>
                    ))}
                    {Array.isArray(tracesData.latest_outfit.generation_trace) && tracesData.latest_outfit.generation_trace.length > 3 && (
                      <p className="text-xs text-muted-foreground">
                        ... and {tracesData.latest_outfit.generation_trace.length - 3} more steps
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ) : tracesData?.status === 'no_data' ? (
              <p className="text-muted-foreground">No outfit traces found</p>
            ) : (
              <p className="text-muted-foreground">No trace data available</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>API Endpoints</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div>
              <p className="text-sm font-medium">Health Check:</p>
              <p className="font-mono text-xs text-muted-foreground">GET /api/diagnostics/public/health</p>
            </div>
            <div>
              <p className="text-sm font-medium">Outfit Traces:</p>
              <p className="font-mono text-xs text-muted-foreground">GET /api/diagnostics/public/outfit-traces</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 