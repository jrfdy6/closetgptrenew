import { z } from 'zod';

// Base types
export type UserId = string;
export type ImageUrl = string;
export type Timestamp = number;

// Base enums
export const ClothingTypeEnum = z.enum([
  'shirt',
  'dress_shirt',
  'pants',
  'shorts',
  'skirt',
  'dress',
  'jacket',
  'sweater',
  'shoes',
  'dress_shoes',
  'loafers',
  'sneakers',
  'accessory',
  'other',
  't-shirt',
  'blouse',
  'tank_top',
  'crop_top',
  'polo',
  'hoodie',
  'cardigan',
  'blazer',
  'coat',
  'vest',
  'jeans',
  'chinos',
  'slacks',
  'joggers',
  'sweatpants',
  'mini_skirt',
  'midi_skirt',
  'maxi_skirt',
  'pencil_skirt',
  'sundress',
  'cocktail_dress',
  'maxi_dress',
  'mini_dress',
  'boots',
  'sandals',
  'heels',
  'flats',
  'hat',
  'scarf',
  'belt',
  'jewelry',
  'bag',
  'watch'
]);

export const SeasonEnum = z.enum(['spring', 'summer', 'fall', 'winter']);

export const StyleTagEnum = z.enum([
  'Dark Academia',
  'Old Money',
  'Streetwear',
  'Y2K',
  'Minimalist',
  'Boho',
  'Preppy',
  'Grunge',
  'Classic',
  'Techwear',
  'Androgynous',
  'Coastal Chic',
  'Business Casual',
  'Avant-Garde',
  'Cottagecore',
  'Edgy',
  'Athleisure',
  'Casual Cool',
  'Romantic',
  'Artsy'
]);

export const OccasionTypeEnum = z.enum([
  'Casual',
  'Business Casual',
  'Formal',
  'Gala',
  'Party',
  'Date Night',
  'Work',
  'Interview',
  'Brunch',
  'Wedding Guest',
  'Cocktail',
  'Travel',
  'Airport',
  'Loungewear',
  'Beach',
  'Vacation',
  'Festival',
  'Rainy Day',
  'Snow Day',
  'Hot Weather',
  'Cold Weather',
  'Night Out',
  'Athletic / Gym',
  'School',
  'Holiday',
  'Concert',
  'Errands',
  'Chilly Evening',
  'Museum / Gallery',
  'First Date',
  'Business Formal',
  'Funeral / Memorial',
  'Fashion Event',
  'Outdoor Gathering'
]);

// Color types
export type Color = {
  name: string;
  hex: string;
  rgb: [number, number, number];
};

export const ColorSchema = z.object({
  name: z.string(),
  hex: z.string(),
  rgb: z.tuple([z.number(), z.number(), z.number()])
});

// New enums for compatibility
export const TemperatureRangeEnum = z.enum(['very_cold', 'cold', 'cool', 'mild', 'warm', 'hot', 'very_hot']);
export const MaterialEnum = z.enum(['cotton', 'wool', 'silk', 'linen', 'denim', 'leather', 'synthetic', 'knit', 'fleece', 'other']);
export const BodyTypeEnum = z.enum(['hourglass', 'pear', 'apple', 'rectangle', 'inverted_triangle']);
export const SkinToneEnum = z.enum(['warm', 'cool', 'neutral']);

// New compatibility schemas
export const TemperatureCompatibilitySchema = z.object({
  minTemp: z.number(),
  maxTemp: z.number(),
  recommendedLayers: z.array(z.string()),
  materialPreferences: z.array(MaterialEnum)
});

export const MaterialCompatibilitySchema = z.object({
  compatibleMaterials: z.array(MaterialEnum),
  weatherAppropriate: z.record(z.array(MaterialEnum))
});

export const BodyTypeCompatibilitySchema = z.object({
  recommendedFits: z.record(BodyTypeEnum, z.array(z.string())),
  styleRecommendations: z.record(BodyTypeEnum, z.array(z.string()))
});

export const SkinToneCompatibilitySchema = z.object({
  compatibleColors: z.record(SkinToneEnum, z.array(z.string())),
  recommendedPalettes: z.record(SkinToneEnum, z.array(z.string()))
});

export const OutfitScoringSchema = z.object({
  versatility: z.number().min(0).max(10),
  seasonality: z.number().min(0).max(10),
  formality: z.number().min(0).max(10),
  trendiness: z.number().min(0).max(10),
  quality: z.number().min(0).max(10)
});

