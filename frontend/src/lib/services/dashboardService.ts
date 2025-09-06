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
  todaysOutfit: TodaysOutfit | null;
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

export interface TodaysOutfit {
  id: string;
  outfitId: string;
  outfitName: string;
  outfitImage: string;
  dateWorn: number;
  weather: {
    temperature: number;
    condition: string;
    humidity: number;
  };
  occasion: string;
  mood: string;
  notes: string;
  tags: string[];
  createdAt: number;
  updatedAt: number;
}

class DashboardService {
  private async makeAuthenticatedRequest(endpoint: string, user: User, options: RequestInit = {}): Promise<any> {
    if (!user) {
      throw new Error('Authentication required');
    }

    const token = await user.getIdToken();
    if (!token) {
      throw new Error('Failed to get authentication token');
    }

    // Use backend URL for API calls
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-backend-production.up.railway.app';
    const fullUrl = endpoint.startsWith('http') ? endpoint : `${backendUrl}${endpoint}`;

    const response = await fetch(fullUrl, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
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
        trendingStyles,
        todaysOutfit,
        topWornItems
      ] = await Promise.all([
        this.getWardrobeStats(user),
        this.getOutfitHistory(user),
        this.getTrendingStyles(user),
        this.getTodaysOutfit(user),
        this.getTopWornItems(user)
      ]);

      console.log('🔍 DEBUG: All API calls completed, processing data...');

      // Process and combine the data
      console.log('🔍 DEBUG: Processing wardrobeStats:', wardrobeStats);
      console.log('🔍 DEBUG: wardrobeStats.total_items:', wardrobeStats.total_items);
      console.log('🔍 DEBUG: wardrobeStats type:', typeof wardrobeStats);
      console.log('🔍 DEBUG: wardrobeStats keys:', Object.keys(wardrobeStats || {}));
      
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
        topItems: this.buildTopItems(topWornItems),
        recentOutfits: this.buildRecentOutfits(outfitHistory),
        todaysOutfit: todaysOutfit
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
      console.log('🔍 DEBUG: Fetching wardrobe stats from /api/wardrobe/');
      const response = await this.makeAuthenticatedRequest('/api/wardrobe/', user);
      console.log('🔍 DEBUG: Wardrobe stats response:', response);
      
      // Process the wardrobe items to create stats
      const items = response.items || response.wardrobe_items || response || [];
      const totalItems = Array.isArray(items) ? items.length : 0;
      
      // Calculate categories and colors from the actual items
      const categories: { [key: string]: number } = {};
      const colors: { [key: string]: number } = {};
      
      if (Array.isArray(items)) {
        items.forEach((item: any) => {
          // Count categories
          const category = item.type || item.category || 'unknown';
          categories[category] = (categories[category] || 0) + 1;
          
          // Count colors
          const color = item.color || 'unknown';
          colors[color] = (colors[color] || 0) + 1;
        });
      }
      
      return {
        total_items: totalItems,
        categories,
        colors,
        user_id: user.uid,
        items: items // Include items for favorites calculation
      };
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
      console.log('🔍 DEBUG: Fetching outfit history from /api/outfits');
      const response = await this.makeAuthenticatedRequest('/api/outfits', user);
      console.log('🔍 DEBUG: Outfit history response:', response);
      return response || [];
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
      return response.data || response || {};
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

  private async getTodaysOutfit(user: User) {
    try {
      console.log('🔍 DEBUG: Fetching today\'s outfit suggestion from /api/today-suggestion');
      const response = await this.makeAuthenticatedRequest('/api/today-suggestion', user);
      console.log('🔍 DEBUG: Today\'s outfit suggestion response:', response);
      
      // Handle new suggestion format
      if (response.suggestion) {
        const suggestion = response.suggestion;
        const outfitData = suggestion.outfitData || {};
        
        return {
          suggestionId: suggestion.id,
          outfitName: outfitData.name || 'Daily Suggestion',
          outfitImage: outfitData.imageUrl || '',
          occasion: outfitData.occasion || 'Daily Suggestion',
          mood: outfitData.mood || 'Confident',
          weather: outfitData.weather || {},
          items: outfitData.items || [],
          isWorn: response.isWorn || false,
          wornAt: response.wornAt,
          generatedAt: suggestion.generatedAt,
          isSuggestion: true // Flag to distinguish from worn outfits
        };
      }
      
      return null;
    } catch (error) {
      console.error('Error fetching today\'s outfit:', error);
      // Return null for production when backend is not ready
      return null;
    }
  }

  private async getTopWornItems(user: User) {
    try {
      console.log('🔍 DEBUG: Fetching top worn items from /api/wardrobe/top-worn-items');
      const response = await this.makeAuthenticatedRequest('/api/wardrobe/top-worn-items?limit=5', user);
      console.log('🔍 DEBUG: Top worn items response:', response);
      return response.data || response || {};
    } catch (error) {
      console.error('Error fetching top worn items:', error);
      // Return fallback data for production when backend is not ready
      return {
        top_worn_items: [],
        total_items: 0,
        total_wear_count: 0,
        avg_wear_count: 0
      };
    }
  }

  async markSuggestionAsWorn(user: User, suggestionId: string): Promise<boolean> {
    try {
      console.log('👕 DEBUG: Marking suggestion as worn:', suggestionId);
      const response = await this.makeAuthenticatedRequest('/api/outfit-history/today-suggestion/wear', user, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ suggestionId }),
      });
      
