/**
 * Converts frontend outfit generation data to Pydantic-compatible format
 * for the active /api/outfits-existing-data/generate-personalized endpoint
 */

import { generationGarmentMetadata } from './garmentMetadata';
import { generationWeatherProvenance, GenerationWeatherProvenance } from './generationWeather';

export interface FrontendWardrobeItem {
  id: string;
  name: string;
  type: string;
  color: string;
  style?: string | string[];
  occasion?: string | string[];
  season?: string | string[];
  tags?: string[];
  imageUrl?: string;
  brand?: string;
  material?: string;
  fit?: string;
  [key: string]: any;
}

export interface FrontendUserProfile {
  id: string;
  name?: string;
  email?: string;
  gender?: string;
  age?: number;
  height?: string;
  weight?: string;
  bodyType?: string;
  skinTone?: string | null;
  stylePreferences?: string[];
  measurements?: Record<string, unknown>;
  style_preferences?: string[];
  color_preferences?: string[];
  size_preferences?: string[];
  [key: string]: any;
}

export interface FrontendWeatherData extends GenerationWeatherProvenance {
  temperature: number;
  condition: string;
  humidity?: number;
  wind_speed?: number;
  location?: string;
  precipitation?: number;
}

export interface FrontendOutfitRequest {
  occasion: string;
  style: string;
  mood: string;
  weather: FrontendWeatherData;
  wardrobe: FrontendWardrobeItem[];
  user_profile: FrontendUserProfile;
  likedOutfits?: string[];
  trendingStyles?: string[];
  preferences?: Record<string, any>;
  baseItemId?: string;
}

/**
 * Convert frontend wardrobe item to Pydantic-compatible format
 */
function convertWardrobeItem(item: FrontendWardrobeItem, userId: string): any {
  const now = Date.now();
  
  const metadata = generationGarmentMetadata(item);

  const converted = {
    id: item.id,
    name: item.name,
    type: normalizeClothingType(item.type),
    color: item.color || 'unknown',
    season: normalizeToList(item.season) || ['all'],
    imageUrl: item.imageUrl || '',
    tags: normalizeToList(item.tags) || [],
    style: normalizeToList(item.style) || [],
    userId: userId,
    dominantColors: [],
    matchingColors: [],
    occasion: normalizeToList(item.occasion) || ['casual'],
    brand: item.brand || null,
    createdAt: now,
    updatedAt: now,
    wearCount: item.wearCount || 0,
    favorite_score: item.favorite_score || 0.0,
    subType: item.subType || null,
    colorName: item.colorName || null,
    backgroundRemoved: item.backgroundRemoved || null,
    embedding: item.embedding || null,
    // Preserve raw analysis for provenance and merge its visual facts with
    // authoritative root edits before downstream sanitization.
    analysis: item.analysis && typeof item.analysis === 'object' ? item.analysis : null,
    material: Array.isArray(item.material) ? item.material.join(', ') : item.material || null,
    metadata: {
      ...metadata,
      analysisTimestamp: metadata.analysisTimestamp ?? now,
      styleTags: normalizeToList(metadata.styleTags) || [],
      occasionTags: normalizeToList(metadata.occasionTags) || [],
    }
  };
  
  return converted;
}

/**
 * Convert frontend user profile to Pydantic-compatible format
 */
function convertUserProfile(profile: FrontendUserProfile): any {
  return {
    ...profile,
    id: profile.id,
    name: profile.name || 'User',
    email: profile.email || '',
    gender: profile.gender || '',
    age: typeof profile.age === 'number' && Number.isFinite(profile.age)
      && profile.age > 0 && profile.age <= 120 ? profile.age : undefined,
    height: profile.height || '',
    weight: profile.weight || '',
    bodyType: profile.bodyType || '',
    skinTone: profile.skinTone || null,
    stylePreferences: normalizeToList(profile.stylePreferences) || [],
    style_preferences: normalizeToList(profile.style_preferences) || [],
    color_preferences: normalizeToList(profile.color_preferences) || [],
    size_preferences: normalizeToList(profile.size_preferences) || [],
    measurements: profile.measurements || {}
  };
}

/**
 * Convert frontend weather data to Pydantic-compatible format
 */
/**
 * Normalize weather condition to match backend enum
 */
function normalizeWeatherCondition(condition: string): string {
  const conditionMap: Record<string, string> = {
    // OpenWeatherMap API conditions → Backend enum
    'Clouds': 'Cloudy',
    'Partly Cloudy': 'Cloudy',
    'Overcast': 'Overcast',
    'Clear': 'Clear',
    'Rain': 'Rainy',
    'Light Rain': 'Rainy',
    'Heavy Rain': 'Rainy',
    'Drizzle': 'Rainy',
    'Snow': 'Snowy',
    'Light Snow': 'Snowy',
    'Heavy Snow': 'Snowy',
    'Thunderstorm': 'Stormy',
    'Mist': 'Foggy',
    'Fog': 'Foggy',
    'Haze': 'Foggy',
    'Smoke': 'Foggy',
    'Dust': 'Windy',
    'Sand': 'Windy',
    'Ash': 'Windy',
    'Squall': 'Windy',
    'Tornado': 'Stormy',
    // Already normalized conditions
    'Cloudy': 'Cloudy',
    'Rainy': 'Rainy',
    'Snowy': 'Snowy',
    'Stormy': 'Stormy',
    'Foggy': 'Foggy',
    'Windy': 'Windy',
    'Sunny': 'Clear'
  };
  
  // Unknown labels are not evidence of clear skies. Keep the original label
  // separately while limiting the scorer to supported condition categories.
  const match = Object.entries(conditionMap).find(([label]) => label.toLowerCase() === condition?.trim().toLowerCase());
  return match?.[1] || 'Unknown';
}