// New layering-specific enums
export const LayerLevelEnum = z.enum(['base', 'inner', 'middle', 'outer']);
export const WarmthFactorEnum = z.enum(['light', 'medium', 'heavy']);
export const CoreCategoryEnum = z.enum(['top', 'bottom', 'dress', 'outerwear', 'shoes', 'accessory']);

// Metadata schemas
export const VisualAttributesSchema = z.object({
  material: z.string().nullable().optional(),
  pattern: z.string().nullable().optional(),
  textureStyle: z.string().nullable().optional(),
  fabricWeight: z.enum(["light", "medium", "heavy"]).nullable().optional(),
  fit: z.enum(["slim", "loose", "oversized"]).nullable().optional(),
  silhouette: z.string().nullable().optional(),
  length: z.string().nullable().optional(),
  genderTarget: z.string().nullable().optional(),
  sleeveLength: z.string().nullable().optional(),
  hangerPresent: z.boolean().nullable().optional(),
  backgroundRemoved: z.boolean().nullable().optional(),
  wearLayer: z.enum(["inner", "outer", "base"]).nullable().optional(),
  formalLevel: z.enum(["casual", "semi-formal", "formal"]).nullable().optional(),
  // New layering properties
  layerLevel: LayerLevelEnum.optional(),
  warmthFactor: WarmthFactorEnum.optional(),
  coreCategory: CoreCategoryEnum.optional(),
  canLayer: z.boolean().optional(),
  maxLayers: z.number().min(1).max(5).optional(),
  // Add new compatibility attributes
  temperatureCompatibility: TemperatureCompatibilitySchema.optional(),
  materialCompatibility: MaterialCompatibilitySchema.optional(),
  bodyTypeCompatibility: BodyTypeCompatibilitySchema.optional(),
  skinToneCompatibility: SkinToneCompatibilitySchema.optional(),
  outfitScoring: OutfitScoringSchema.optional()
});

export const ItemMetadataSchema = z.object({
  priceEstimate: z.number().nullable().optional(),
  careInstructions: z.string().nullable().optional(),
  tags: z.array(z.string()).optional(),
  brand: z.string().nullable().optional()
});

export const BasicMetadataSchema = z.object({
  width: z.number().nullable().optional(),
  height: z.number().nullable().optional(),
  orientation: z.string().nullable().optional(),
  dateTaken: z.string().nullable().optional(),
  deviceModel: z.string().nullable().optional(),
  gps: z.object({
    latitude: z.number(),
    longitude: z.number()
  }).nullable().optional(),
  flashUsed: z.boolean().nullable().optional(),
  imageHash: z.string().nullable().optional()
});

export const ColorAnalysisSchema = z.object({
  dominant: z.array(ColorSchema),
  matching: z.array(ColorSchema)
});

export const MetadataSchema = z.object({
  originalType: z.string(),
  analysisTimestamp: z.number(),
  basicMetadata: BasicMetadataSchema.optional(),
  visualAttributes: VisualAttributesSchema.optional(),
  itemMetadata: ItemMetadataSchema.optional(),
  colorAnalysis: ColorAnalysisSchema,
  naturalDescription: z.string().nullable().optional(),
  // Add new compatibility attributes
  temperatureCompatibility: TemperatureCompatibilitySchema.optional(),
  materialCompatibility: MaterialCompatibilitySchema.optional(),
  bodyTypeCompatibility: BodyTypeCompatibilitySchema.optional(),
  skinToneCompatibility: SkinToneCompatibilitySchema.optional(),
  outfitScoring: OutfitScoringSchema.optional()
});

// Clothing item types
export const ClothingItemSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: ClothingTypeEnum,
  color: z.string(),
  season: z.array(SeasonEnum),
  imageUrl: z.string(),
  tags: z.array(z.string()),
  style: z.array(z.string()),
  userId: z.string(),
  dominantColors: z.array(ColorSchema),
  matchingColors: z.array(ColorSchema),
  occasion: z.array(z.string()),
  createdAt: z.number(),
  updatedAt: z.number(),
  subType: z.string().nullable().optional(),
  brand: z.string().nullable().optional(),
  colorName: z.string().nullable().optional(),
  metadata: MetadataSchema.optional(),
  embedding: z.array(z.number()).optional(),
  backgroundRemoved: z.boolean().optional(),
  favorite: z.boolean().optional(),
  // Wear tracking fields
  wearCount: z.number().default(0).optional(),
  lastWorn: z.number().nullable().optional()
});

