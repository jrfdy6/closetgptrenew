import { User } from 'firebase/auth';
import { publishWearReceipt } from '@/lib/wardrobeActivity';
import { wearOperationKey, clearWearOperation } from '@/lib/savedOutfit';

export interface DashboardData {
  totalItems: number;
  favorites: number;
  styleGoalsCompleted: number;
  totalStyleGoals: number;
  outfitsThisWeek: number | null;
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

const WARDROBE_CATEGORY_CONFIG: Array<{ id: "top" | "bottom" | "shoe" | "accessory" | "jacket"; keywords: string[] }> = [
  {
    id: "top",
    keywords: ["top", "shirt", "t-shirt", "tee", "blouse", "sweater", "hoodie", "polo", "tank", "henley", "longsleeve", "long sleeve", "rugby", "jersey"],
  },
  {
    id: "bottom",
    keywords: ["bottom", "pant", "pants", "trouser", "jean", "short", "skirt", "chino"],
  },
  {
    id: "shoe",
    keywords: ["shoe", "sneaker", "boot", "loafer", "heel", "slides", "footwear"],
  },
  {
    id: "accessory",
    keywords: ["accessory", "belt", "watch", "scarf", "hat", "glove", "bag", "bracelet", "necklace", "jewelry", "suspenders", "sunglass", "sunglasses"],
  },
  {
    id: "jacket",
    keywords: ["jacket", "coat", "outerwear", "blazer"],
  },
];

const normalizeString = (value: unknown): string =>
  typeof value === "string" ? value.toLowerCase() : "";

const flattenStringArray = (value: unknown): string =>
  Array.isArray(value) ? value.map((entry) => normalizeString(entry)).join(" ") : "";

const itemMatchesCategory = (item: any, keywords: string[]): boolean => {
  const type = normalizeString(item?.type);
  const name = normalizeString(item?.name);
  const tags = flattenStringArray(item?.tags);
  const style = flattenStringArray(item?.style);
  const occasion = flattenStringArray(item?.occasion);
  const combined = `${type} ${name} ${tags} ${style} ${occasion}`;
  return keywords.some((keyword) => combined.includes(keyword.toLowerCase()));
};

const mapWardrobeItemToTopItem = (item: any) => ({
  id: item.id,
  name: item.name || "Unknown Item",
  type: item.type || "clothing",
  color: item.color || "unknown",
  brand: item.brand || "Unknown",
  wear_count: item.wearCount || 0,
  last_worn: item.lastWorn,
  image_url: item.imageUrl || item.image_url || item.image || "",
  is_favorite: item.favorite || item.isFavorite || false,
});

const calculatePreferenceScore = (item: any) => {
  const wearCount = item?.wearCount ?? 0;
  const isFavorite = Boolean(item?.favorite || item?.isFavorite);
  return wearCount * (isFavorite ? 1.1 : 1);
};

class DashboardService {
  private async makeAuthenticatedRequest(
    endpoint: string,
    user: User | null,
    options: RequestInit = {},
    timeoutMs: number = 15000,
  ): Promise<any> {
    if (!user) throw new Error('Please sign in to load your dashboard.');
    if (!endpoint.startsWith('/') || endpoint.startsWith('//')) {
      throw new Error('Your dashboard could not be loaded. Please try again.');
    }

    const controller = new AbortController();
    let timeoutId: ReturnType<typeof setTimeout> | undefined;
    const deadline = new Promise<never>((_, reject) => {
      timeoutId = setTimeout(() => {
        controller.abort();
        reject(new Error('Dashboard request timed out'));
      }, timeoutMs);
    });
    const request = async () => {
      const token = await user.getIdToken();
      // Token acquisition cannot be cancelled; a late token must not start I/O.
      if (controller.signal.aborted) throw new Error('Dashboard request timed out');
      if (!token) throw new Error('Authentication unavailable');
      const headers = new Headers(options.headers);
      headers.set('Authorization', `Bearer ${token}`);
      headers.set('Content-Type', 'application/json');
      const response = await fetch(`/api${endpoint}`, {
        method: 'GET',
        ...options,
        headers,
        cache: 'no-store',
        signal: controller.signal,
      });
      if (!response.ok) throw new Error('Dashboard request failed');
      return await response.json();
    };
    try {
      // The deadline covers token acquisition, fetch, and response parsing.
      return await Promise.race([request(), deadline]);
    } catch {
      // Upstream bodies, tokens and private profile/wardrobe data stay out of logs
      // and user-facing errors. Required callers must not replace failures with 0.
      throw new Error('Your dashboard could not be loaded. Please try again.');
    } finally {
      if (timeoutId !== undefined) clearTimeout(timeoutId);
    }
  }

