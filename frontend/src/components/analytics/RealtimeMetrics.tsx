'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Activity, Users, TrendingUp, AlertTriangle } from 'lucide-react';
import { apiWithAnalytics } from '../../shared/utils/apiWithAnalytics';

interface RealtimeData {
  active_users: number;
  events_per_minute: number;
  error_rate: number;
  outfits_generated: number;
  last_updated: string;
}

export default function RealtimeMetrics() {
  const [data, setData] = useState<RealtimeData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRealtimeData();
    const interval = setInterval(fetchRealtimeData, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const fetchRealtimeData = async () => {
    try {
      const response = await apiWithAnalytics.get('/api/analytics/realtime');
      setData(response);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch realtime data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Real-time Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-4 w-4" />
          Real-time Metrics
          <Badge variant="outline" className="ml-auto">
            Live
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <Users className="h-4 w-4 text-blue-500" />
              <span className="text-sm font-medium">Active Users</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {data.active_users}
            </div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium">Events/min</span>
            </div>
            <div className="text-2xl font-bold text-green-600">
              {data.events_per_minute}
            </div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <AlertTriangle className="h-4 w-4 text-red-500" />
              <span className="text-sm font-medium">Error Rate</span>
            </div>
            <div className="text-2xl font-bold text-red-600">
              {data.error_rate}%
            </div>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-purple-500" />
              <span className="text-sm font-medium">Outfits</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">
              {data.outfits_generated}
            </div>
          </div>
        </div>

        <div className="mt-4 text-xs text-gray-500 text-center">
          Last updated: {new Date(data.last_updated).toLocaleTimeString()}
        </div>
      </CardContent>
    </Card>
  );
} 