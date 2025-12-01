/**
 * Privacy Service
 * Handles user privacy settings and data management
 */

import { User } from 'firebase/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-production.up.railway.app';

export interface PrivacySettings {
  share_analytics: boolean;
  share_style_data: boolean;
  allow_data_collection: boolean;
  allow_personalization: boolean;
  data_retention_days: number | null;
  last_updated?: string | null;
}

export interface PrivacySummary {
  data_summary: {
    outfits: number;
    wardrobe_items: number;
    analytics_entries: number;
    total: number;
  };
  privacy_settings: {
    share_analytics: boolean;
    share_style_data: boolean;
    allow_data_collection: boolean;
    allow_personalization: boolean;
  };
  data_retention: number | null;
  last_updated: string | null;
}

class PrivacyService {
  private async getAuthToken(user: User | null): Promise<string> {
    if (!user) {
      throw new Error('User not authenticated');
    }
    return await user.getIdToken();
  }

  async getPrivacySettings(user: User | null): Promise<PrivacySettings> {
    const token = await this.getAuthToken(user);
    
    const response = await fetch(`${API_URL}/api/privacy-settings`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch privacy settings' }));
      throw new Error(error.detail || 'Failed to fetch privacy settings');
    }

    return response.json();
  }

  async updatePrivacySettings(
    user: User | null,
    settings: Partial<PrivacySettings>
  ): Promise<PrivacySettings> {
    const token = await this.getAuthToken(user);
    
    const response = await fetch(`${API_URL}/api/privacy-settings`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(settings)
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to update privacy settings' }));
      throw new Error(error.detail || 'Failed to update privacy settings');
    }

    const result = await response.json();
    return result.settings;
  }

  async getPrivacySummary(user: User | null): Promise<PrivacySummary> {
    const token = await this.getAuthToken(user);
    
    const response = await fetch(`${API_URL}/api/privacy-summary`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch privacy summary' }));
      throw new Error(error.detail || 'Failed to fetch privacy summary');
    }

    return response.json();
  }

  async deleteUserData(
    user: User | null,
    dataType?: 'all' | 'outfits' | 'wardrobe' | 'analytics'
  ): Promise<{ success: boolean; message: string; deleted: string[] }> {
    const token = await this.getAuthToken(user);
    
    const url = dataType 
      ? `${API_URL}/api/privacy-data?data_type=${dataType}`
      : `${API_URL}/api/privacy-data`;
    
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to delete data' }));
      throw new Error(error.detail || 'Failed to delete data');
    }

    return response.json();
  }
}

export const privacyService = new PrivacyService();

