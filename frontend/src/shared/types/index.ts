import { z } from 'zod';
export { UserProfileSchema, type UserProfile } from './user';
export type { AppError, SuccessResponse, ErrorResponse, ApiResponse } from './responses';

// Canonical values mirror backend/src/custom_types/wardrobe.py.
export const SeasonEnum = z.enum(['spring', 'summer', 'fall', 'winter']);
export const ClothingTypeEnum = z.enum(['shirt', 'dress_shirt', 'pants', 'shorts', 'skirt', 'dress', 'jacket', 'sweater', 'shoes', 'dress_shoes', 'loafers', 'sneakers', 'accessory', 'other', 't-shirt', 'blouse', 'tank_top', 'crop_top', 'polo', 'hoodie', 'cardigan', 'blazer', 'coat', 'vest', 'jeans', 'chinos', 'slacks', 'joggers', 'sweatpants', 'mini_skirt', 'midi_skirt', 'maxi_skirt', 'pencil_skirt', 'sundress', 'cocktail_dress', 'maxi_dress', 'mini_dress', 'boots', 'sandals', 'heels', 'flats', 'hat', 'scarf', 'belt', 'jewelry', 'bag', 'watch']);
export const StyleTagEnum = z.enum(['Casual', 'Formal', 'Sports', 'Trendy', 'Vintage', 'Statement', 'Smart Casual', 'Business', 'Luxury', 'Streetwear', 'Minimalist', 'Bohemian', 'Classic', 'Elegant', 'Athletic', 'Preppy', 'Gothic', 'Punk', 'Hipster', 'Retro']);
export const LayerLevelEnum = z.enum(['base', 'inner', 'middle', 'outer']);
export const WarmthFactorEnum = z.enum(['light', 'medium', 'heavy']);
export const CoreCategoryEnum = z.enum(['top', 'bottom', 'dress', 'outerwear', 'shoes', 'accessory']);

const optionalText = z.string().nullish();
const optionalNumber = z.number().nullish();
const textList = z.union([z.string(), z.array(z.string())]);
const timestamp = z.union([z.number(), z.string(), z.date(), z.object({
  seconds: z.number(), nanoseconds: z.number().optional(),
}).passthrough()]);

// Preserve unknown persisted fields; validation must never silently drop metadata.
export const ColorSchema = z.object({
  name: z.string(), hex: z.string().optional(), rgb: z.array(z.number()).optional(),
}).passthrough();
export const VisualAttributesSchema = z.object({
  material: optionalText, pattern: optionalText, textureStyle: optionalText,
  fabricWeight: optionalText, fit: optionalText, silhouette: optionalText,
  length: optionalText, genderTarget: optionalText, sleeveLength: optionalText,
  neckline: optionalText, wearLayer: optionalText, formalLevel: optionalText,
  hangerPresent: z.boolean().nullish(), backgroundRemoved: z.boolean().nullish(),
  layerLevel: LayerLevelEnum.nullish(), warmthFactor: WarmthFactorEnum.nullish(),
  coreCategory: CoreCategoryEnum.nullish(), canLayer: z.boolean().nullish(),
  maxLayers: optionalNumber,
}).passthrough();
export const ItemMetadataSchema = z.object({
  priceEstimate: optionalText, careInstructions: optionalText, tags: z.array(z.string()).optional(),
}).passthrough();
export const BasicMetadataSchema = z.object({
  width: optionalNumber, height: optionalNumber, orientation: optionalText,
  dateTaken: optionalText, deviceModel: optionalText, gps: optionalText,
  flashUsed: z.boolean().nullish(), imageHash: optionalText,
}).passthrough();
export const ColorAnalysisSchema = z.object({
  dominant: z.array(ColorSchema), matching: z.array(ColorSchema),
}).passthrough();
export const MetadataSchema = z.object({
  analysisTimestamp: optionalNumber, originalType: optionalText, originalSubType: optionalText,
  styleTags: z.array(z.string()).optional(), occasionTags: z.array(z.string()).optional(),
  brand: optionalText, imageHash: optionalText, naturalDescription: optionalText,
  basicMetadata: BasicMetadataSchema.nullish(), visualAttributes: VisualAttributesSchema.nullish(),
  itemMetadata: ItemMetadataSchema.nullish(), colorAnalysis: ColorAnalysisSchema.nullish(),
}).passthrough();

export const ClothingItemSchema = z.object({
  id: z.string().optional(), userId: z.string(), name: z.string(), type: ClothingTypeEnum,
  subType: optionalText, color: z.string(), colorName: optionalText,
  season: textList, imageUrl: z.string().nullish(), tags: z.array(z.string()).default([]),
  style: z.array(z.string()).default([]), occasion: z.array(z.string()).default([]),
  dominantColors: z.array(ColorSchema).default([]), matchingColors: z.array(ColorSchema).default([]),
  createdAt: timestamp.nullish(), updatedAt: timestamp.nullish(), brand: optionalText,
  material: optionalText, embedding: z.array(z.number()).nullish(), metadata: z.record(z.unknown()).nullish(),
}).passthrough();
export const OpenAIClothingAnalysisSchema = z.object({
  type: z.string(), subType: optionalText, season: textList, style: z.array(z.string()),
  dominantColors: z.array(ColorSchema), matchingColors: z.array(ColorSchema), occasion: z.array(z.string()),
  brand: optionalText, pattern: optionalText, material: optionalText, fit: optionalText,
  confidence: optionalNumber, metadata: MetadataSchema.nullish(),
}).passthrough();
export const OutfitSchema = z.object({
  id: z.string().optional(), userId: z.string(), name: z.string(), items: z.array(ClothingItemSchema),
  season: textList, occasion: textList, createdAt: timestamp.nullish(), updatedAt: timestamp.nullish(),
  favorite: z.boolean().optional(), wearCount: optionalNumber, lastWorn: timestamp.nullish(),
  metadata: z.object({ style: optionalText, season: optionalText, colorHarmony: optionalText, styleNotes: optionalText }).passthrough().nullish(),
}).passthrough();
// Generated API outfits support either garment IDs or expanded wardrobe records.
export const OutfitGeneratedOutfitSchema = z.object({
  id: z.string().optional(), name: z.string(), description: z.string(),
  items: z.array(z.union([z.string(), ClothingItemSchema])), explanation: z.string(), reasoning: z.string(),
  pieces: z.array(z.object({}).passthrough()), styleTags: z.array(z.string()),
  colorHarmony: z.string(), styleNotes: z.string(), occasion: z.string(), season: z.string(), style: z.string(),
  mood: z.string().optional(), createdAt: timestamp.optional(), updatedAt: timestamp.optional(),
  user_id: optionalText, metadata: z.record(z.unknown()).nullish(),
}).passthrough();
export type ClothingItem = z.infer<typeof ClothingItemSchema>;
export type OpenAIClothingAnalysis = z.infer<typeof OpenAIClothingAnalysisSchema>;
export type Outfit = z.infer<typeof OutfitSchema>;
export type BasicMetadata = z.infer<typeof BasicMetadataSchema>;
export type ColorAnalysis = z.infer<typeof ColorAnalysisSchema>;
export type Metadata = z.infer<typeof MetadataSchema>;
export type Season = z.infer<typeof SeasonEnum>;
