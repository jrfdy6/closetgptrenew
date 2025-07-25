# Outfit Feedback System

A comprehensive feedback system for collecting user feedback on generated outfits, with analytics and data lake integration.

## Overview

The feedback system allows users to:
- **Like** outfits with 1-5 star ratings
- **Dislike** outfits they don't like
- **Report issues** with specific categories and descriptions

All feedback is stored with comprehensive context data for analytics and machine learning improvements.

## Architecture

### Backend Components

#### 1. Feedback API (`backend/src/routes/feedback.py`)
- **POST** `/api/feedback/outfit` - Submit outfit feedback
- **GET** `/api/feedback/outfit/{outfit_id}/summary` - Get feedback summary for an outfit
- **GET** `/api/feedback/analytics/summary` - Get user's overall feedback analytics

#### 2. Data Models
```python
class FeedbackType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    ISSUE = "issue"

class IssueCategory(str, Enum):
    INAPPROPRIATE_ITEMS = "inappropriate_items"
    WRONG_STYLE = "wrong_style"
    WRONG_OCCASION = "wrong_occasion"
    WRONG_WEATHER = "wrong_weather"
    DUPLICATE_ITEMS = "duplicate_items"
    MISSING_ITEMS = "missing_items"
    COLOR_MISMATCH = "color_mismatch"
    SIZING_ISSUES = "sizing_issues"
    OTHER = "other"
```

#### 3. Data Storage
- **Firestore Collections:**
  - `outfit_feedback` - Individual feedback records
  - `analytics_events` - Events for data lake processing
  - `outfits` - Updated with feedback summaries

### Frontend Components

#### 1. OutfitFeedback Component (`frontend/src/components/OutfitFeedback.tsx`)
- Interactive feedback form with like/dislike/issue buttons
- Star rating system for likes
- Issue category selection with descriptions
- Optional detailed issue descriptions
- Real-time feedback summary

#### 2. FeedbackAnalytics Component (`frontend/src/components/FeedbackAnalytics.tsx`)
- Dashboard showing feedback statistics
- User preference analysis
- Issue trend analysis
- Performance metrics

#### 3. API Service (`frontend/src/lib/api/feedbackApi.ts`)
- TypeScript interfaces for feedback data
- API client functions for all feedback operations
- Error handling and response processing

## Data Collection

### Feedback Context Data
Each feedback submission includes:

```typescript
{
  outfit_id: string;
  feedback_type: 'like' | 'dislike' | 'issue';
  rating?: number; // 1-5 for likes
  issue_category?: string;
  issue_description?: string;
  context_data: {
    user_agent: string;
    platform: string;
    location: string;
    session_data: {
      timestamp: string;
      url: string;
      referrer: string;
    }
  }
}
```

### Outfit Context
Automatically captured outfit information:
- Occasion, mood, style
- Number of items and item types
- Creation timestamp
- Generation method

### User Context
User information and preferences:
- User ID and email
- User preferences from profile
- Feedback timestamp
- Session data

## Analytics & Data Lake

### Analytics Events
All feedback is stored in `analytics_events` collection for data lake processing:

```json
{
  "event_type": "outfit_feedback",
  "event_data": { /* complete feedback data */ },
  "timestamp": "2024-01-01T12:00:00Z",
  "user_id": "user123",
  "outfit_id": "outfit456",
  "feedback_type": "like",
  "rating": 5,
  "metadata": {
    "source": "user_feedback",
    "version": "1.0",
    "processed": false
  }
}
```

### Data Export Script
Run `backend/scripts/export_feedback.py` to export feedback data:

```bash
cd backend
python scripts/export_feedback.py
```

This creates a JSON file with all feedback data for analysis.

## Usage

### Adding Feedback to Outfit Pages

```tsx
import { OutfitFeedback } from '@/components/OutfitFeedback';

function OutfitPage({ outfitId }) {
  return (
    <div>
      {/* Outfit details */}
      <OutfitFeedback 
        outfitId={outfitId}
        onFeedbackSubmitted={() => {
          // Handle feedback submission
        }}
      />
    </div>
  );
}
```

### Adding Analytics Dashboard

```tsx
import { FeedbackAnalytics } from '@/components/FeedbackAnalytics';

function AnalyticsPage() {
  return (
    <div>
      <h1>Feedback Analytics</h1>
      <FeedbackAnalytics />
    </div>
  );
}
```

### API Usage

```typescript
import { feedbackApi } from '@/lib/api/feedbackApi';

// Submit feedback
await feedbackApi.submitFeedback({
  outfit_id: 'outfit123',
  feedback_type: 'like',
  rating: 5,
  context_data: {
    user_agent: navigator.userAgent,
    platform: navigator.platform,
    location: 'web'
  }
});

// Get analytics
const analytics = await feedbackApi.getAnalyticsSummary();
```

## Benefits

### For Users
- Easy way to provide feedback on outfit quality
- Helps improve future outfit generation
- Clear categories for reporting issues
- Star rating system for positive feedback

### For Development
- Comprehensive data collection for ML training
- Real-time analytics on outfit performance
- Issue tracking and trend analysis
- User preference learning

### For Analytics
- Structured data for data lake processing
- Rich context for machine learning
- Historical trend analysis
- Performance optimization insights

## Future Enhancements

1. **ML Integration**: Use feedback data to train outfit generation models
2. **A/B Testing**: Test different generation algorithms based on feedback
3. **Personalization**: Use feedback to personalize outfit recommendations
4. **Automated Insights**: Generate automated reports on outfit performance
5. **Real-time Alerts**: Alert developers to trending issues

## Security & Privacy

- All feedback is tied to authenticated users
- User data is anonymized in analytics exports
- Feedback data is stored securely in Firestore
- API endpoints require authentication
- GDPR-compliant data handling

## Monitoring

- Feedback submission success/failure rates
- API response times
- Data export completion
- Error tracking and alerting
- User engagement metrics 