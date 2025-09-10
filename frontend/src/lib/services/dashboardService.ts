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
  private async makeAuthenticatedRequest(endpoint: string, user: User | null, options: RequestInit = {}): Promise<any> {
    // For testing purposes, use test token if user is not authenticated
    let token: string;
    if (!user || user.email === 'test@example.com' || !user.email) {
      token = 'test';
      console.log('🔍 DEBUG: Using test token for dashboard testing');
    } else {
      token = await user.getIdToken();
      if (!token) {
        throw new Error('Failed to get authentication token');
      }
    }
    
    console.log('🔍 DEBUG: Firebase token obtained:', token.substring(0, 20) + '...');
    console.log('🔍 DEBUG: Token length:', token.length);

    // Use Next.js API routes as proxy to avoid Railway HTTPS redirect issues
    console.log('🔍 DEBUG: Environment variables:', {
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
      NODE_ENV: process.env.NODE_ENV
    });
    
    // Use Next.js API route as proxy instead of calling backend directly
    const fullUrl = endpoint.startsWith('http') ? endpoint : `/api${endpoint}`;
    
    console.log('🔍 DEBUG: Making request to Next.js API route:', fullUrl);
    console.log('🔍 DEBUG: Making request to:', fullUrl);

    const response = await fetch(fullUrl, {
      method: 'GET', // Default to GET, can be overridden in options
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      console.error('🔍 DEBUG: API request failed:', response.status, response.statusText);
      const errorText = await response.text().catch(() => 'Unable to read error');
      console.error('🔍 DEBUG: Error details:', errorText);
      
      // Try to parse error as JSON for better error messages
      let errorData = {};
      try {
        errorData = await response.json();
      } catch (e) {
        // If JSON parsing fails, use the text error
      }
      
      throw new Error(`API request failed: ${response.status} ${JSON.stringify(errorData)}`);
    }

    return response.json();
  }

  async getDashboardData(user: User | null): Promise<DashboardData> {
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

      // Process and combine the data with proper backend response mapping
      console.log('🔍 DEBUG: Processing wardrobeStats:', wardrobeStats);
      console.log('🔍 DEBUG: Processing outfitHistory:', outfitHistory);
      console.log('🔍 DEBUG: Processing trendingStyles:', trendingStyles);
      console.log('🔍 DEBUG: Processing todaysOutfit:', todaysOutfit);
      console.log('🔍 DEBUG: Processing topWornItems:', topWornItems);
      
      // Extract data from backend responses with proper fallbacks
      // Now using /wardrobe/ endpoint which returns individual items
      const wardrobeItems = (wardrobeStats as any)?.items || [];
      const totalItems = (wardrobeStats as any)?.total_items || 0;
      
      const topWornItemsList = (topWornItems as any)?.data?.items || (topWornItems as any)?.items || topWornItems || [];
      const trendingStylesList = (trendingStyles as any)?.data?.styles || (trendingStyles as any)?.styles || trendingStyles || [];
      // Calculate outfits this week with fallback
      let outfitsThisWeek = this.calculateOutfitsThisWeek(outfitHistory);
      
      // If outfit history is empty, try to get outfits from the outfits endpoint as fallback
      if (outfitsThisWeek === 0) {
        console.log('🔍 DEBUG: Outfit history is empty, trying fallback method...');
        try {
          const outfitsResponse = await this.makeAuthenticatedRequest('/outfits/', user);
          const outfits = Array.isArray(outfitsResponse) ? outfitsResponse : [];
          outfitsThisWeek = this.calculateOutfitsThisWeekFromOutfits(outfits);
          console.log('🔍 DEBUG: Fallback calculation result:', outfitsThisWeek);
        } catch (error) {
          console.error('🔍 DEBUG: Fallback method also failed:', error);
        }
      }
      
      console.log('🔍 DEBUG: Extracted data:');
      console.log('🔍 DEBUG: - wardrobeItems:', wardrobeItems.length, 'items (empty - backend only returns stats)');
      console.log('🔍 DEBUG: - totalItems:', totalItems);
      console.log('🔍 DEBUG: - topWornItemsList:', topWornItemsList.length, 'items');
      console.log('🔍 DEBUG: - trendingStylesList:', trendingStylesList.length, 'styles');
      console.log('🔍 DEBUG: - outfitsThisWeek:', outfitsThisWeek);
      console.log('🔍 DEBUG: - wardrobeStats structure:', {
        total_items: (wardrobeStats as any)?.data?.total_items,
        item_types: Object.keys((wardrobeStats as any)?.data?.item_types || {}).length,
        colors: Object.keys((wardrobeStats as any)?.data?.colors || {}).length,
        styles: Object.keys((wardrobeStats as any)?.data?.styles || {}).length
      });
      
      const dashboardData: DashboardData = {
        totalItems: totalItems,
        favorites: this.calculateFavorites(wardrobeStats),
        styleGoalsCompleted: this.calculateStyleGoals(wardrobeStats, trendingStyles),
        totalStyleGoals: 5, // Default value, could be configurable
        outfitsThisWeek: outfitsThisWeek,
        overallProgress: this.calculateOverallProgress(wardrobeStats, trendingStyles),
        styleCollections: this.buildStyleCollections(wardrobeStats, trendingStyles),
        styleExpansions: this.buildStyleExpansions(wardrobeStats, trendingStyles),
        seasonalBalance: this.buildSeasonalBalance(wardrobeStats),
        colorVariety: this.buildColorVariety(wardrobeStats),
        wardrobeGaps: this.buildWardrobeGaps(wardrobeStats),
        topItems: this.buildTopItems(topWornItems),
        recentOutfits: this.buildRecentOutfits(outfitHistory),
        todaysOutfit: (todaysOutfit as any)?.todaysOutfit || todaysOutfit || null
      };

      console.log('🔍 DEBUG: Dashboard data processed:', dashboardData);
      console.log('🔍 DEBUG: Dashboard data totalItems:', dashboardData.totalItems);
      console.log('🔍 DEBUG: Dashboard data styleCollections length:', dashboardData.styleCollections.length);
      console.log('🔍 DEBUG: Dashboard data colorVariety:', dashboardData.colorVariety);
      console.log('🔍 DEBUG: Dashboard data seasonalBalance:', dashboardData.seasonalBalance);
      console.log('🔍 DEBUG: Dashboard data wardrobeGaps length:', dashboardData.wardrobeGaps.length);
      return dashboardData;

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }

  private async getWardrobeStats(user: User) {
    try {
      console.log('🔍 DEBUG: Fetching wardrobe items from /wardrobe/ (not wardrobe-stats)');
      const response = await this.makeAuthenticatedRequest('/wardrobe/', user, {
        method: 'GET'
      });
      console.log('🔍 DEBUG: Wardrobe stats response:', response);
      console.log('🔍 DEBUG: Wardrobe stats response type:', typeof response);
      console.log('🔍 DEBUG: Wardrobe stats response keys:', Object.keys(response || {}));
      console.log('🔍 DEBUG: response.items:', response.items);
      console.log('🔍 DEBUG: response.wardrobe_items:', response.wardrobe_items);
      
      // Process the wardrobe items to create stats with null checks
      // The /wardrobe/ endpoint returns: {"success": true, "items": [...], "count": N}
      const wardrobeItems = response?.items || [];
      const totalItems = response?.count || wardrobeItems.length;
      
      console.log('🔍 DEBUG: Extracted wardrobeItems:', wardrobeItems);
      console.log('🔍 DEBUG: WardrobeItems type:', typeof wardrobeItems);
      console.log('🔍 DEBUG: WardrobeItems isArray:', Array.isArray(wardrobeItems));
      console.log('🔍 DEBUG: Total items from response:', totalItems);
      
      // Calculate categories and colors from the actual items
      const categories: { [key: string]: number } = {};
      const colors: { [key: string]: number } = {};
      
      if (Array.isArray(wardrobeItems)) {
        wardrobeItems.forEach((item: any) => {
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
        items: wardrobeItems // Include items for favorites calculation
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
      console.log('🔍 DEBUG: Fetching outfit history stats via Next.js API route');
      
      // Use Next.js API route as proxy instead of calling backend directly
      const response = await this.makeAuthenticatedRequest('/outfit-history/stats?days=7', user);
      
      console.log('🔍 DEBUG: Outfit history stats response:', response);
      
      // Return the stats object with outfitsThisWeek count
      return response;
    } catch (error) {
      console.error('Error fetching outfit history:', error);
      // Return empty array for production when backend is not ready
      return [];
    }
  }

  private async getTrendingStyles(user: User) {
    try {
      console.log('🔍 DEBUG: Fetching trending styles from /wardrobe/trending-styles');
      const response = await this.makeAuthenticatedRequest('/wardrobe/trending-styles', user, {
        method: 'GET'
      });
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
      console.log('🔍 DEBUG: Fetching today\'s outfit suggestion from /outfit-history/today-suggestion');
      console.log('🔍 DEBUG: User ID:', user.uid);
      console.log('🔍 DEBUG: User email:', user.email);
      const response = await this.makeAuthenticatedRequest('/outfit-history/today-suggestion', user);
      console.log('🔍 DEBUG: Today\'s outfit suggestion response:', response);
      console.log('🔍 DEBUG: Today\'s outfit suggestion response details:', JSON.stringify(response, null, 2));
      
      // Handle new suggestion format
      if (response.suggestion) {
        const suggestion = response.suggestion;
        const outfitData = suggestion.outfitData || {};
        
        console.log('🔍 DEBUG: Today\'s outfit suggestion data:', JSON.stringify(suggestion, null, 2));
        console.log('🔍 DEBUG: Today\'s outfit items count:', Array.isArray(outfitData.items) ? outfitData.items.length : 'not an array');
        console.log('🔍 DEBUG: Today\'s outfit name:', outfitData.name);
        
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
      
      // Handle case where no suggestion is returned
      console.log('🔍 DEBUG: No suggestion found in response, response keys:', Object.keys(response));
      
      return null;
    } catch (error) {
      console.error('Error fetching today\'s outfit:', error);
      // Return null for production when backend is not ready
      return null;
    }
  }

  private async getTopWornItems(user: User) {
    try {
      console.log('🔍 DEBUG: Fetching top worn items from /wardrobe/top-worn-items');
      const response = await this.makeAuthenticatedRequest('/wardrobe/top-worn-items?limit=5', user, {
        method: 'GET'
      });
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
      const response = await this.makeAuthenticatedRequest('/outfit-history/today-suggestion/wear', user, {
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

  private calculateOutfitsThisWeek(outfitHistoryStats: any): number {
    // Use server-side calculated stats instead of client-side filtering
    console.log('🔍 DEBUG: Using server-side calculated outfits this week from stats API');
    console.log('🔍 DEBUG: Outfit history stats:', outfitHistoryStats);
    
    // Extract outfitsThisWeek from stats response
    const outfitsThisWeek = outfitHistoryStats?.stats?.outfitsThisWeek || 0;
    
    console.log('🔍 DEBUG: Server calculated outfits this week:', outfitsThisWeek);
    return outfitsThisWeek;
  }

  // Fallback method to calculate outfits this week from individual outfit wear counts
  private calculateOutfitsThisWeekFromOutfits(outfits: any[]): number {
    const now = new Date();
    const oneWeekAgo = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
    
    console.log('🔍 DEBUG: Fallback: Calculating outfits this week from individual outfit wear counts');
    console.log('🔍 DEBUG: Total outfits:', outfits.length);
    
    let thisWeekCount = 0;
    
    outfits.forEach(outfit => {
      if (outfit.lastWorn) {
        let lastWornDate: Date;
        
        // Handle different date formats
        if (typeof outfit.lastWorn === 'number') {
          lastWornDate = new Date(outfit.lastWorn);
        } else if (typeof outfit.lastWorn === 'string') {
          lastWornDate = new Date(outfit.lastWorn);
        } else if (outfit.lastWorn.toDate) {
          // Firestore timestamp
          lastWornDate = outfit.lastWorn.toDate();
        } else {
          return;
        }
        
        if (lastWornDate >= oneWeekAgo) {
          thisWeekCount += outfit.wearCount || 0;
          console.log('🔍 DEBUG: Outfit', outfit.name, 'worn', outfit.wearCount, 'times this week');
        }
      }
    });
    
    console.log('🔍 DEBUG: Fallback: Found', thisWeekCount, 'total wears this week');
    return thisWeekCount;
  }

  private calculateOverallProgress(wardrobeStats: any, trendingStyles: any): number {
    // Calculate overall progress based on style collections completion
    const collections = this.buildStyleCollections(wardrobeStats, trendingStyles);
    
    // Calculate average completion of style collections
    const totalProgress = collections.reduce((sum, collection) => {
      const completion = Math.min(collection.progress / collection.target * 100, 100);
      return sum + completion;
    }, 0);
    
    const averageProgress = totalProgress / collections.length;
    
    console.log('🔍 DEBUG: Overall Progress Calculation (Style Collections Based):');
    collections.forEach(collection => {
      const completion = Math.min(collection.progress / collection.target * 100, 100);
      console.log(`  - ${collection.name}: ${collection.progress}/${collection.target} (${Math.round(completion)}%)`);
    });
    console.log('  - Average Progress:', Math.round(averageProgress), '%');
    
    return Math.round(averageProgress);
  }

  private calculateColorVarietyScore(wardrobeStats: any): number {
    const colors = wardrobeStats.colors || {};
    const uniqueColors = Object.keys(colors).length;
    const score = Math.min(uniqueColors / 8 * 100, 100); // Target: 8 colors
    console.log('🔍 DEBUG: Color Variety - Unique colors:', uniqueColors, 'Score:', score, '%');
    return score;
  }

  private calculateSeasonalBalanceScore(wardrobeStats: any): number {
    // Production backend doesn't have seasonal data yet, return default score
    return 25; // Default 25% score
  }

  private buildStyleCollections(wardrobeStats: any, trendingStyles: any): StyleCollection[] {
    console.log('🔍 DEBUG: buildStyleCollections - wardrobeStats:', wardrobeStats);
    console.log('🔍 DEBUG: buildStyleCollections - wardrobeStats.items:', wardrobeStats.items);
    
    // Use individual items from /wardrobe/ endpoint
    const items = wardrobeStats?.items || [];
    const categories: { [key: string]: number } = {};
    
    console.log('🔍 DEBUG: Using individual items array with length:', items.length);
    if (Array.isArray(items) && items.length > 0) {
      items.forEach((item: any, index: number) => {
        console.log(`🔍 DEBUG: Processing item ${index}:`, item);
        const type = item.type || 'unknown';
        categories[type] = (categories[type] || 0) + 1;
      });
    } else {
      console.log('🔍 DEBUG: No items available, using empty categories');
    }
    
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
    const items = wardrobeStats.items || [];
    
    // Count items by type from the actual items array
    const categories: { [key: string]: number } = {};
    items.forEach((item: any) => {
      const type = item.type || 'unknown';
      categories[type] = (categories[type] || 0) + 1;
    });
    
    const expansions: StyleExpansion[] = [];
    
    // Map actual wardrobe categories to style expansion areas
    const styleMappings = [
      { category: 'shoes', name: 'Footwear', threshold: 5 },
      { category: 'accessory', name: 'Accessories', threshold: 5 },
      { category: 'jacket', name: 'Outerwear', threshold: 3 },
      { category: 'sweater', name: 'Layering', threshold: 3 },
      { category: 'shorts', name: 'Casual Wear', threshold: 3 },
      { category: 'pants', name: 'Bottoms', threshold: 5 }
    ];
    
    styleMappings.forEach(mapping => {
      const count = categories[mapping.category] || 0;
      if (count > 0) {
        expansions.push({
          name: mapping.name,
          direction: count >= mapping.threshold ? 'Established' : 'New Direction'
        });
      }
    });
    
    console.log('🔍 DEBUG: Style Expansions:', expansions);
    return expansions;
  }

  private buildSeasonalBalance(wardrobeStats: any): SeasonalBalance {
    // Use individual items from /wardrobe/ endpoint
    const items = wardrobeStats?.items || [];
    const categories: { [key: string]: number } = {};
    
    if (Array.isArray(items) && items.length > 0) {
      items.forEach((item: any) => {
        const type = item.type || 'unknown';
        categories[type] = (categories[type] || 0) + 1;
      });
    }
    
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
    
    // Use individual items from /wardrobe/ endpoint
    const items = wardrobeStats?.items || [];
    const categories: { [key: string]: number } = {};
    
    if (Array.isArray(items) && items.length > 0) {
      items.forEach((item: any) => {
        const type = item.type || 'unknown';
        categories[type] = (categories[type] || 0) + 1;
      });
    }
    
    const totalItems = wardrobeStats?.total_items || items.length;
    
    console.log('🔍 DEBUG: Building wardrobe gaps from data:', totalItems, 'total items');
    console.log('🔍 DEBUG: Categories counted:', categories);
    
    // Essential wardrobe categories with minimum requirements
    // Updated to match actual item types in the wardrobe
    const essentialCategories = {
      'Tops': {
        items: ['shirt', 'sweater'], // Based on actual wardrobe: 57 shirts, 9 sweaters
        minRequired: 20, // Adjusted based on actual counts
        priority: 'high',
        description: 'Essential tops for layering and variety'
      },
      'Bottoms': {
        items: ['pants', 'shorts'], // Based on actual wardrobe: 10 pants, 6 shorts
        minRequired: 8, // Adjusted based on actual counts
        priority: 'high',
        description: 'Versatile bottoms for different occasions'
      },
      'Shoes': {
        items: ['shoes'], // Based on actual wardrobe: 22 shoes
        minRequired: 5, // Adjusted based on actual counts
        priority: 'high',
        description: 'Footwear for different activities and seasons'
      },
      'Outerwear': {
        items: ['jacket', 'sweater'], // Based on actual wardrobe: 12 jackets, 9 sweaters
        minRequired: 5, // Adjusted based on actual counts
        priority: 'medium',
        description: 'Layering pieces for weather protection'
      },
      'Accessories': {
        items: ['accessory'], // Based on actual wardrobe: 13 accessories
        minRequired: 3, // Adjusted based on actual counts
        priority: 'low',
        description: 'Finishing touches to complete outfits'
      }
    };
    
    // Check each essential category
    Object.entries(essentialCategories).forEach(([categoryName, config]) => {
      const count = config.items.reduce((total, itemType) => {
        return total + (categories[itemType] || 0);
      }, 0);
      
      if (count < config.minRequired) {
        const percentage = totalItems > 0 ? Math.round((count / totalItems) * 100) : 0;
        gaps.push({
          category: categoryName,
          description: `${config.description} (${count}/${config.minRequired} items, ${percentage}% of wardrobe)`,
          priority: config.priority as 'high' | 'medium' | 'low',
          suggestedItems: config.items.slice(0, 3) // Suggest top 3 item types
        });
      }
    });
    
    // Check for seasonal gaps
    const seasonalGaps = this.analyzeSeasonalGaps(categories, totalItems);
    gaps.push(...seasonalGaps);
    
    // Check for style diversity gaps - analyze by style attributes
    const styleGaps = this.analyzeStyleGapsFromItems(items, totalItems);
    gaps.push(...styleGaps);
    
    // Check for color variety gaps
    const colorGaps = this.analyzeColorGaps(wardrobeStats);
    gaps.push(...colorGaps);
    
    console.log('🔍 DEBUG: Wardrobe gaps identified:', gaps);
    return gaps;
  }
  
  private analyzeSeasonalGaps(categories: any, totalItems: number): WardrobeGap[] {
    const gaps: WardrobeGap[] = [];
    
    // Winter items (warm clothing) - using actual item types
    const winterItems = (categories['sweater'] || 0) + (categories['jacket'] || 0);
    if (winterItems < 5) { // Adjusted threshold based on actual counts (9 sweaters + 12 jackets = 21)
      gaps.push({
        category: 'Seasonal Coverage',
        description: `Limited winter clothing (${winterItems} items) - consider sweaters or jackets`,
        priority: 'medium',
        suggestedItems: ['sweater', 'jacket']
      });
    }
    
    // Summer items (light clothing) - using actual item types
    const summerItems = (categories['shorts'] || 0) + (categories['shirt'] || 0); // shirts can be summer wear
    if (summerItems < 20) { // Adjusted threshold based on actual counts (6 shorts + 57 shirts = 63)
      gaps.push({
        category: 'Seasonal Coverage',
        description: `Limited summer clothing (${summerItems} items) - consider shorts or lightweight shirts`,
        priority: 'medium',
        suggestedItems: ['shorts', 'shirt']
      });
    }
    
    return gaps;
  }
  
  private analyzeStyleGaps(categories: any, totalItems: number): WardrobeGap[] {
    const gaps: WardrobeGap[] = [];
    
    // We need to analyze items by style, not just type
    // This will be handled in the main buildWardrobeGaps method
    // where we have access to the full items array
    
    return gaps;
  }

  private analyzeStyleGapsFromItems(items: any[], totalItems: number): WardrobeGap[] {
    const gaps: WardrobeGap[] = [];
    
    // Define formal style keywords
    const formalStyles = ['formal', 'business', 'professional', 'dress', 'suit', 'blazer', 'dress_shirt'];
    const casualStyles = ['casual', 'streetwear', 'urban', 'sporty', 'relaxed', 'comfortable'];
    
    // Count formal and casual items based on style attributes
    let formalItems = 0;
    let casualItems = 0;
    
    items.forEach(item => {
      const styles = item.style || [];
      const styleString = styles.join(' ').toLowerCase();
      const itemName = (item.name || '').toLowerCase();
      
      // Check if item has formal characteristics
      const hasFormalStyle = formalStyles.some(style => styleString.includes(style));
      const hasFormalName = formalStyles.some(style => itemName.includes(style));
      const hasCasualStyle = casualStyles.some(style => styleString.includes(style));
      
      // Count as formal if it has formal styles OR formal name keywords
      if (hasFormalStyle || hasFormalName) {
        formalItems++;
      }
      
      // Count as casual if it has casual styles or is a casual type
      if (hasCasualStyle || ['shirt', 'pants', 'shorts', 'shoes', 'sweater', 'accessory'].includes(item.type)) {
        casualItems++;
      }
    });
    
    console.log('🔍 DEBUG: Style analysis - Formal items:', formalItems, 'Casual items:', casualItems);
    console.log('🔍 DEBUG: Total items analyzed:', items.length);
    console.log('🔍 DEBUG: Formal styles keywords:', formalStyles);
    
    // Debug: Show some sample items with formal styles
    const formalSample = items.filter(item => {
      const styles = item.style || [];
      const styleString = styles.join(' ').toLowerCase();
      const itemName = (item.name || '').toLowerCase();
      return formalStyles.some(style => styleString.includes(style)) || formalStyles.some(style => itemName.includes(style));
    }).slice(0, 3);
    console.log('🔍 DEBUG: Sample formal items found:', formalSample.map(item => ({name: item.name, style: item.style})));
    
    // Check for formal wear gaps
    if (formalItems < 3) {
      gaps.push({
        category: 'Style Variety',
        description: `Limited formal wear (${formalItems} items) - consider blazers, dress pants, or dress shirts`,
        priority: 'low',
        suggestedItems: ['blazer', 'dress_pants', 'dress_shirt']
      });
    }
    
    // Check for casual wear gaps (adjusted threshold)
    if (casualItems < 20) {
      gaps.push({
        category: 'Style Variety',
        description: `Limited casual wear (${casualItems} items) - consider more casual shirts, pants, or shoes`,
        priority: 'medium',
        suggestedItems: ['shirt', 'pants', 'shoes']
      });
    }
    
    return gaps;
  }
  
  private analyzeColorGaps(wardrobeStats: any): WardrobeGap[] {
    const gaps: WardrobeGap[] = [];
    const colors = wardrobeStats.colors || {};
    const uniqueColors = Object.keys(colors);
    
    if (uniqueColors.length < 5) {
      gaps.push({
        category: 'Color Variety',
        description: `Limited color variety (${uniqueColors.length} colors) - consider adding more colorful pieces`,
        priority: 'low',
        suggestedItems: ['Colorful tops', 'Patterned items', 'Accent pieces']
      });
    }
    
    // Check for neutral base colors
    const neutralColors = ['black', 'white', 'gray', 'navy', 'brown', 'beige'];
    const hasNeutrals = neutralColors.some(color => colors[color] > 0);
    if (!hasNeutrals) {
      gaps.push({
        category: 'Color Variety',
        description: 'Missing neutral base colors - consider black, white, gray, or navy pieces',
        priority: 'medium',
        suggestedItems: ['Black basics', 'White shirts', 'Gray sweaters', 'Navy pants']
      });
    }
    
    return gaps;
  }

  private buildTopItems(topWornItemsResponse: any): TopItem[] {
    try {
      // Handle different response structures
      const topWornItems = topWornItemsResponse.data?.top_worn_items || 
                          topWornItemsResponse.top_worn_items || 
                          topWornItemsResponse || [];
      console.log('🔍 DEBUG: Processing top worn items:', topWornItems);
      console.log('🔍 DEBUG: Top worn items response structure:', topWornItemsResponse);
      
      if (!Array.isArray(topWornItems)) {
        console.log('🔍 DEBUG: Top worn items is not an array:', topWornItems);
        return [];
      }
      
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

  private buildRecentOutfits(outfitHistory: any): RecentOutfit[] {
    // Handle both array and object response formats
    const historyArray = Array.isArray(outfitHistory) 
      ? outfitHistory 
      : outfitHistory?.outfitHistory || [];
    
    return historyArray.slice(0,5).map(outfit => ({
      id: outfit.id || outfit.outfitId || 'unknown',
      name: outfit.outfitName || 'Unnamed Outfit',
      occasion: outfit.occasion || 'casual',
      createdAt: outfit.createdAt || outfit.dateWorn || new Date().toISOString(),
      items: outfit.tags || []
    }));
  }

  // Test function to directly hit production backend
  async testWardrobeStatsDirect(user: User) {
    try {
      console.log('🧪 TEST: Testing wardrobe-stats endpoint directly against production backend');
      
      const token = await user.getIdToken();
      if (!token) {
        throw new Error('Failed to get authentication token');
      }
      
      console.log('🧪 TEST: Token obtained, length:', token.length);
      
      // Use production URL as fallback since environment variables aren't loading
      const API_BASE_URL = 'https://closetgptrenew-backend-production.up.railway.app/api';
      
      const testUrl = `${API_BASE_URL}/wardrobe/wardrobe-stats`;
      console.log('🧪 TEST: Testing URL:', testUrl);
      
      const response = await fetch(testUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      console.log('🧪 TEST: Response status:', response.status);
      console.log('🧪 TEST: Response ok:', response.ok);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('🧪 TEST: Error response:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('✅ TEST: Wardrobe stats response:', data);
      return data;
      
    } catch (err) {
      console.error('❌ TEST: Error fetching wardrobe stats:', err);
      throw err;
    }
  }
}

export const dashboardService = new DashboardService();
