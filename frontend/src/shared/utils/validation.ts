import { z } from "zod";
import { ClothingItem, ClothingItemSchema, OpenAIClothingAnalysis, OpenAIClothingAnalysisSchema, ClothingTypeEnum, BasicMetadata, ColorAnalysis, OutfitSchema, UserProfileSchema, type Outfit, type UserProfile, type AppError, SuccessResponse, ErrorResponse } from '@shared/types';
import unidecode from 'unidecode';

// Maximum lengths for strings
const MAX_TYPE_LENGTH = 32;
const MAX_SUBTYPE_LENGTH = 64;

// Get the enum values as a const array
const CLOTHING_TYPE_VALUES = ClothingTypeEnum.options;

// Type for the clothing type mappings
type ClothingTypeMapping = {
  [K in z.infer<typeof ClothingTypeEnum>]: readonly string[];
};

// Canonical type mappings with synonyms
const TYPE_MAPPINGS: ClothingTypeMapping = {
  shirt: ['t-shirt', 'tee', 'tshirt', 'tee shirt', 'v neck', 'v-neck', 'vneck', 'tank top', 'polo'],
  dress_shirt: ['button down', 'button-up', 'oxford', 'formal shirt', 'dress shirt'],
  pants: ['jeans', 'trousers', 'slacks', 'chinos', 'khakis', 'leggings', 'joggers'],
  shorts: ['short pants', 'athletic shorts', 'basketball shorts', 'running shorts', 'cargo shorts'],
  skirt: ['mini skirt', 'maxi skirt', 'pleated', 'a-line'],
  dress: ['gown', 'frock', 'sundress', 'cocktail dress', 'maxi', 'mini'],
  jacket: ['denim', 'blazer', 'bomber', 'parka', 'windbreaker', 'coat', 'raincoat'],
  sweater: ['sweatshirt', 'hoodie', 'cardigan', 'pullover', 'jumper'],
  shoes: ['boots', 'heels', 'flats', 'pumps'],
  dress_shoes: ['oxfords', 'derby', 'wingtip', 'monk strap', 'formal shoes'],
  loafers: ['slip-ons', 'penny loafers', 'tassel loafers'],
  sneakers: ['trainers', 'athletic shoes', 'running shoes', 'kicks'],
  accessory: ['bag', 'purse', 'scarf', 'hat', 'jewelry', 'watch'],
  other: []
} as const;

// Helper function to normalize strings
export const normalizeString = (input: string | null | undefined): string => {
  if (!input) return '';
  
  // Convert to lowercase and normalize unicode
  let normalized = unidecode(input.toLowerCase().trim());
  
  // Remove special characters but keep spaces and hyphens
  normalized = normalized.replace(/[^a-z0-9\s-]/g, '');
  
  // Collapse multiple spaces and hyphens
  normalized = normalized.replace(/[\s-]+/g, ' ');
  
  return normalized;
};

// Helper function to find the closest match using Levenshtein distance
const findClosestMatch = (input: string, options: string[]): string | null => {
  if (!input || !options.length) return null;
  
  const normalizedInput = normalizeString(input);
  let bestMatch = null;
  let bestScore = 0.8; // Minimum similarity threshold
  
  for (const option of options) {
    const normalizedOption = normalizeString(option);
    const score = calculateSimilarity(normalizedInput, normalizedOption);
    
    if (score > bestScore) {
      bestScore = score;
      bestMatch = option;
    }
  }
  
  return bestMatch;
};

// Levenshtein distance calculation
const calculateSimilarity = (str1: string, str2: string): number => {
  const track = Array(str2.length + 1).fill(null).map(() =>
    Array(str1.length + 1).fill(null));
  
  for (let i = 0; i <= str1.length; i += 1) {
    track[0][i] = i;
  }
  for (let j = 0; j <= str2.length; j += 1) {
    track[j][0] = j;
  }

  for (let j = 1; j <= str2.length; j += 1) {
    for (let i = 1; i <= str1.length; i += 1) {
      const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
      track[j][i] = Math.min(
        track[j][i - 1] + 1,
        track[j - 1][i] + 1,
        track[j - 1][i - 1] + indicator
      );
    }
  }

  const maxLength = Math.max(str1.length, str2.length);
  return 1 - (track[str2.length][str1.length] / maxLength);
};

// Normalize clothing type
export const normalizeClothingType = (type: string | null | undefined): z.infer<typeof ClothingTypeEnum> => {
  if (!type) return 'other';
  
  const normalized = normalizeString(type);
  if (!normalized) return 'other';
  
  // Check direct matches first
  if (CLOTHING_TYPE_VALUES.includes(normalized as z.infer<typeof ClothingTypeEnum>)) {
    return normalized as z.infer<typeof ClothingTypeEnum>;
  }
  
  // Check all synonyms
  for (const [canonicalType, synonyms] of Object.entries(TYPE_MAPPINGS)) {
    if (synonyms.includes(normalized)) {
      return canonicalType as z.infer<typeof ClothingTypeEnum>;
    }
  }
  
  // Try fuzzy matching
  const allOptions = [...CLOTHING_TYPE_VALUES, ...Object.values(TYPE_MAPPINGS).flat()];
  const match = findClosestMatch(normalized, allOptions);
  
  if (match) {
    // Find the canonical type for the matched synonym
    for (const [canonicalType, synonyms] of Object.entries(TYPE_MAPPINGS)) {
      if (synonyms.includes(match)) {
        return canonicalType as z.infer<typeof ClothingTypeEnum>;
      }
    }
    // If match is a canonical type
    if (CLOTHING_TYPE_VALUES.includes(match as z.infer<typeof ClothingTypeEnum>)) {
      return match as z.infer<typeof ClothingTypeEnum>;
    }
  }
  
  return 'other';
};

