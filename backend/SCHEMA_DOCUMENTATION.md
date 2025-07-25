# ClosetGPT Firestore Schema Documentation

## Overview
This document outlines the complete Firestore database schema for the ClosetGPT application, including all collections, their fields, data types, and relationships.

## Collections

### 1. `users` Collection
Stores user authentication and profile information.

**Document ID**: Firebase Auth UID

```typescript
{
  id: string,                    // Firebase Auth UID
  name: string,                  // User's display name
  email: string,                 // User's email address
  gender?: string,               // Optional gender preference
  preferences: {
    style: string[],             // Preferred style types
    colors: string[],            // Preferred colors
    occasions: string[]          // Preferred occasions
  },
  measurements: {
    height: number,              // Height in cm
    weight: number,              // Weight in kg
    bodyType: string,            // Body type classification
    skinTone?: string            // Skin tone for color matching
  },
  stylePreferences: string[],    // Array of style preferences
  bodyType: string,              // Primary body type
  skinTone?: string,             // Skin tone classification
  fitPreference?: string,        // Preferred fit (loose, regular, tight)
  createdAt: number,             // Unix timestamp
  updatedAt: number              // Unix timestamp
}
```

### 2. `wardrobe` Collection
Stores individual clothing items with comprehensive metadata.

**Document ID**: UUID4 string

```typescript
{
  id: string,                    // UUID4 identifier
  userId: string,                // Reference to user document
  name: string,                  // Item name/description
  type: ClothingType,            // Primary clothing type
  color: string,                 // Primary color
  season: string[],              // Suitable seasons
  imageUrl: string,              // Image URL
  tags: string[],                // Searchable tags
  style: string[],               // Style classifications
  dominantColors: Color[],       // Dominant colors with hex/rgb
  matchingColors: Color[],       // Compatible colors
  occasion: string[],            // Suitable occasions
  brand?: string,                // Brand name
  createdAt: number,             // Unix timestamp
  updatedAt: number,             // Unix timestamp
  subType?: string,              // Sub-category (e.g., "denim" for jacket)
  colorName?: string,            // Specific color name
  backgroundRemoved?: boolean,   // Image processing flag
  embedding?: number[],          // CLIP embedding vector
  metadata?: Metadata            // Comprehensive metadata object
}
```

#### Metadata Object Structure
```typescript
{
  analysisTimestamp: number,     // When analysis was performed
  originalType: string,          // Original type classification
  originalSubType?: string,      // Original subtype
  styleTags: string[],           // AI-detected style tags
  occasionTags: string[],        // AI-detected occasion tags
  brand?: string,                // Detected brand
  imageHash?: string,            // Image hash for deduplication
  colorAnalysis: {
    dominant: Color[],           // Dominant colors
    matching: Color[]            // Matching colors
  },
  basicMetadata?: {
    width: number,               // Image width
    height: number,              // Image height
    orientation: string,         // Image orientation
    dateTaken: string,           // Photo timestamp
    deviceModel: string,         // Camera device
    gps?: string,                // Location data
    flashUsed: boolean           // Flash usage
  },
  visualAttributes?: {
    pattern: string,             // Pattern type (solid, striped, etc.)
    formalLevel: string,         // Formality level
    fit: string,                 // Fit type
    length: string,              // Item length
    sleeveLength?: string,       // Sleeve length
    genderTarget: string,        // Target gender
    textureStyle: string,        // Texture description
    backgroundRemoved: boolean,  // Background removal status
    silhouette: string,          // Silhouette type
    hangerPresent: boolean,      // Hanger detection
    wearLayer: string,           // Layering position
    material: string,            // Material type
    fabricWeight: string         // Fabric weight
  },
  itemMetadata?: {
    priceEstimate?: string,      // Estimated price
    careInstructions?: string,   // Care instructions
    tags: string[]               // Additional tags
  },
  naturalDescription?: string,   // AI-generated description
  temperatureCompatibility?: {
    minTemp: number,             // Minimum temperature
    maxTemp: number,             // Maximum temperature
    recommendedLayers: string[], // Layer recommendations
    materialPreferences: Material[] // Temperature-appropriate materials
  },
  materialCompatibility?: {
    compatibleMaterials: Material[], // Compatible materials
    weatherAppropriate: {        // Weather-specific materials
      [weatherType: string]: Material[]
    }
  },
  bodyTypeCompatibility?: {
    recommendedFits: {           // Body type to fit mapping
      [bodyType: string]: string[]
    },
    styleRecommendations: {      // Body type to style mapping
      [bodyType: string]: string[]
    }
  },
  skinToneCompatibility?: {
    compatibleColors: {          // Skin tone to color mapping
      [skinTone: string]: string[]
    },
    recommendedPalettes: {       // Skin tone to palette mapping
      [skinTone: string]: string[]
    }
  },
  outfitScoring?: {
    versatility: number,         // 0-10 score
    seasonality: number,         // 0-10 score
    formality: number,           // 0-10 score
    trendiness: number,          // 0-10 score
    quality: number              // 0-10 score
  }
}
```

