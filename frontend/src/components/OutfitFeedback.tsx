"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { ThumbsUp, ThumbsDown, AlertTriangle, Star, CheckCircle, XCircle } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { authenticatedFetch } from '@/lib/utils/auth';

interface OutfitFeedbackProps {
  outfitId: string;
  onFeedbackSubmitted?: () => void;
  className?: string;
}

type FeedbackType = 'like' | 'dislike' | 'issue';

type IssueCategory = 
  | 'inappropriate_items'
  | 'wrong_style'
  | 'wrong_occasion'
  | 'wrong_weather'
  | 'duplicate_items'
  | 'missing_items'
  | 'color_mismatch'
  | 'sizing_issues'
  | 'other'
  | 'outfit_doesnt_make_sense';

interface FeedbackData {
  outfit_id: string;
  feedback_type: FeedbackType;
  issue_category?: IssueCategory;
  issue_description?: string;
  rating?: number;
  context_data?: {
    user_agent?: string;
    platform?: string;
    location?: string;
    session_data?: any;
  };
}

const ISSUE_CATEGORIES: { value: IssueCategory; label: string; description: string }[] = [
  { value: 'outfit_doesnt_make_sense', label: 'Outfit Doesn\'t Make Sense', description: 'The overall outfit combination is illogical or confusing' },
  { value: 'inappropriate_items', label: 'Inappropriate Items', description: 'Items don\'t match the occasion or style' },
  { value: 'wrong_style', label: 'Wrong Style', description: 'Style doesn\'t match what I requested' },
  { value: 'wrong_occasion', label: 'Wrong Occasion', description: 'Outfit isn\'t suitable for the occasion' },
  { value: 'wrong_weather', label: 'Wrong Weather', description: 'Items aren\'t appropriate for the weather' },
  { value: 'duplicate_items', label: 'Duplicate Items', description: 'Same item appears multiple times' },
  { value: 'missing_items', label: 'Missing Items', description: 'Essential items are missing' },
  { value: 'color_mismatch', label: 'Color Mismatch', description: 'Colors don\'t work well together' },
  { value: 'sizing_issues', label: 'Sizing Issues', description: 'Items don\'t fit properly' },
  { value: 'other', label: 'Other', description: 'Something else is wrong' }
];