// Export all types
export type Season = z.infer<typeof SeasonEnum>;
export type StyleTag = z.infer<typeof StyleTagEnum>;
export type LayerLevel = z.infer<typeof LayerLevelEnum>;
export type WarmthFactor = z.infer<typeof WarmthFactorEnum>;
export type CoreCategory = z.infer<typeof CoreCategoryEnum>;
export type VisualAttributes = z.infer<typeof VisualAttributesSchema>;
export type ItemMetadata = z.infer<typeof ItemMetadataSchema>;
export type BasicMetadata = z.infer<typeof BasicMetadataSchema>;
export type ColorAnalysis = z.infer<typeof ColorAnalysisSchema>;
export type Metadata = z.infer<typeof MetadataSchema>;
export type ClothingItem = z.infer<typeof ClothingItemSchema>;

// OpenAI Analysis types
export const OpenAIClothingAnalysisSchema = z.object({
  type: z.string(),
  subType: z.string().nullable().optional(),
  name: z.string().optional(),
  dominantColors: z.array(z.object({
    name: z.string(),
    hex: z.string(),
    rgb: z.tuple([z.number(), z.number(), z.number()])
  })),
  matchingColors: z.array(z.object({
    name: z.string(),
    hex: z.string(),
    rgb: z.tuple([z.number(), z.number(), z.number()])
  })),
  style: z.array(z.string()),
  brand: z.string().nullable().optional(),
  season: z.array(z.enum(['spring', 'summer', 'fall', 'winter'])),
  occasion: z.array(z.string()),
  suggestedOutfits: z.array(z.object({
    description: z.string(),
    items: z.array(z.string())
  })).optional(),
  metadata: z.object({
    analysisTimestamp: z.number().optional(),
    originalType: z.string().optional(),
    originalSubType: z.string().optional(),
    styleTags: z.array(z.string()).optional(),
    occasionTags: z.array(z.string()).optional(),
    colorAnalysis: z.object({
      dominant: z.array(z.object({
        name: z.string(),
        hex: z.string(),
        rgb: z.tuple([z.number(), z.number(), z.number()])
      })),
      matching: z.array(z.object({
        name: z.string(),
        hex: z.string(),
        rgb: z.tuple([z.number(), z.number(), z.number()])
      }))
    }).optional(),
    basicMetadata: z.object({
      width: z.union([z.string(), z.number()]).transform(val => typeof val === 'string' ? parseInt(val, 10) : val).nullable().optional(),
      height: z.union([z.string(), z.number()]).transform(val => typeof val === 'string' ? parseInt(val, 10) : val).nullable().optional(),
      orientation: z.string().nullable().optional(),
      dateTaken: z.string().nullable().optional(),
      deviceModel: z.string().nullable().optional(),
      gps: z.object({
        latitude: z.number(),
        longitude: z.number()
      }).nullable().optional(),
      flashUsed: z.boolean().nullable().optional()
    }).optional(),
    visualAttributes: z.object({
      material: z.string().nullable().optional(),
      pattern: z.string().nullable().optional(),
      textureStyle: z.string().nullable().optional(),
      fabricWeight: z.string().nullable().optional(),
      fit: z.string().nullable().optional(),
      silhouette: z.string().nullable().optional(),
      length: z.string().nullable().optional(),
      genderTarget: z.string().nullable().optional(),
      sleeveLength: z.string().nullable().optional(),
      hangerPresent: z.boolean().nullable().optional(),
      backgroundRemoved: z.boolean().nullable().optional(),
      wearLayer: z.string().nullable().optional(),
      formalLevel: z.string().nullable().optional(),
      // Enhanced analysis fields
      temperatureCompatibility: z.object({
        minTemp: z.number(),
        maxTemp: z.number(),
        recommendedLayers: z.array(z.string()),
        materialPreferences: z.array(z.string())
      }).optional(),
      materialCompatibility: z.object({
        compatibleMaterials: z.array(z.string()),
        weatherAppropriate: z.object({
          spring: z.array(z.string()),
          summer: z.array(z.string()),
          fall: z.array(z.string()),
          winter: z.array(z.string())
        })
      }).optional(),
      bodyTypeCompatibility: z.object({
        hourglass: z.object({
          recommendedFits: z.array(z.string()),
          styleRecommendations: z.array(z.string())
        }),
        pear: z.object({
          recommendedFits: z.array(z.string()),
          styleRecommendations: z.array(z.string())
        }),
        apple: z.object({
          recommendedFits: z.array(z.string()),
          styleRecommendations: z.array(z.string())
        }),
        rectangle: z.object({
          recommendedFits: z.array(z.string()),
          styleRecommendations: z.array(z.string())
        }),
        inverted_triangle: z.object({
          recommendedFits: z.array(z.string()),
          styleRecommendations: z.array(z.string())
        })
      }).optional(),
      skinToneCompatibility: z.object({
        warm: z.object({
          compatibleColors: z.array(z.string()),
          recommendedColorPalette: z.array(z.string())
        }),
        cool: z.object({
          compatibleColors: z.array(z.string()),
          recommendedColorPalette: z.array(z.string())
        }),
        neutral: z.object({
          compatibleColors: z.array(z.string()),
          recommendedColorPalette: z.array(z.string())
        })
      }).optional()
    }).optional(),
    itemMetadata: z.object({
      priceEstimate: z.string().nullable().optional(),
      careInstructions: z.string().nullable().optional(),
      tags: z.array(z.string()).optional()
    }).optional(),
    naturalDescription: z.string().nullable().optional(),
    // Enhanced analysis metadata
    clipAnalysis: z.object({
      primaryStyle: z.string().nullable().optional(),
      styleConfidence: z.number().optional(),
      topStyles: z.array(z.string()).optional(),
      styleBreakdown: z.record(z.number()).optional(),
      analysisMethod: z.string().optional()
    }).nullable().optional(),
    confidenceScores: z.object({
      styleAnalysis: z.number(),
      gptAnalysis: z.number(),
      overallConfidence: z.number()
    }).optional(),
    styleCompatibility: z.object({
      primaryStyle: z.string().nullable().optional(),
      compatibleStyles: z.array(z.string()),
      avoidStyles: z.array(z.string()),
      styleNotes: z.string()
    }).optional(),
    enhancedStyles: z.array(z.string()).optional(),
    enhancedOccasions: z.array(z.string()).optional(),
    enhancedColorAnalysis: z.object({
      dominant: z.array(z.object({
        name: z.string(),
        hex: z.string(),
        rgb: z.tuple([z.number(), z.number(), z.number()])
      })),
      matching: z.array(z.object({
        name: z.string(),
        hex: z.string(),
        rgb: z.tuple([z.number(), z.number(), z.number()])
      }))
    }).optional()
  }).optional()
});

