/**
 * Privacy Service
 * Handles user privacy settings and data management
 */

import { User } from 'firebase/auth';
import { buildPublicBackendUrl } from '@/lib/publicBackendUrl';

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

export interface DataClearStatus {
  success: boolean;
  status: 'idle' | 'pending' | 'running' | 'failed' | 'complete';
  completed: boolean;
  job_id?: string;
  scope?: 'all' | 'outfits' | 'wardrobe' | 'analytics';
  deleted?: number;
  retryable?: boolean;
  error?: string | null;
  retained?: string[];
}

function confirmClearStatus(result: DataClearStatus): DataClearStatus {
  if (result?.success !== true || !['idle', 'pending', 'running', 'failed', 'complete'].includes(result.status) ||
      result.completed !== (result.status === 'complete')) throw new Error('The data-clear status could not be confirmed.');
  return result;
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
    
    const response = await fetch(buildPublicBackendUrl('/api/privacy-settings'), {
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
    
    const response = await fetch(buildPublicBackendUrl('/api/privacy-settings'), {
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
    
    const response = await fetch(buildPublicBackendUrl('/api/privacy-summary'), {
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
  ): Promise<DataClearStatus> {
    const token = await this.getAuthToken(user);
    
    const url = dataType 
      ? buildPublicBackendUrl(`/api/privacy-data?data_type=${encodeURIComponent(dataType)}`)
      : buildPublicBackendUrl('/api/privacy-data');
    
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

    return confirmClearStatus(await response.json());
  }

  async getDataClearStatus(user: User | null): Promise<DataClearStatus> {
    const token = await this.getAuthToken(user);
    const response = await fetch(buildPublicBackendUrl('/api/privacy-data/status'), {
      cache: 'no-store', headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error('The data-clear status is unavailable. Please check again.');
    return confirmClearStatus(await response.json());
  }

}

export const privacyService = new PrivacyService();
