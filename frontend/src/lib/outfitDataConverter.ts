/**
 * Converts frontend outfit generation data to Pydantic-compatible format
 * for the advanced /api/outfit/generate endpoint
 */

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
  style_preferences?: string[];
  color_preferences?: string[];
  size_preferences?: string[];
  [key: string]: any;
}

export interface FrontendWeatherData {
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
  
  return {
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
    wearCount: 0,
    favorite_score: 0.0,
    subType: null,
    colorName: null,
    backgroundRemoved: null,
    embedding: null,
    metadata: {}
  };
}

/**
 * Convert frontend user profile to Pydantic-compatible format
 */
function convertUserProfile(profile: FrontendUserProfile): any {
  return {
    id: profile.id,
    name: profile.name || 'User',
    email: profile.email || '',
    gender: profile.gender || 'male',
    age: profile.age || 25,
    height: profile.height || '',
    weight: profile.weight || '',
    bodyType: profile.bodyType || 'average',
    style_preferences: normalizeToList(profile.style_preferences) || [],
    color_preferences: normalizeToList(profile.color_preferences) || [],
    size_preferences: normalizeToList(profile.size_preferences) || [],
    // Add any other fields that might be needed
    ...profile
  };
}

/**
 * Convert frontend weather data to Pydantic-compatible format
 */
function convertWeatherData(weather: FrontendWeatherData): any {
  return {
    temperature: weather.temperature,
    condition: weather.condition,
    humidity: weather.humidity || 0,
    wind_speed: weather.wind_speed || 0,
    location: weather.location || 'Unknown',
    precipitation: weather.precipitation || 0
  };
}

/**
 * Normalize clothing type to enum-compatible format
 */
function normalizeClothingType(type: string): string {
  const typeMap: Record<string, string> = {
    't-shirt': 'T_SHIRT',
    'tshirt': 'T_SHIRT',
    'shirt': 'SHIRT',
    'blouse': 'BLOUSE',
    'sweater': 'SWEATER',
    'jacket': 'JACKET',
    'blazer': 'BLAZER',
    'pants': 'PANTS',
    'jeans': 'JEANS',
    'shorts': 'SHORTS',
    'skirt': 'SKIRT',
    'dress': 'DRESS',
    'shoes': 'SHOES',
    'sneakers': 'SNEAKERS',
    'boots': 'BOOTS',
    'sandals': 'SANDALS',
    'heels': 'HEELS',
    'accessory': 'ACCESSORY',
    'belt': 'BELT',
    'hat': 'HAT',
    'scarf': 'SCARF',
    'other': 'OTHER'
  };
  
  const normalized = type.toLowerCase().replace(/\s+/g, '_');
  return typeMap[normalized] || 'OTHER';
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
    console.error('❌ Wardrobe is empty');
    return false;
  }
  
  console.log('✅ Converted data validation passed');
  return true;
}