### 3. `outfits` Collection
Stores generated and saved outfits.

**Document ID**: UUID4 string

```typescript
{
  id: string,                    // UUID4 identifier
  userId: string,                // Reference to user document
  name: string,                  // Outfit name
  description: string,           // Outfit description
  items: OutfitPiece[],          // Array of outfit pieces
  occasion: string,              // Primary occasion
  season: string,                // Primary season
  style: string,                 // Primary style
  styleTags: string[],           // Style classifications
  colorHarmony: string,          // Color harmony description
  styleNotes: string,            // Styling notes
  createdAt: number,             // Unix timestamp
  updatedAt: number,             // Unix timestamp
  metadata?: {                   // Additional metadata
    [key: string]: any
  }
}
```

#### OutfitPiece Structure
```typescript
{
  itemId: string,                // Reference to wardrobe item
  name: string,                  // Item name
  type: string,                  // Item type
  reason: string,                // Why this item was chosen
  dominantColors: string[],      // Dominant colors
  style: string[],               // Style tags
  occasion: string[],            // Occasion tags
  imageUrl: string               // Item image URL
}
```

### 4. `style_profiles` Collection
Stores user style preferences and quiz results.

**Document ID**: Firebase Auth UID

```typescript
{
  userId: string,                // Reference to user document
  styleGoals: string[],          // Style goals from quiz
  preferredStyles: string[],     // Preferred style types
  colorPreferences: string[],    // Preferred colors
  occasionPreferences: string[], // Preferred occasions
  bodyType: string,              // Body type
  skinTone: string,              // Skin tone
  budget: string,                // Budget range
  brands: string[],              // Preferred brands
  createdAt: number,             // Unix timestamp
  updatedAt: number              // Unix timestamp
}
```

### 5. `fashion_trends` Collection
Stores current fashion trends and seasonal data.

**Document ID**: UUID4 string

```typescript
{
  id: string,                    // UUID4 identifier
  season: string,                // Season (spring, summer, fall, winter)
  year: number,                  // Year
  trends: {
    colors: string[],            // Trending colors
    styles: string[],            // Trending styles
    patterns: string[],          // Trending patterns
    materials: string[]          // Trending materials
  },
  popularity: number,            // Trend popularity score
  createdAt: number,             // Unix timestamp
  updatedAt: number              // Unix timestamp
}
```

### 6. `analytics` Collection
Stores user analytics and usage data.

**Document ID**: UUID4 string

```typescript
{
  id: string,                    // UUID4 identifier
  userId: string,                // Reference to user document
  eventType: string,             // Event type (outfit_generated, item_added, etc.)
  eventData: {                   // Event-specific data
    [key: string]: any
  },
  timestamp: number,             // Unix timestamp
  sessionId?: string,            // Session identifier
  metadata?: {                   // Additional context
    [key: string]: any
  }
}
```

## Zod Schema Validation (Frontend)

The frontend uses Zod schemas for runtime type validation and type safety. These schemas mirror the Firestore data structures and ensure data integrity across the application.

### Core Zod Schemas

#### ClothingItemSchema
```typescript
const ClothingItemSchema = z.object({
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
  backgroundRemoved: z.boolean().optional()
});
```

