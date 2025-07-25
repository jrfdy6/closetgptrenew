import {
  // Schemas
  ClothingItemSchema,
  OutfitSchema,
  OutfitGeneratedOutfitSchema,
  OpenAIClothingAnalysisSchema,
  UserProfileSchema,
  // Other schemas
  ColorSchema,
  VisualAttributesSchema,
  ItemMetadataSchema,
  BasicMetadataSchema,
  ColorAnalysisSchema,
  MetadataSchema,
  // Enums
  SeasonEnum,
  StyleTagEnum,
  ClothingTypeEnum
} from '../types';

// Infer types from schemas
export type ClothingItem = typeof ClothingItemSchema._type;
export type Outfit = typeof OutfitSchema._type;
export type OutfitGeneratedOutfit = typeof OutfitGeneratedOutfitSchema._type;
export type OpenAIClothingAnalysis = typeof OpenAIClothingAnalysisSchema._type;
export type UserProfile = typeof UserProfileSchema._type;
export type Color = typeof ColorSchema._type;
export type VisualAttributes = typeof VisualAttributesSchema._type;
export type ItemMetadata = typeof ItemMetadataSchema._type;
export type BasicMetadata = typeof BasicMetadataSchema._type;
export type ColorAnalysis = typeof ColorAnalysisSchema._type;
export type Metadata = typeof MetadataSchema._type;

// Re-export schemas and enums
export {
  // Schemas
  ClothingItemSchema,
  OutfitSchema,
  OutfitGeneratedOutfitSchema,
  OpenAIClothingAnalysisSchema,
  UserProfileSchema,
  ColorSchema,
  VisualAttributesSchema,
  ItemMetadataSchema,
  BasicMetadataSchema,
  ColorAnalysisSchema,
  MetadataSchema,
  // Enums
  SeasonEnum,
  StyleTagEnum,
  ClothingTypeEnum
};

// Export validation functions
export const validateClothingItem = (item: unknown): ClothingItem => {
  return ClothingItemSchema.parse(item);
};

export const validateClothingItems = (items: unknown[]): ClothingItem[] => {
  return items.map(item => ClothingItemSchema.parse(item));
};

export const validateUserProfile = (profile: unknown): UserProfile => {
  return UserProfileSchema.parse(profile);
}; 