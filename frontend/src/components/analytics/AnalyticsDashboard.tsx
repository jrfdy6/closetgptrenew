'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Calendar, Users, TrendingUp, Activity, AlertTriangle, Clock } from 'lucide-react';
import { apiWithAnalytics } from '../../shared/utils/apiWithAnalytics';

interface AnalyticsData {
  overview: {
    total_users: number;
    active_users_today: number;
    total_outfits_generated: number;
    success_rate: number;
    average_response_time: number;
  };
  events: {
    event_type: string;
    count: number;
    percentage: number;
  }[];
  user_activity: {
    date: string;
    users: number;
    outfits: number;
    errors: number;
  }[];
  top_events: {
    event_type: string;
    count: number;
    trend: 'up' | 'down' | 'stable';
  }[];
  errors: {
    error_type: string;
    count: number;
    last_occurrence: string;
  }[];
  performance: {
    endpoint: string;
    avg_response_time: number;
    success_rate: number;
    total_calls: number;
  }[];
}

export default function AnalyticsDashboard() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await apiWithAnalytics.get(`/api/analytics/dashboard?range=${timeRange}`);
      setData(response);
      setError(null);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Analytics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-2" />
          <p className="text-red-600">{error}</p>
          <Button onClick={fetchAnalyticsData} className="mt-2">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-gray-600">Monitor your app's performance and user behavior</p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border rounded px-3 py-1"
          >
            <option value="1d">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <Button onClick={fetchAnalyticsData} variant="outline">
            Refresh
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.overview.total_users.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {data.overview.active_users_today} active today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Outfits Generated</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.overview.total_outfits_generated.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {data.overview.success_rate}% success rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.overview.average_response_time}ms</div>
            <p className="text-xs text-muted-foreground">
              API performance
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              <Badge variant={data.overview.success_rate > 95 ? 'default' : 'destructive'}>
                {data.overview.success_rate}%
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Overall success rate
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="events">Events</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="errors">Errors</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Event Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Event Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.events.map((event) => (
                    <div key={event.event_type} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{event.event_type}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${event.percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600 w-12 text-right">
                          {event.count}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Top Events */}
            <Card>
              <CardHeader>
                <CardTitle>Top Events</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.top_events.map((event) => (
                    <div key={event.event_type} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{event.event_type}</span>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm">{event.count}</span>
                        <Badge
                          variant={
                            event.trend === 'up' ? 'default' : 
                            event.trend === 'down' ? 'destructive' : 'secondary'
                          }
                        >
                          {event.trend === 'up' ? '↗' : event.trend === 'down' ? '↘' : '→'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Event Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Event Type</th>
                      <th className="text-left py-2">Count</th>
                      <th className="text-left py-2">Percentage</th>
                      <th className="text-left py-2">Trend</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.events.map((event) => (
                      <tr key={event.event_type} className="border-b">
                        <td className="py-2">{event.event_type}</td>
                        <td className="py-2">{event.count.toLocaleString()}</td>
                        <td className="py-2">{event.percentage.toFixed(1)}%</td>
                        <td className="py-2">
                          <div className="w-32 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${event.percentage}%` }}
                            ></div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>API Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Endpoint</th>
                      <th className="text-left py-2">Avg Response Time</th>
                      <th className="text-left py-2">Success Rate</th>
                      <th className="text-left py-2">Total Calls</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.performance.map((endpoint) => (
                      <tr key={endpoint.endpoint} className="border-b">
                        <td className="py-2 font-mono text-sm">{endpoint.endpoint}</td>
                        <td className="py-2">{endpoint.avg_response_time}ms</td>
                        <td className="py-2">
                          <Badge variant={endpoint.success_rate > 95 ? 'default' : 'destructive'}>
                            {endpoint.success_rate}%
                          </Badge>
                        </td>
                        <td className="py-2">{endpoint.total_calls.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Error Tracking</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Error Type</th>
                      <th className="text-left py-2">Count</th>
                      <th className="text-left py-2">Last Occurrence</th>
                      <th className="text-left py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.errors.map((error) => (
                      <tr key={error.error_type} className="border-b">
                        <td className="py-2">{error.error_type}</td>
                        <td className="py-2">{error.count}</td>
                        <td className="py-2">{new Date(error.last_occurrence).toLocaleString()}</td>
                        <td className="py-2">
                          <Badge variant={error.count > 10 ? 'destructive' : 'secondary'}>
                            {error.count > 10 ? 'High' : 'Low'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 