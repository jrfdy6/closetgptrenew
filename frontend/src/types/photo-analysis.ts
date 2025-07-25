export interface BodyMeasurements {
  height: number;
  shoulderWidth: number;
  waistWidth: number;
  hipWidth: number;
  inseam: number;
  bodyType: BodyType;
  weight?: number;
  skinTone?: string;
  fitPreference?: 'fitted' | 'relaxed' | 'oversized' | 'loose';
}

export type BodyType = 
  | 'Athletic'
  | 'Curvy'
  | 'Rectangular'
  | 'Hourglass'
  | 'Pear'
  | 'Apple'
  | 'Inverted Triangle'
  | 'hourglass'
  | 'rectangle'
  | 'triangle'
  | 'inverted-triangle'
  | 'oval';

export interface ColorAnalysis {
  primaryColors: string[];
  secondaryColors: string[];
  skinTone: {
    undertone: 'warm' | 'cool' | 'neutral' | 'olive';
    shade: 'deep' | 'medium' | 'fair';
  };
  dominantColors: Color[];
  matchingColors: Color[];
  compatibleColors?: string[];
}

export interface Color {
  name: string;
  hex: string;
  rgb: number[];
}

export type GarmentType = 
  | 'shirt' | 'pants' | 'shorts' | 'skirt' | 'dress' | 'jacket' | 'sweater' | 'shoes' | 'accessory' | 'other'
  | 't-shirt' | 'blouse' | 'hoodie' | 'coat'
  | 'jeans' | 'boots' | 'sneakers' | 'sandals' | 'heels';

export type GarmentStyle = 
  | 'Casual' | 'Formal' | 'Business' | 'Athletic / Gym' | 'Trendy' | 'Vintage' | 'Statement' | 'Smart Casual'
  | 'Minimal Luxe' | 'Gorpcore' | 'Boho' | 'Streetwear' | 'Old Money' | 'Clean Girl' | 'Korean Core' | 'Y2K'
  | 'Coastal Grandmother' | 'Dark Academia'
  | 'elegant' | 'classic' | 'modern' | 'bohemian' | 'preppy' | 'bold' | 'streetwear';

export type GarmentPattern = 
  | 'solid' | 'striped' | 'plaid' | 'floral' | 'geometric' | 'abstract'
  | 'animal-print' | 'polka-dot' | 'checkered' | 'tie-dye';

export type GarmentFit = 
  | 'slim' | 'regular' | 'loose' | 'oversized' | 'fitted' | 'relaxed';

export type GarmentMaterial = 
  | 'cotton' | 'denim' | 'wool' | 'silk' | 'leather' | 'synthetic'
  | 'linen' | 'knit' | 'fleece' | 'suede' | 'velvet';

export interface VisualAttributes {
  material: string | null;
  pattern: string | null;
  textureStyle: string | null;
  fabricWeight: string | null;
  fit: string | null;
  silhouette: string | null;
  length: string | null;
  genderTarget: string;
  sleeveLength: string | null;
  hangerPresent: boolean | null;
  backgroundRemoved: boolean | null;
  wearLayer: string;
  formalLevel: string;
}

export interface ItemMetadata {
  priceEstimate: string | null;
  careInstructions: string | null;
  tags: string[];
}

export interface BasicMetadata {
  width: number | null;
  height: number | null;
  orientation: string | null;
  dateTaken: string | null;
  deviceModel: string | null;
  gps: string | null;
  flashUsed: boolean | null;
}

export interface Garment {
  id?: string;
  type: GarmentType;
  color: string; // Hex color code
  style: GarmentStyle[];
  pattern: GarmentPattern;
  fit: GarmentFit;
  material: GarmentMaterial;
  confidence: number; // Confidence score for detection
  subType?: string;
  colorName?: string;
  backgroundRemoved?: boolean;
  dominantColors: Color[];
  matchingColors: Color[];
  occasion: string[];
  season: OutfitSeason[];
  brand?: string;
  metadata?: {
    visualAttributes?: VisualAttributes;
    itemMetadata?: ItemMetadata;
    basicMetadata?: BasicMetadata;
  };
  userId?: string;
  name?: string;
  tags?: string[];
  createdAt?: number;
  updatedAt?: number;
}

export type OutfitFormality = 
  | 'very-casual' | 'casual' | 'smart-casual' | 'business-casual'
  | 'business' | 'semi-formal' | 'formal' | 'very-formal';

export type OutfitOccasion = 
  | 'everyday' | 'work' | 'business' | 'party' | 'date'
  | 'formal-event' | 'athletic' | 'outdoor' | 'travel';

export type OutfitSeason = 
  | 'spring' | 'summer' | 'fall' | 'winter' | 'all-season';

export interface OutfitAnalysis {
  id?: string;
  userId?: string;
  name?: string;
  description?: string;
  garments: Garment[];
  overallStyle: GarmentStyle[];
  colorPalette: string[]; // Array of hex color codes
  formality: OutfitFormality;
  occasion: OutfitOccasion;
  season: OutfitSeason;
  colorHarmony: {
    primary: string; // Main color
    secondary: string; // Supporting color
    accent: string; // Accent color
    complementary: string[]; // Complementary colors
  };
  styleCoherence: number; // Score from 0-1 indicating how well the styles work together
  confidence: number; // Overall confidence score for the analysis
  metadata?: {
    colorHarmony?: string;
    styleNotes?: string;
    feedback?: string;
    weather?: {
      temperature: number;
      condition: string;
      location: string;
      humidity: number;
      wind_speed: number;
      precipitation: number;
    };
  };
  createdAt?: number;
  updatedAt?: number;
}

export interface PhotoAnalysis {
  bodyMeasurements: BodyMeasurements;
  colorAnalysis: ColorAnalysis;
  outfitAnalysis?: OutfitAnalysis;
  confidence: number;
  metadata?: {
    imageHash?: string;
    analysisTimestamp: number;
    naturalDescription?: string;
  };
}

export interface UserPhotos {
  fullBodyPhoto?: string; // URL to stored photo
  outfitPhotos: string[]; // URLs to stored photos
  analyses: {
    fullBody?: PhotoAnalysis;
    outfits: OutfitAnalysis[];
  };
  lastUpdated: string;
}

export interface GarmentDetails {
  hasCollar: boolean;
  hasButtons: boolean;
  hasHood: boolean;
  hasHeel: boolean;
  isOpen: boolean;
  isAthletic: boolean;
  hasStripes: boolean;
  hasMesh: boolean;
  sleeveLength?: string;
  length?: string;
  silhouette?: string;
  textureStyle?: string;
  fabricWeight?: string;
  wearLayer?: string;
  formalLevel?: string;
} 