  async getDashboardData(user: User | null, forceFresh: boolean = false): Promise<DashboardData> {
    try {
      if (!user) throw new Error('Please sign in to load your dashboard.');
      const fetchWithTimeout = async (promise: Promise<any>, timeoutMs: number, fallback: any) => {
        let timeoutId: ReturnType<typeof setTimeout> | undefined;
        try {
          return await Promise.race([
            promise,
            new Promise((_, reject) => {
              timeoutId = setTimeout(() => reject(new Error('Dashboard insight timed out')), timeoutMs);
            }),
          ]);
        } catch {
          return fallback;
        } finally {
          if (timeoutId !== undefined) clearTimeout(timeoutId);
        }
      };

      // These are required inputs. An unavailable wardrobe/profile is not an
      // empty wardrobe; let the page preserve its last successful state or retry.
      const [userProfile, wardrobeStats] = await Promise.all([
        this.getUserProfile(user),
        this.getWardrobeStats(user),
      ]);
      const wardrobeItems = wardrobeStats.items;
      const hasWardrobeItems = wardrobeItems.length > 0;

      // Optional insights retain their existing bounded fallbacks.
      const [simpleAnalytics, trendingStyles, todaysOutfit, topWornItems] = await Promise.all([
        fetchWithTimeout(this.getSimpleAnalytics(user, forceFresh), 15000, null),
        fetchWithTimeout(this.getTrendingStyles(user), 8000, { success: true, data: { styles: [] } }),
        fetchWithTimeout(this.getTodaysOutfit(user), 8000, { success: true, suggestion: null }),
        fetchWithTimeout(this.getTopWornItems(user, wardrobeItems, hasWardrobeItems), 8000, { success: true, data: { items: [] } }),
      ]);
      const styleCollections = this.buildStyleCollections(wardrobeStats, trendingStyles, userProfile);
      const styleGoalsData = this.calculateStyleGoals(styleCollections);
      const resolvedWardrobeGaps = hasWardrobeItems
        ? await fetchWithTimeout(this.getWardrobeGapsFromBackend(user), 10000, [])
        : [];

      return {
        totalItems: wardrobeStats.total_items,
        favorites: this.calculateFavorites(wardrobeStats),
        styleGoalsCompleted: styleGoalsData.completed,
        totalStyleGoals: styleGoalsData.total,
        outfitsThisWeek: simpleAnalytics?.outfits_worn_this_week ?? null,
        overallProgress: this.calculateOverallProgress(wardrobeStats, trendingStyles, userProfile),
        styleCollections,
        styleExpansions: this.buildStyleExpansions(wardrobeStats, trendingStyles),
        seasonalBalance: this.buildSeasonalBalance(wardrobeStats),
        colorVariety: this.buildColorVariety(wardrobeStats),
        wardrobeGaps: resolvedWardrobeGaps,
        topItems: this.buildTopItems(topWornItems),
        recentOutfits: this.buildRecentOutfits(),
        todaysOutfit: todaysOutfit?.todaysOutfit || todaysOutfit || null,
        shoppingRecommendations: null,
      };
    } catch {
      // Keep a failed refresh distinguishable from a successful empty response.
      throw new Error('Your dashboard could not be loaded. Please try again.');
    }
  }

