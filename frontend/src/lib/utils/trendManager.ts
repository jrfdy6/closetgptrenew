import { OpenAI } from "openai";

// Define types locally instead of importing
interface UserProfile {
  id: string;
  name: string;
  stylePreferences: string[];
  occasions: string[];
  bodyType?: string;
  skinTone?: string;
}

interface ClothingItem {
  id: string;
  name: string;
  type: string;
  color: string;
  style: string[];
  season: string[];
  brand?: string;
  price?: number;
}

// Types
export interface FashionTrend {
  id: string;
  name: string;
  category: TrendCategory;
  subCategories: TrendSubCategory[];
  season: TrendSeason;
  popularity: number;
  description: string;
  keyItems: string[];
  createdAt: Date;
  updatedAt: Date;
  gender: "Men" | "Women" | "Unisex";
  priceRange: "Budget" | "Mid-Range" | "Luxury";
  sustainability: boolean;
  culturalInfluence?: string;
  colorPalette?: string[];
  fabricTypes?: string[];
  imageUrl: string;
}

export interface TrendAnalytics {
  trendId: string;
  trendName: string;
  adoptionRate: number;
  userEngagement: number;
  seasonalRelevance: number;
  predictedLifespan: number;
  lastUpdated: Date;
}

export type TrendCategory = 
  // Core Aesthetics & Styles
  | "Quiet Luxury"
  | "Gorpcore"
  | "Old Money"
  | "Grandpacore"
  | "Dark Academia"
  | "Streetwear"
  | "Athleisure"
  | "Minimalist"
  | "Y2K Revival"
  | "Techwear"
  | "Coquette"
  | "Cottagecore"
  | "Mob Wife"
  | "Balletcore"
  | "Gothcore"
  | "Boho Chic"
  | "Preppy";

export type TrendSubCategory = 
  // Key Pieces & Fabrics
  | "Knitwear"
  | "Cardigans"
  | "Turtlenecks"
  | "Argyle"
  | "Outerwear"
  | "Henley"
  | "Cargo"
  | "Vintage"
  | "Overcoats"
  // Colors & Patterns
  | "Earth Tones"
  | "Monochromatic"
  | "Plaid"
  | "Pastel"
  | "Bold Prints"
  | "Neon"
  | "Camouflage"
  | "Tie-Dye"
  | "Color Blocking"
  | "Metallic"
  // Footwear
  | "Sneakers"
  | "Loafers"
  | "Combat Boots"
  | "Slip-Ons"
  | "High-Tops"
  | "Espadrilles"
  | "Sandals"
  | "Moccasins"
  | "Chelsea Boots"
  | "Derby Shoes"
  // Accessories
  | "Beanies"
  | "Bucket Hats"
  | "Crossbody Bags"
  | "Statement Belts"
  | "Layered Necklaces"
  | "Bracelets"
  | "Sunglasses"
  | "Watches"
  | "Scarves"
  | "Gloves"
  // Seasonal
  | "Linen"
  | "Shorts Suits"
  | "Layered Outerwear"
  | "Flannel"
  | "Puffer"
  | "Raincoats"
  | "Thermal"
  | "Swim"
  | "Denim"
  | "Track Suits"
  // Cultural
  | "Scandinavian"
  | "Italian"
  | "British"
  | "American"
  | "Japanese"
  | "French"
  | "African"
  | "Latin American"
  | "Middle Eastern"
  | "Indian";

export type TrendSeason = "Spring" | "Summer" | "Fall" | "Winter";

export interface TrendFilter {
  category?: TrendCategory;
  subCategory?: TrendSubCategory;
  season?: TrendSeason;
  minPopularity?: number;
  minEngagement?: number;
  gender?: "Men" | "Women" | "Unisex";
  priceRange?: "Budget" | "Mid-Range" | "Luxury";
  sustainability?: boolean;
}

// Constants
export const TREND_CATEGORIES: TrendCategory[] = [
  "Quiet Luxury",
  "Gorpcore",
  "Old Money",
  "Grandpacore",
  "Dark Academia",
  "Streetwear",
  "Athleisure",
  "Minimalist",
  "Y2K Revival",
  "Techwear",
  "Coquette",
  "Cottagecore",
  "Mob Wife",
  "Balletcore",
  "Gothcore",
  "Boho Chic",
  "Preppy",
];

