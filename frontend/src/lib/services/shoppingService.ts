import { User } from 'firebase/auth';

export interface ShoppingRecommendation {
  id: string;
  name: string;
  category: string;
  item_type: string;
  description: string;
  style_tags: string[];
  colors: string[];
  sizes: string[];
  materials: string[];
  estimated_price: number;
  priority: string;
  why_needed: string;
  styling_tips: string;
  care_instructions: string;
  versatility_score: number;
  seasonality: string[];
  formality_level: string;
}

export interface StoreRecommendation {
  name: string;
  description: string;
  price_range: string;
}

export interface ShoppingStrategy {
  total_items_needed: number;
  high_priority_items: number;
  estimated_total_cost: number;
  budget_range: string;
  shopping_phases: Array<{
    phase: number;
    name: string;
    description: string;
    items: ShoppingRecommendation[];
    estimated_cost: number;
  }>;
  tips: string[];
}

export interface ShoppingRecommendationsResponse {
  success: boolean;
  recommendations: ShoppingRecommendation[];
  store_recommendations: StoreRecommendation[];
  shopping_strategy: ShoppingStrategy;
  total_estimated_cost: number;
  budget_range: string;
  generated_at: string;
}

class ShoppingService {
  private async makeAuthenticatedRequest(endpoint: string, user: User | null, options: RequestInit = {}): Promise<any> {
    if (!user) {
      throw new Error('User not authenticated');
    }

    const token = await user.getIdToken();
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
    
    const response = await fetch(`${baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getShoppingRecommendations(
    user: User | null,
    budgetRange?: string,
    preferredStores?: string[]
  ): Promise<ShoppingRecommendationsResponse | null> {
    try {
      console.log('🛍️ Fetching shopping recommendations...');
      
      const params = new URLSearchParams();
      if (budgetRange) params.append('budget_range', budgetRange);
      if (preferredStores) params.append('preferred_stores', preferredStores.join(','));

      const endpoint = `/wardrobe/gaps${params.toString() ? `?${params.toString()}` : ''}`;
      const response = await this.makeAuthenticatedRequest(endpoint, user);
      
      if (response?.success && response?.data?.shopping_recommendations) {
        console.log('✅ Shopping recommendations fetched successfully');
        return response.data.shopping_recommendations;
      } else {
        console.log('⚠️ No shopping recommendations available');
        return null;
      }
    } catch (error) {
      console.error('❌ Error fetching shopping recommendations:', error);
      return null;
    }
  }

  async getStoreRecommendations(
    user: User | null,
    budgetRange: string = 'medium'
  ): Promise<StoreRecommendation[]> {
    try {
      const recommendations = await this.getShoppingRecommendations(user, budgetRange);
      return recommendations?.store_recommendations || [];
    } catch (error) {
      console.error('❌ Error fetching store recommendations:', error);
      return [];
    }
  }

  async getShoppingStrategy(
    user: User | null,
    budgetRange?: string
  ): Promise<ShoppingStrategy | null> {
    try {
      const recommendations = await this.getShoppingRecommendations(user, budgetRange);
      return recommendations?.shopping_strategy || null;
    } catch (error) {
      console.error('❌ Error fetching shopping strategy:', error);
      return null;
    }
  }

  // Helper method to format price
  formatPrice(price: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  }

  // Helper method to get priority color
  getPriorityColor(priority: string): string {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'medium': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      case 'low': return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
    }
  }

  // Helper method to get versatility color
  getVersatilityColor(score: number): string {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  }

  // Helper method to sort recommendations
  sortRecommendations(
    recommendations: ShoppingRecommendation[],
    sortBy: 'priority' | 'price' | 'versatility'
  ): ShoppingRecommendation[] {
    return [...recommendations].sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
          return (priorityOrder[b.priority as keyof typeof priorityOrder] || 0) - 
                 (priorityOrder[a.priority as keyof typeof priorityOrder] || 0);
        case 'price':
          return a.estimated_price - b.estimated_price;
        case 'versatility':
          return b.versatility_score - a.versatility_score;
        default:
          return 0;
      }
    });
  }
}

export const shoppingService = new ShoppingService();
