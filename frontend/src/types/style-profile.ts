import { BodyType, GarmentStyle, OutfitFormality, OutfitOccasion, OutfitSeason } from './photo-analysis';

export interface BodyMeasurements {
  height: number;
  shoulderWidth: number;
  waistWidth: number;
  hipWidth: number;
  inseam: number;
  // Additional measurements
  chestWidth?: number;
  armLength?: number;
  neckCircumference?: number;
  thighCircumference?: number;
  calfCircumference?: number;
}

export interface SkinTone {
  undertone: 'warm' | 'cool' | 'neutral';
  shade: string; // Hex color code
  season: 'spring' | 'summer' | 'autumn' | 'winter'; // Color season
  contrast: 'high' | 'medium' | 'low'; // Contrast level
}

export interface ColorPreferences {
  primary: string[]; // Most frequently worn colors
  secondary: string[]; // Supporting colors
  accent: string[]; // Accent colors
  avoid: string[]; // Colors to avoid
  seasonal: {
    spring: string[];
    summer: string[];
    fall: string[];
    winter: string[];
  };
}

export interface StylePreferences {
  preferredStyles: GarmentStyle[];
  preferredFormality: OutfitFormality[];
  preferredOccasions: OutfitOccasion[];
  preferredSeasons: OutfitSeason[];
  stylePersonality: {
    classic: number; // 0-1 score
    modern: number;
    creative: number;
    minimal: number;
    bold: number;
  };
  styleGoals: string[]; // e.g., ["professional", "sustainable", "trendy"]
}

export interface FitPreferences {
  preferredFits: {
    tops: 'slim' | 'regular' | 'loose';
    bottoms: 'slim' | 'regular' | 'loose';
    dresses: 'fitted' | 'regular' | 'flowy';
  };
  comfortLevel: {
    tight: number; // 0-1 score
    loose: number;
    structured: number;
    relaxed: number;
  };
}

export interface MaterialPreferences {
  preferred: string[]; // e.g., ["cotton", "wool", "silk"]
  avoid: string[]; // e.g., ["polyester", "acrylic"]
  seasonal: {
    spring: string[];
    summer: string[];
    fall: string[];
    winter: string[];
  };
}

export interface StyleProfile {
  bodyType: BodyType;
  measurements: BodyMeasurements;
  skinTone: SkinTone;
  colorPreferences: ColorPreferences;
  stylePreferences: StylePreferences;
  fitPreferences: FitPreferences;
  materialPreferences: MaterialPreferences;
  styleHistory: {
    recentOutfits: string[]; // URLs of recent outfit photos
    favoriteOutfits: string[]; // URLs of favorite outfit photos
    styleEvolution: {
      date: string;
      changes: string[];
    }[];
  };
  styleInsights: {
    strengths: string[];
    areasForImprovement: string[];
    recommendations: string[];
  };
  lastUpdated: string; // ISO date string
} 