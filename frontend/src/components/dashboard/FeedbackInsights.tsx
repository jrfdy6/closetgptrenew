'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  Star, 
  ThumbsUp, 
  ThumbsDown, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown,
  Heart,
  Target,
  Lightbulb,
  BarChart3
} from 'lucide-react';
import { authenticatedFetch } from '@/lib/utils/auth';
import { useAuth } from '@/hooks/useAuth';

interface FeedbackInsightsData {
  total_feedback: number;
  likes: number;
  dislikes: number;
  issues: number;
  average_rating: number;
  top_rated_styles: string[];
  improvement_areas: string[];
  feedback_by_style: Record<string, {
    average_rating: number;
    total_feedback: number;
    ratings: number[];
  }>;
  feedback_by_occasion: Record<string, {
    average_rating: number;
    total_feedback: number;
    ratings: number[];
  }>;
  recent_feedback: Array<{
    outfit_id: string;
    feedback_type: string;
    rating?: number;
    timestamp: number;
    outfit_context?: {
      occasion?: string;
      style?: string;
    };
  }>;
}

export default function FeedbackInsights() {
  const [feedbackData, setFeedbackData] = useState<FeedbackInsightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, isAuthenticated, authLoading } = useAuth();

  useEffect(() => {
    const fetchFeedbackData = async () => {
      if (authLoading || !isAuthenticated || !user) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await authenticatedFetch('/api/feedback/user/summary');
        
        if (!response.ok) {
          throw new Error('Failed to fetch feedback data');
        }
        
        const data = await response.json();
        setFeedbackData(data.data);
      } catch (err) {
        console.error('Error fetching feedback insights:', err);
        setError('Failed to load feedback insights');
      } finally {
        setLoading(false);
      }
    };

    fetchFeedbackData();
  }, [user, isAuthenticated, authLoading]);

  const getSatisfactionScore = () => {
    if (!feedbackData) return 0;
    const total = feedbackData.likes + feedbackData.dislikes;
    return total > 0 ? Math.round((feedbackData.likes / total) * 100) : 0;
  };

  const getTopStyle = () => {
    if (!feedbackData || feedbackData.top_rated_styles.length === 0) return null;
    const topStyle = feedbackData.top_rated_styles[0];
    return feedbackData.feedback_by_style[topStyle];
  };

  const getImprovementSuggestions = () => {
    if (!feedbackData || feedbackData.improvement_areas.length === 0) {
      return ['Keep providing feedback to get personalized suggestions'];
    }
    return feedbackData.improvement_areas.slice(0, 3);
  };

  if (loading) {
    return (
      <Card className="border border-border bg-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Feedback Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border border-border bg-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Feedback Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-red-600">{error}</div>
        </CardContent>
      </Card>
    );
  }

  if (!feedbackData || feedbackData.total_feedback === 0) {
    return (
      <Card className="border border-border bg-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Feedback Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Heart className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground mb-2">No feedback yet</p>
            <p className="text-sm text-muted-foreground mb-4">
              Start rating outfits to get personalized insights about your style preferences
            </p>
            <Button variant="outline" size="sm">
              Rate an Outfit
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const satisfactionScore = getSatisfactionScore();
  const topStyle = getTopStyle();
  const improvementSuggestions = getImprovementSuggestions();

  return (
    <Card className="border border-border bg-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          Feedback Insights
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Based on {feedbackData.total_feedback} feedback submissions
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Overall Satisfaction */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-foreground">Overall Satisfaction</h3>
            <Badge variant="outline">{satisfactionScore}%</Badge>
          </div>
          <Progress value={satisfactionScore} className="h-2" />
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <ThumbsUp className="w-4 h-4 text-green-500" />
              <span>{feedbackData.likes} likes</span>
            </div>
            <div className="flex items-center gap-1">
              <ThumbsDown className="w-4 h-4 text-red-500" />
              <span>{feedbackData.dislikes} dislikes</span>
            </div>
            {feedbackData.issues > 0 && (
              <div className="flex items-center gap-1">
                <AlertTriangle className="w-4 h-4 text-orange-500" />
                <span>{feedbackData.issues} issues</span>
              </div>
            )}
          </div>
        </div>

        {/* Average Rating */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-center gap-1 mb-2">
              <Star className="w-5 h-5 text-blue-500" />
              <span className="text-2xl font-bold text-blue-700">
                {feedbackData.average_rating.toFixed(1)}
              </span>
            </div>
            <div className="text-sm text-blue-600">Average Rating</div>
          </div>
          
          {topStyle && (
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="flex items-center justify-center gap-1 mb-2">
                <Heart className="w-5 h-5 text-green-500" />
                <span className="text-2xl font-bold text-green-700">
                  {topStyle.average_rating.toFixed(1)}
                </span>
              </div>
              <div className="text-sm text-green-600">
                Top Style Rating
              </div>
            </div>
          )}
        </div>

        {/* Top Rated Styles */}
        {feedbackData.top_rated_styles.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-500" />
              Your Top Styles
            </h3>
            <div className="flex flex-wrap gap-2">
              {feedbackData.top_rated_styles.map((style, index) => {
                const styleData = feedbackData.feedback_by_style[style];
                return (
                  <Badge key={style} variant="secondary" className="text-sm">
                    {style.charAt(0).toUpperCase() + style.slice(1)}
                    <span className="ml-1 text-xs opacity-75">
                      ({styleData.average_rating.toFixed(1)}★)
                    </span>
                  </Badge>
                );
              })}
            </div>
          </div>
        )}

        {/* Improvement Areas */}
        {feedbackData.improvement_areas.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <Target className="w-4 h-4 text-orange-500" />
              Areas for Improvement
            </h3>
            <div className="space-y-2">
              {improvementSuggestions.map((area, index) => (
                <div key={index} className="flex items-start gap-2 p-2 bg-orange-50 rounded border border-orange-200">
                  <Lightbulb className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-orange-700">{area}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Style Performance */}
        {Object.keys(feedbackData.feedback_by_style).length > 0 && (
          <div className="space-y-3">
            <h3 className="font-semibold text-foreground">Style Performance</h3>
            <div className="space-y-2">
              {Object.entries(feedbackData.feedback_by_style)
                .sort(([, a], [, b]) => b.average_rating - a.average_rating)
                .slice(0, 3)
                .map(([style, data]) => (
                  <div key={style} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm font-medium capitalize">{style}</span>
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1">
                        <Star className="w-3 h-3 text-yellow-500" />
                        <span className="text-sm">{data.average_rating.toFixed(1)}</span>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {data.total_feedback} ratings
                      </Badge>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Recent Feedback */}
        {feedbackData.recent_feedback.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-semibold text-foreground">Recent Activity</h3>
            <div className="space-y-2">
              {feedbackData.recent_feedback.slice(0, 3).map((feedback, index) => (
                <div key={index} className="flex items-center gap-3 p-2 bg-gray-50 rounded">
                  <div className={`p-1 rounded ${getFeedbackColor(feedback.feedback_type)}`}>
                    {feedback.feedback_type === 'like' && <ThumbsUp className="w-3 h-3" />}
                    {feedback.feedback_type === 'dislike' && <ThumbsDown className="w-3 h-3" />}
                    {feedback.feedback_type === 'issue' && <AlertTriangle className="w-3 h-3" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium capitalize">
                      {feedback.feedback_type}
                    </div>
                    {feedback.outfit_context?.occasion && (
                      <div className="text-xs text-muted-foreground">
                        {feedback.outfit_context.occasion}
                      </div>
                    )}
                  </div>
                  {feedback.rating && (
                    <div className="flex items-center gap-1">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span className="text-sm">{feedback.rating}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Call to Action */}
        <div className="text-center pt-4 border-t">
          <p className="text-sm text-muted-foreground mb-3">
            Keep rating outfits to get more personalized insights
          </p>
          <Button variant="outline" size="sm">
            View All Feedback
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

const getFeedbackColor = (type: string) => {
  switch (type) {
    case "like": return "bg-green-100 text-green-800";
    case "dislike": return "bg-red-100 text-red-800";
    case "issue": return "bg-orange-100 text-orange-800";
    default: return "bg-gray-100 text-gray-800";
  }
};