export function OutfitFeedback({ outfitId, onFeedbackSubmitted, className = "" }: OutfitFeedbackProps) {
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackType | null>(null);
  const [rating, setRating] = useState<number>(0);
  const [issueCategory, setIssueCategory] = useState<IssueCategory | ''>('');
  const [issueDescription, setIssueDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const { toast } = useToast();

  const handleFeedbackSelect = (feedbackType: FeedbackType) => {
    setSelectedFeedback(feedbackType);
    if (feedbackType !== 'like') {
      setRating(0);
    }
  };

  const handleRatingSelect = (newRating: number) => {
    setRating(newRating);
  };

  const handleSubmit = async () => {
    if (!selectedFeedback) {
      toast({
        title: "No feedback selected",
        description: "Please select like, dislike, or report an issue",
        variant: "destructive",
      });
      return;
    }

    if (selectedFeedback === 'like' && rating === 0) {
      toast({
        title: "No rating selected",
        description: "Please select a rating from 1-5 stars",
        variant: "destructive",
      });
      return;
    }

    if (selectedFeedback === 'issue' && !issueCategory) {
      toast({
        title: "No issue category selected",
        description: "Please select what type of issue you're reporting",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const feedbackData: FeedbackData = {
        outfit_id: outfitId,
        feedback_type: selectedFeedback,
        context_data: {
          user_agent: navigator.userAgent,
          platform: navigator.platform,
          location: 'web',
          session_data: {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            referrer: document.referrer
          }
        }
      };

      if (selectedFeedback === 'like' && rating > 0) {
        feedbackData.rating = rating;
      }

      if (selectedFeedback === 'issue') {
        feedbackData.issue_category = issueCategory as IssueCategory;
        if (issueDescription.trim()) {
          feedbackData.issue_description = issueDescription.trim();
        }
      }

      const response = await authenticatedFetch('/api/feedback/outfit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit feedback');
      }

      const result = await response.json();
      
      setHasSubmitted(true);
      
      toast({
        title: "Feedback submitted!",
        description: "Thank you for your feedback. It helps us improve our outfit generation.",
      });

      onFeedbackSubmitted?.();

    } catch (error) {
      console.error('Error submitting feedback:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to submit feedback",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setSelectedFeedback(null);
    setRating(0);
    setIssueCategory('');
    setIssueDescription('');
    setHasSubmitted(false);
  };

  if (hasSubmitted) {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
            <h3 className="text-lg font-semibold">Thank you for your feedback!</h3>
            <p className="text-gray-600">
              Your feedback helps us improve our outfit generation algorithm.
            </p>
            <Button onClick={handleReset} variant="outline">
              Submit Another Feedback
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          Rate this Outfit
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Feedback Type Selection */}
        <div className="space-y-3">
          <Label>How do you feel about this outfit?</Label>
          <div className="flex gap-3">
            <Button
              variant={selectedFeedback === 'like' ? 'default' : 'outline'}
              onClick={() => handleFeedbackSelect('like')}
              className="flex-1"
              disabled={isSubmitting}
            >
              <ThumbsUp className="h-4 w-4 mr-2" />
              I Like It
            </Button>
            <Button
              variant={selectedFeedback === 'dislike' ? 'default' : 'outline'}
              onClick={() => handleFeedbackSelect('dislike')}
              className="flex-1"
              disabled={isSubmitting}
            >
              <ThumbsDown className="h-4 w-4 mr-2" />
              I Don't Like It
            </Button>
            <Button
              variant={selectedFeedback === 'issue' ? 'default' : 'outline'}
              onClick={() => handleFeedbackSelect('issue')}
              className="flex-1"
              disabled={isSubmitting}
            >
              <AlertTriangle className="h-4 w-4 mr-2" />
              Report Issue
            </Button>
          </div>
        </div>

        {/* Rating for Likes */}
        {selectedFeedback === 'like' && (
          <div className="space-y-3">
            <Label>Rate this outfit (1-5 stars)</Label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <Button
                  key={star}
                  variant={rating >= star ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleRatingSelect(star)}
                  disabled={isSubmitting}
                  className="p-2"
                >
                  <Star className={`h-4 w-4 ${rating >= star ? 'fill-current' : ''}`} />
                </Button>
              ))}
            </div>
            {rating > 0 && (
              <p className="text-sm text-gray-600">
                {rating === 1 && "Poor"}
                {rating === 2 && "Fair"}
                {rating === 3 && "Good"}
                {rating === 4 && "Very Good"}
                {rating === 5 && "Excellent"}
              </p>
            )}
          </div>
        )}

        {/* Issue Category Selection */}
        {selectedFeedback === 'issue' && (
          <div className="space-y-3">
            <Label>What type of issue are you reporting?</Label>
            <Select
              value={issueCategory}
              onValueChange={(value) => setIssueCategory(value as IssueCategory)}
              disabled={isSubmitting}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select issue category" />
              </SelectTrigger>
              <SelectContent>
                {ISSUE_CATEGORIES.map((category) => (
                  <SelectItem key={category.value} value={category.value}>
                    <div>
                      <div className="font-medium">{category.label}</div>
                      <div className="text-sm text-gray-500">{category.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Issue Description */}
        {selectedFeedback === 'issue' && issueCategory && (
          <div className="space-y-3">
            <Label>Additional details (optional)</Label>
            <Textarea
              placeholder="Please describe the issue in more detail..."
              value={issueDescription}
              onChange={(e) => setIssueDescription(e.target.value)}
              disabled={isSubmitting}
              rows={3}
            />
          </div>
        )}

        {/* Submit Button */}
        {selectedFeedback && (
          <div className="flex gap-3">
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex-1"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Submitting...
                </>
              ) : (
                'Submit Feedback'
              )}
            </Button>
            <Button
              onClick={handleReset}
              variant="outline"
              disabled={isSubmitting}
            >
              <XCircle className="h-4 w-4 mr-2" />
              Cancel
            </Button>
          </div>
        )}

        {/* Feedback Summary */}
        {selectedFeedback && (
          <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
            <div className="font-medium mb-1">You're about to submit:</div>
            <div className="space-y-1">
              <div>• Feedback Type: <Badge variant="secondary">{selectedFeedback}</Badge></div>
              {selectedFeedback === 'like' && rating > 0 && (
                <div>• Rating: <Badge variant="secondary">{rating}/5 stars</Badge></div>
              )}
              {selectedFeedback === 'issue' && issueCategory && (
                <div>• Issue: <Badge variant="secondary">
                  {ISSUE_CATEGORIES.find(c => c.value === issueCategory)?.label}
                </Badge></div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 