export type OpenAIClothingAnalysis = z.infer<typeof OpenAIClothingAnalysisSchema>;

// Outfit types
export const OutfitSchema = z.object({
  id: z.string().optional(),
  userId: z.string(),
  name: z.string(),
  description: z.string(),
  items: z.array(ClothingItemSchema),
  occasion: z.array(z.string()),
  season: z.array(z.enum(['spring', 'summer', 'fall', 'winter'])),
  createdAt: z.number(),
  updatedAt: z.number(),
  metadata: z.record(z.unknown()).optional()
});

export type Outfit = z.infer<typeof OutfitSchema>;

// API Response types
export type ApiResponse<T> = {
  success: boolean;
  data?: T;
  error?: string;
};

// Error types
export type AppError = {
  code: string;
  message: string;
  details?: unknown;
};

// User Profile types
export const UserProfileSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string(),
  gender: z.enum(["male", "female"]).optional(),
  preferences: z.object({
    style: z.array(z.string()),
    colors: z.array(z.string()),
    occasions: z.array(z.string()),
  }),
  measurements: z.object({
    height: z.number(),
    weight: z.number(),
    bodyType: z.string(),
    skinTone: z.string().optional(),
  }),
  stylePreferences: z.array(z.string()),
  bodyType: z.string(),
  skinTone: z.string().optional(),
  fitPreference: z.enum(["fitted", "relaxed", "oversized", "loose"]).optional(),
  sizePreference: z.enum(["XS", "S", "M", "L", "XL", "XXL", "Custom"]).optional(),
  createdAt: z.number(),
  updatedAt: z.number(),
});

export type UserProfile = z.infer<typeof UserProfileSchema>;

// Feedback types
export const FeedbackSchema = z.object({
  id: z.string().optional(),
  userId: z.string(),
  targetId: z.string(), // ID of the item/outfit being rated
  targetType: z.enum(['item', 'outfit']),
  rating: z.number().min(1).max(5),
  comment: z.string().optional(),
  createdAt: z.number(),
  updatedAt: z.number()
});

