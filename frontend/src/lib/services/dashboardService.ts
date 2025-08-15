import { User } from 'firebase/auth';

export interface DashboardData {
  totalItems: number;
  favorites: number;
  styleGoalsCompleted: number;
  totalStyleGoals: number;
  outfitsThisWeek: number;
  overallProgress: number;
  styleCollections: StyleCollection[];
  styleExpansions: StyleExpansion[];
  seasonalBalance: SeasonalBalance;
  colorVariety: ColorVariety;
  wardrobeGaps: WardrobeGap[];
  topItems: TopItem[];
  recentOutfits: RecentOutfit[];
}

export interface StyleCollection {
  name: string;
  progress: number;
  target: number;
  status: string;
}

export interface StyleExpansion {
  name: string;
  direction: string;
}

export interface SeasonalBalance {
  score: number;
  status: string;
  recommendations: string[];
  winterItems: number;
  winterPercentage: number;
  springItems: number;
  summerItems: number;
  fallItems: number;
}

export interface ColorVariety {
  current: number;
  target: number;
  status: string;
  colors: string[];
}

export interface WardrobeGap {
  category: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  suggestedItems: string[];
}

export interface TopItem {
  id: string;
  name: string;
  type: string;
  imageUrl: string;
  wearCount: number;
  rating: number;
}

export interface RecentOutfit {
  id: string;
  name: string;
  occasion: string;
  createdAt: string;
  items: string[];
}