export const TREND_SUBCATEGORIES: TrendSubCategory[] = [
  // Key Pieces & Fabrics
  "Knitwear",
  "Cardigans",
  "Turtlenecks",
  "Argyle",
  "Outerwear",
  "Henley",
  "Cargo",
  "Vintage",
  "Overcoats",
  // Colors & Patterns
  "Earth Tones",
  "Monochromatic",
  "Plaid",
  "Pastel",
  "Bold Prints",
  "Neon",
  "Camouflage",
  "Tie-Dye",
  "Color Blocking",
  "Metallic",
  // Footwear
  "Sneakers",
  "Loafers",
  "Combat Boots",
  "Slip-Ons",
  "High-Tops",
  "Espadrilles",
  "Sandals",
  "Moccasins",
  "Chelsea Boots",
  "Derby Shoes",
  // Accessories
  "Beanies",
  "Bucket Hats",
  "Crossbody Bags",
  "Statement Belts",
  "Layered Necklaces",
  "Bracelets",
  "Sunglasses",
  "Watches",
  "Scarves",
  "Gloves",
  // Seasonal
  "Linen",
  "Shorts Suits",
  "Layered Outerwear",
  "Flannel",
  "Puffer",
  "Raincoats",
  "Thermal",
  "Swim",
  "Denim",
  "Track Suits",
  // Cultural
  "Scandinavian",
  "Italian",
  "British",
  "American",
  "Japanese",
  "French",
  "African",
  "Latin American",
  "Middle Eastern",
  "Indian",
];

export const SEASONS: TrendSeason[] = ["Spring", "Summer", "Fall", "Winter"];

export const PRICE_RANGES = ["Budget", "Mid-Range", "Luxury"] as const;

// Trend API Integration
export async function fetchTrendingStyles(): Promise<FashionTrend[]> {
  try {
    // Use the real backend API endpoint
    const response = await fetch("/api/wardrobe/trending-styles", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch trends");
    }

    const data = await response.json();
    
    if (data.success && data.data?.trending_styles) {
      // Convert backend format to frontend format
      return data.data.trending_styles.map((trend: any, index: number) => ({
        id: `trend-${index}`,
        name: trend.name,
        category: trend.category || "General",
        subCategories: trend.related_styles || [],
        season: "All Seasons", // Backend doesn't provide season info
        popularity: trend.popularity / 100, // Convert from 0-100 to 0-1
        description: trend.description,
        keyItems: trend.key_items || [],
        createdAt: new Date(trend.last_updated || Date.now()),
        updatedAt: new Date(trend.last_updated || Date.now()),
        gender: "Unisex",
        priceRange: "Mid-Range",
        sustainability: true,
        culturalInfluence: trend.category,
        colorPalette: trend.colors || [],
        fabricTypes: [],
        imageUrl: "", // Backend doesn't provide images
      }));
    }
    
    throw new Error("Invalid response format");
  } catch (error) {
    console.error("Error fetching trends:", error);
    // Fallback to local trends if API fails
    return getLocalTrends();
  }
}

// Local trends fallback
function getLocalTrends(): FashionTrend[] {
  return [
    {
      id: "1",
      name: "Minimal Luxe",
      category: "Minimalist",
      subCategories: ["Outerwear", "Monochromatic", "Loafers"],
      season: "Spring",
      popularity: 0.85,
      description: "Clean lines, neutral colors, and high-quality materials",
      keyItems: ["Tailored Blazer", "Silk Shirt", "Straight-leg Pants"],
      createdAt: new Date(),
      updatedAt: new Date(),
      gender: "Unisex",
      priceRange: "Luxury",
      sustainability: true,
      culturalInfluence: "Scandinavian",
      colorPalette: ["Beige", "White", "Gray", "Black"],
      fabricTypes: ["Silk", "Wool", "Cashmere"],
      imageUrl: "",
    },
    {
      id: "2",
      name: "Gorpcore",
      category: "Streetwear",
      subCategories: ["Outerwear", "Cargo", "Sneakers"],
      season: "Fall",
      popularity: 0.75,
      description: "Outdoor-inspired technical wear meets street style",
      keyItems: ["Hiking Boots", "Technical Vest", "Cargo Pants"],
      createdAt: new Date(),
      updatedAt: new Date(),
      gender: "Unisex",
      priceRange: "Mid-Range",
      sustainability: false,
      culturalInfluence: "American",
      colorPalette: ["Olive", "Black", "Orange", "Navy"],
      fabricTypes: ["Nylon", "Gore-Tex", "Polyester"],
      imageUrl: "",
    },
    // Add more local trends...
  ];
}