#### UserProfileSchema
```typescript
const UserProfileSchema = z.object({
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
```

#### OpenAIClothingAnalysisSchema
```typescript
const OpenAIClothingAnalysisSchema = z.object({
  type: z.string(),
  subType: z.string().nullable().optional(),
  name: z.string().optional(),
  dominantColors: z.array(ColorSchema),
  matchingColors: z.array(ColorSchema),
  style: z.array(z.string()),
  brand: z.string().nullable().optional(),
  season: z.array(SeasonEnum),
  occasion: z.array(z.string()),
  metadata: z.object({
    analysisTimestamp: z.number().optional(),
    originalType: z.string().optional(),
    originalSubType: z.string().optional(),
    styleTags: z.array(z.string()).optional(),
    occasionTags: z.array(z.string()).optional(),
    colorAnalysis: ColorAnalysisSchema.optional(),
    basicMetadata: BasicMetadataSchema.optional(),
    visualAttributes: VisualAttributesSchema.optional(),
    itemMetadata: ItemMetadataSchema.optional(),
    naturalDescription: z.string().nullable().optional(),
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
    enhancedColorAnalysis: ColorAnalysisSchema.optional()
  }).optional()
});
```

### Enum Schemas

#### ClothingTypeEnum
```typescript
const ClothingTypeEnum = z.enum([
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
  'other'
]);
```

#### SeasonEnum
```typescript
const SeasonEnum = z.enum(['spring', 'summer', 'fall', 'winter']);
```

#### StyleTagEnum
```typescript
const StyleTagEnum = z.enum([
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
```

#### OccasionTypeEnum
```typescript
const OccasionTypeEnum = z.enum([
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
```

### Metadata Schemas

#### ColorSchema
```typescript
const ColorSchema = z.object({
  name: z.string(),
  hex: z.string(),
  rgb: z.tuple([z.number(), z.number(), z.number()])
});
```

#### VisualAttributesSchema
```typescript
const VisualAttributesSchema = z.object({
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
  temperatureCompatibility: TemperatureCompatibilitySchema.optional(),
  materialCompatibility: MaterialCompatibilitySchema.optional(),
  bodyTypeCompatibility: BodyTypeCompatibilitySchema.optional(),
  skinToneCompatibility: SkinToneCompatibilitySchema.optional(),
  outfitScoring: OutfitScoringSchema.optional()
});
```

#### MetadataSchema
```typescript
const MetadataSchema = z.object({
  originalType: z.string(),
  analysisTimestamp: z.number(),
  basicMetadata: BasicMetadataSchema.optional(),
  visualAttributes: VisualAttributesSchema.optional(),
  itemMetadata: ItemMetadataSchema.optional(),
  colorAnalysis: ColorAnalysisSchema,
  naturalDescription: z.string().nullable().optional(),
  temperatureCompatibility: TemperatureCompatibilitySchema.optional(),
  materialCompatibility: MaterialCompatibilitySchema.optional(),
  bodyTypeCompatibility: BodyTypeCompatibilitySchema.optional(),
  skinToneCompatibility: SkinToneCompatibilitySchema.optional(),
  outfitScoring: OutfitScoringSchema.optional()
});
```

### Validation Functions

The frontend provides validation functions that use these schemas:

```typescript
// Validate individual clothing item
export const validateClothingItem = (item: unknown): ClothingItem => {
  return ClothingItemSchema.parse(item);
};

// Validate array of clothing items
export const validateClothingItems = (items: unknown[]): ClothingItem[] => {
  return items.map(item => ClothingItemSchema.parse(item));
};

// Validate user profile
export const validateUserProfile = (profile: unknown): UserProfile => {
  return UserProfileSchema.parse(profile);
};

// Validate OpenAI analysis
export const validateOpenAIAnalysis = (analysis: unknown): OpenAIClothingAnalysis => {
  return OpenAIClothingAnalysisSchema.parse(analysis);
};
```

### API Response Validation

```typescript
// Generic API response validation
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

// Specific response validators
export function validateClothingItemResponse(response: unknown): ApiResponse<ClothingItem> {
  const validatedResponse = validateApiResponse<ClothingItem>(response);
  if (validatedResponse.success && validatedResponse.data) {
    validatedResponse.data = validateClothingItem(validatedResponse.data);
  }
  return validatedResponse;
}
```

