import { 
  ALLOWED_STYLE_TYPES, 
  STYLE_TYPE_MAPPING, 
  CLOTHING_TYPES, 
  TYPE_MAPPING,
  ClothingType
} from '../constants';
import { ClothingItem as SharedClothingItem, ClothingItemSchema, Season, StyleTag } from '@shared/types';
import { validateClothingItem as validateSharedClothingItem, normalizeClothingType as normalizeSharedClothingType, normalizeSubType as normalizeSharedSubType } from '@shared/utils/validation';

export type ClothingItem = SharedClothingItem;

export function normalizeStyleTags(styles: string[]): StyleTag[] {
  return styles
    .map(style => {
      // Map to normalized style if in mapping
      const normalizedStyle = STYLE_TYPE_MAPPING[style] || style;
      // Only include if it's a valid style tag
      return ALLOWED_STYLE_TYPES.includes(normalizedStyle as StyleTag) 
        ? normalizedStyle as StyleTag 
        : null;
    })
    .filter((style): style is StyleTag => style !== null);
}

export function normalizeClothingType(type: string): ClothingType {
  return TYPE_MAPPING[type] || CLOTHING_TYPES.OTHER;
}

export function normalizeSubType(subType: string | undefined | null): string | undefined {
  if (!subType) return undefined;
  // Remove special characters and normalize
  return subType
    .split('')
    .filter(c => /[a-zA-Z0-9\s-]/.test(c))
    .join('')
    .trim();
}

export function validateClothingItem(item: ClothingItem): {
  isValid: boolean;
  errors: string[];
  normalizedItem: ClothingItem;
} {
  const errors: string[] = [];
  const normalizedItem = { ...item };

  // Validate and normalize type
  normalizedItem.type = normalizeClothingType(item.type);

  // Validate and normalize subType
  normalizedItem.subType = normalizeSubType(item.subType);

  // Validate and normalize style tags
  normalizedItem.style = normalizeStyleTags(item.style);

  // Validate required fields
  if (!item.name?.trim()) errors.push("Name is required");
  if (!item.color?.trim()) errors.push("Color is required");
  if (!item.imageUrl?.trim()) errors.push("Image URL is required");
  if (!item.season || item.season.length === 0) errors.push("At least one season is required");

  // Validate season values
  const validSeasons = ["spring", "summer", "fall", "winter"] as const;
  const invalidSeasons = item.season.filter(s => !validSeasons.includes(s.toLowerCase().trim() as Season));
  if (invalidSeasons.length > 0) {
    errors.push(`Invalid seasons: ${invalidSeasons.join(", ")}`);
    normalizedItem.season = item.season
      .map(s => s.toLowerCase().trim() as Season)
      .filter(s => validSeasons.includes(s));
  }

  // Validate image URL format
  try {
    new URL(item.imageUrl.trim());
  } catch {
    errors.push("Invalid image URL format");
  }

  return {
    isValid: errors.length === 0,
    errors,
    normalizedItem
  };
}

export function getFilteringFeedback(
  totalItems: number,
  filteredItems: number,
  filteringInfo: {
    season_mismatch: number;
    style_mismatch: number;
    invalid_style_tags: number;
  },
  warnings: string[]
): string[] {
  const feedback: string[] = [];

  // Add warnings
  feedback.push(...warnings);

  // Add filtering statistics
  if (filteredItems < totalItems) {
    feedback.push(
      `⚠️ Only ${filteredItems} of your ${totalItems} wardrobe items are suitable for the current conditions.`
    );
  }

  if (filteringInfo.season_mismatch > 0) {
    feedback.push(
      `🌡️ ${filteringInfo.season_mismatch} items were filtered out due to season mismatch.`
    );
  }

  if (filteringInfo.style_mismatch > 0) {
    feedback.push(
      `👔 ${filteringInfo.style_mismatch} items were filtered out due to style mismatch.`
    );
  }

  if (filteringInfo.invalid_style_tags > 0) {
    feedback.push(
      `🏷️ ${filteringInfo.invalid_style_tags} items had invalid style tags that were normalized.`
    );
  }

  return feedback;
}

// Type guard for clothing items
export const isClothingItem = (item: unknown): item is ClothingItem => {
  try {
    validateClothingItem(item as ClothingItem);
    return true;
  } catch {
    return false;
  }
}; 