import { z } from 'zod';
import {
  ClothingItem,
  ClothingItemSchema,
  OpenAIClothingAnalysis,
  OpenAIClothingAnalysisSchema,
  ApiResponse,
  AppError
} from '../frontend/src/types/wardrobe';

// Validation functions
export const validateClothingItem = (data: unknown): ClothingItem => {
  return ClothingItemSchema.parse(data);
};

export const validateClothingItems = (data: unknown): ClothingItem[] => {
  if (!Array.isArray(data)) {
    throw new Error("Expected an array of clothing items");
  }
  return data.map(item => validateClothingItem(item));
};

export const validateApiResponse = <T>(response: unknown): ApiResponse<T> => {
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
};

// API response helpers
export const createSuccessResponse = <T>(data: T): ApiResponse<T> => ({
  success: true,
  data
});

export const createErrorResponse = <T>(error: string): ApiResponse<T> => ({
  success: false,
  error
});

// Error handling
export const createAppError = (code: string, message: string, details?: unknown): AppError => ({
  code,
  message,
  details
});

// Data transformation
export const convertOpenAIAnalysisToClothingItem = (
  analysis: OpenAIClothingAnalysis,
  userId: string,
  imageUrl: string
): Omit<ClothingItem, 'id'> => {
  const now = Date.now();
  return {
    userId,
    name: `${analysis.type}${analysis.subType ? ` - ${analysis.subType}` : ''}`,
    type: analysis.type as ClothingItem['type'],
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
    subType: analysis.subType,
    brand: analysis.brand,
    colorName: analysis.dominantColors[0]?.name
  };
};

// Color utilities
export const hexToRgb = (hex: string): [number, number, number] => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) {
    throw new Error('Invalid hex color');
  }
  return [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16)
  ];
};

export const rgbToHex = (r: number, g: number, b: number): string => {
  return '#' + [r, g, b].map(x => {
    const hex = x.toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  }).join('');
};

// Date utilities
export const formatDate = (timestamp: number): string => {
  return new Date(timestamp).toISOString();
};

// Validation helpers
export const isValidImageUrl = (url: string): boolean => {
  try {
    new URL(url);
    return url.match(/\.(jpeg|jpg|gif|png|webp)$/) !== null;
  } catch {
    return false;
  }
};

export const isValidUserId = (userId: string): boolean => {
  return typeof userId === 'string' && userId.length > 0;
}; 