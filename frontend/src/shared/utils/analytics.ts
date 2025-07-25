/**
 * Lightweight frontend analytics utility
 * Sends events to backend analytics endpoint without external SDKs
 */

export interface AnalyticsEvent {
  user_id?: string;
  event_type: string;
  metadata?: Record<string, any>;
  timestamp?: string;
  session_id?: string;
}

export interface AnalyticsConfig {
  enabled: boolean;
  endpoint: string;
  session_id: string;
  user_id?: string;
}

class Analytics {
  private config: AnalyticsConfig;
  private queue: AnalyticsEvent[] = [];
  private isProcessing = false;

  constructor() {
    this.config = {
      enabled: true,
      endpoint: '/api/analytics/event',
      session_id: this.generateSessionId(),
    };
  }

  private generateSessionId(): string {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Initialize analytics with user ID
   */
  init(userId?: string): void {
    this.config.user_id = userId;
    console.log('Analytics initialized', { session_id: this.config.session_id, user_id: userId });
  }

  /**
   * Enable or disable analytics
   */
  setEnabled(enabled: boolean): void {
    this.config.enabled = enabled;
  }

  /**
   * Track a page view
   */
  trackPageView(page: string, metadata?: Record<string, any>): void {
    this.track('page_view', {
      page,
      url: window.location.href,
      referrer: document.referrer,
      ...metadata,
    });
  }

  /**
   * Track a button click
   */
  trackClick(button: string, metadata?: Record<string, any>): void {
    this.track('button_click', {
      button,
      ...metadata,
    });
  }

  /**
   * Track a form submission
   */
  trackFormSubmit(form: string, metadata?: Record<string, any>): void {
    this.track('form_submit', {
      form,
      ...metadata,
    });
  }

  /**
   * Track an error
   */
  trackError(error: string, metadata?: Record<string, any>): void {
    this.track('frontend_error', {
      error,
      url: window.location.href,
      user_agent: navigator.userAgent,
      ...metadata,
    });
  }

  /**
   * Track user interaction
   */
  trackInteraction(action: string, metadata?: Record<string, any>): void {
    this.track('user_interaction', {
      action,
      ...metadata,
    });
  }

  /**
   * Track API call
   */
  trackApiCall(endpoint: string, method: string, status: number, duration?: number): void {
    this.track('api_call', {
      endpoint,
      method,
      status,
      duration,
    });
  }

  /**
   * Track custom event
   */
  track(eventType: string, metadata?: Record<string, any>): void {
    if (!this.config.enabled) {
      return;
    }

    const event: AnalyticsEvent = {
      user_id: this.config.user_id,
      event_type: eventType,
      metadata: {
        session_id: this.config.session_id,
        timestamp: new Date().toISOString(),
        ...metadata,
      },
    };

    this.queue.push(event);
    this.processQueue();
  }

  /**
   * Process the event queue
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) {
      return;
    }

    this.isProcessing = true;

    try {
      const event = this.queue.shift();
      if (!event) return;

      await this.sendEvent(event);
    } catch (error) {
      console.warn('Failed to send analytics event:', error);
      // Don't retry failed events to avoid infinite loops
    } finally {
      this.isProcessing = false;
      
      // Process next event if queue is not empty
      if (this.queue.length > 0) {
        setTimeout(() => this.processQueue(), 100);
      }
    }
  }

  /**
   * Send event to backend
   */
  private async sendEvent(event: AnalyticsEvent): Promise<void> {
    try {
      const response = await fetch(this.config.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(event),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.warn('Analytics event failed to send:', error);
      throw error;
    }
  }

  /**
   * Get current session ID
   */
  getSessionId(): string {
    return this.config.session_id;
  }

  /**
   * Get current user ID
   */
  getUserId(): string | undefined {
    return this.config.user_id;
  }
}

// Create singleton instance
export const analytics = new Analytics();

// Auto-track page views on route changes (for SPAs)
if (typeof window !== 'undefined') {
  let currentPath = window.location.pathname;
  
  // Track initial page view
  analytics.trackPageView(currentPath);
  
  // Listen for route changes (basic implementation)
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;
  
  history.pushState = function(...args) {
    originalPushState.apply(history, args);
    const newPath = window.location.pathname;
    if (newPath !== currentPath) {
      currentPath = newPath;
      analytics.trackPageView(newPath);
    }
  };
  
  history.replaceState = function(...args) {
    originalReplaceState.apply(history, args);
    const newPath = window.location.pathname;
    if (newPath !== currentPath) {
      currentPath = newPath;
      analytics.trackPageView(newPath);
    }
  };
  
  // Track popstate events
  window.addEventListener('popstate', () => {
    const newPath = window.location.pathname;
    if (newPath !== currentPath) {
      currentPath = newPath;
      analytics.trackPageView(newPath);
    }
  });
}

export default analytics; 