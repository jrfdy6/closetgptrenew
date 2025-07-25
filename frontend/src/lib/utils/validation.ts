import { z } from 'zod';
import {
  ClothingItem,
  ClothingItemSchema,
  OpenAIClothingAnalysis,
  OpenAIClothingAnalysisSchema,
  ApiResponse
} from '../../shared/types/index';

// Validation functions
export const validateClothingItem = (item: unknown): ClothingItem => {
  return ClothingItemSchema.parse(item);
};

export const validateClothingItems = (items: unknown[]): ClothingItem[] => {
  return z.array(ClothingItemSchema).parse(items);
};

export const validateOpenAIAnalysis = (analysis: unknown): OpenAIClothingAnalysis => {
  return OpenAIClothingAnalysisSchema.parse(analysis);
};

// API Response helpers
export const createSuccessResponse = <T>(data: T): ApiResponse<T> => ({
  success: true,
  data
});

export const createErrorResponse = (error: string): ApiResponse<never> => ({
  success: false,
  error
});

// Conversion function
export const convertOpenAIAnalysisToClothingItem = (
  analysis: OpenAIClothingAnalysis,
  userId: string,
  imageUrl: string
): Omit<ClothingItem, 'id'> => {
  const now = Date.now();
  return {
    userId,
    type: analysis.type as ClothingItem['type'],
    subType: analysis.subType,
    name: `${analysis.type}${analysis.subType ? ` - ${analysis.subType}` : ''}`,
    color: analysis.dominantColors[0]?.name || 'unknown',
    season: analysis.season,
    imageUrl,
    tags: analysis.style,
    style: analysis.style,
    dominantColors: analysis.dominantColors,
    matchingColors: analysis.matchingColors,
    occasion: analysis.occasion,
    createdAt: now,
    updatedAt: now,
    brand: analysis.brand,
    colorName: analysis.dominantColors[0]?.name,
    metadata: {
      analysisTimestamp: now,
      originalType: analysis.type,
      originalSubType: analysis.subType,
      styleTags: analysis.style,
      occasionTags: analysis.occasion,
      brand: analysis.brand,
      colorAnalysis: {
        dominant: analysis.dominantColors,
        matching: analysis.matchingColors
      }
    }
  };
};

// API Response validation
export function validateApiResponse<T>(response: unknown): ApiResponse<T> {
  if (typeof response !== "object" || response === null) {
    throw new Error("Invalid API response: expected an object");
  }

  const { success, data, error } = response as ApiResponse<T>;
  
  if (typeof success !== "boolean") {
    throw new Error("Invalid API response: success must be a boolean");
  }

  if (success && data === undefined) {
    throw new Error("Invalid API response: data is required when success is true");
  }

  if (!success && error === undefined) {
    throw new Error("Invalid API response: error is required when success is false");
  }

  return response as ApiResponse<T>;
}

export function validateClothingItemResponse(response: unknown): ApiResponse<ClothingItem> {
  const validatedResponse = validateApiResponse<ClothingItem>(response);
  if (validatedResponse.success && validatedResponse.data) {
    validatedResponse.data = validateClothingItem(validatedResponse.data);
  }
  return validatedResponse;
}

export function validateClothingItemsResponse(response: unknown): ApiResponse<ClothingItem[]> {
  const validatedResponse = validateApiResponse<ClothingItem[]>(response);
  if (validatedResponse.success && validatedResponse.data) {
    validatedResponse.data = validateClothingItems(validatedResponse.data);
  }
  return validatedResponse;
} 