export interface UserProfile {
  id: string;
  name: string;
  email: string;
  gender?: string;
  createdAt: number;
  updatedAt: number;
  
  // Basic preferences
  preferences: {
    style: string[];
    colors: string[];
    occasions: string[];
  };
  
  // Basic measurements
  measurements: {
    height: number;
    weight: number;
    bodyType: string;
    skinTone?: string;
  };
  
  // Style preferences
  stylePreferences: string[];
  bodyType?: string;
  skinTone?: string;
  fitPreference?: string;
  sizePreference?: 'XS' | 'S' | 'M' | 'L' | 'XL' | 'XXL' | 'XXXL';
  
  // Detailed measurements
  heightFeetInches?: string;
  topSize?: string;
  bottomSize?: string;
  shoeSize?: string;
  dressSize?: string;
  jeanWaist?: string;
  braSize?: string;
  inseam?: string;
  waist?: string;
  chest?: string;
  shoulderWidth?: number;
  waistWidth?: number;
  hipWidth?: number;
  armLength?: number;
  neckCircumference?: number;
  thighCircumference?: number;
  calfCircumference?: number;
  
  // Color preferences
  colorPalette?: {
    primary: string[];
    secondary: string[];
    accent: string[];
    neutral: string[];
    avoid: string[];
  };
  
  // Style personality scores (0-1)
  stylePersonality?: {
    classic: number;
    modern: number;
    creative: number;
    minimal: number;
    bold: number;
  };
  
  // Material preferences
  materialPreferences?: {
    preferred: string[];
    avoid: string[];
    seasonal: {
      spring: string[];
      summer: string[];
      fall: string[];
      winter: string[];
    };
  };
  
  // Fit preferences
  fitPreferences?: {
    tops: string;
    bottoms: string;
    dresses: string;
  };
  
  // Comfort levels (0-1)
  comfortLevel?: {
    tight: number;
    loose: number;
    structured: number;
    relaxed: number;
  };
  
  // Brand preferences
  preferredBrands?: string[];
  
  // Budget preference
  budget?: string;
  
  // Legacy favorite fields (for backward compatibility)
  favoriteColors?: string[];
  favoriteStyles?: string[];
  favoriteBrands?: string[];
  favoriteOccasions?: string[];
  favoriteSeasons?: string[];
  favoriteMaterials?: string[];
  favoritePatterns?: string[];
  favoriteSilhouettes?: string[];
  favoriteAccessories?: string[];
  favoriteShoes?: string[];
  favoriteOuterwear?: string[];
  favoriteBottoms?: string[];
  favoriteTops?: string[];
  favoriteDresses?: string[];
  favoriteSuits?: string[];
  favoriteFormal?: string[];
  favoriteCasual?: string[];
  favoriteAthletic?: string[];
  favoriteBusiness?: string[];
  favoriteEvening?: string[];
  favoriteBeach?: string[];
  favoriteWinter?: string[];
  favoriteSummer?: string[];
  favoriteSpring?: string[];
  favoriteFall?: string[];
} 