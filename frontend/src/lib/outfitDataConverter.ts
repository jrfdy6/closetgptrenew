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
  
  // DEBUG: Track metadata for collared shirts
  if ((item.name || '').toLowerCase().includes('george') || 
      (item.name || '').toLowerCase().includes('tommy') ||
      (item.name || '').toLowerCase().includes('van heusen') ||
      (item.name || '').toLowerCase().includes('michael kors')) {
    console.log(`🔍 FRONTEND CONVERTER INPUT: ${item.name}`, {
      hasMetadata: !!item.metadata,
      metadataType: typeof item.metadata,
      visualAttributes: item.metadata?.visualAttributes || null,
      neckline: item.metadata?.visualAttributes?.neckline || 'NONE',
      metadataKeys: item.metadata ? Object.keys(item.metadata) : []
    });
  }
  
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
    // Preserve existing metadata if it exists, otherwise create basic structure
    metadata: item.metadata ? {
      // Preserve existing metadata fields
      ...item.metadata,
      // Ensure critical fields exist
      analysisTimestamp: item.metadata.analysisTimestamp || now,
      styleTags: item.metadata.styleTags || normalizeToList(item.style) || [],
      occasionTags: item.metadata.occasionTags || normalizeToList(item.occasion) || ['casual'],
    } : {
      // Create basic metadata if none exists
      analysisTimestamp: now,
      originalType: item.type,
      originalSubType: null,
      styleTags: normalizeToList(item.style) || [],
      occasionTags: normalizeToList(item.occasion) || ['casual'],
      brand: item.brand || null,
      imageHash: null,
      colorAnalysis: {
        dominant: [],
        matching: []
      },
      basicMetadata: null,
      visualAttributes: null,
      itemMetadata: null,
      naturalDescription: null,
      temperatureCompatibility: null,
      materialCompatibility: null,
      bodyTypeCompatibility: null,
      skinToneCompatibility: null,
      outfitScoring: null
    }
  };
  
  // DEBUG: Verify metadata after conversion
  if ((item.name || '').toLowerCase().includes('george') || 
      (item.name || '').toLowerCase().includes('tommy') ||
      (item.name || '').toLowerCase().includes('van heusen') ||
      (item.name || '').toLowerCase().includes('michael kors')) {
    console.log(`✅ FRONTEND CONVERTED: ${item.name}`, {
      hasMetadata: !!converted.metadata,
      metadataType: typeof converted.metadata,
      visualAttributes: converted.metadata?.visualAttributes || null,
      neckline: converted.metadata?.visualAttributes?.neckline || 'NONE',
      metadataKeys: converted.metadata ? Object.keys(converted.metadata) : []
    });
  }
  
  return converted;
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
/**
 * Normalize weather condition to match backend enum
 */
function normalizeWeatherCondition(condition: string): string {
  const conditionMap: Record<string, string> = {
    // OpenWeatherMap API conditions → Backend enum
    'Clouds': 'Cloudy',
    'Clear': 'Clear',
    'Rain': 'Rainy',
    'Drizzle': 'Rainy',
    'Snow': 'Snowy',
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
  
  return conditionMap[condition] || 'Clear';
}

function convertWeatherData(weather: FrontendWeatherData): any {
  return {
    temperature: weather.temperature,
    condition: normalizeWeatherCondition(weather.condition),
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
    console.warn('⚠️ Wardrobe is empty - outfit generation may use fallback items');
    // Allow empty wardrobe - let backend handle gracefully
  }
  
  console.log('✅ Converted data validation passed');
  return true;
}
