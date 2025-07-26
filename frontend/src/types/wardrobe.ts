import { z } from 'zod';
import {
  ClothingItemSchema,
  UserProfileSchema,
  OpenAIClothingAnalysisSchema
} from '../shared/types';
import type {
  ClothingItem,
  UserProfile,
  OpenAIClothingAnalysis
} from '../shared/types';
import { ApiResponse } from './api';

// Stub schemas and types
export const OutfitSchema = { parse: (data: any) => data };
export const OutfitGeneratedOutfitSchema = { parse: (data: any) => data };
export const ClothingTypeEnum = { parse: (data: any) => data };

// Stub validation functions
export const validateClothingItem = (item: any) => item;
export const validateClothingItems = (items: any[]) => items;
export const validateUserProfile = (profile: any) => profile;

// Stub types
export type Outfit = any;
export type OutfitGeneratedOutfit = any;
export type Color = any;
export type Metadata = any;
export type ColorAnalysis = any;

// Define ClothingType locally
export type ClothingType = string;

// Re-export types from shared types
export type {
  ClothingItem,
  UserProfile,
  OpenAIClothingAnalysis
} from '../shared/types';

// Additional types for the frontend
export type ProcessImagesResult = {
  success: boolean;
  data?: {
    newItems: ClothingItem[];
    totalProcessed: number;
    successfulUploads: number;
  };
  error?: string;
};

export type ProcessImagesResponse = ApiResponse<{
  newItems: ClothingItem[];
  totalProcessed: number;
  successfulUploads: number;
}>;

export type WardrobeItemResponse = ApiResponse<ClothingItem>;
export type WardrobeItemsResponse = ApiResponse<ClothingItem[]>;
export type ImageAnalysisResult = OpenAIClothingAnalysis;
export type ImageAnalysisResponse = ApiResponse<ImageAnalysisResult>;
export type SuccessResponse<T> = {
  success: true;
  data: T;
};
export type ErrorResponse = {
  success: false;
  error: string;
  data: null;
};

// Helper functions
export const isSuccessResponse = <T>(response: ApiResponse<T>): response is SuccessResponse<T> => {
  return response.success === true;
};

export const isErrorResponse = <T>(response: ApiResponse<T>): response is ErrorResponse => {
  return response.success === false;
};

export type Season = 'spring' | 'summer' | 'fall' | 'winter';

export type TemperatureRange = 'very_cold' | 'cold' | 'cool' | 'mild' | 'warm' | 'hot' | 'very_hot';
export type Material = 'cotton' | 'wool' | 'silk' | 'linen' | 'denim' | 'leather' | 'synthetic' | 'knit' | 'fleece' | 'other';
export type BodyType = 'hourglass' | 'pear' | 'apple' | 'rectangle' | 'inverted_triangle';
export type SkinTone = 'warm' | 'cool' | 'neutral';

export interface TemperatureCompatibility {
  minTemp: number;
  maxTemp: number;
  recommendedLayers: string[];
  materialPreferences: Material[];
}

export interface MaterialCompatibility {
  compatibleMaterials: Material[];
  weatherAppropriate: Record<string, Material[]>;
}

export interface BodyTypeCompatibility {
  recommendedFits: Record<BodyType, string[]>;
  styleRecommendations: Record<BodyType, string[]>;
}

export interface SkinToneCompatibility {
  compatibleColors: Record<SkinTone, string[]>;
  recommendedPalettes: Record<SkinTone, string[]>;
}

export interface OutfitScoring {
  versatility: number;
  seasonality: number;
  formality: number;
  trendiness: number;
  quality: number;
}

export interface WardrobeItem {
  id: string;
  name: string;
  type: ClothingType;
  color: string;
  season: Season[];
  style: string[];
  tags?: string[];
  imageUrl: string;
  createdAt: number;
  updatedAt: number;
  favorite?: boolean; // Added to match backend implementation
  wearCount?: number; // Wear count tracking
  lastWorn?: number | null; // Last worn timestamp
  occasion?: string[]; // Occasion tags
  metadata?: {
    brand?: string;
    material?: string;
    pattern?: string;
    fit?: string;
    colorAnalysis?: {
      dominant?: string[];
      matching?: string[];
    };
    temperatureCompatibility?: TemperatureCompatibility;
    materialCompatibility?: MaterialCompatibility;
    bodyTypeCompatibility?: BodyTypeCompatibility;
    skinToneCompatibility?: SkinToneCompatibility;
    outfitScoring?: OutfitScoring;
  };
} 