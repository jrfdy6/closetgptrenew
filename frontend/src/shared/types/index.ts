// Stub types for @shared/types
// This is a temporary fix to resolve import errors

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  gender: string | null;
  preferences: {
    style: string[];
    colors: string[];
    occasions: string[];
  };
  measurements: {
    height: number;
    weight: number;
    bodyType: string | null;
    skinTone: string | null;
  };
  stylePreferences: any[];
  bodyType: string | null;
  skinTone: string | null;
  fitPreference: string | null;
  sizePreference: string | null;
  createdAt: any;
  updatedAt: any;
  onboardingCompleted: boolean;
}

export const UserProfileSchema = {
  parse: (data: any) => data as UserProfile
};

// Additional stub types
export interface ClothingItem {
  id?: string;
  userId: string;
  type: string;
  subType?: string;
  name: string;
  color: string;
  season: string;
  imageUrl: string;
  tags: string[];
  style: string[];
  dominantColors: any[];
  matchingColors: any[];
  occasion: string[];
  createdAt: number;
  updatedAt: number;
  brand?: string;
  colorName?: string;
  metadata?: any;
}

export const ClothingItemSchema = {
  parse: (data: any) => data as ClothingItem
};

export interface OpenAIClothingAnalysis {
  type: string;
  subType?: string;
  season: string;
  style: string[];
  dominantColors: any[];
  matchingColors: any[];
  occasion: string[];
  brand?: string;
}

export const OpenAIClothingAnalysisSchema = {
  parse: (data: any) => data as OpenAIClothingAnalysis
};

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Additional stub types
export interface Outfit {
  id?: string;
  userId: string;
  name: string;
  items: ClothingItem[];
  season: string;
  occasion: string[];
  createdAt: number;
  updatedAt: number;
  favorite?: boolean;
  wearCount?: number;
  lastWorn?: number | null;
  metadata?: any;
} 