class DashboardService {
  private async makeAuthenticatedRequest(endpoint: string, user: User): Promise<any> {
    if (!user) {
      throw new Error('Authentication required');
    }

    const token = await user.getIdToken();
    if (!token) {
      throw new Error('Failed to get authentication token');
    }

    const response = await fetch(endpoint, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getDashboardData(user: User): Promise<DashboardData> {
    try {
      console.log('🔍 DEBUG: Fetching dashboard data...');
      
      // Fetch data from multiple endpoints in parallel using frontend API routes
      const [
        wardrobeStats,
        outfitHistory,
        trendingStyles
      ] = await Promise.all([
        this.getWardrobeStats(user),
        this.getOutfitHistory(user),
        this.getTrendingStyles(user)
      ]);

      console.log('🔍 DEBUG: All API calls completed, processing data...');

      // Process and combine the data
      const dashboardData: DashboardData = {
        totalItems: wardrobeStats.total_items || 0,
        favorites: this.calculateFavorites(wardrobeStats),
        styleGoalsCompleted: this.calculateStyleGoals(wardrobeStats, trendingStyles),
        totalStyleGoals: 5, // Default value, could be configurable
        outfitsThisWeek: this.calculateOutfitsThisWeek(outfitHistory),
        overallProgress: this.calculateOverallProgress(wardrobeStats, trendingStyles),
        styleCollections: this.buildStyleCollections(wardrobeStats, trendingStyles),
        styleExpansions: this.buildStyleExpansions(wardrobeStats, trendingStyles),
        seasonalBalance: this.buildSeasonalBalance(wardrobeStats),
        colorVariety: this.buildColorVariety(wardrobeStats),
        wardrobeGaps: this.buildWardrobeGaps(wardrobeStats),
        topItems: this.buildTopItems(wardrobeStats),
        recentOutfits: this.buildRecentOutfits(outfitHistory)
      };

      console.log('🔍 DEBUG: Dashboard data processed:', dashboardData);
      return dashboardData;

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }

  private async getWardrobeStats(user: User) {
    try {
      console.log('🔍 DEBUG: Fetching wardrobe stats from /api/analytics/wardrobe-stats');
      const response = await this.makeAuthenticatedRequest('/api/analytics/wardrobe-stats', user);
      console.log('🔍 DEBUG: Wardrobe stats response:', response);
      return response || {};
    } catch (error) {
      console.error('Error fetching wardrobe stats:', error);
      // Return fallback data for production when backend is not ready
      return {
        total_items: 0,
        categories: {},
        colors: {},
        user_id: user.uid
      };
    }
  }

  private async getOutfitHistory(user: User) {
    try {
      console.log('🔍 DEBUG: Fetching outfit history from /api/outfit-history/');
      const response = await this.makeAuthenticatedRequest('/api/outfit-history/', user);
      console.log('🔍 DEBUG: Outfit history response:', response);
      return response.outfitHistory || [];
    } catch (error) {
      console.error('Error fetching outfit history:', error);
      // Return empty array for production when backend is not ready
      return [];
    }
  }

  private async getTrendingStyles(user: User) {
    try {
      console.log('🔍 DEBUG: Fetching trending styles from /api/wardrobe/trending-styles');
      const response = await this.makeAuthenticatedRequest('/api/wardrobe/trending-styles', user);
      console.log('🔍 DEBUG: Trending styles response:', response);
      return response.data || {};
    } catch (error) {
      console.error('Error fetching trending styles:', error);
      // Return fallback data for production when backend is not ready
      return {
        trending_styles: [],
        total_trends: 0,
        most_popular: null
      };
    }
  }

  private calculateFavorites(wardrobeStats: any): number {
    // This would need to be implemented based on your data structure
    // For now, return a placeholder
    return 1;
  }

  private calculateStyleGoals(wardrobeStats: any, trendingStyles: any): number {
    // Calculate based on style coverage and preferences
    const categories = wardrobeStats.categories || {};
    const totalCategories = Object.keys(categories).length;
    const targetCategories = 5; // Default target
    
    return Math.min(totalCategories, targetCategories);
  }

  private calculateOutfitsThisWeek(outfitHistory: any[]): number {
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    
    return outfitHistory.filter(outfit => {
      const dateWorn = outfit.dateWorn;
      if (!dateWorn) return false;
      
      // Handle both timestamp and ISO string formats
      let outfitDate: Date;
      if (typeof dateWorn === 'number') {
        outfitDate = new Date(dateWorn);
      } else {
        outfitDate = new Date(dateWorn);
      }
      
      return outfitDate >= oneWeekAgo;
    }).length;
  }

  private calculateOverallProgress(wardrobeStats: any, trendingStyles: any): number {
    // Calculate overall progress based on multiple factors
    const factors = [
      this.calculateStyleGoals(wardrobeStats, trendingStyles) / 5 * 100, // Style goals (20%)
      Math.min((wardrobeStats.total_items || 0) / 100 * 100, 100), // Wardrobe size (30%)
      this.calculateColorVarietyScore(wardrobeStats), // Color variety (25%)
      this.calculateSeasonalBalanceScore(wardrobeStats) // Seasonal balance (25%)
    ];
    
    const weights = [0.2, 0.3, 0.25, 0.25];
    const weightedSum = factors.reduce((sum, factor, index) => sum + factor * weights[index], 0);
    
    return Math.round(weightedSum);
  }

  private calculateColorVarietyScore(wardrobeStats: any): number {
    const colors = wardrobeStats.colors || {};
    const uniqueColors = Object.keys(colors).length;
    return Math.min(uniqueColors / 8 * 100, 100); // Target: 8 colors
  }

  private calculateSeasonalBalanceScore(wardrobeStats: any): number {
    // Production backend doesn't have seasonal data yet, return default score
    return 25; // Default 25% score
  }

  private buildStyleCollections(wardrobeStats: any, trendingStyles: any): StyleCollection[] {
    const categories = wardrobeStats.categories || {};
    const collections: StyleCollection[] = [];
    
    // Basic Collection
    const basicCount = categories['basic'] || categories['tops'] || 0;
    collections.push({
      name: 'Basic Collection',
      progress: basicCount,
      target: 15,
      status: basicCount >= 15 ? 'Great job! Consider exploring new styles' : 'Building your basic collection'
    });
    
    // Bottoms Collection
    const bottomsCount = categories['bottoms'] || categories['pants'] || 0;
    collections.push({
      name: 'Bottoms Collection',
      progress: bottomsCount,
      target: 15,
      status: bottomsCount >= 15 ? 'Great job! Consider exploring new styles' : 'Building your bottoms collection'
    });
    
    return collections;
  }

  private buildStyleExpansions(wardrobeStats: any, trendingStyles: any): StyleExpansion[] {
    const categories = wardrobeStats.categories || {};
    const expansions: StyleExpansion[] = [];
    
    const potentialStyles = ['dresses', 'outerwear', 'shoes', 'accessories'];
    
    potentialStyles.forEach(style => {
      const count = categories[style] || 0;
      if (count > 0) {
        expansions.push({
          name: style,
          direction: count >= 5 ? 'Established' : 'New Direction'
        });
      }
    });
    
    return expansions;
  }

  private buildSeasonalBalance(wardrobeStats: any): SeasonalBalance {
    // Production backend doesn't have seasonal data yet, return default
    return {
      score: 25,
      status: "Basic Coverage",
      recommendations: ["Add seasonal items"],
      winterItems: 0,
      winterPercentage: 0,
      springItems: 0,
      summerItems: 0,
      fallItems: 0
    };
  }

  private buildColorVariety(wardrobeStats: any): ColorVariety {
    const colors = wardrobeStats.colors || {};
    const uniqueColors = Object.keys(colors);
    const target = 8;
    
    let status = 'Building color variety...';
    if (uniqueColors.length >= target) {
      status = 'Excellent color variety!';
    } else if (uniqueColors.length >= target * 0.7) {
      status = 'Good color variety, keep expanding!';
    }
    
    return {
      current: uniqueColors.length,
      target,
      status,
      colors: uniqueColors
    };
  }

  private buildWardrobeGaps(wardrobeStats: any): WardrobeGap[] {
    const gaps: WardrobeGap[] = [];
    
    // Analyze item types based on production backend data
    const categories = wardrobeStats.categories || {};
    const essentialTypes = ['tops', 'bottoms', 'outerwear', 'shoes'];
    
    essentialTypes.forEach(type => {
      const count = categories[type] || 0;
      if (count < 3) {
        gaps.push({
          category: 'Essential Items',
          description: `Need more ${type} (currently have ${count})`,
          priority: count === 0 ? 'high' : 'medium',
          suggestedItems: [`${type} options`]
        });
      }
    });
    
    return gaps;
  }

  private buildTopItems(wardrobeStats: any): TopItem[] {
    // Production backend doesn't have top items data yet, return empty array
    return [];
  }

  private buildRecentOutfits(outfitHistory: any[]): RecentOutfit[] {
    return outfitHistory.slice(0,5).map(outfit => ({
      id: outfit.id || outfit.outfitId || 'unknown',
      name: outfit.outfitName || 'Unnamed Outfit',
      occasion: outfit.occasion || 'casual',
      createdAt: outfit.createdAt || outfit.dateWorn || new Date().toISOString(),
      items: outfit.tags || []
    }));
  }
}

export const dashboardService = new DashboardService();
