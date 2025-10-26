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
  shoppingRecommendations?: {
    success: boolean;
    recommendations: any[];
    store_recommendations: any[];
    shopping_strategy: any;
    total_estimated_cost: number;
    budget_range: string;
  };
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
  currentCount: number;
  recommendedCount: number;
  gapSize: number;
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
    console.log('🔍 DEBUG: makeAuthenticatedRequest called with user:', user ? 'authenticated' : 'null');
    console.log('🔍 DEBUG: User email:', user?.email);
    console.log('🔍 DEBUG: User UID:', user?.uid);
    
    // Get authentication token
    let token: string;
    if (!user) {
      throw new Error('User not authenticated. Please log in.');
    }
    
    token = await user.getIdToken();
    if (!token) {
      throw new Error('Failed to get authentication token');
    }
    console.log('🔍 DEBUG: Got real token:', token.substring(0, 20) + '...');
    
    // Use Next.js API route as proxy instead of calling backend directly
    const fullUrl = endpoint.startsWith('http') ? endpoint : `/api${endpoint}`;
    console.log('🔍 DEBUG: Making request to:', fullUrl);
    console.log('🔍 DEBUG: Authorization header:', `Bearer ${token.substring(0, 20)}...`);

    // Keep headers simple to avoid CORS issues
    const headers: Record<string, string> = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(fullUrl, {
      method: 'GET', // Default to GET, can be overridden in options
      headers,
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

  async getDashboardData(user: User | null, forceFresh: boolean = false): Promise<DashboardData> {
    try {
      console.log('🔍 DEBUG: Fetching dashboard data...');
      
      // Fetch data with individual timeouts to prevent one slow API from blocking everything
      const fetchWithTimeout = async (promise: Promise<any>, timeoutMs: number, fallback: any, endpointName: string = 'unknown') => {
        try {
          return await Promise.race([
            promise,
            new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout after ${timeoutMs}ms`)), timeoutMs))
          ]);
        } catch (error) {
          console.error(`❌ DEBUG: ${endpointName} failed:`, error);
          if (error instanceof Error && error.message.includes('Timeout')) {
            console.error(`⏱️ DEBUG: ${endpointName} timed out after ${timeoutMs}ms - using fallback data`);
            console.error(`⏱️ DEBUG: This could mean the endpoint is slow or the backend is overloaded`);
          }
          console.warn(`⚠️ DEBUG: Using fallback data for ${endpointName}:`, fallback);
          return fallback;
        }
      };

      // Fetch user profile with persona data
      const userProfile = await fetchWithTimeout(
        this.getUserProfile(user),
        5000,
        { stylePersona: null },
        'UserProfile'
      );

      // Fetch wardrobe data first, then use it for top worn items calculation
      const wardrobeStats = await fetchWithTimeout(
        this.getWardrobeStats(user), 
        20000, 
        { items: [], total_items: 0 }, 
        'WardrobeStats'
      );
      
      // Extract wardrobe items for top worn calculation
      const wardrobeItems = (wardrobeStats as any)?.items || [];
      console.log('🔍 DEBUG: Using', wardrobeItems.length, 'wardrobe items for top worn calculation');
      
      // Fetch remaining data in parallel, passing wardrobe items to top worn calculator
      const [
        simpleAnalytics,
        trendingStyles,
        todaysOutfit,
        topWornItems
      ] = await Promise.all([
        fetchWithTimeout(this.getSimpleAnalytics(user, forceFresh), 15000, { success: true, outfits_worn_this_week: 0 }, 'SimpleAnalytics'),
        fetchWithTimeout(this.getTrendingStyles(user), 8000, { success: true, data: { styles: [] } }, 'TrendingStyles'),
        fetchWithTimeout(this.getTodaysOutfit(user), 8000, { success: true, suggestion: null }, 'TodaysOutfit'),
        fetchWithTimeout(this.getTopWornItems(user, wardrobeItems), 8000, { success: true, data: { items: [] } }, 'TopWornItems')
      ]);

      console.log('🔍 DEBUG: All API calls completed, processing data...');

      // Process and combine the data with proper backend response mapping
      console.log('🔍 DEBUG: Processing wardrobeStats:', wardrobeStats);
      console.log('🔍 DEBUG: Processing simpleAnalytics:', simpleAnalytics);
      console.log('🔍 DEBUG: Processing trendingStyles:', trendingStyles);
      console.log('🔍 DEBUG: Processing todaysOutfit:', todaysOutfit);
      console.log('🔍 DEBUG: Processing topWornItems:', topWornItems);
      
      // Extract data from backend responses with proper fallbacks
      // Now using /wardrobe endpoint which returns individual items
      const totalItems = (wardrobeStats as any)?.total_items || wardrobeItems.length || 0;
      
      const topWornItemsList = (topWornItems as any)?.data?.items || (topWornItems as any)?.items || topWornItems || [];
      const trendingStylesList = (trendingStyles as any)?.data?.styles || (trendingStyles as any)?.styles || trendingStyles || [];
      // Get outfits worn this week from simple analytics - no complex fallbacks needed
      const outfitsThisWeek = (simpleAnalytics as any)?.outfits_worn_this_week || 0;
      console.log('🔍 DEBUG: Simple analytics returned:', outfitsThisWeek, 'outfits worn this week');
      
      // Force browser cache refresh - removed all outfitHistory references
      
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
      
      // Build style collections first so we can calculate goals from them
      const styleCollections = this.buildStyleCollections(wardrobeStats, trendingStyles, userProfile);
      const styleGoalsData = this.calculateStyleGoals(styleCollections);
      
      const dashboardData: DashboardData = {
        totalItems: totalItems,
        favorites: this.calculateFavorites(wardrobeStats),
        styleGoalsCompleted: styleGoalsData.completed,
        totalStyleGoals: styleGoalsData.total,
        outfitsThisWeek: outfitsThisWeek,
        overallProgress: this.calculateOverallProgress(wardrobeStats, trendingStyles, userProfile),
        styleCollections: styleCollections,
        styleExpansions: this.buildStyleExpansions(wardrobeStats, trendingStyles),
        seasonalBalance: this.buildSeasonalBalance(wardrobeStats),
        colorVariety: this.buildColorVariety(wardrobeStats),
        wardrobeGaps: await this.getWardrobeGapsFromBackend(user),
        topItems: this.buildTopItems(topWornItems),
        recentOutfits: this.buildRecentOutfits(),
        todaysOutfit: (todaysOutfit as any)?.todaysOutfit || todaysOutfit || null,
        shoppingRecommendations: null // Will be populated by the enhanced component
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

  private async getUserProfile(user: User | null) {
    try {
      if (!user) return { stylePersona: null };
      
      const token = await user.getIdToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app'}/api/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const profileData = await response.json();
        console.log('🎭 [Dashboard] Fetched user profile with persona:', profileData?.stylePersona?.name || 'No persona');
        return profileData;
      }
      
      return { stylePersona: null };
    } catch (error) {
      console.error('Error fetching user profile:', error);
      return { stylePersona: null };
    }
  }

  private async getWardrobeStats(user: User) {
    try {
      console.log('🔍 DEBUG: Fetching wardrobe items from /wardrobe (not wardrobe-stats)');
      console.log('🔍 DEBUG: User ID:', user.uid);
      console.log('🔍 DEBUG: User email:', user.email);
      
      // Use simple GET request without custom headers (to avoid CORS issues)
      const response = await this.makeAuthenticatedRequest('/wardrobe', user, {
        method: 'GET'
      });
      console.log('🔍 DEBUG: Wardrobe stats response:', response);
      console.log('🔍 DEBUG: Wardrobe stats response type:', typeof response);
      console.log('🔍 DEBUG: Wardrobe stats response keys:', Object.keys(response || {}));
      console.log('🔍 DEBUG: response.success:', response?.success);
      console.log('🔍 DEBUG: response.error:', response?.error);
      console.log('🔍 DEBUG: response.count:', response?.count);
      console.log('🔍 DEBUG: response.items:', response.items);
      console.log('🔍 DEBUG: response.items length:', response?.items?.length);
      console.log('🔍 DEBUG: response.user_id:', response?.user_id);
      console.log('🔍 DEBUG: response.wardrobe_items:', response.wardrobe_items);
      
      // Check if the response indicates an error
      if (response?.error || response?.success === false) {
        console.error('❌ DEBUG: Backend returned error:', response.error);
        console.error('❌ DEBUG: This means the backend could not fetch your wardrobe data');
        console.error('❌ DEBUG: Possible reasons: authentication issue, backend down, or database query failed');
      }
      
      // Process the wardrobe items to create stats with null checks
      // The /wardrobe endpoint returns: {"success": true, "items": [...], "count": N}
      const wardrobeItems = response?.items || [];
      const totalItems = response?.count || wardrobeItems.length;
      
      console.log('🔍 DEBUG: Extracted wardrobeItems:', wardrobeItems);
      console.log('🔍 DEBUG: WardrobeItems type:', typeof wardrobeItems);
      console.log('🔍 DEBUG: WardrobeItems isArray:', Array.isArray(wardrobeItems));
      console.log('🔍 DEBUG: Total items from response:', totalItems);
      
      // Alert if we got 0 items - this is unusual
      if (totalItems === 0) {
        console.warn('⚠️ DEBUG: Got 0 wardrobe items from backend!');
        console.warn('⚠️ DEBUG: This could mean:');
        console.warn('⚠️ DEBUG: 1. Your wardrobe is empty (unlikely if you just made changes)');
        console.warn('⚠️ DEBUG: 2. The backend query is not finding your items (field name mismatch?)');
        console.warn('⚠️ DEBUG: 3. Authentication token is incorrect');
        console.warn('⚠️ DEBUG: 4. Backend is returning fallback/mock data');
      }
      
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

  // Removed getOutfitHistory - replaced with getSimpleAnalytics

  private async getSimpleAnalytics(user: User, forceFresh: boolean = false) {
    try {
      console.log('🔍 DEBUG: [FRONTEND FIX] Counting outfits directly from Firestore - bypassing broken backend');
      console.log('🔍 DEBUG: forceFresh:', forceFresh);
      console.log('🔍 DEBUG: User ID:', user.uid);
      
      // Import Firestore with getDocsFromServer for fresh data
      const { db } = await import('@/lib/firebase/config');
      const { collection, query, where, getDocs, getDocsFromServer } = await import('firebase/firestore');
      
      console.log('🔍 DEBUG: Firestore imports loaded successfully');
      console.log('🔍 DEBUG: getDocsFromServer available:', typeof getDocsFromServer);
      
      // Calculate week start (Sunday 00:00:00 in user's local timezone)
      const now = new Date();
      const dayOfWeek = now.getDay(); // 0 = Sunday, 6 = Saturday
      const daysToSubtract = dayOfWeek; // If Sunday (0), subtract 0 days
      const weekStart = new Date(now);
      weekStart.setDate(now.getDate() - daysToSubtract);
      weekStart.setHours(0, 0, 0, 0);
      
      // For debugging: show both local time and timestamp
      console.log('📅 Current date:', now.toLocaleString());
      console.log('📅 Day of week:', dayOfWeek, '(0=Sunday, 6=Saturday)');
      console.log('📅 Week starts:', weekStart.toLocaleString());
      console.log('📅 Week start timestamp:', weekStart.getTime());
      console.log('📅 Week start ISO:', weekStart.toISOString());
      
      // Query outfit_history collection for this user, this week
      const historyRef = collection(db, 'outfit_history');
      const historyQuery = query(
        historyRef,
        where('user_id', '==', user.uid)
      );
      
      // Use getDocsFromServer when forceFresh is true to bypass cache
      const snapshot = forceFresh 
        ? await getDocsFromServer(historyQuery)
        : await getDocs(historyQuery);
      
      console.log(`📊 Query returned ${snapshot.size} entries (source: ${forceFresh ? 'server' : 'cache-or-server'})`);
      
      // Count entries worn this week
      let wornThisWeek = 0;
      const allEntries: any[] = [];
      
      snapshot.forEach((doc) => {
        const data = doc.data();
        const dateWorn = data.date_worn;
        
        // Enhanced logging for each entry
        console.log(`\n📅 Processing entry ${doc.id}:`);
        console.log(`  Outfit: ${data.outfit_name}`);
        console.log(`  date_worn raw:`, dateWorn);
        console.log(`  date_worn type: ${typeof dateWorn}`);
        
        // Handle multiple date formats
        let wornDate: Date | null = null;
        if (typeof dateWorn === 'number') {
          // Unix timestamp in milliseconds
          wornDate = new Date(dateWorn);
          console.log(`  ➜ Parsed as number timestamp`);
          console.log(`     Local time: ${wornDate.toLocaleString()}`);
          console.log(`     ISO: ${wornDate.toISOString()}`);
          console.log(`     Timestamp: ${wornDate.getTime()}`);
        } else if (dateWorn && dateWorn.toDate && typeof dateWorn.toDate === 'function') {
          // Firestore Timestamp
          wornDate = dateWorn.toDate();
          console.log(`  ➜ Parsed as Firestore Timestamp: ${wornDate.toISOString()}`);
        } else if (typeof dateWorn === 'string') {
          // ISO string
          wornDate = new Date(dateWorn);
          console.log(`  ➜ Parsed as string: ${wornDate.toISOString()}`);
        } else {
          console.log(`  ⚠️ Unknown date format, cannot parse`);
        }
        
        // Validate the parsed date
        const isValidDate = wornDate && !isNaN(wornDate.getTime());
        const isThisWeek = isValidDate && wornDate >= weekStart;
        
        console.log(`  ➜ Date valid: ${isValidDate}`);
        if (isValidDate) {
          console.log(`  ➜ Comparison: ${wornDate.getTime()} >= ${weekStart.getTime()}`);
          console.log(`  ➜ Result: ${wornDate.getTime() >= weekStart.getTime()}`);
          console.log(`  ➜ This week: ${isThisWeek}${isThisWeek ? ' ✅' : ' ❌'}`);
        }
        
        const entry = {
          id: doc.id,
          outfit_name: data.outfit_name,
          date_worn: dateWorn,
          parsed_date: isValidDate ? wornDate.toISOString() : null,
          is_this_week: isThisWeek
        };
        allEntries.push(entry);
        
        if (isThisWeek) {
          wornThisWeek++;
        }
      });
      
      // Log all entries for debugging
      console.log('📊 DEBUG: All outfit_history entries:', allEntries);
      
      console.log(`✅ DEBUG: Counted ${wornThisWeek} outfits worn this week (frontend calculation, ${forceFresh ? 'FRESH from server' : 'cache-or-server'})`);
      console.log(`📊 DEBUG: Week starts at ${weekStart.toISOString()}, current time: ${new Date().toISOString()}`);
      console.log(`📊 DEBUG: Total entries in outfit_history for user: ${snapshot.size}`);
      console.log(`📊 DEBUG: Entries this week: ${wornThisWeek}`);
      
      return {
        success: true,
        outfits_worn_this_week: wornThisWeek,
        user_id: user.uid,
        week_start: weekStart.toISOString(),
        calculated_at: new Date().toISOString(),
        source: forceFresh ? 'frontend_firestore_server_fresh' : 'frontend_firestore_direct',
        version: '2025-10-26-cache-fix-v2'
      };
    } catch (error) {
      console.error('Error fetching worn outfits analytics:', error);
      // Return fallback data that matches the expected structure
      return {
        success: true,
        outfits_worn_this_week: 0,
        message: 'Using fallback data due to analytics service unavailable'
      };
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
      // Temporarily disabled due to 405 errors on outfit-history endpoints
      console.log('🔍 DEBUG: Today\'s outfit suggestion temporarily disabled');
      return null;
      
      // TODO: Re-enable when backend outfit-history routes are fixed
      // console.log('🔍 DEBUG: Fetching today\'s outfit suggestion from /outfit-history/today-suggestion');
      // console.log('🔍 DEBUG: User ID:', user.uid);
      // console.log('🔍 DEBUG: User email:', user.email);
      // const response = await this.makeAuthenticatedRequest('/outfit-history/today-suggestion', user);
      // console.log('🔍 DEBUG: Today\'s outfit suggestion response:', response);
      // console.log('🔍 DEBUG: Today\'s outfit suggestion response details:', JSON.stringify(response, null, 2));
      
      // Handle new suggestion format
      // if (response.suggestion) {
      //   const suggestion = response.suggestion;
      //   const outfitData = suggestion.outfitData || {};
      //   
      //   console.log('🔍 DEBUG: Today\'s outfit suggestion data:', JSON.stringify(suggestion, null, 2));
      //   console.log('🔍 DEBUG: Today\'s outfit items count:', Array.isArray(outfitData.items) ? outfitData.items.length : 'not an array');
      //   console.log('🔍 DEBUG: Today\'s outfit name:', outfitData.name);
      //   
      //   return {
      //     suggestionId: suggestion.id,
      //     outfitName: outfitData.name || 'Daily Suggestion',
      //     outfitImage: outfitData.imageUrl || '',
      //     occasion: outfitData.occasion || 'Daily Suggestion',
      //     mood: outfitData.mood || 'Confident',
      //     weather: outfitData.weather || {},
      //     items: outfitData.items || [],
      //     isWorn: response.isWorn || false,
      //     wornAt: response.wornAt,
      //     generatedAt: suggestion.generatedAt,
      //     isSuggestion: true // Flag to distinguish from worn outfits
      //   };
      // }
      // 
      // // Handle case where no suggestion is returned
      // console.log('🔍 DEBUG: No suggestion found in response, response keys:', Object.keys(response));
      // 
      // return null;
    } catch (error) {
      console.error('Error fetching today\'s outfit:', error);
      // Return null for production when backend is not ready
      return null;
    }
  }

  private async getTopWornItems(user: User, wardrobeItems: any[] = []) {
    try {
      console.log('🔍 DEBUG: Calculating top worn items from wardrobe data');
      console.log('🔍 DEBUG: Wardrobe items count:', wardrobeItems.length);
      
      // Calculate top worn items from the wardrobe data we already have
      if (wardrobeItems && wardrobeItems.length > 0) {
        // Sort by wear count and get top 5
        const topItems = [...wardrobeItems]
          .filter(item => item.wearCount > 0) // Only items that have been worn
          .sort((a, b) => (b.wearCount || 0) - (a.wearCount || 0))
          .slice(0, 5)
          .map(item => ({
            id: item.id,
            name: item.name || 'Unknown Item',
            type: item.type || 'clothing',
            color: item.color || 'unknown',
            brand: item.brand || 'Unknown',
            wear_count: item.wearCount || 0,
            last_worn: item.lastWorn,
            image_url: item.imageUrl || item.image_url || item.image || '',
            is_favorite: item.favorite || item.isFavorite || false
          }));
        
        console.log('🔍 DEBUG: Calculated top worn items:', topItems.length);
        console.log('🔍 DEBUG: Top items with images:', topItems.filter(i => i.image_url).length);
        topItems.forEach(item => {
          console.log(`🔍 DEBUG: ${item.name} - imageUrl: ${item.image_url}`);
        });
        
        return {
          success: true,
          top_worn_items: topItems,
          count: topItems.length,
          message: 'Calculated from wardrobe data'
        };
      }
      
      // Fallback to API if no wardrobe items provided
      console.log('🔍 DEBUG: No wardrobe items, fetching from API');
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

  private calculateStyleGoals(styleCollections: StyleCollection[]): { completed: number, total: number } {
    // Calculate based on actual style collection progress
    // Sum up all the progress and target values across all collections
    const completed = styleCollections.reduce((sum, collection) => sum + collection.progress, 0);
    const total = styleCollections.reduce((sum, collection) => sum + collection.target, 0);
    
    console.log('🎯 [Style Goals] Calculating from collections:', {
      collections: styleCollections.map(c => `${c.name}: ${c.progress}/${c.target}`),
      totalCompleted: completed,
      totalTarget: total
    });
    
    return { completed, total };
  }

  // Removed complex calculation methods - using simple analytics instead

  private calculateOverallProgress(wardrobeStats: any, trendingStyles: any, userProfile: any): number {
    // Calculate overall progress based on style collections completion
    const collections = this.buildStyleCollections(wardrobeStats, trendingStyles, userProfile);
    
    // Calculate average completion of style collections
    const totalProgress = collections.reduce((sum, collection) => {
      const completion = Math.min(collection.progress / collection.target * 100, 100);
      return sum + completion;
    }, 0);
    
    const averageProgress = collections.length > 0 ? totalProgress / collections.length : 0;
    
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

  private buildStyleCollections(wardrobeStats: any, trendingStyles: any, userProfile: any): StyleCollection[] {
    // Use individual items from /wardrobe endpoint
    const items = wardrobeStats?.items || [];
    const categories: { [key: string]: number } = {};
    const itemStyles: { [key: string]: number } = {}; // Count items by their style tags
    
    if (Array.isArray(items) && items.length > 0) {
      items.forEach((item: any, index: number) => {
        const type = item.type || 'unknown';
        categories[type] = (categories[type] || 0) + 1;
        
        // Count items by their style tags
        const styles = item.style || [];
        if (Array.isArray(styles)) {
          styles.forEach((style: string) => {
            const normalizedStyle = style.toLowerCase().trim();
            itemStyles[normalizedStyle] = (itemStyles[normalizedStyle] || 0) + 1;
          });
        }
      });
    }
    
    // Get user's style preferences from profile
    const stylePreferences = userProfile?.stylePreferences || userProfile?.preferences?.style || [];
    console.log(`🎭 [Style Collections] User style preferences:`, stylePreferences);
    console.log(`🎭 [Style Collections] Item style distribution:`, itemStyles);
    
    // Build dynamic collections based on user's style preferences
    const dynamicCollections = this.getDynamicStyleCollections(stylePreferences, categories, itemStyles, items);
    
    return dynamicCollections;
  }

  private matchesStyleKeywords(item: any, keywords: string[]): boolean {
    // Check multiple sources for style keyword matches
    const searchableText = [
      item.name || '',
      item.metadata?.naturalDescription || '',
      ...(item.metadata?.styleTags || []),
      ...(item.style || []),
      ...(item.occasion || []),
      item.metadata?.visualAttributes?.formalLevel || '',
      item.type || ''
    ].join(' ').toLowerCase();
    
    // Count how many keywords match
    const matchCount = keywords.filter(keyword => 
      searchableText.includes(keyword.toLowerCase())
    ).length;
    
    // Require at least one keyword match (not just "casual" which is too broad)
    // If "casual" is the only match and it's from a generic list, be more strict
    if (matchCount === 1 && searchableText.includes('casual') && !searchableText.includes('street') && !searchableText.includes('urban')) {
      // Only casual match with no specific urban/street indicators - don't count for urban street
      if (keywords.includes('casual') && keywords.includes('urban')) {
        return false;
      }
    }
    
    return matchCount > 0;
  }

  private getDynamicStyleCollections(
    stylePreferences: string[], 
    categories: { [key: string]: number },
    itemStyles: { [key: string]: number },
    items: any[]
  ): StyleCollection[] {
    const collections: StyleCollection[] = [];
    
    // Comprehensive style mappings with all related/adjacent aesthetics
    const styleMappings: { [key: string]: any } = {
      'classic': {
        name: 'Classic Essentials',
        types: ['shirt', 'blazer', 'pants', 'trousers', 'shoes', 'dress shirt', 'oxford'],
        styleKeywords: [
          'classic', 'timeless', 'elegant', 'formal', 'traditional', 'refined', 'sophisticated',
          'polished', 'tailored', 'structured', 'crisp', 'clean-cut', 'smart', 'professional',
          'understated', 'quality', 'investment', 'heritage', 'button-up', 'oxford'
        ],
        target: 12,
        description: 'Timeless pieces that never go out of style'
      },
      'the classic': {
        name: 'Classic Essentials',
        types: ['shirt', 'blazer', 'pants', 'trousers', 'shoes', 'dress shirt', 'oxford'],
        styleKeywords: [
          'classic', 'timeless', 'elegant', 'formal', 'traditional', 'refined', 'sophisticated',
          'polished', 'tailored', 'structured', 'crisp', 'clean-cut', 'smart', 'professional',
          'understated', 'quality', 'investment', 'heritage', 'button-up', 'oxford'
        ],
        target: 12,
        description: 'Timeless pieces that never go out of style'
      },
      'old money': {
        name: 'Old Money Staples',
        types: ['blazer', 'sweater', 'pants', 'trousers', 'shoes', 'cardigan', 'turtleneck', 'oxford'],
        styleKeywords: [
          'old money', 'preppy', 'refined', 'sophisticated', 'classic', 'timeless', 'elegant',
          'heritage', 'traditional', 'understated', 'quality', 'tailored', 'ivy league',
          'country club', 'nautical', 'polo', 'cashmere', 'oxford', 'loafer', 'blazer',
          'smart', 'polished', 'distinguished', 'aristocratic', 'luxe', 'quiet luxury'
        ],
        target: 10,
        description: 'Refined, heritage pieces that speak to quiet luxury'
      },
      'urban street': {
        name: 'Urban Streetwear',
        types: ['shirt', 't-shirt', 'hoodie', 'jeans', 'sneakers', 'shoes', 'jacket', 'sweatshirt'],
        styleKeywords: [
          'urban', 'street', 'streetwear', 'edgy', 'contemporary', 'modern', 'hip-hop',
          'skate', 'athleisure', 'graphic', 'bold', 'oversized', 'trendy', 'cool', 'fresh',
          'dope', 'fire', 'hype', 'sneaker', 'hoodie', 'drop', 'collab', 'limited'
        ],
        target: 10,
        description: 'Contemporary street-ready pieces with an urban edge'
      },
      'street style': {
        name: 'Street Style Collection',
        types: ['shirt', 't-shirt', 'jeans', 'sneakers', 'jacket', 'hoodie', 'bomber'],
        styleKeywords: [
          'street', 'urban', 'streetwear', 'edgy', 'bold', 'contemporary', 'trendy',
          'fashion-forward', 'cool', 'fresh', 'statement', 'graphic', 'oversized',
          'layered', 'mixed', 'eclectic', 'creative', 'individual', 'unique'
        ],
        target: 10,
        description: 'Bold street-inspired pieces for everyday wear'
      },
      'minimalist': {
        name: 'Minimalist Basics',
        types: ['shirt', 't-shirt', 'pants', 'sweater', 'trousers', 'sneakers'],
        styleKeywords: [
          'minimalist', 'simple', 'clean', 'minimal', 'modern', 'sleek', 'understated',
          'monochrome', 'essential', 'streamlined', 'neutral', 'pared-back', 'refined',
          'subtle', 'elegant', 'timeless', 'versatile', 'effortless', 'scandinavian'
        ],
        target: 12,
        description: 'Clean, essential pieces with simple lines'
      },
      'casual': {
        name: 'Casual Staples',
        types: ['shirt', 't-shirt', 'jeans', 'pants', 'sneakers', 'hoodie', 'shorts'],
        styleKeywords: [
          'casual', 'everyday', 'comfortable', 'relaxed', 'laid-back', 'easy', 'effortless',
          'weekend', 'leisure', 'cozy', 'soft', 'breathable', 'versatile', 'go-to',
          'staple', 'basic', 'essential', 'easygoing', 'low-key', 'chill'
        ],
        target: 15,
        description: 'Comfortable everyday pieces for relaxed looks'
      },
      'preppy': {
        name: 'Preppy Collection',
        types: ['shirt', 'blazer', 'sweater', 'pants', 'shoes', 'polo', 'button-up', 'cardigan'],
        styleKeywords: [
          'preppy', 'classic', 'collegiate', 'smart', 'traditional', 'refined', 'polished',
          'ivy league', 'nautical', 'country club', 'polo', 'oxford', 'button-down',
          'argyle', 'striped', 'clean-cut', 'fresh', 'wholesome', 'timeless', 'heritage'
        ],
        target: 10,
        description: 'Polished, collegiate-inspired pieces'
      },
      'smart casual': {
        name: 'Smart Casual Mix',
        types: ['shirt', 'blazer', 'pants', 'shoes', 'sweater', 'button-up', 'chinos'],
        styleKeywords: [
          'smart casual', 'polished', 'versatile', 'refined', 'sophisticated', 'business casual',
          'elevated', 'professional', 'tailored', 'put-together', 'crisp', 'sharp',
          'modern', 'contemporary', 'office-ready', 'adaptable', 'smart', 'chic'
        ],
        target: 12,
        description: 'Versatile pieces that work from office to evening'
      },
      'bohemian': {
        name: 'Bohemian Collection',
        types: ['shirt', 'dress', 'skirt', 'pants', 'sandals', 'kimono', 'tunic'],
        styleKeywords: [
          'bohemian', 'boho', 'free-spirited', 'eclectic', 'artistic', 'relaxed', 'flowing',
          'ethnic', 'vintage', 'retro', 'hippie', 'festival', 'romantic', 'whimsical',
          'layered', 'textured', 'earthy', 'natural', 'unconventional', 'creative'
        ],
        target: 10,
        description: 'Free-spirited, artistic pieces with bohemian flair'
      },
      'athletic': {
        name: 'Athletic Collection',
        types: ['t-shirt', 'shorts', 'pants', 'sneakers', 'hoodie', 'jacket', 'tank'],
        styleKeywords: [
          'athletic', 'sporty', 'active', 'performance', 'athleisure', 'gym', 'workout',
          'fitness', 'sport', 'running', 'training', 'technical', 'moisture-wicking',
          'breathable', 'stretch', 'flexible', 'dynamic', 'energetic', 'functional'
        ],
        target: 12,
        description: 'Performance and athleisure pieces for active lifestyles'
      },
      'vintage': {
        name: 'Vintage Collection',
        types: ['shirt', 'jeans', 'jacket', 'dress', 'sweater', 'coat'],
        styleKeywords: [
          'vintage', 'retro', 'classic', 'nostalgic', 'throwback', 'old-school', 'heritage',
          'timeless', 'authentic', 'original', 'worn-in', 'distressed', 'faded',
          'era', 'decade', 'antique', 'traditional', 'period', 'historical'
        ],
        target: 8,
        description: 'Timeless vintage and retro-inspired pieces'
      },
      'edgy': {
        name: 'Edgy Collection',
        types: ['jacket', 'jeans', 'boots', 't-shirt', 'leather', 'denim'],
        styleKeywords: [
          'edgy', 'bold', 'dark', 'rebellious', 'rock', 'punk', 'grunge', 'alternative',
          'leather', 'studded', 'ripped', 'distressed', 'black', 'metal', 'gothic',
          'fierce', 'attitude', 'statement', 'unconventional', 'daring'
        ],
        target: 8,
        description: 'Bold, rebellious pieces with an edge'
      }
    };
    
    // If user has style preferences, create collections for each
    if (stylePreferences && stylePreferences.length > 0) {
      stylePreferences.forEach((stylePref: string) => {
        const normalizedStyle = stylePref.toLowerCase().trim();
        const styleConfig = styleMappings[normalizedStyle];
        
        if (styleConfig) {
          // Intelligent matching: check each item's name, metadata, and tags
          const matchingItems = items.filter(item => {
            // First check: Does the item type match this style?
            const typeMatches = styleConfig.types.includes(item.type?.toLowerCase());
            
            // Second check: Does the item's metadata/name contain style keywords?
            const keywordMatches = this.matchesStyleKeywords(item, styleConfig.styleKeywords);
            
            // Third check: Does the item have tags that directly match the style preference?
            const itemTags = [
              ...(item.style || []),
              ...(item.metadata?.styleTags || []),
              ...(item.tags || []),
              ...(item.occasion || [])
            ].map(tag => tag.toLowerCase().trim());
            
            const styleNameParts = normalizedStyle.split(' '); // e.g., "urban street" → ["urban", "street"]
            const hasMatchingTag = itemTags.some(tag => 
              // Tag contains the style name or any part of it
              styleNameParts.some(part => tag.includes(part) || part.includes(tag))
            );
            
            // Fourth check: Multiple keyword matches (strong signal)
            const hasMultipleKeywords = styleConfig.styleKeywords.filter((keyword: string) => {
              const searchText = [
                item.name || '',
                item.metadata?.naturalDescription || '',
                ...(item.metadata?.styleTags || []),
                ...(item.style || [])
              ].join(' ').toLowerCase();
              return searchText.includes(keyword.toLowerCase());
            }).length >= 2;
            
            // Item matches if ANY of these conditions are true:
            // 1. Type matches AND has keyword matches
            // 2. Has multiple keyword matches (strong signal)
            // 3. Has tags that directly match the style preference name
            return (typeMatches && keywordMatches) || hasMultipleKeywords || hasMatchingTag;
          });
          
          const finalCount = matchingItems.length;
          
          console.log(`🎭 [${styleConfig.name}] Matched ${finalCount} items:`, 
            matchingItems.map(i => `${i.name} (${i.type})`));
          
          collections.push({
            name: styleConfig.name,
            progress: finalCount,
            target: styleConfig.target,
            status: finalCount >= styleConfig.target 
              ? `Complete! ${styleConfig.description}` 
              : styleConfig.description
          });
        }
      });
    }
    
    // If no style preferences or no matching collections, add default collections
    if (collections.length === 0) {
      // Fallback to basic type-based collections
      collections.push({
        name: 'Top Collection',
        progress: (categories['shirt'] || 0) + (categories['sweater'] || 0) + (categories['t-shirt'] || 0) + (categories['hoodie'] || 0),
        target: 12,
        status: 'Building your top collection'
      });
      
      collections.push({
        name: 'Bottom Collection',
        progress: (categories['pants'] || 0) + (categories['jeans'] || 0) + (categories['shorts'] || 0),
        target: 10,
        status: 'Building your bottom collection'
      });
      
      collections.push({
        name: 'Footwear Collection',
        progress: (categories['shoes'] || 0) + (categories['sneakers'] || 0) + (categories['boots'] || 0),
        target: 8,
        status: 'Building your footwear collection'
      });
    }
    
    return collections;
  }

  private getPersonaCollections(persona: string, categories: { [key: string]: number }): StyleCollection[] {
    const collections: StyleCollection[] = [];
    
    // Persona-specific collection definitions
    const personaMappings: { [key: string]: any } = {
      rebel: {
        collections: [
          {
            name: 'Statement Pieces',
            types: ['shirt', 'sweater', 'jacket', 'blazer'],
            target: 10,
            description: 'Bold, eye-catching pieces that make you stand out'
          },
          {
            name: 'Edgy Bottoms',
            types: ['pants', 'jeans', 'shorts'],
            target: 8,
            description: 'Unique pants and jeans that break the mold'
          },
          {
            name: 'Statement Footwear',
            types: ['shoes', 'boots', 'sneakers'],
            target: 6,
            description: 'Bold shoes that complete your rebellious look'
          }
        ]
      },
      architect: {
        collections: [
          {
            name: 'Clean Basics',
            types: ['shirt', 'sweater', 't-shirt'],
            target: 12,
            description: 'Timeless, well-fitted basics that form your foundation'
          },
          {
            name: 'Tailored Bottoms',
            types: ['pants', 'jeans', 'trousers'],
            target: 10,
            description: 'Well-structured pants with clean lines'
          },
          {
            name: 'Minimal Footwear',
            types: ['shoes', 'boots', 'sneakers'],
            target: 6,
            description: 'Sleek, versatile shoes for every occasion'
          }
        ]
      },
      strategist: {
        collections: [
          {
            name: 'Versatile Tops',
            types: ['shirt', 'sweater', 'blazer'],
            target: 12,
            description: 'Smart pieces that work across multiple occasions'
          },
          {
            name: 'Smart Bottoms',
            types: ['pants', 'jeans', 'shorts'],
            target: 10,
            description: 'Adaptable pants that transition seamlessly'
          },
          {
            name: 'Functional Footwear',
            types: ['shoes', 'boots', 'sneakers'],
            target: 8,
            description: 'Practical shoes that work hard for you'
          }
        ]
      },
      modernist: {
        collections: [
          {
            name: 'Contemporary Tops',
            types: ['shirt', 'sweater', 't-shirt'],
            target: 12,
            description: 'Modern, streamlined pieces with clean lines'
          },
          {
            name: 'Sleek Bottoms',
            types: ['pants', 'jeans'],
            target: 10,
            description: 'Forward-thinking pants with contemporary cuts'
          },
          {
            name: 'Modern Footwear',
            types: ['shoes', 'sneakers'],
            target: 8,
            description: 'Fashion-forward shoes for the modern wardrobe'
          }
        ]
      },
      connoisseur: {
        collections: [
          {
            name: 'Luxury Basics',
            types: ['shirt', 'sweater', 'blazer'],
            target: 10,
            description: 'Investment pieces with refined details'
          },
          {
            name: 'Premium Bottoms',
            types: ['pants', 'jeans', 'trousers'],
            target: 8,
            description: 'High-quality pants that speak to your refined taste'
          },
          {
            name: 'Designer Footwear',
            types: ['shoes', 'boots'],
            target: 6,
            description: 'Luxury shoes that complete your sophisticated look'
          }
        ]
      }
    };
    
    // Get persona-specific collections, fallback to architect if persona not found
    const personaConfig = personaMappings[persona] || personaMappings['architect'];
    
    // Build collections based on persona
    personaConfig.collections.forEach((collection: any) => {
      const count = collection.types.reduce((sum: number, type: string) => {
        return sum + (categories[type] || 0);
      }, 0);
      
      collections.push({
        name: collection.name,
        progress: count,
        target: collection.target,
        status: count >= collection.target 
          ? `Complete! ${collection.description}` 
          : collection.description
      });
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
    // Use individual items from /wardrobe endpoint
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

  private async getWardrobeGapsFromBackend(user: User | null): Promise<WardrobeGap[]> {
    try {
      console.log('🔍 DEBUG: Fetching wardrobe gaps from backend...');
      const response = await this.makeAuthenticatedRequest('/wardrobe-analysis/gaps', user);
      
      if (response?.success && response?.data?.gaps) {
        console.log('✅ DEBUG: Successfully fetched wardrobe gaps from backend:', response.data.gaps.length);
        console.log('🔍 DEBUG: Gap Analysis Debug Info:', response.debug);
        console.log('🔍 DEBUG: Wardrobe Stats from Gap Analysis:', response.debug?.wardrobe_stats);
        console.log('🔍 DEBUG: Parsing Errors (first 10):', response.debug?.parsing_errors);
        return response.data.gaps;
      } else {
        console.log('⚠️ DEBUG: No gaps data from backend, falling back to local analysis');
        return [];
      }
    } catch (error) {
      console.error('❌ DEBUG: Error fetching wardrobe gaps from backend:', error);
      return [];
    }
  }

  private buildWardrobeGaps(wardrobeStats: any): WardrobeGap[] {
    const gaps: WardrobeGap[] = [];
    
    // Use individual items from /wardrobe endpoint
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
          suggestedItems: config.items.slice(0, 3), // Suggest top 3 item types
          currentCount: count,
          recommendedCount: config.minRequired,
          gapSize: config.minRequired - count
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
    const winterTarget = 5;
    if (winterItems < winterTarget) { // Adjusted threshold based on actual counts (9 sweaters + 12 jackets = 21)
      gaps.push({
        category: 'Seasonal Coverage',
        description: `Limited winter clothing (${winterItems} items) - consider sweaters or jackets`,
        priority: 'medium',
        suggestedItems: ['sweater', 'jacket'],
        currentCount: winterItems,
        recommendedCount: winterTarget,
        gapSize: winterTarget - winterItems
      });
    }
    
    // Summer items (light clothing) - using actual item types
    const summerItems = (categories['shorts'] || 0) + (categories['shirt'] || 0); // shirts can be summer wear
    const summerTarget = 20;
    if (summerItems < summerTarget) { // Adjusted threshold based on actual counts (6 shorts + 57 shirts = 63)
      gaps.push({
        category: 'Seasonal Coverage',
        description: `Limited summer clothing (${summerItems} items) - consider shorts or lightweight shirts`,
        priority: 'medium',
        suggestedItems: ['shorts', 'shirt'],
        currentCount: summerItems,
        recommendedCount: summerTarget,
        gapSize: summerTarget - summerItems
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
    const formalTarget = 3;
    if (formalItems < formalTarget) {
      gaps.push({
        category: 'Style Variety',
        description: `Limited formal wear (${formalItems} items) - consider blazers, dress pants, or dress shirts`,
        priority: 'low',
        suggestedItems: ['blazer', 'dress_pants', 'dress_shirt'],
        currentCount: formalItems,
        recommendedCount: formalTarget,
        gapSize: formalTarget - formalItems
      });
    }
    
    // Check for casual wear gaps (adjusted threshold)
    const casualTarget = 20;
    if (casualItems < casualTarget) {
      gaps.push({
        category: 'Style Variety',
        description: `Limited casual wear (${casualItems} items) - consider more casual shirts, pants, or shoes`,
        priority: 'medium',
        suggestedItems: ['shirt', 'pants', 'shoes'],
        currentCount: casualItems,
        recommendedCount: casualTarget,
        gapSize: casualTarget - casualItems
      });
    }
    
    return gaps;
  }
  
  private analyzeColorGaps(wardrobeStats: any): WardrobeGap[] {
    const gaps: WardrobeGap[] = [];
    const colors = wardrobeStats.colors || {};
    const uniqueColors = Object.keys(colors);
    
    const colorTarget = 5;
    if (uniqueColors.length < colorTarget) {
      gaps.push({
        category: 'Color Variety',
        description: `Limited color variety (${uniqueColors.length} colors) - consider adding more colorful pieces`,
        priority: 'low',
        suggestedItems: ['Colorful tops', 'Patterned items', 'Accent pieces'],
        currentCount: uniqueColors.length,
        recommendedCount: colorTarget,
        gapSize: colorTarget - uniqueColors.length
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
        suggestedItems: ['Black basics', 'White shirts', 'Gray sweaters', 'Navy pants'],
        currentCount: 0,
        recommendedCount: 1,
        gapSize: 1
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
      
      return topWornItems.map((item: any) => {
        // Handle multiple possible image field names and provide fallback
        const imageUrl = item.image_url || item.imageUrl || item.image || '';
        console.log('🔍 DEBUG: Item:', item.name, '- Image URL:', imageUrl || '(none)');
        
        return {
          id: item.id,
          name: item.name || 'Unknown Item',
          type: item.type || 'clothing',
          imageUrl: imageUrl,
          wearCount: item.wear_count || item.wearCount || 0,
          rating: item.is_favorite || item.isFavorite ? 5 : 3 // Use favorite status as rating proxy
        };
      });
    } catch (error) {
      console.error('Error building top items:', error);
      return [];
    }
  }

  private buildRecentOutfits(): RecentOutfit[] {
    // Return empty array for now - recent outfits feature disabled
    // Can be re-implemented with direct outfit queries if needed
    return [];
  }

}

export const dashboardService = new DashboardService();