// Trend Analytics
export async function analyzeTrends(trends: FashionTrend[]): Promise<TrendAnalytics[]> {
  const openai = new OpenAI({
    apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
  });

  try {
    const prompt = `Analyze these fashion trends and provide analytics:
    ${JSON.stringify(trends, null, 2)}
    
    For each trend, provide:
    1. Adoption rate (0-1)
    2. User engagement score (0-1)
    3. Seasonal relevance (0-1)
    4. Predicted lifespan in months
    
    Return as JSON array of TrendAnalytics.`;

    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.7,
      max_tokens: 1000,
    });

    const content = response.choices[0].message.content;
    if (!content) throw new Error("No response from OpenAI");

    return JSON.parse(content) as TrendAnalytics[];
  } catch (error) {
    console.error("Error analyzing trends:", error);
    return trends.map(trend => ({
      trendId: trend.id,
      trendName: trend.name,
      adoptionRate: trend.popularity,
      userEngagement: 0.5,
      seasonalRelevance: 0.5,
      predictedLifespan: 6,
      lastUpdated: new Date(),
    }));
  }
}

// Trend Recommendation Engine
export async function recommendTrends(
  userProfile: UserProfile,
  wardrobe: ClothingItem[],
  currentTrends: FashionTrend[]
): Promise<FashionTrend[]> {
  const openai = new OpenAI({
    apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
  });

  try {
    const prompt = `Recommend fashion trends for this user:
    User Profile: ${JSON.stringify(userProfile, null, 2)}
    Wardrobe: ${JSON.stringify(wardrobe, null, 2)}
    Current Trends: ${JSON.stringify(currentTrends, null, 2)}
    
    Consider:
    1. User's style preferences
    2. Existing wardrobe items
    3. Current trends
    4. Seasonal relevance
    5. User's body type and skin tone
    
    Return top 5 recommended trends as JSON array.`;

    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.7,
      max_tokens: 1000,
    });

    const content = response.choices[0].message.content;
    if (!content) throw new Error("No response from OpenAI");

    return JSON.parse(content) as FashionTrend[];
  } catch (error) {
    console.error("Error recommending trends:", error);
    // Fallback to basic recommendation based on user preferences
    return currentTrends
      .filter(trend => 
        userProfile.stylePreferences.some((pref: string) => 
          trend.category.toLowerCase().includes(pref.toLowerCase())
        )
      )
      .slice(0, 5);
  }
}

// Trend Cache Management
const TREND_CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours

interface CachedTrends {
  trends: FashionTrend[];
  analytics: TrendAnalytics[];
  timestamp: number;
}

let trendCache: CachedTrends | null = null;

export async function getTrendsWithAnalytics(): Promise<{
  trends: FashionTrend[];
  analytics: TrendAnalytics[];
}> {
  if (
    trendCache &&
    Date.now() - trendCache.timestamp < TREND_CACHE_DURATION
  ) {
    return trendCache;
  }

  const trends = await fetchTrendingStyles();
  const analytics = await analyzeTrends(trends);

  trendCache = {
    trends,
    analytics,
    timestamp: Date.now(),
  };

  return trendCache;
}

// Trend Utility Functions
export function getTrendByCategory(
  trends: FashionTrend[],
  category: TrendCategory
): FashionTrend[] {
  return trends.filter(trend => trend.category === category);
}

export function getTrendsBySeason(
  trends: FashionTrend[],
  season: string
): FashionTrend[] {
  return trends.filter(trend => trend.season === season);
}

export function getTrendsByPopularity(
  trends: FashionTrend[],
  minPopularity: number = 0.5
): FashionTrend[] {
  return trends.filter(trend => trend.popularity >= minPopularity);
}

export function getTrendsByEngagement(
  analytics: TrendAnalytics[],
  minEngagement: number = 0.5
): TrendAnalytics[] {
  return analytics.filter(analytics => analytics.userEngagement >= minEngagement);
}

// Add new utility functions for filtering
export function filterTrends(trends: FashionTrend[], filter: TrendFilter): FashionTrend[] {
  return trends.filter(trend => {
    if (filter.category && trend.category !== filter.category) return false;
    if (filter.subCategory && !trend.subCategories.includes(filter.subCategory)) return false;
    if (filter.season && trend.season !== filter.season) return false;
    if (filter.minPopularity && trend.popularity < filter.minPopularity) return false;
    if (filter.gender && trend.gender !== filter.gender) return false;
    if (filter.priceRange && trend.priceRange !== filter.priceRange) return false;
    if (filter.sustainability !== undefined && trend.sustainability !== filter.sustainability) return false;
    return true;
  });
} 