// Normalize subtype
export const normalizeSubType = (type: string | null | undefined, subType: string | null | undefined): string | null => {
  if (!subType) return null;
  
  const normalized = normalizeString(subType);
  if (!normalized) return null;
  
  // If the subtype is actually a type, return null
  if (CLOTHING_TYPE_VALUES.includes(normalized as z.infer<typeof ClothingTypeEnum>)) {
    return null;
  }
  
  // Check if the subtype is a synonym of the main type
  if (type && TYPE_MAPPINGS[type as keyof typeof TYPE_MAPPINGS]?.includes(normalized)) {
    return null;
  }
  
  return normalized.slice(0, MAX_SUBTYPE_LENGTH);
};

// Main validation function
export const validateClothingItem = (item: unknown): ClothingItem => {
  // First normalize the type and subtype
  const normalizedItem = {
    ...(item as Record<string, unknown>),
    type: normalizeClothingType((item as any)?.type),
    subType: normalizeSubType((item as any)?.type, (item as any)?.subType)
  };
  
  // Then validate against the schema
  return ClothingItemSchema.parse(normalizedItem);
};

export function validateClothingItems(items: Partial<ClothingItem>[]): ClothingItem[] {
  try {
    // First normalize all items
    const normalizedItems = items.map(item => ({
      ...item,
      type: normalizeClothingType(item.type),
      subType: normalizeSubType(item.type, item.subType)
    }));
    
    // Then validate against the schema
    return z.array(ClothingItemSchema).parse(normalizedItems);
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error('Validation error:', error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', '));
    }
    throw error;
  }
}

export const validateOpenAIAnalysis = (analysis: unknown): OpenAIClothingAnalysis => {
  return OpenAIClothingAnalysisSchema.parse(analysis);
};

export function validateOutfit(outfit: unknown): Outfit {
  return OutfitSchema.parse(outfit);
}

export function validateUserProfile(profile: unknown): UserProfile {
  return UserProfileSchema.parse(profile);
}

// API Response helpers
export function createSuccessResponse<T>(data: { data: T; message?: string }): SuccessResponse<T> {
  return {
    success: true,
    data: data.data,
    message: data.message
  };
}

export function createErrorResponse(error: { code: string; message: string; details?: unknown }): ErrorResponse {
  return {
    success: false,
    data: null,
    error: `${error.code}: ${error.message}${error.details ? ` - ${JSON.stringify(error.details)}` : ''}`
  };
}

// Conversion functions
export function convertOpenAIAnalysisToClothingItem(
  analysis: OpenAIClothingAnalysis,
  userId: string,
  imageUrl: string
): Omit<ClothingItem, 'id'> {
  const basicMetadata = analysis.metadata?.basicMetadata ? {
    width: analysis.metadata.basicMetadata.width,
    height: analysis.metadata.basicMetadata.height,
    orientation: analysis.metadata.basicMetadata.orientation,
    dateTaken: analysis.metadata.basicMetadata.dateTaken,
    deviceModel: analysis.metadata.basicMetadata.deviceModel,
    gps: analysis.metadata.basicMetadata.gps,
    flashUsed: analysis.metadata.basicMetadata.flashUsed,
    imageHash: null
  } : undefined;

  const colorAnalysis: ColorAnalysis = {
    dominant: analysis.dominantColors,
    matching: analysis.matchingColors
  };

  return {
    name: analysis.type,
    type: normalizeClothingType(analysis.type),
    subType: normalizeSubType(analysis.type, analysis.subType),
    color: analysis.dominantColors[0]?.name || 'unknown',
    season: analysis.season,
    imageUrl,
    tags: [],
    style: analysis.style,
    userId,
    dominantColors: analysis.dominantColors,
    matchingColors: analysis.matchingColors,
    occasion: analysis.occasion,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    brand: analysis.brand,
    metadata: {
      originalType: analysis.type,
      analysisTimestamp: Date.now(),
      basicMetadata,
      colorAnalysis,
      naturalDescription: null
    }
  };
}

// Validation error helpers
export function isValidationError(error: unknown): error is z.ZodError {
  return error instanceof z.ZodError;
}

export function formatValidationError(error: z.ZodError): { code: string; message: string; details: unknown } {
  return {
    code: 'VALIDATION_ERROR',
    message: 'Invalid data format',
    details: error.errors.map(e => ({
      path: e.path.join('.'),
      message: e.message
    }))
  };
}

// Type guard
export const isClothingItem = (item: unknown): item is ClothingItem => {
  try {
    validateClothingItem(item);
    return true;
  } catch {
    return false;
  }
}; 