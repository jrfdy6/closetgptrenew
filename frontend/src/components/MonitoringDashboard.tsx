'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  TrendingUp, 
  Users,
  Zap,
  Database,
  Layers
} from 'lucide-react';

interface MonitoringStats {
  overview: {
    outfit_generation_success_rate: number;
    outfit_generation_p95_ms: number;
    cache_hit_rate: number;
    total_operations: number;
    recent_errors: number;
  };
  detailed_stats: {
    success_rates: Record<string, number>;
    performance: Record<string, {
      p50_ms: number;
      p95_ms: number;
      p99_ms: number;
    }>;
    cache_hit_rate: number;
    recent_errors: Array<{
      operation: string;
      error: string;
      timestamp: string;
    }>;
    user_funnel: Record<string, {
      completed: number;
      conversion_rate: number;
    }>;
    service_layers: Record<string, {
      count: number;
      percentage: number;
    }>;
  };
  timestamp: string;
}

export function MonitoringDashboard() {
  const [stats, setStats] = useState<MonitoringStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeWindow, setTimeWindow] = useState(60); // minutes

  useEffect(() => {
    fetchStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [timeWindow]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/monitoring/dashboard?time_window_minutes=${timeWindow}`);
      if (!response.ok) throw new Error('Failed to fetch monitoring data');
      const data = await response.json();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="flex flex-col items-center gap-4">
          <Activity className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Loading monitoring data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Failed to load monitoring data: {error}
        </AlertDescription>
      </Alert>
    );
  }

  if (!stats) return null;

  const getStatusColor = (value: number, threshold: number, inverse = false) => {
    if (inverse) {
      return value < threshold ? 'text-green-600' : 'text-red-600';
    }
    return value >= threshold ? 'text-green-600' : 'text-red-600';
  };

  const getStatusBadge = (value: number, threshold: number, inverse = false) => {
    const isGood = inverse ? value < threshold : value >= threshold;
    return (
      <Badge variant={isGood ? 'default' : 'destructive'}>
        {isGood ? 'Healthy' : 'Needs Attention'}
      </Badge>
    );
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Production Monitoring</h1>
          <p className="text-sm text-muted-foreground">
            Last updated: {new Date(stats.timestamp).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setTimeWindow(15)}
            className={`px-3 py-1 rounded ${timeWindow === 15 ? 'bg-primary text-white' : 'bg-secondary'}`}
          >
            15m
          </button>
          <button
            onClick={() => setTimeWindow(60)}
            className={`px-3 py-1 rounded ${timeWindow === 60 ? 'bg-primary text-white' : 'bg-secondary'}`}
          >
            1h
          </button>
          <button
            onClick={() => setTimeWindow(240)}
            className={`px-3 py-1 rounded ${timeWindow === 240 ? 'bg-primary text-white' : 'bg-secondary'}`}
          >
            4h
          </button>
          <button
            onClick={() => setTimeWindow(1440)}
            className={`px-3 py-1 rounded ${timeWindow === 1440 ? 'bg-primary text-white' : 'bg-secondary'}`}
          >
            24h
          </button>
        </div>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getStatusColor(stats.overview.outfit_generation_success_rate, 95)}`}>
              {stats.overview.outfit_generation_success_rate.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Target: &gt; 95%
            </p>
            {getStatusBadge(stats.overview.outfit_generation_success_rate, 95)}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Response Time (p95)</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getStatusColor(stats.overview.outfit_generation_p95_ms, 5000, true)}`}>
              {(stats.overview.outfit_generation_p95_ms / 1000).toFixed(2)}s
            </div>
            <p className="text-xs text-muted-foreground">
              Target: &lt; 5s
            </p>
            {getStatusBadge(stats.overview.outfit_generation_p95_ms, 5000, true)}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cache Hit Rate</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getStatusColor(stats.overview.cache_hit_rate, 40)}`}>
              {stats.overview.cache_hit_rate.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Target: &gt; 40%
            </p>
            {getStatusBadge(stats.overview.cache_hit_rate, 40)}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Operations</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.overview.total_operations}
            </div>
            <p className="text-xs text-muted-foreground">
              Last {timeWindow} minutes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Errors</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${stats.overview.recent_errors > 5 ? 'text-red-600' : 'text-green-600'}`}>
              {stats.overview.recent_errors}
            </div>
            <p className="text-xs text-muted-foreground">
              Last {timeWindow} minutes
            </p>
            {getStatusBadge(stats.overview.recent_errors, 5, true)}
          </CardContent>
        </Card>
      </div>

      {/* Detailed Stats Tabs */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="errors">Errors</TabsTrigger>
          <TabsTrigger value="funnel">User Funnel</TabsTrigger>
          <TabsTrigger value="services">Service Layers</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Operation Performance</CardTitle>
              <CardDescription>Response times for all monitored operations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(stats.detailed_stats.performance).map(([operation, perf]) => (
                  <div key={operation} className="flex items-center justify-between border-b pb-2">
                    <div className="flex-1">
                      <p className="font-medium">{operation.replace(/_/g, ' ').toUpperCase()}</p>
                      <p className="text-xs text-muted-foreground">
                        Success Rate: {stats.detailed_stats.success_rates[operation]?.toFixed(1) || '0.0'}%
                      </p>
                    </div>
                    <div className="flex gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">p50</p>
                        <p className="font-medium">{perf.p50_ms ? (perf.p50_ms / 1000).toFixed(2) : '0.00'}s</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">p95</p>
                        <p className="font-medium">{perf.p95_ms ? (perf.p95_ms / 1000).toFixed(2) : '0.00'}s</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">p99</p>
                        <p className="font-medium">{perf.p99_ms ? (perf.p99_ms / 1000).toFixed(2) : '0.00'}s</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Errors</CardTitle>
              <CardDescription>Latest error events with context</CardDescription>
            </CardHeader>
            <CardContent>
              {stats.detailed_stats.recent_errors.length === 0 ? (
                <div className="flex items-center justify-center p-8 text-muted-foreground">
                  <CheckCircle2 className="mr-2 h-5 w-5" />
                  No errors in the last {timeWindow} minutes
                </div>
              ) : (
                <div className="space-y-3">
                  {stats.detailed_stats.recent_errors.map((error, idx) => (
                    <Alert key={idx} variant="destructive">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium">{error.operation}</p>
                            <p className="text-sm mt-1">{error.error}</p>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {new Date(error.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </AlertDescription>
                    </Alert>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="funnel" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>User Journey Funnel</CardTitle>
              <CardDescription>Conversion rates for key milestones</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(stats.detailed_stats.user_funnel).map(([step, data]) => (
                  <div key={step} className="flex items-center justify-between border-b pb-2">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <p className="font-medium">{step.replace(/_/g, ' ').toUpperCase()}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <p className="text-sm text-muted-foreground">{data.completed} users</p>
                      <div className="w-24 bg-secondary rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full"
                          style={{ width: `${data.conversion_rate}%` }}
                        />
                      </div>
                      <p className="font-medium w-16 text-right">{data.conversion_rate.toFixed(1)}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Service Layer Distribution</CardTitle>
              <CardDescription>Which generation strategies are being used</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(stats.detailed_stats.service_layers).map(([layer, data]) => {
                  const isFallback = layer.includes('fallback') || layer.includes('rule_based');
                  return (
                    <div key={layer} className="flex items-center justify-between border-b pb-2">
                      <div className="flex items-center gap-2">
                        <Layers className={`h-4 w-4 ${isFallback ? 'text-yellow-500' : 'text-green-500'}`} />
                        <p className="font-medium">{layer.replace(/_/g, ' ').toUpperCase()}</p>
                        {isFallback && (
                          <Badge variant="outline" className="text-yellow-600">Fallback</Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-4">
                        <p className="text-sm text-muted-foreground">{data.count} times</p>
                        <div className="w-24 bg-secondary rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${isFallback ? 'bg-yellow-500' : 'bg-green-500'}`}
                            style={{ width: `${data.percentage}%` }}
                          />
                        </div>
                        <p className="font-medium w-16 text-right">{data.percentage.toFixed(1)}%</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

