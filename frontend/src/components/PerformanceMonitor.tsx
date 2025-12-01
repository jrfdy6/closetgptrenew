'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { performanceService } from '@/lib/services/performanceService';
import { Activity, Zap, TrendingUp, RefreshCw, BarChart3 } from 'lucide-react';

interface PerformanceMonitorProps {
  className?: string;
  showDetails?: boolean;
}

export default function PerformanceMonitor({ 
  className = '',
  showDetails = false 
}: PerformanceMonitorProps) {
  const [metrics, setMetrics] = useState(performanceService.getMetrics());
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Update metrics every 5 seconds
    const interval = setInterval(() => {
      setMetrics(performanceService.getMetrics());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleReset = () => {
    performanceService.resetMetrics();
    setMetrics(performanceService.getMetrics());
  };

  // Only show in development or if explicitly enabled
  if (process.env.NODE_ENV === 'production' && !showDetails) {
    return null;
  }

  const hitRateColor = metrics.hitRate >= 70 ? 'text-green-600' : metrics.hitRate >= 50 ? 'text-yellow-600' : 'text-red-600';
  const avgResponseTimeColor = metrics.avgResponseTime < 500 ? 'text-green-600' : metrics.avgResponseTime < 1000 ? 'text-yellow-600' : 'text-red-600';

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Activity className="h-4 w-4" />
              Performance Monitor
            </CardTitle>
            <CardDescription className="text-xs">
              Cache and API performance metrics
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsVisible(!isVisible)}
              className="h-8"
            >
              {isVisible ? 'Hide' : 'Show'}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="h-8"
            >
              <RefreshCw className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      {isVisible && (
        <CardContent className="space-y-4">
          {/* Key Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <Zap className="h-4 w-4 text-blue-600" />
                <span className="text-xs font-medium text-muted-foreground">Cache Hit Rate</span>
              </div>
              <div className={`text-2xl font-bold ${hitRateColor}`}>
                {metrics.hitRate.toFixed(1)}%
              </div>
              <div className="text-xs text-muted-foreground">
                {metrics.cacheHits} hits / {metrics.cacheMisses} misses
              </div>
            </div>

            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <span className="text-xs font-medium text-muted-foreground">Avg Response Time</span>
              </div>
              <div className={`text-2xl font-bold ${avgResponseTimeColor}`}>
                {metrics.avgResponseTime.toFixed(0)}ms
              </div>
              <div className="text-xs text-muted-foreground">
                {metrics.apiCalls} API calls
              </div>
            </div>
          </div>

          {/* Detailed Stats */}
          {showDetails && (
            <div className="space-y-2 pt-4 border-t">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Total Requests</span>
                <span className="font-medium">{metrics.totalRequests}</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Cache Size</span>
                <span className="font-medium">{metrics.cacheSize} entries</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Cache Hits</span>
                <Badge variant="outline" className="text-xs">
                  {metrics.cacheHits}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Cache Misses</span>
                <Badge variant="outline" className="text-xs">
                  {metrics.cacheMisses}
                </Badge>
              </div>
            </div>
          )}

          {/* Performance Indicator */}
          <div className="pt-2 border-t">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium">Performance Status</span>
              <Badge 
                variant={
                  metrics.hitRate >= 70 && metrics.avgResponseTime < 500 
                    ? "default" 
                    : metrics.hitRate >= 50 && metrics.avgResponseTime < 1000
                    ? "secondary"
                    : "destructive"
                }
                className="text-xs"
              >
                {metrics.hitRate >= 70 && metrics.avgResponseTime < 500 
                  ? "Excellent" 
                  : metrics.hitRate >= 50 && metrics.avgResponseTime < 1000
                  ? "Good"
                  : "Needs Improvement"
                }
              </Badge>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <BarChart3 className="h-3 w-3" />
              <span>
                {metrics.hitRate >= 70 
                  ? "Caching is working efficiently"
                  : "Consider increasing cache TTL for better performance"
                }
              </span>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}

