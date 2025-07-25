import { authenticatedFetch } from '@/lib/utils/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export type IssueCategory = 
  | 'outfit_doesnt_make_sense'
  | 'inappropriate_items'
  | 'wrong_style'
  | 'wrong_occasion'
  | 'wrong_weather'
  | 'duplicate_items'
  | 'missing_items'
  | 'color_mismatch'
  | 'sizing_issues'
  | 'other';

export interface FeedbackData {
  outfit_id: string;
  feedback_type: 'like' | 'dislike' | 'issue';
  issue_category?: string;
  issue_description?: string;
  rating?: number;
  context_data?: {
    user_agent?: string;
    platform?: string;
    location?: string;
    session_data?: any;
  };
}

export interface FeedbackResponse {
  success: boolean;
  message: string;
  feedback_id?: string;
}

export interface FeedbackSummary {
  total_feedback: number;
  likes: number;
  dislikes: number;
  issues: number;
  average_rating: number;
  issue_categories: Record<string, number>;
  recent_feedback: Array<{
    feedback_type: string;
    timestamp: string;
    rating?: number;
    issue_category?: string;
  }>;
}

export interface AnalyticsSummary {
  total_outfits_rated: number;
  total_feedback: number;
  likes: number;
  dislikes: number;
  issues: number;
  average_rating: number;
  top_issue_categories: Record<string, number>;
  feedback_trend: Record<string, any>;
  preferred_occasions: Record<string, number>;
  preferred_styles: Record<string, number>;
}

export const feedbackApi = {
  /**
   * Submit feedback for an outfit
   */
  async submitFeedback(feedback: FeedbackData): Promise<FeedbackResponse> {
    const response = await authenticatedFetch(`${API_BASE_URL}/api/feedback/outfit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(feedback),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to submit feedback');
    }

    return response.json();
  },

  /**
   * Get feedback summary for a specific outfit
   */
  async getOutfitFeedbackSummary(outfitId: string): Promise<FeedbackSummary> {
    const response = await authenticatedFetch(`${API_BASE_URL}/api/feedback/outfit/${outfitId}/summary`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get feedback summary');
    }

    const data = await response.json();
    return data.data;
  },

  /**
   * Get overall feedback analytics summary for the user
   */
  async getAnalyticsSummary(): Promise<AnalyticsSummary> {
    const response = await authenticatedFetch(`${API_BASE_URL}/api/feedback/analytics/summary`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get analytics summary');
    }

    const data = await response.json();
    return data.data;
  },

  /**
   * Get feedback statistics for dashboard
   */
  async getFeedbackStats(): Promise<{
    totalFeedback: number;
    averageRating: number;
    topIssues: Array<{ category: string; count: number }>;
    recentActivity: Array<{ outfitId: string; feedbackType: string; timestamp: string }>;
  }> {
    try {
      const analytics = await this.getAnalyticsSummary();
      
      const topIssues = Object.entries(analytics.top_issue_categories)
        .map(([category, count]) => ({ category, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

      return {
        totalFeedback: analytics.total_feedback,
        averageRating: analytics.average_rating,
        topIssues,
        recentActivity: [] // This would need a separate endpoint for recent activity
      };
    } catch (error) {
      console.error('Error getting feedback stats:', error);
      return {
        totalFeedback: 0,
        averageRating: 0,
        topIssues: [],
        recentActivity: []
      };
    }
  }
}; 