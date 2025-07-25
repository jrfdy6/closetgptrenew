import { useCallback, useEffect } from 'react';
import { analytics } from '../utils/analytics';
import { useAuth } from '../../hooks/useAuth';

/**
 * React hook for analytics
 * Provides easy access to analytics functions and automatically initializes with user ID
 */
export const useAnalytics = () => {
  const { user } = useAuth();

  // Initialize analytics with user ID when user changes
  useEffect(() => {
    if (user?.uid) {
      analytics.init(user.uid);
    } else {
      analytics.init(); // Initialize without user ID for anonymous users
    }
  }, [user?.uid]);

  const trackPageView = useCallback((page: string, metadata?: Record<string, any>) => {
    analytics.trackPageView(page, metadata);
  }, []);

  const trackClick = useCallback((button: string, metadata?: Record<string, any>) => {
    analytics.trackClick(button, metadata);
  }, []);

  const trackFormSubmit = useCallback((form: string, metadata?: Record<string, any>) => {
    analytics.trackFormSubmit(form, metadata);
  }, []);

  const trackError = useCallback((error: string, metadata?: Record<string, any>) => {
    analytics.trackError(error, metadata);
  }, []);

  const trackInteraction = useCallback((action: string, metadata?: Record<string, any>) => {
    analytics.trackInteraction(action, metadata);
  }, []);

  const trackApiCall = useCallback((endpoint: string, method: string, status: number, duration?: number) => {
    analytics.trackApiCall(endpoint, method, status, duration);
  }, []);

  const track = useCallback((eventType: string, metadata?: Record<string, any>) => {
    analytics.track(eventType, metadata);
  }, []);

  const setEnabled = useCallback((enabled: boolean) => {
    analytics.setEnabled(enabled);
  }, []);

  return {
    trackPageView,
    trackClick,
    trackFormSubmit,
    trackError,
    trackInteraction,
    trackApiCall,
    track,
    setEnabled,
    sessionId: analytics.getSessionId(),
    userId: analytics.getUserId(),
  };
};

export default useAnalytics; 