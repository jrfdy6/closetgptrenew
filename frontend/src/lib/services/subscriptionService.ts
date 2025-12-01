/**
 * Subscription Service
 * Handles subscription management and payment integration
 */

import { User } from 'firebase/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-production.up.railway.app';

export interface Subscription {
  role: string;
  status: string;
  flatlays_remaining: number;
  trial_end?: number;
  is_trialing?: boolean;
  days_remaining_in_trial?: number;
  trial_used?: boolean;
}

export interface SubscriptionTier {
  id: string;
  name: string;
  price: string;
  pricePerMonth: number;
  features: string[];
  limit: string;
  popular?: boolean;
}

export const SUBSCRIPTION_TIERS: SubscriptionTier[] = [
  {
    id: 'tier1',
    name: 'Free',
    price: '$0',
    pricePerMonth: 0,
    features: [
      'Basic outfit generation',
      '1 flat lay per week',
      'Wardrobe management',
      'Style recommendations'
    ],
    limit: '1 flat lay/week'
  },
  {
    id: 'tier2',
    name: 'Pro',
    price: '$9.99',
    pricePerMonth: 9.99,
    features: [
      'Everything in Free',
      'Unlimited outfit generation',
      '7 flat lays per week',
      'Advanced styling options',
      'Style persona analysis',
      'Advanced outfit filtering',
      'Priority support'
    ],
    limit: '7 flat lays/week',
    popular: true
  },
  {
    id: 'tier3',
    name: 'Premium',
    price: '$29.99',
    pricePerMonth: 29.99,
    features: [
      'Everything in Pro',
      '30 flat lays per week',
      'AI-powered styling insights',
      'Early access to features',
      'Premium support'
    ],
    limit: '30 flat lays/week'
  }
];

class SubscriptionService {
  private async getAuthToken(user: User | null): Promise<string> {
    if (!user) {
      throw new Error('User not authenticated');
    }
    return await user.getIdToken();
  }

  async getCurrentSubscription(user: User | null): Promise<Subscription> {
    const token = await this.getAuthToken(user);
    
    const response = await fetch(`${API_URL}/api/payments/subscription/current`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch subscription' }));
      throw new Error(error.detail || 'Failed to fetch subscription');
    }

    return response.json();
  }

  async createCheckoutSession(user: User | null, role: string): Promise<{ checkout_url: string; session_id: string }> {
    const token = await this.getAuthToken(user);
    
    const response = await fetch(`${API_URL}/api/payments/checkout/create-session`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ role })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create checkout session' }));
      throw new Error(error.detail || 'Failed to create checkout session');
    }

    return response.json();
  }

  async createPortalSession(user: User | null): Promise<{ url: string }> {
    const token = await this.getAuthToken(user);
    
    const response = await fetch(`${API_URL}/api/payments/checkout/create-portal-session`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create portal session' }));
      throw new Error(error.detail || 'Failed to create portal session');
    }

    return response.json();
  }

  getTierDisplayName(role: string): string {
    const tier = SUBSCRIPTION_TIERS.find(t => t.id === role);
    return tier?.name || 'Free';
  }

  getTierInfo(role: string): SubscriptionTier | undefined {
    return SUBSCRIPTION_TIERS.find(t => t.id === role);
  }

  canAccessFeature(role: string, feature: 'semantic_filtering' | 'style_persona'): boolean {
    // Both features require tier2 or tier3
    return role === 'tier2' || role === 'tier3';
  }

  async consumeFlatLayQuota(user: User | null): Promise<{ remaining: number; limit: number }> {
    const token = await this.getAuthToken(user);
    
    const response = await fetch(`${API_URL}/api/payments/flatlay/consume`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to consume flat lay quota' }));
      throw new Error(error.detail || 'Failed to consume flat lay quota');
    }

    return response.json();
  }
}

export const subscriptionService = new SubscriptionService();

