'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Calendar, 
  TrendingUp, 
  Palette, 
  Shirt, 
  BarChart3,
  Download,
  Share2,
  ArrowLeft,
  ArrowRight
} from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import { performanceService } from '@/lib/services/performanceService';

interface StyleReport {
  month: string;
  year: number;
  totalOutfits: number;
  styleBreakdown: {
    casual: number;
    business: number;
    formal: number;
    athletic: number;
    [key: string]: number;
  };
  colorPalette: {
    color: string;
    count: number;
    percentage: number;
  }[];
  topItems: {
    id: string;
    name: string;
    imageUrl?: string;
    wearCount: number;
  }[];
  trends: {
    increasing: string[];
    decreasing: string[];
    stable: string[];
  };
}

interface MonthlyStyleReportProps {
  className?: string;
  userId?: string;
}

export default function MonthlyStyleReport({ 
  className = '',
  userId
}: MonthlyStyleReportProps) {
  const { user } = useFirebase();
  const [report, setReport] = useState<StyleReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [error, setError] = useState<string | null>(null);

  const targetUserId = userId || user?.uid;

  useEffect(() => {
    if (targetUserId) {
      fetchReport();
    }
  }, [targetUserId, currentMonth]);

  const fetchReport = async () => {
    if (!targetUserId) return;

    setLoading(true);
    setError(null);

    try {
      const monthKey = `${currentMonth.getFullYear()}-${String(currentMonth.getMonth() + 1).padStart(2, '0')}`;
      
      // Try cache first
      const cacheKey = `style-report:${targetUserId}:${monthKey}`;
      const cached = performanceService.get<StyleReport>(cacheKey);
      
      if (cached) {
        setReport(cached);
        setLoading(false);
        return;
      }

      // Fetch from API
      const token = await user?.getIdToken();
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-production.up.railway.app';
      const response = await fetch(
        `${apiUrl}/api/style-report?month=${monthKey}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch style report' }));
        throw new Error(errorData.detail || 'Failed to fetch style report');
      }

      const data = await response.json();
      setReport(data);
      
      // Cache for 1 hour
      performanceService.set(cacheKey, data, 60 * 60 * 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load report');
      // Generate mock data for demo
      setReport(generateMockReport());
    } finally {
      setLoading(false);
    }
  };

  const generateMockReport = (): StyleReport => {
    const now = new Date();
    return {
      month: now.toLocaleString('default', { month: 'long' }),
      year: now.getFullYear(),
      totalOutfits: 25,
      styleBreakdown: {
        casual: 15,
        business: 7,
        formal: 2,
        athletic: 1
      },
      colorPalette: [
        { color: 'Navy', count: 12, percentage: 48 },
        { color: 'White', count: 8, percentage: 32 },
        { color: 'Gray', count: 5, percentage: 20 }
      ],
      topItems: [],
      trends: {
        increasing: ['Casual', 'Layering'],
        decreasing: ['Formal'],
        stable: ['Business Casual']
      }
    };
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentMonth(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1);
      } else {
        newDate.setMonth(prev.getMonth() + 1);
      }
      return newDate;
    });
  };

  const handleShare = async () => {
    if (navigator.share && report) {
      try {
        await navigator.share({
          title: `My Style Report - ${report.month} ${report.year}`,
          text: `I created ${report.totalOutfits} outfits this month! Check out my style breakdown.`,
        });
      } catch (err) {
        console.log('Error sharing:', err);
      }
    }
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="p-8">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error && !report) {
    return (
      <Card className={className}>
        <CardContent className="p-8 text-center">
          <p className="text-red-600 dark:text-red-400">{error}</p>
          <Button onClick={fetchReport} className="mt-4" variant="outline">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!report) return null;

  const totalStyleCount = Object.values(report.styleBreakdown).reduce((a, b) => a + b, 0);
  const maxStyleCount = Math.max(...Object.values(report.styleBreakdown));

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Monthly Style Report
            </CardTitle>
            <CardDescription>
              {report.month} {report.year}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigateMonth('prev')}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigateMonth('next')}
              disabled={currentMonth >= new Date()}
            >
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleShare}
            >
              <Share2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Shirt className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Total Outfits</span>
            </div>
            <div className="text-3xl font-bold text-blue-600">
              {report.totalOutfits}
            </div>
          </div>
          <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium">Top Style</span>
            </div>
            <div className="text-lg font-bold text-purple-600">
              {Object.entries(report.styleBreakdown)
                .sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'}
            </div>
          </div>
        </div>

        {/* Style Breakdown */}
        <div>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Style Breakdown
          </h3>
          <div className="space-y-3">
            {Object.entries(report.styleBreakdown)
              .sort((a, b) => b[1] - a[1])
              .map(([style, count]) => {
                const percentage = totalStyleCount > 0 ? (count / totalStyleCount) * 100 : 0;
                return (
                  <div key={style} className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium capitalize">{style}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">{count} outfits</span>
                        <Badge variant="outline">{percentage.toFixed(0)}%</Badge>
                      </div>
                    </div>
                    <Progress value={percentage} className="h-2" />
                  </div>
                );
              })}
          </div>
        </div>

        {/* Color Palette */}
        {report.colorPalette.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Palette className="h-5 w-5" />
              Color Palette
            </h3>
            <div className="grid grid-cols-3 gap-3">
              {report.colorPalette.map((color, index) => (
                <div
                  key={index}
                  className="p-3 rounded-lg border"
                  style={{
                    backgroundColor: `${color.color.toLowerCase()}20`,
                    borderColor: `${color.color.toLowerCase()}40`
                  }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{color.color}</span>
                    <span className="text-xs text-muted-foreground">{color.percentage}%</span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {color.count} times
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trends */}
        {report.trends && (
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Style Trends
            </h3>
            <div className="grid grid-cols-3 gap-4">
              {report.trends.increasing.length > 0 && (
                <div>
                  <div className="text-sm font-medium text-green-600 mb-2">↑ Increasing</div>
                  <div className="space-y-1">
                    {report.trends.increasing.map((trend, i) => (
                      <Badge key={i} variant="outline" className="bg-green-50 dark:bg-green-900/20">
                        {trend}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              {report.trends.decreasing.length > 0 && (
                <div>
                  <div className="text-sm font-medium text-red-600 mb-2">↓ Decreasing</div>
                  <div className="space-y-1">
                    {report.trends.decreasing.map((trend, i) => (
                      <Badge key={i} variant="outline" className="bg-red-50 dark:bg-red-900/20">
                        {trend}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              {report.trends.stable.length > 0 && (
                <div>
                  <div className="text-sm font-medium text-gray-600 mb-2">→ Stable</div>
                  <div className="space-y-1">
                    {report.trends.stable.map((trend, i) => (
                      <Badge key={i} variant="outline">
                        {trend}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