  private async getUserProfile(user: User) {
    const isMobile = typeof navigator !== 'undefined' && /Mobile|Android|iPhone|iPad/i.test(navigator.userAgent);
    const profile = await this.makeAuthenticatedRequest('/user/profile', user, {}, isMobile ? 30000 : 15000);
    if (!profile || typeof profile !== 'object' || Array.isArray(profile) ||
        profile.userId !== user.uid || profile.success === false || profile.error ||
        ['user_id', 'firebase_uid'].some(key => profile[key] != null && profile[key] !== user.uid) ||
        (profile.stylePreferences != null && (!Array.isArray(profile.stylePreferences) ||
          profile.stylePreferences.some((value: unknown) => typeof value !== 'string'))) ||
        (profile.preferences != null && (typeof profile.preferences !== 'object' || Array.isArray(profile.preferences))) ||
        (profile.preferences?.style != null && (!Array.isArray(profile.preferences.style) ||
          profile.preferences.style.some((value: unknown) => typeof value !== 'string')))) {
      throw new Error('Your dashboard could not be loaded. Please try again.');
    }
    return profile;
  }

  private async getWardrobeStats(user: User) {
    const isMobile = typeof navigator !== 'undefined' && /Mobile|Android|iPhone|iPad/i.test(navigator.userAgent);
    const response = await this.makeAuthenticatedRequest('/wardrobe', user, {}, isMobile ? 60000 : 35000);
    if (!response || response.success !== true || response.error || !Array.isArray(response.items) ||
        !Number.isInteger(response.count) || response.count < 0 || response.count !== response.items.length ||
        response.items.some((item: unknown) => !item || typeof item !== 'object' || Array.isArray(item) ||
          typeof (item as { id?: unknown }).id !== 'string' || !(item as { id: string }).id.trim())) {
      throw new Error('Your dashboard could not be loaded. Please try again.');
    }
    const wardrobeItems = response.items;
    const itemsForStats = isMobile ? wardrobeItems.slice(0, 200) : wardrobeItems;
    const categories: Record<string, number> = {};
    const colors: Record<string, number> = {};
    itemsForStats.forEach((item: any) => {
      const category = item.type || item.category || 'unknown';
      categories[category] = (categories[category] || 0) + 1;
      const color = item.color || 'unknown';
      colors[color] = (colors[color] || 0) + 1;
    });
    return { total_items: response.count, categories, colors, user_id: user.uid, items: wardrobeItems };
  }

  // Removed getOutfitHistory - replaced with getSimpleAnalytics

  private async getSimpleAnalytics(user: User, _forceFresh: boolean = false) {
    const response = await this.makeAuthenticatedRequest('/simple-analytics/outfits-worn-this-week', user);
    const count = response?.outfits_worn_this_week ?? response?.worn_this_week;
    if (response?.success !== true || !Number.isInteger(count) || count < 0) {
      throw new Error('Your wear history could not be loaded. Please try again.');
    }
    return { outfits_worn_this_week: count };
  }

  private async getTrendingStyles(user: User) {
    try {
      const response = await this.makeAuthenticatedRequest('/wardrobe/trending-styles', user, {
        method: 'GET'
      });

      return response.data || response || {};
    } catch {
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

      return null;
      
      // TODO: Re-enable when backend outfit-history routes are fixed
      // const response = await this.makeAuthenticatedRequest('/outfit-history/today-suggestion', user);
      
      // Handle new suggestion format
      // if (response.suggestion) {
      //   const suggestion = response.suggestion;
      //   const outfitData = suggestion.outfitData || {};
      //   
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
      // 
      // return null;
    } catch {
      // Return null for production when backend is not ready
      return null;
    }
  }