export type Feedback = z.infer<typeof FeedbackSchema>;

// Weather types
export const WeatherSchema = z.object({
  temperature: z.number(),
  condition: z.string(),
  humidity: z.number(),
  windSpeed: z.number(),
  location: z.string(),
  timestamp: z.number(),
});

export type Weather = z.infer<typeof WeatherSchema>;

// Generated Outfit types
export const OutfitGeneratedOutfitSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  items: z.array(z.union([z.string(), ClothingItemSchema])),
  occasion: z.string(),
  season: z.string(),
  style: z.string(),
  styleTags: z.array(z.string()),
  createdAt: z.number(),
  updatedAt: z.number(),
  // NEW: Add validation and warning fields
  wasSuccessful: z.boolean().optional(),
  validationErrors: z.array(z.string()).optional(),
  warnings: z.array(z.string()).optional(),
  validation_details: z.object({
    errors: z.array(z.string()).optional(),
    warnings: z.array(z.string()).optional(),
    fixes: z.array(z.object({
      method: z.string(),
      original_error: z.string(),
      applied: z.boolean()
    })).optional()
  }).optional(),
  metadata: z.object({
    colorHarmony: z.string().optional(),
    styleNotes: z.string().optional(),
    feedback: z.string().optional(),
    // NEW: Add validation metadata
    validation_summary: z.object({
      total_errors: z.number().optional(),
      total_warnings: z.number().optional(),
      success_rate: z.number().optional()
    }).optional()
  }).optional()
});

export type OutfitGeneratedOutfit = z.infer<typeof OutfitGeneratedOutfitSchema>;

export const ProcessImagesResult = z.object({
  success: z.boolean(),
  error: z.string().optional(),
  data: z.array(z.object({
    id: z.string(),
    name: z.string(),
    type: z.enum(["shirt", "pants", "shorts", "dress", "skirt", "jacket", "sweater", "shoes", "accessory", "other"]),
    color: z.string(),
    season: z.array(z.enum(["spring", "summer", "fall", "winter"])),
    imageUrl: z.string(),
    tags: z.array(z.string()),
    style: z.array(z.string()),
    userId: z.string(),
    dominantColors: z.array(z.object({
      hex: z.string(),
      name: z.string(),
      rgb: z.array(z.number())
    })),
    matchingColors: z.array(z.object({
      hex: z.string(),
      name: z.string(),
      rgb: z.array(z.number())
    })),
    occasion: z.array(z.string()),
    createdAt: z.number(),
    updatedAt: z.number(),
    subType: z.string().nullable().optional(),
    brand: z.string().nullable().optional(),
    colorName: z.string().nullable().optional(),
    metadata: z.object({
      basicMetadata: z.object({
        width: z.number().nullable().optional(),
        height: z.number().nullable().optional(),
        orientation: z.string().nullable().optional(),
        dateTaken: z.string().nullable().optional(),
        deviceModel: z.string().nullable().optional(),
        gps: z.object({
          latitude: z.number(),
          longitude: z.number()
        }).nullable().optional(),
        flashUsed: z.boolean().nullable().optional()
      }).optional(),
      visualAttributes: z.object({
        material: z.string().nullable().optional(),
        pattern: z.string().nullable().optional(),
        textureStyle: z.string().nullable().optional(),
        fabricWeight: z.enum(["light", "medium", "heavy"]).nullable().optional(),
        fit: z.enum(["slim", "loose", "oversized"]).nullable().optional(),
        silhouette: z.string().nullable().optional(),
        length: z.string().nullable().optional(),
        genderTarget: z.enum(["men", "women", "unisex"]).nullable().optional(),
        sleeveLength: z.string().nullable().optional(),
        hangerPresent: z.boolean().nullable().optional(),
        backgroundRemoved: z.boolean().nullable().optional(),
        wearLayer: z.enum(["inner", "outer", "base"]).nullable().optional(),
        formalLevel: z.enum(["casual", "semi-formal", "formal"]).nullable().optional()
      }).optional(),
      itemMetadata: z.object({
        priceEstimate: z.number().nullable().optional(),
        careInstructions: z.string().nullable().optional(),
        tags: z.array(z.string()).optional()
      }).optional()
    }).optional(),
    embedding: z.array(z.number()).optional(),
    backgroundRemoved: z.boolean().optional()
  })).optional()
});

export type OccasionType = z.infer<typeof OccasionTypeEnum>; 