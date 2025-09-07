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
    const items = wardrobeStats.items || [];
    
    // Count items by type from the actual items array
    const categories: { [key: string]: number } = {};
    items.forEach((item: any) => {
      const type = item.type || 'unknown';
      categories[type] = (categories[type] || 0) + 1;
    });
    
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
    const items = wardrobeStats.items || [];
    
    // Count items by type from the actual items array
    const categories: { [key: string]: number } = {};
    items.forEach((item: any) => {
      const type = item.type || 'unknown';
      categories[type] = (categories[type] || 0) + 1;
    });
    
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
    const items = wardrobeStats.items || [];
    const totalItems = items.length;
    
    // Count items by type from the actual items array
    const categories: { [key: string]: number } = {};
    items.forEach((item: any) => {
      const type = item.type || 'unknown';
      categories[type] = (categories[type] || 0) + 1;
    });
    
    console.log('🔍 DEBUG: Building wardrobe gaps from items:', items.length, 'items');
    console.log('🔍 DEBUG: Categories counted from items:', categories);
    
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
