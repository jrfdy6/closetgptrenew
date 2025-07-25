# Frontend Analytics Integration Guide

This guide shows how to integrate analytics into your ClosetGPT frontend components without external SDKs.

## Quick Start

### 1. Import the Analytics Hook

```tsx
import { useAnalytics } from '../shared/hooks/useAnalytics';
```

### 2. Use Analytics in Your Component

```tsx
const MyComponent = () => {
  const { trackClick, trackFormSubmit, trackError } = useAnalytics();

  const handleButtonClick = () => {
    trackClick('my_button', {
      location: 'dashboard',
      action: 'important_action',
    });
    // Your logic here
  };

  return (
    <button onClick={handleButtonClick}>
      Click Me
    </button>
  );
};
```

## Available Analytics Methods

### Page Views
```tsx
const { trackPageView } = useAnalytics();

// Track page view (usually done automatically)
trackPageView('/dashboard', {
  section: 'main',
  user_type: 'premium',
});
```

### Button Clicks
```tsx
const { trackClick } = useAnalytics();

trackClick('generate_outfit', {
  location: 'dashboard',
  occasion: 'casual',
  user_preference: 'minimalist',
});
```

### Form Submissions
```tsx
const { trackFormSubmit } = useAnalytics();

trackFormSubmit('user_registration', {
  form_type: 'signup',
  has_avatar: true,
  completed_steps: 3,
});
```

### User Interactions
```tsx
const { trackInteraction } = useAnalytics();

trackInteraction('style_preference_selected', {
  style: 'business_casual',
  location: 'onboarding',
  step: 2,
});
```

### Errors
```tsx
const { trackError } = useAnalytics();

trackError('validation_error', {
  form: 'login',
  field: 'email',
  error_type: 'invalid_format',
});
```

### Custom Events
```tsx
const { track } = useAnalytics();

track('wardrobe_item_added', {
  item_type: 'shirt',
  color: 'blue',
  brand: 'nike',
  price_range: 'mid',
});
```

## API Call Tracking

Use the `apiWithAnalytics` wrapper for automatic API call tracking:

```tsx
import { apiWithAnalytics } from '../shared/utils/apiWithAnalytics';

// Instead of fetch()
const data = await apiWithAnalytics.get('/api/outfits');

// Instead of fetch() with POST
const result = await apiWithAnalytics.post('/api/wardrobe/add', {
  name: 'Blue Shirt',
  type: 'shirt',
});
```

This automatically tracks:
- API call duration
- Success/failure status
- Error details
- Endpoint and method

## Integration Examples

### Login Form
```tsx
const LoginForm = () => {
  const { trackFormSubmit, trackError } = useAnalytics();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      trackError('form_validation_error', {
        form: 'login',
        missing_fields: [!email && 'email', !password && 'password'].filter(Boolean),
      });
      return;
    }

    trackFormSubmit('login', {
      email_provided: !!email,
      password_length: password.length,
    });

    // Your login logic
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
    </form>
  );
};
```

### Outfit Generation
```tsx
const OutfitGenerator = () => {
  const { trackClick, trackError } = useAnalytics();

  const generateOutfit = async (occasion) => {
    trackClick('generate_outfit', {
      occasion,
      location: 'wardrobe',
      user_wardrobe_size: wardrobeItems.length,
    });

    try {
      const outfit = await apiWithAnalytics.post('/api/outfit/generate', {
        occasion,
        weather_conditions: currentWeather,
      });
      
      // Success handling
    } catch (error) {
      trackError('outfit_generation_failed', {
        occasion,
        error: error.message,
        weather_conditions: currentWeather,
      });
    }
  };

  return (
    <button onClick={() => generateOutfit('casual')}>
      Generate Casual Outfit
    </button>
  );
};
```

### Photo Upload
```tsx
const PhotoUpload = () => {
  const { trackClick, trackError } = useAnalytics();

  const handleUpload = async (file) => {
    trackClick('upload_photo', {
      file_size: file.size,
      file_type: file.type,
      source: 'camera',
    });

    try {
      const result = await apiWithAnalytics.post('/api/analyze', file);
      // Success handling
    } catch (error) {
      trackError('photo_upload_failed', {
        file_size: file.size,
        file_type: file.type,
        error: error.message,
      });
    }
  };

  return (
    <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />
  );
};
```

## Best Practices

### 1. Be Specific with Event Names
```tsx
// Good
trackClick('generate_outfit_casual');

// Better
trackClick('generate_outfit', {
  occasion: 'casual',
  location: 'dashboard',
});
```

### 2. Include Relevant Context
```tsx
trackClick('add_to_wardrobe', {
  item_type: 'shirt',
  color: 'blue',
  brand: 'nike',
  price_range: 'mid',
  source: 'search_results',
});
```

### 3. Track Errors with Context
```tsx
trackError('api_call_failed', {
  endpoint: '/api/outfits',
  method: 'GET',
  status_code: 500,
  user_action: 'refresh_page',
});
```

### 4. Use Consistent Metadata Keys
```tsx
// Use consistent keys across components
trackClick('button_click', {
  location: 'dashboard', // consistent
  action: 'generate_outfit', // consistent
  user_type: 'premium', // consistent
});
```

## Privacy Considerations

- Analytics events include user ID only when user is logged in
- Session ID is automatically generated for anonymous users
- No personally identifiable information is sent without consent
- Analytics can be disabled via `setEnabled(false)`

## Testing Analytics

1. Open browser developer tools
2. Look for analytics events in the Network tab
3. Check console for analytics initialization messages
4. Verify events are being sent to `/api/analytics/event`

## Event Types Overview

| Event Type | Description | Common Use Cases |
|------------|-------------|------------------|
| `page_view` | Page navigation | Route changes, landing pages |
| `button_click` | Button interactions | Generate outfit, upload photo |
| `form_submit` | Form submissions | Login, signup, feedback |
| `user_interaction` | General interactions | Style preferences, onboarding |
| `frontend_error` | Client-side errors | Validation errors, API failures |
| `api_call` | API requests | All backend communication |
| `api_error` | API failures | Network errors, server errors |

## Next Steps

1. Integrate analytics into your existing components
2. Add error tracking to catch and monitor issues
3. Use the analytics data to improve user experience
4. Consider adding analytics dashboard for insights 