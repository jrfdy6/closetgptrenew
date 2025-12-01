'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useFirebase } from '@/lib/firebase-context';
import { performanceService } from '@/lib/services/performanceService';
import { 
  TrendingUp, 
  Calendar, 
  BarChart3,
  LineChart,
  PieChart,
  ArrowUp,
  ArrowDown,
  Minus,
  RefreshCw
} from 'lucide-react';

interface TrendData {
  period: string;
  casual: number;
  business: number;
  formal: number;
  athletic: number;
  total: number;
}

interface SeasonalComparison {
  season: string;
  year: number;
  styleBreakdown: {
    casual: number;
    business: number;
    formal: number;
    athletic: number;
  };
  topColors: string[];
  avgOutfitsPerWeek: number;
}

interface StyleTrendsVisualizationProps {
  className?: string;
  trendData?: TrendData[];
  seasonalData?: SeasonalComparison[];
  months?: number;
  year?: number;
}

export default function StyleTrendsVisualization({
  className = '',
  trendData: propTrendData,
  seasonalData: propSeasonalData,
  months = 6,
  year
}: StyleTrendsVisualizationProps) {
  const { user, loading: authLoading } = useFirebase();
  const [trendData, setTrendData] = useState<TrendData[]>(propTrendData || []);
  const [seasonalData, setSeasonalData] = useState<SeasonalComparison[]>(propSeasonalData || []);
  const [loading, setLoading] = useState(!propTrendData && !propSeasonalData);
  const [error, setError] = useState<string | null>(null);
  const [apiSucceeded, setApiSucceeded] = useState(false); // Track if API calls succeeded

  useEffect(() => {
    // Wait for auth to finish loading, then check if we need to fetch data
    if (!authLoading && (!propTrendData || !propSeasonalData) && user) {
      console.log('🔄 [StyleTrends] Fetching trend data for user:', user.uid);
      fetchTrendData();
    } else if (!authLoading && !user) {
      console.warn('⚠️ [StyleTrends] No user available, cannot fetch data');
    }
  }, [user, authLoading, months, year, propTrendData, propSeasonalData]);

  const fetchTrendData = async () => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      const token = await user.getIdToken();
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-production.up.railway.app';

      // Fetch trend data
      if (!propTrendData) {
        const trendCacheKey = `style-trends:${user.uid}:${months}`;
        const cachedTrends = performanceService.get<{ trendData: TrendData[] }>(trendCacheKey);
        
        if (cachedTrends && cachedTrends.trendData) {
          console.log('✅ [StyleTrends] Using cached trend data:', cachedTrends.trendData.length, 'items');
          setTrendData(cachedTrends.trendData);
          setApiSucceeded(true); // Mark as succeeded since we have cached data from previous successful API call
        } else {
          console.log('🌐 [StyleTrends] Fetching trend data from API...');
          const trendResponse = await fetch(
            `${apiUrl}/api/style-trends?months=${months}`,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
          );

          if (trendResponse.ok) {
            const trendResult = await trendResponse.json();
            const data = trendResult.trendData || trendResult.data || [];
            console.log('✅ [StyleTrends] API returned trend data:', data.length, 'items', data);
            setTrendData(data);
            setApiSucceeded(true); // Mark API as succeeded
            performanceService.set(trendCacheKey, { trendData: data }, 60 * 60 * 1000); // Cache 1 hour
          } else {
            const errorText = await trendResponse.text();
            console.error('❌ [StyleTrends] Failed to fetch trend data:', trendResponse.status, trendResponse.statusText, errorText);
            setApiSucceeded(false);
          }
        }
      }

      // Fetch seasonal data
      if (!propSeasonalData) {
        const seasonalCacheKey = `seasonal-comparison:${user.uid}:${year || 'current'}`;
        const cachedSeasonal = performanceService.get<{ seasonalData: SeasonalComparison[] }>(seasonalCacheKey);
        
        if (cachedSeasonal && cachedSeasonal.seasonalData) {
          console.log('✅ [StyleTrends] Using cached seasonal data:', cachedSeasonal.seasonalData.length, 'seasons');
          setSeasonalData(cachedSeasonal.seasonalData);
          setApiSucceeded(true); // Mark as succeeded since we have cached data from previous successful API call
        } else {
          console.log('🌐 [StyleTrends] Fetching seasonal data from API...');
          const seasonalUrl = year 
            ? `${apiUrl}/api/seasonal-comparison?year=${year}`
            : `${apiUrl}/api/seasonal-comparison`;
          
          const seasonalResponse = await fetch(seasonalUrl, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (seasonalResponse.ok) {
            const seasonalResult = await seasonalResponse.json();
            const data = seasonalResult.seasonalData || seasonalResult.data || [];
            console.log('✅ [StyleTrends] API returned seasonal data:', data.length, 'seasons', data);
            setSeasonalData(data);
            setApiSucceeded(true); // Mark API as succeeded
            performanceService.set(seasonalCacheKey, { seasonalData: data }, 60 * 60 * 1000); // Cache 1 hour
          } else {
            const errorText = await seasonalResponse.text();
            console.error('❌ [StyleTrends] Failed to fetch seasonal data:', seasonalResponse.status, seasonalResponse.statusText, errorText);
            setApiSucceeded(false);
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load trend data');
      console.error('Error fetching trend data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Generate mock data only if no real data and not loading
  const mockTrendData: TrendData[] = trendData.length > 0 
    ? trendData 
    : loading 
      ? [] 
      : [
          { period: 'Jan', casual: 12, business: 8, formal: 2, athletic: 3, total: 25 },
          { period: 'Feb', casual: 15, business: 6, formal: 1, athletic: 4, total: 26 },
          { period: 'Mar', casual: 18, business: 5, formal: 2, athletic: 2, total: 27 },
          { period: 'Apr', casual: 20, business: 4, formal: 1, athletic: 3, total: 28 },
          { period: 'May', casual: 22, business: 3, formal: 0, athletic: 5, total: 30 },
          { period: 'Jun', casual: 25, business: 2, formal: 0, athletic: 6, total: 33 },
        ];

  const mockSeasonalData: SeasonalComparison[] = seasonalData.length > 0 
    ? seasonalData 
    : loading 
      ? [] 
      : [
    {
      season: 'Winter',
      year: new Date().getFullYear(),
      styleBreakdown: { casual: 15, business: 10, formal: 5, athletic: 3 },
      topColors: ['Navy', 'Gray', 'Black'],
      avgOutfitsPerWeek: 4.2
    },
    {
      season: 'Spring',
      year: new Date().getFullYear(),
      styleBreakdown: { casual: 20, business: 8, formal: 2, athletic: 5 },
      topColors: ['Navy', 'White', 'Beige'],
      avgOutfitsPerWeek: 5.1
    },
    {
      season: 'Summer',
      year: new Date().getFullYear(),
      styleBreakdown: { casual: 25, business: 5, formal: 1, athletic: 8 },
      topColors: ['White', 'Navy', 'Light Blue'],
      avgOutfitsPerWeek: 6.2
    },
    {
      season: 'Fall',
      year: new Date().getFullYear(),
      styleBreakdown: { casual: 18, business: 9, formal: 3, athletic: 4 },
      topColors: ['Navy', 'Brown', 'Gray'],
      avgOutfitsPerWeek: 4.8
    }
        ];

  const calculateTrend = (current: number, previous: number): 'up' | 'down' | 'stable' => {
    const diff = current - previous;
    if (Math.abs(diff) < 0.5) return 'stable';
    return diff > 0 ? 'up' : 'down';
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <ArrowUp className="h-4 w-4 text-green-500" />;
      case 'down':
        return <ArrowDown className="h-4 w-4 text-red-500" />;
      default:
        return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  // Use real data if available, only use mock data if API failed
  const displayTrendData = trendData.length > 0 ? trendData : (apiSucceeded ? [] : mockTrendData);
  const displaySeasonalData = seasonalData.length > 0 ? seasonalData : (apiSucceeded ? [] : mockSeasonalData);
  const isUsingMockData = !apiSucceeded && trendData.length === 0 && seasonalData.length === 0 && !loading;
  
  const maxValue = displayTrendData.length > 0 ? Math.max(...displayTrendData.map(d => d.total)) : 0;

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <LineChart className="h-5 w-5" />
              Style Trends & Evolution
            </CardTitle>
            <CardDescription>
              Track your style preferences over time
            </CardDescription>
          </div>
          {isUsingMockData && (
            <Badge variant="outline" className="text-xs">
              Sample Data
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="timeline" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="timeline">
              <Calendar className="h-4 w-4 mr-2" />
              Timeline
            </TabsTrigger>
            <TabsTrigger value="seasonal">
              <PieChart className="h-4 w-4 mr-2" />
              Seasonal
            </TabsTrigger>
          </TabsList>

          <TabsContent value="timeline" className="space-y-4 mt-4">
            {/* Trend Summary */}
            <div className="grid grid-cols-4 gap-2">
              {['casual', 'business', 'formal', 'athletic'].map((style) => {
                const first = displayTrendData[0]?.[style as keyof TrendData] as number || 0;
                const last = displayTrendData[displayTrendData.length - 1]?.[style as keyof TrendData] as number || 0;
                const trend = calculateTrend(last, first);
                
                return (
                  <div key={style} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium capitalize">{style}</span>
                      {getTrendIcon(trend)}
                    </div>
                    <div className="text-lg font-bold">{last}</div>
                    <div className="text-xs text-muted-foreground">
                      {trend === 'up' ? '+' : trend === 'down' ? '' : ''}
                      {Math.abs(last - first)} from start
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Timeline Chart */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Monthly Breakdown
              </h3>
              <div className="space-y-3">
                {displayTrendData.map((data, index) => {
                  const previous = displayTrendData[index - 1];
                  const trend = previous ? calculateTrend(data.total, previous.total) : 'stable';
                  
                  return (
                    <div key={data.period} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm">{data.period}</span>
                          {previous && getTrendIcon(trend)}
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold">{data.total} outfits</span>
                          <Badge variant="outline" className="text-xs">
                            {previous 
                              ? `${trend === 'up' ? '+' : ''}${data.total - previous.total}`
                              : 'New'
                            }
                          </Badge>
                        </div>
                      </div>
                      
                      {/* Stacked Bar */}
                      <div className="flex h-6 rounded overflow-hidden border">
                        <div
                          className="bg-blue-500"
                          style={{ width: `${(data.casual / data.total) * 100}%` }}
                          title={`Casual: ${data.casual}`}
                        />
                        <div
                          className="bg-purple-500"
                          style={{ width: `${(data.business / data.total) * 100}%` }}
                          title={`Business: ${data.business}`}
                        />
                        <div
                          className="bg-gray-500"
                          style={{ width: `${(data.formal / data.total) * 100}%` }}
                          title={`Formal: ${data.formal}`}
                        />
                        <div
                          className="bg-green-500"
                          style={{ width: `${(data.athletic / data.total) * 100}%` }}
                          title={`Athletic: ${data.athletic}`}
                        />
                      </div>
                      
                      {/* Style Breakdown */}
                      <div className="flex gap-2 text-xs text-muted-foreground">
                        <span>C: {data.casual}</span>
                        <span>B: {data.business}</span>
                        <span>F: {data.formal}</span>
                        <span>A: {data.athletic}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Key Insights */}
            <div className="pt-4 border-t">
              <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Key Insights
              </h3>
              <div className="space-y-2">
                <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded">
                  <div className="text-xs font-medium text-green-700 dark:text-green-300">
                    ↑ Casual style increased by {displayTrendData.length > 0 ? displayTrendData[displayTrendData.length - 1].casual - displayTrendData[0].casual : 0} outfits
                  </div>
                </div>
                <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                  <div className="text-xs font-medium text-blue-700 dark:text-blue-300">
                    Your most consistent style is Casual (worn {displayTrendData.length > 0 ? Math.round((displayTrendData.reduce((sum, d) => sum + d.casual, 0) / displayTrendData.length)) : 0} times/month on average)
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="seasonal" className="space-y-4 mt-4">
            <div className="grid grid-cols-2 gap-4">
              {displaySeasonalData.map((season) => {
                const total = Object.values(season.styleBreakdown).reduce((a, b) => a + b, 0);
                
                return (
                  <div key={season.season} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold capitalize">{season.season}</h3>
                      <Badge variant="outline">{season.year}</Badge>
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      {Object.entries(season.styleBreakdown).map(([style, count]) => (
                        <div key={style} className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span className="capitalize">{style}</span>
                            <span className="font-medium">{count} ({Math.round((count / total) * 100)}%)</span>
                          </div>
                          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-500"
                              style={{ width: `${(count / total) * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="pt-3 border-t space-y-2">
                      <div className="text-xs">
                        <span className="font-medium">Top Colors: </span>
                        {season.topColors.join(', ')}
                      </div>
                      <div className="text-xs">
                        <span className="font-medium">Avg Outfits/Week: </span>
                        {season.avgOutfitsPerWeek}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Seasonal Comparison */}
            <div className="pt-4 border-t">
              <h3 className="text-sm font-semibold mb-3">Seasonal Comparison</h3>
              <div className="space-y-2">
                {displaySeasonalData.map((season, index) => {
                  const previous = displaySeasonalData[index - 1];
                  if (!previous) return null;
                  
                  const currentTotal = Object.values(season.styleBreakdown).reduce((a, b) => a + b, 0);
                  const previousTotal = Object.values(previous.styleBreakdown).reduce((a, b) => a + b, 0);
                  const trend = calculateTrend(currentTotal, previousTotal);
                  
                  return (
                    <div key={season.season} className="p-2 bg-gray-50 dark:bg-gray-800 rounded flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium capitalize">{season.season}</span>
                        {getTrendIcon(trend)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {trend === 'up' ? '+' : ''}{currentTotal - previousTotal} from {previous.season}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