      console.log('✅ DEBUG: Suggestion marked as worn:', response);
      return response.success || false;
    } catch (error) {
      console.error('Error marking suggestion as worn:', error);
      return false;
    }
  }

  private calculateFavorites(wardrobeStats: any): number {
    // Calculate favorites from wardrobe stats
    if (wardrobeStats && wardrobeStats.favorites !== undefined) {
      return wardrobeStats.favorites;
    }
    
    // Calculate favorites from wardrobe items if available
    if (wardrobeStats && wardrobeStats.items) {
      const items = Array.isArray(wardrobeStats.items) ? wardrobeStats.items : [];
      return items.filter((item: any) => item.favorite === true).length;
    }
    
    // Fallback: if no favorites count in stats, return 0
    return 0;
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
    
    console.log('🔍 DEBUG: Calculating outfits this week from:', outfitHistory);
    
    return outfitHistory.filter(outfit => {
      // Use the createdAt field from the outfit data
      const createdAt = outfit.createdAt || outfit.generated_at;
      if (!createdAt) return false;
      
      console.log('🔍 DEBUG: Checking outfit date:', createdAt, 'for outfit:', outfit);
      
      // Handle both timestamp and ISO string formats
      let outfitDate: Date;
      if (typeof createdAt === 'number') {
        outfitDate = new Date(createdAt);
      } else {
        outfitDate = new Date(createdAt);
      }
      
      const isThisWeek = outfitDate >= oneWeekAgo;
      console.log('🔍 DEBUG: Outfit date:', outfitDate, 'is this week:', isThisWeek);
      
      return isThisWeek;
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
    
    // Basic Collection (shirts, sweaters, basic tops)
    const basicCount = (categories['shirt'] || 0) + (categories['dress_shirt'] || 0) + (categories['sweater'] || 0);
    collections.push({
      name: 'Basic Collection',
      progress: basicCount,
      target: 15,
      status: basicCount >= 15 ? 'Great job! Consider exploring new styles' : 'Building your basic collection'
    });
    
    // Bottoms Collection (pants, shorts, jeans)
    const bottomsCount = (categories['pants'] || 0) + (categories['shorts'] || 0) + (categories['jeans'] || 0);
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
    const categories = wardrobeStats.categories || {};
    
    // Map items to seasons based on type
    const winterItems = (categories['sweater'] || 0) + (categories['jacket'] || 0);
    const summerItems = (categories['shorts'] || 0);
    const springItems = (categories['shirt'] || 0) + (categories['dress_shirt'] || 0);
    const fallItems = (categories['pants'] || 0) + (categories['jeans'] || 0);
    
    const totalItems = winterItems + springItems + summerItems + fallItems;
    const winterPercentage = totalItems > 0 ? Math.round((winterItems / totalItems) * 100) : 0;
    
    // Calculate seasonal balance score based on distribution
    const seasons = [winterItems, springItems, summerItems, fallItems];
    const maxSeason = Math.max(...seasons);
    const minSeason = Math.min(...seasons);
    const avgSeason = totalItems / 4;
    
    // Score based on how balanced the seasons are (higher = more balanced)
    let score = 0;
    if (totalItems > 0) {
      // Base score from having items in each season
      const seasonsWithItems = seasons.filter(count => count > 0).length;
      const baseScore = (seasonsWithItems / 4) * 50;
      
      // Balance bonus (how evenly distributed)
      const balanceRatio = minSeason > 0 ? minSeason / maxSeason : 0;
      const balanceBonus = balanceRatio * 50;
      
      score = Math.round(baseScore + balanceBonus);
    }
    
    let status = "Basic Coverage";
    let recommendations = ["Add seasonal items"];
    
    // Determine status and recommendations based on actual data
    if (winterItems === 0) {
      status = "Needs Winter Items";
      recommendations = ["Consider adding items for: Winter (0 items, 0%)", "Focus on: Add winter clothing"];
    } else if (summerItems === 0) {
      status = "Needs Summer Items";
      recommendations = ["Consider adding items for: Summer (0 items, 0%)", "Focus on: Add summer clothing"];
    } else if (score >= 75) {
      status = "Excellent Coverage";
      recommendations = ["Great seasonal balance!"];
    } else if (score >= 50) {
      status = "Good Coverage";
      recommendations = ["Consider adding more seasonal variety"];
    } else {
      status = "Basic Coverage";
      recommendations = ["Add seasonal items for better coverage"];
    }
    
    return {
      score,
      status,
      recommendations,
      winterItems,
      winterPercentage,
      springItems,
      summerItems,
      fallItems
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
    
    // Map actual category names to expected types
    const categoryMapping = {
      'tops': ['shirt', 'dress_shirt', 'sweater'],
      'bottoms': ['pants', 'shorts', 'jeans'],
      'outerwear': ['jacket'],
      'shoes': ['shoes', 'sneakers', 'dress_shoes']
    };
    
    Object.entries(categoryMapping).forEach(([type, categoryNames]) => {
      const count = categoryNames.reduce((total, categoryName) => {
        return total + (categories[categoryName] || 0);
      }, 0);
      
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

  private buildTopItems(topWornItemsResponse: any): TopItem[] {
    try {
      const topWornItems = topWornItemsResponse.top_worn_items || [];
      console.log('🔍 DEBUG: Processing top worn items:', topWornItems);
      
      return topWornItems.map((item: any) => ({
        id: item.id,
        name: item.name || 'Unknown Item',
        type: item.type || 'clothing',
        imageUrl: item.image_url || '',
        wearCount: item.wear_count || 0,
        rating: item.is_favorite ? 5 : 3 // Use favorite status as rating proxy
      }));
    } catch (error) {
      console.error('Error building top items:', error);
      return [];
    }
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
