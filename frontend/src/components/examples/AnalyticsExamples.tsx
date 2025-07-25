import React from 'react';
import { useAnalytics } from '../../shared/hooks/useAnalytics';

/**
 * Example component showing how to track button clicks
 */
export const AnalyticsButtonExample: React.FC = () => {
  const { trackClick } = useAnalytics();

  const handleGenerateOutfit = () => {
    trackClick('generate_outfit', {
      location: 'dashboard',
      occasion: 'casual',
    });
    // Your outfit generation logic here
  };

  const handleUploadPhoto = () => {
    trackClick('upload_photo', {
      location: 'wardrobe',
      source: 'camera',
    });
    // Your photo upload logic here
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Analytics Button Examples</h3>
      <div className="space-x-4">
        <button
          onClick={handleGenerateOutfit}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Generate Outfit
        </button>
        <button
          onClick={handleUploadPhoto}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Upload Photo
        </button>
      </div>
    </div>
  );
};

/**
 * Example component showing how to track form submissions
 */
export const AnalyticsFormExample: React.FC = () => {
  const { trackFormSubmit, trackError } = useAnalytics();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!email || !password) {
      trackError('form_validation_error', {
        form: 'login',
        missing_fields: [!email && 'email', !password && 'password'].filter(Boolean),
      });
      return;
    }

    // Track successful form submission
    trackFormSubmit('login', {
      email_provided: !!email,
      password_length: password.length,
    });

    // Your login logic here
    console.log('Logging in with:', { email, password });
  };

  return (
    <div className="max-w-md">
      <h3 className="text-lg font-semibold mb-4">Analytics Form Example</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your email"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your password"
          />
        </div>
        <button
          type="submit"
          className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Login
        </button>
      </form>
    </div>
  );
};

/**
 * Example component showing how to track user interactions
 */
export const AnalyticsInteractionExample: React.FC = () => {
  const { trackInteraction } = useAnalytics();

  const handleStylePreference = (style: string) => {
    trackInteraction('style_preference_selected', {
      style,
      location: 'onboarding',
    });
  };

  const handleOnboardingStep = (step: number) => {
    trackInteraction('onboarding_step_completed', {
      step,
      total_steps: 5,
    });
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Analytics Interaction Examples</h3>
      
      <div>
        <h4 className="font-medium mb-2">Style Preferences</h4>
        <div className="space-x-2">
          {['Casual', 'Business', 'Athletic', 'Formal'].map((style) => (
            <button
              key={style}
              onClick={() => handleStylePreference(style)}
              className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
            >
              {style}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h4 className="font-medium mb-2">Onboarding Steps</h4>
        <div className="space-x-2">
          {[1, 2, 3, 4, 5].map((step) => (
            <button
              key={step}
              onClick={() => handleOnboardingStep(step)}
              className="px-3 py-1 bg-blue-200 rounded hover:bg-blue-300"
            >
              Step {step}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * Example component showing how to track errors
 */
export const AnalyticsErrorExample: React.FC = () => {
  const { trackError } = useAnalytics();

  const simulateError = () => {
    try {
      // Simulate an error
      throw new Error('This is a simulated error for testing analytics');
    } catch (error) {
      trackError('simulated_error', {
        error_type: 'test_error',
        component: 'AnalyticsErrorExample',
        user_action: 'clicked_simulate_error',
      });
      console.error('Error caught and tracked:', error);
    }
  };

  const simulateApiError = () => {
    trackError('api_error_simulation', {
      endpoint: '/api/test',
      status: 500,
      error_message: 'Internal server error simulation',
    });
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Analytics Error Examples</h3>
      <div className="space-x-4">
        <button
          onClick={simulateError}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Simulate Error
        </button>
        <button
          onClick={simulateApiError}
          className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600"
        >
          Simulate API Error
        </button>
      </div>
    </div>
  );
};

/**
 * Main example component that combines all examples
 */
export const AnalyticsExamples: React.FC = () => {
  const { trackPageView } = useAnalytics();

  React.useEffect(() => {
    trackPageView('analytics_examples', {
      section: 'documentation',
    });
  }, [trackPageView]);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <h2 className="text-2xl font-bold">Frontend Analytics Integration Examples</h2>
      <p className="text-gray-600">
        These examples show how to integrate analytics into your React components.
        All events are automatically sent to your backend analytics endpoint.
      </p>

      <AnalyticsButtonExample />
      <AnalyticsFormExample />
      <AnalyticsInteractionExample />
      <AnalyticsErrorExample />

      <div className="bg-gray-100 p-4 rounded">
        <h3 className="font-semibold mb-2">Analytics Events Being Tracked:</h3>
        <ul className="text-sm space-y-1">
          <li>• Page views (automatic)</li>
          <li>• Button clicks with context</li>
          <li>• Form submissions with validation</li>
          <li>• User interactions and preferences</li>
          <li>• Errors and exceptions</li>
          <li>• API calls (automatic via apiWithAnalytics)</li>
        </ul>
      </div>
    </div>
  );
};

export default AnalyticsExamples; 