function convertWeatherData(weather: FrontendWeatherData): any {
  return {
    ...generationWeatherProvenance(weather),
    temperature: weather.temperature,
    condition: normalizeWeatherCondition(weather.condition),
    rawCondition: weather.rawCondition || weather.condition,
    humidity: weather.humidity || 0,
    wind_speed: weather.wind_speed || 0,
    location: weather.location || 'Unknown',
    precipitation: weather.precipitation || 0
  };
}

/**
 * Normalize clothing type to backend enum format (UPPERCASE_WITH_UNDERSCORES)
 */
function normalizeClothingType(type: string): string {
  // Backend expects: T_SHIRT, SHIRT, PANTS, SHOES, etc.
  const typeMap: Record<string, string> = {
    // Tops
    't-shirt': 'T_SHIRT',
    'tshirt': 'T_SHIRT',
    't shirt': 'T_SHIRT',
    'shirt': 'SHIRT',
    'blouse': 'BLOUSE',
    'sweater': 'SWEATER',
    'tank': 'TANK_TOP',
    'tank top': 'TANK_TOP',
    'tank_top': 'TANK_TOP',
    // Outerwear
    'jacket': 'JACKET',
    'blazer': 'BLAZER',
    'coat': 'COAT',
    'vest': 'VEST',
    // Bottoms
    'pants': 'PANTS',
    'jeans': 'JEANS',
    'shorts': 'SHORTS',
    'skirt': 'SKIRT',
    'trousers': 'PANTS',
    // Dresses
    'dress': 'DRESS',
    'jumpsuit': 'JUMPSUIT',
    // Shoes
    'shoes': 'SHOES',
    'sneakers': 'SNEAKERS',
    'boots': 'BOOTS',
    'sandals': 'SANDALS',
    'heels': 'HEELS',
    'loafers': 'LOAFERS',
    'oxfords': 'OXFORDS',
    // Accessories
    'accessory': 'ACCESSORY',
    'belt': 'BELT',
    'hat': 'HAT',
    'scarf': 'SCARF',
    'tie': 'TIE',
    'bag': 'BAG',
    'jewelry': 'JEWELRY',
    'watch': 'WATCH',
    'sunglasses': 'SUNGLASSES',
    // Fallback
    'other': 'OTHER'
  };
  
  // Normalize input: lowercase, replace spaces/hyphens with underscores
  const normalized = type.toLowerCase().trim().replace(/[\s-]+/g, '_');
  
  // Try exact match first
  if (typeMap[normalized]) {
    return typeMap[normalized];
  }
  
  // Try without underscores (e.g., "t_shirt" → "tshirt")
  const noUnderscore = normalized.replace(/_/g, '');
  if (typeMap[noUnderscore]) {
    return typeMap[noUnderscore];
  }
  
  // Try with hyphen instead (e.g., "t shirt" → "t-shirt")
  const withHyphen = normalized.replace(/_/g, '-');
  if (typeMap[withHyphen]) {
    return typeMap[withHyphen];
  }
  
  // Fallback: return as uppercase with underscores
  return 'OTHER';
}

/**
 * Normalize value to list format
 */
function normalizeToList(value: any): string[] {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  if (typeof value === 'string') return [value];
  return [];
}

/**
 * Main converter function - converts frontend data to Pydantic-compatible format
 */
export function convertToPydanticShape(frontendData: FrontendOutfitRequest): any {
  console.log('🔄 Converting frontend data to Pydantic format:', frontendData);
  console.log('🚨 CONVERTER INPUT: baseItemId =', frontendData.baseItemId);
  console.log('🚨 CONVERTER INPUT: baseItemId type =', typeof frontendData.baseItemId);
  
  try {
    const converted = {
      occasion: frontendData.occasion,
      weather: convertWeatherData(frontendData.weather),
      wardrobe: frontendData.wardrobe.map(item => 
        convertWardrobeItem(item, frontendData.user_profile.id)
      ),
      user_profile: convertUserProfile(frontendData.user_profile),
      likedOutfits: frontendData.likedOutfits || [],
      trendingStyles: frontendData.trendingStyles || [],
      preferences: frontendData.preferences || null,
      outfitHistory: null,
      randomSeed: null,
      season: null,
      style: frontendData.style,
      mood: frontendData.mood,
      baseItem: null,
      baseItemId: frontendData.baseItemId || null
    };
    
    console.log('🚨 CONVERTER OUTPUT: baseItemId =', converted.baseItemId);
    console.log('✅ Successfully converted to Pydantic format:', converted);
    return converted;
    
  } catch (error) {
    console.error('❌ Failed to convert frontend data:', error);
    throw new Error(`Data conversion failed: ${error}`);
  }
}

/**
 * Validate that the converted data has all required fields
 */
export function validateConvertedData(convertedData: any): boolean {
  const requiredFields = ['occasion', 'weather', 'wardrobe', 'user_profile'];
  
  for (const field of requiredFields) {
    if (!convertedData[field]) {
      console.error(`❌ Missing required field: ${field}`);
      return false;
    }
  }
  
  if (!convertedData.wardrobe.length) {
    console.warn('⚠️ Wardrobe is empty - outfit generation may use fallback items');
    // Allow empty wardrobe - let backend handle gracefully
  }
  
  console.log('✅ Converted data validation passed');
  return true;
}
