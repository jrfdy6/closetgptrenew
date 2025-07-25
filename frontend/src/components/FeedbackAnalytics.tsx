"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ThumbsUp, ThumbsDown, AlertTriangle, Star, TrendingUp, BarChart3 } from 'lucide-react';
import { feedbackApi, AnalyticsSummary } from '@/lib/api/feedbackApi';
import { useToast } from '@/components/ui/use-toast';

export function FeedbackAnalytics() {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await feedbackApi.getAnalyticsSummary();
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
      toast({
        title: "Error",
        description: "Failed to load feedback analytics",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">Loading feedback analytics...</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="space-y-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-red-500 mb-4">
              {error || "Failed to load analytics"}
            </div>
            <div className="flex justify-center">
              <Button onClick={loadAnalytics} variant="outline">
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const topIssues = Object.entries(analytics.top_issue_categories)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  const topOccasions = Object.entries(analytics.preferred_occasions)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  const topStyles = Object.entries(analytics.preferred_styles)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.total_feedback}</div>
            <p className="text-xs text-muted-foreground">
              Across {analytics.total_outfits_rated} outfits
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.average_rating.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground">
              Out of 5 stars
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Likes</CardTitle>
            <ThumbsUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{analytics.likes}</div>
            <p className="text-xs text-muted-foreground">
              {analytics.total_feedback > 0 ? `${((analytics.likes / analytics.total_feedback) * 100).toFixed(1)}%` : '0%'} of feedback
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Issues Reported</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{analytics.issues}</div>
            <p className="text-xs text-muted-foreground">
              {analytics.total_feedback > 0 ? `${((analytics.issues / analytics.total_feedback) * 100).toFixed(1)}%` : '0%'} of feedback
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Issues */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              Top Issues Reported
            </CardTitle>
          </CardHeader>
          <CardContent>
            {topIssues.length > 0 ? (
              <div className="space-y-3">
                {topIssues.map(([category, count]) => (
                  <div key={category} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="capitalize">
                        {category.replace('_', ' ')}
                      </Badge>
                    </div>
                    <div className="text-sm font-medium">{count} reports</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No issues reported yet</p>
            )}
          </CardContent>
        </Card>

        {/* Preferred Occasions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Preferred Occasions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {topOccasions.length > 0 ? (
              <div className="space-y-3">
                {topOccasions.map(([occasion, count]) => (
                  <div key={occasion} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="capitalize">
                        {occasion}
                      </Badge>
                    </div>
                    <div className="text-sm font-medium">{count} likes</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No occasion preferences yet</p>
            )}
          </CardContent>
        </Card>

        {/* Preferred Styles */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5 text-yellow-600" />
              Preferred Styles
            </CardTitle>
          </CardHeader>
          <CardContent>
            {topStyles.length > 0 ? (
              <div className="space-y-3">
                {topStyles.map(([style, count]) => (
                  <div key={style} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="capitalize">
                        {style}
                      </Badge>
                    </div>
                    <div className="text-sm font-medium">{count} likes</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No style preferences yet</p>
            )}
          </CardContent>
        </Card>

        {/* Feedback Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-purple-600" />
              Feedback Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ThumbsUp className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Likes</span>
                </div>
                <div className="text-sm font-medium">{analytics.likes}</div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ThumbsDown className="h-4 w-4 text-red-600" />
                  <span className="text-sm">Dislikes</span>
                </div>
                <div className="text-sm font-medium">{analytics.dislikes}</div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                  <span className="text-sm">Issues</span>
                </div>
                <div className="text-sm font-medium">{analytics.issues}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center">
        <Button onClick={loadAnalytics} variant="outline">
          Refresh Analytics
        </Button>
      </div>
    </div>
  );
} 