## Enums and Constants

### ClothingType Enum
```typescript
enum ClothingType {
  SHIRT = "shirt",
  DRESS_SHIRT = "dress_shirt",
  PANTS = "pants",
  SHORTS = "shorts",
  SKIRT = "skirt",
  DRESS = "dress",
  JACKET = "jacket",
  SWEATER = "sweater",
  SHOES = "shoes",
  DRESS_SHOES = "dress_shoes",
  LOAFERS = "loafers",
  SNEAKERS = "sneakers",
  ACCESSORY = "accessory",
  OTHER = "other"
}
```

### StyleType Enum
```typescript
enum StyleType {
  CASUAL = "Casual",
  FORMAL = "Formal",
  SPORTS = "Sports",
  TRENDY = "Trendy",
  VINTAGE = "Vintage",
  STATEMENT = "Statement",
  SMART_CASUAL = "Smart Casual",
  BUSINESS = "Business",
  LUXURY = "Luxury",
  STREETWEAR = "Streetwear",
  MINIMALIST = "Minimalist",
  BOHEMIAN = "Bohemian",
  CLASSIC = "Classic",
  ELEGANT = "Elegant",
  ATHLETIC = "Athletic",
  PREPPY = "Preppy",
  GOTHIC = "Gothic",
  PUNK = "Punk",
  HIPSTER = "Hipster",
  RETRO = "Retro"
}
```

### Season Enum
```typescript
enum Season {
  SPRING = "spring",
  SUMMER = "summer",
  FALL = "fall",
  WINTER = "winter"
}
```

### Color Object Structure
```typescript
{
  name: string,                  // Color name
  hex: string,                   // Hex color code
  rgb: number[]                  // RGB values [r, g, b]
}
```

## Indexes

### Required Firestore Indexes

1. **wardrobe collection**:
   - `userId` (ascending)
   - `type` (ascending)
   - `season` (array-contains)
   - `occasion` (array-contains)
   - `style` (array-contains)

2. **outfits collection**:
   - `userId` (ascending)
   - `occasion` (ascending)
   - `season` (ascending)
   - `style` (ascending)

3. **analytics collection**:
   - `userId` (ascending)
   - `eventType` (ascending)
   - `timestamp` (descending)

## Security Rules

### Basic Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Wardrobe items belong to users
    match /wardrobe/{itemId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
    
    // Outfits belong to users
    match /outfits/{outfitId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
    
    // Style profiles belong to users
    match /style_profiles/{userId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == userId;
    }
    
    // Fashion trends are public read-only
    match /fashion_trends/{trendId} {
      allow read: if true;
      allow write: if false;
    }
    
    // Analytics belong to users
    match /analytics/{analyticsId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
  }
}
```

## Data Migration Considerations

1. **Schema Versioning**: Each document includes `createdAt` and `updatedAt` timestamps for tracking changes.

2. **Backward Compatibility**: New fields are added as optional to maintain compatibility.

3. **Data Validation**: Pydantic models ensure data integrity on the backend, Zod schemas ensure type safety on the frontend.

4. **Embedding Storage**: CLIP embeddings are stored as arrays of floats for AI-powered similarity search.

5. **Color Normalization**: Colors are stored in multiple formats (name, hex, rgb) for flexibility.

## Performance Considerations

1. **Indexing**: Strategic indexes on frequently queried fields.
2. **Embedding Storage**: CLIP embeddings enable fast similarity search.
3. **Image URLs**: Images are stored as URLs, not base64 data.
4. **Batch Operations**: Use batch writes for multiple document updates.
5. **Pagination**: Implement cursor-based pagination for large collections.

## Future Enhancements

1. **Real-time Updates**: Consider Firestore real-time listeners for live updates.
2. **Offline Support**: Implement offline-first architecture with local caching.
3. **Search Optimization**: Add full-text search capabilities.
4. **Analytics Aggregation**: Implement data aggregation for insights.
5. **Multi-language Support**: Add internationalization for global users. 