'use client';

import { useState, useEffect } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { feedbackApi } from '@/lib/api/feedbackApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ThumbsUp, ThumbsDown, AlertTriangle, Star, Calendar, Clock } from 'lucide-react';

interface FeedbackItem {
  feedback_id: string;
  outfit_id: string;
  feedback_type: 'like' | 'dislike' | 'issue';
  rating?: number;
  issue_category?: string;
  issue_description?: string;
  timestamp: string;
  outfit_context?: {
    occasion?: string;
    mood?: string;
    style?: string;
  };
}

export default function FeedbackReviewPage() {
  const { user } = useFirebase();
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;

    const fetchFeedback = async () => {
      try {
        setLoading(true);
        // For now, we'll use a mock approach since we need to create an endpoint
        // that fetches all feedback for a user
        const analytics = await feedbackApi.getAnalyticsSummary();
        
        // Since we don't have a direct endpoint for all feedback items,
        // we'll show the analytics summary for now
        console.log('Feedback Analytics:', analytics);
        
        // TODO: Create an endpoint to fetch all feedback items
        // For now, show a message that feedback is being collected
        setFeedback([]);
        
      } catch (err) {
        console.error('Error fetching feedback:', err);
        setError('Failed to load feedback data');
      } finally {
        setLoading(false);
      }
    };

    fetchFeedback();
  }, [user]);

  const getFeedbackIcon = (type: string) => {
    switch (type) {
      case 'like':
        return <ThumbsUp className="w-4 h-4 text-green-600" />;
      case 'dislike':
        return <ThumbsDown className="w-4 h-4 text-red-600" />;
      case 'issue':
        return <AlertTriangle className="w-4 h-4 text-orange-600" />;
      default:
        return null;
    }
  };

  const getFeedbackColor = (type: string) => {
    switch (type) {
      case 'like':
        return 'bg-green-100 text-green-800';
      case 'dislike':
        return 'bg-red-100 text-red-800';
      case 'issue':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!user) {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold mb-2">Please Log In</h2>
              <p className="text-muted-foreground">
                You need to be logged in to view your feedback.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="space-y-4">
          <Skeleton className="h-8 w-48" />
          <div className="grid gap-4">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                    <Skeleton className="h-4 w-1/4" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold mb-2 text-red-600">Error</h2>
              <p className="text-muted-foreground">{error}</p>
              <Button 
                onClick={() => window.location.reload()} 
                className="mt-4"
                variant="outline"
              >
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Your Feedback</h1>
        <p className="text-muted-foreground">
          Review all the feedback you've submitted for outfit recommendations.
        </p>
      </div>

      {feedback.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto">
                <ThumbsUp className="w-8 h-8 text-muted-foreground" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">No Feedback Yet</h3>
                <p className="text-muted-foreground mb-4">
                  You haven't submitted any feedback yet. Start by rating some outfits!
                </p>
                <Button onClick={() => window.history.back()}>
                  Go Back to Outfits
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {feedback.map((item) => (
            <Card key={item.feedback_id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {getFeedbackIcon(item.feedback_type)}
                    <div>
                      <CardTitle className="text-lg">
                        {item.feedback_type === 'like' && 'Liked Outfit'}
                        {item.feedback_type === 'dislike' && 'Disliked Outfit'}
                        {item.feedback_type === 'issue' && 'Reported Issue'}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground">
                        Outfit ID: {item.outfit_id}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getFeedbackColor(item.feedback_type)}>
                      {item.feedback_type}
                    </Badge>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Calendar className="w-4 h-4" />
                      {formatDate(item.timestamp)}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {item.rating && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">Rating:</span>
                      <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className={`w-4 h-4 ${
                              star <= item.rating! 
                                ? 'fill-yellow-400 text-yellow-400' 
                                : 'text-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {item.issue_category && (
                    <div>
                      <span className="text-sm font-medium">Issue Category:</span>
                      <Badge variant="outline" className="ml-2">
                        {item.issue_category.replace(/_/g, ' ')}
                      </Badge>
                    </div>
                  )}
                  
                  {item.issue_description && (
                    <div>
                      <span className="text-sm font-medium">Description:</span>
                      <p className="text-sm text-muted-foreground mt-1">
                        {item.issue_description}
                      </p>
                    </div>
                  )}
                  
                  {item.outfit_context && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                      {item.outfit_context.occasion && (
                        <div>
                          <span className="font-medium">Occasion:</span>
                          <p className="text-muted-foreground">{item.outfit_context.occasion}</p>
                        </div>
                      )}
                      {item.outfit_context.style && (
                        <div>
                          <span className="font-medium">Style:</span>
                          <p className="text-muted-foreground">{item.outfit_context.style}</p>
                        </div>
                      )}
                      {item.outfit_context.mood && (
                        <div>
                          <span className="font-medium">Mood:</span>
                          <p className="text-muted-foreground">{item.outfit_context.mood}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
} 