  private async getTopWornItems(user: User, wardrobeItems: any[] = [], hasWardrobeItems: boolean = true) {
    try {
      // OPTIMIZED: Limit items processed on mobile for better performance
      const isMobile = typeof navigator !== 'undefined' && /Mobile|Android|iPhone|iPad/i.test(navigator.userAgent);
      const maxItemsToProcess = isMobile ? 100 : wardrobeItems.length; // Limit to 100 items on mobile
      const itemsToProcess = wardrobeItems.slice(0, maxItemsToProcess);
      
      // Calculate top worn items from the wardrobe data we already have
      if (itemsToProcess && itemsToProcess.length > 0) {
        const usedIds = new Set<string>();
        const categorySelections: any[] = [];

        // OPTIMIZED: Pre-calculate preference scores once instead of multiple times
        const itemsWithScores = itemsToProcess.map(item => ({
          item,
          score: calculatePreferenceScore(item)
        }));

        // OPTIMIZED: Single pass through items instead of nested loops
        WARDROBE_CATEGORY_CONFIG.forEach((config) => {
          let bestItem: any = null;
          let bestScore = -Infinity;

          itemsWithScores.forEach(({ item, score }) => {
            if (!itemMatchesCategory(item, config.keywords)) {
              return;
            }

            if (!bestItem || score > bestScore) {
              bestItem = item;
              bestScore = score;
            }
          });

          if (bestItem && !usedIds.has(bestItem.id)) {
            categorySelections.push(bestItem);
            usedIds.add(bestItem.id);
          }
        });

        // OPTIMIZED: Use pre-sorted items instead of sorting again
        const sortedByPreference = itemsWithScores
          .sort((a, b) => b.score - a.score)
          .map(({ item }) => item);
        
        const combinedItems: any[] = [...categorySelections];

        // Add top items by preference score (already sorted)
        sortedByPreference.forEach((item) => {
          if (!item || usedIds.has(item.id)) {
            return;
          }
          combinedItems.push(item);
          usedIds.add(item.id);
        });

        const desiredCount = Math.max(WARDROBE_CATEGORY_CONFIG.length, 5);
        const topItems = combinedItems
          .slice(0, desiredCount)
          .map(mapWardrobeItemToTopItem);
        
        return {
          success: true,
          top_worn_items: topItems,
          count: topItems.length,
          message: 'Calculated from wardrobe data'
        };
      }
      
      // If the user truly has no wardrobe items, return empty data instead of demo/fallback items
      if (!hasWardrobeItems) {

        return {
          success: true,
          top_worn_items: [],
          count: 0,
          message: 'No wardrobe items available'
        };
      }
      
      // Fallback to API if we expect items but none were passed (e.g., stats endpoint failed)

      const response = await this.makeAuthenticatedRequest('/wardrobe/top-worn-items?limit=5', user, {
        method: 'GET'
      });

      return response.data || response || {};
    } catch {
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
      const response = await this.makeAuthenticatedRequest('/outfit-history/today-suggestion/wear', user, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ suggestionId, idempotency_key: wearOperationKey(user.uid, 'suggestion:' + suggestionId), timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC' }),
      });
      
      publishWearReceipt(user.uid, response);
      clearWearOperation(user.uid, 'suggestion:' + suggestionId);
      return response.undone !== true;
    } catch {
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
    
    return Math.round(averageProgress);
  }

  private calculateColorVarietyScore(wardrobeStats: any): number {
    const colors = wardrobeStats.colors || {};
    const uniqueColors = Object.keys(colors).length;
    const score = Math.min(uniqueColors / 8 * 100, 100); // Target: 8 colors

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
      const response = await this.makeAuthenticatedRequest('/wardrobe-analysis/gaps', user);
      
      if (response?.success && response?.data?.gaps) {

        return response.data.gaps;
      } else {

        return [];
      }
    } catch {
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

      if (!Array.isArray(topWornItems)) {

        return [];
      }
      
      return topWornItems.map((item: any) => {
        // Handle multiple possible image field names and provide fallback
        const imageUrl = item.image_url || item.imageUrl || item.image || '';
        
        return {
          id: item.id,
          name: item.name || 'Unknown Item',
          type: item.type || 'clothing',
          imageUrl: imageUrl,
          wearCount: item.wear_count || item.wearCount || 0,
          rating: item.is_favorite || item.isFavorite ? 5 : 3 // Use favorite status as rating proxy
        };
      });
    } catch {
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
