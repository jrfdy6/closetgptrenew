import { ClothingItem } from './wardrobe';

// Base API Response type
export type ApiResponse<T> = {
  success: boolean;
  data: T | null;
  error?: string;
  message?: string;
};

// Error types
export type AppError = {
  code: string;
  message: string;
  details?: unknown;
};

// Process Images Response types
export type ProcessImagesResult = {
  newItems: ClothingItem[];
  duplicates: string[];
  similarImages: Array<{
    file: File;
    existingItem: ClothingItem;
    similarity: number;
  }>;
};

export type ProcessImagesResponse = ApiResponse<ProcessImagesResult>;

// Wardrobe Item Response types
export type WardrobeItemResponse = ApiResponse<ClothingItem>;
export type WardrobeItemsResponse = ApiResponse<ClothingItem[]>;

// Image Analysis Response types
export type ImageAnalysisResult = {
  name: string;
  type: string;
  color: string;
  seasons: string[];
  tags: string[];
  occasion: string[];
};

export type ImageAnalysisResponse = ApiResponse<ImageAnalysisResult>;

// Response helper types
export type SuccessResponse<T> = {
  success: true;
  data: T;
  message?: string;
  error?: never;
};

export type ErrorResponse = {
  success: false;
  data: null;
  error: string;
  message?: never;
};

// Type guard functions
export function isSuccessResponse<T>(response: ApiResponse<T>): response is SuccessResponse<T> {
  return response.success === true && response.data !== null;
}

export function isErrorResponse<T>(response: ApiResponse<T>): response is ErrorResponse {
  return response.success === false && response.error !== undefined;
} 