import { MAX_FILE_SIZE, ALLOWED_FILE_TYPES } from '../constants';
import { ClothingItem, OpenAIClothingAnalysis } from '../types';
import { averagePairability } from './pairability';

export const validateFile = (file: File): { isValid: boolean; error?: string } => {
  if (!ALLOWED_FILE_TYPES.includes(file.type)) {
    return {
      isValid: false,
      error: 'Invalid file type. Please upload a JPEG, PNG, or WebP image.',
    };
  }

  if (file.size > MAX_FILE_SIZE) {
    return {
      isValid: false,
      error: 'File size too large. Maximum size is 5MB.',
    };
  }

  return { isValid: true };
};

export const formatDate = (date: Date | string): string => {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const getSeasonFromDate = (date: Date = new Date()): string => {
  const month = date.getMonth() + 1; // JavaScript months are 0-based
  if (month >= 3 && month <= 5) return 'spring';
  if (month >= 6 && month <= 8) return 'summer';
  if (month >= 9 && month <= 11) return 'fall';
  return 'winter';
};

// Color harmony scoring
const calculateColorHarmony = (outfit: Outfit): number => {
  let score = 0;
  const items = outfit.items;
  
  // Check if colors are complementary or harmonious
  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      const item1 = items[i];
      const item2 = items[j];
      
      // Check dominant colors
      const dominantColors1 = item1.dominantColors || [];
      const dominantColors2 = item2.dominantColors || [];
      
      // Check matching colors
      const matchingColors1 = item1.matchingColors || [];
      const matchingColors2 = item2.matchingColors || [];
      
      // Score for color harmony
      if (dominantColors1.some(c1 => 
        dominantColors2.some(c2 => c2.name === c1.name) ||
        matchingColors2.some(c2 => c2.name === c1.name)
      )) {
        score += 5;
      }
      
      // Score for matching colors
      if (matchingColors1.some(c1 => 
        dominantColors2.some(c2 => c2.name === c1.name) ||
        matchingColors2.some(c2 => c2.name === c1.name)
      )) {
        score += 3;
      }
    }
  }
  
  return Math.min(score, 20); // Cap color harmony score at 20
};

// Material compatibility scoring
const calculateMaterialCompatibility = (outfit: Outfit): number => {
  let score = 0;
  const items = outfit.items;
  
  // Define material compatibility rules
  const compatibleMaterials: Record<string, string[]> = {
    'Leather': ['Wool', 'Cotton', 'Silk', 'Denim'],
    'Wool': ['Leather', 'Cotton', 'Silk'],
    'Cotton': ['Leather', 'Wool', 'Denim', 'Linen'],
    'Silk': ['Wool', 'Leather', 'Cotton'],
    'Denim': ['Leather', 'Cotton'],
    'Linen': ['Cotton', 'Silk']
  };
  
  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      const material1 = items[i].metadata?.visualAttributes?.material;
      const material2 = items[j].metadata?.visualAttributes?.material;
      
      if (material1 && material2) {
        if (material1 === material2) {
          score += 3; // Same material
        } else if (compatibleMaterials[material1]?.includes(material2)) {
          score += 5; // Compatible materials
        }
      }
    }
  }
  
  return Math.min(score, 15); // Cap material compatibility score at 15
};

// Pattern mixing scoring
const calculatePatternMixing = (outfit: Outfit): number => {
  let score = 0;
  const items = outfit.items;
  const patterns = items.map(item => item.metadata?.visualAttributes?.pattern).filter(Boolean);
  
  // Define pattern compatibility rules
  const patternRules: Record<string, string[]> = {
    'Solid': ['Striped', 'Floral', 'Plaid', 'Geometric'],
    'Striped': ['Solid', 'Floral', 'Geometric'],
    'Floral': ['Solid', 'Striped', 'Geometric'],
    'Plaid': ['Solid', 'Geometric'],
    'Geometric': ['Solid', 'Striped', 'Floral', 'Plaid']
  };
  
  // Check pattern compatibility
  for (let i = 0; i < patterns.length; i++) {
    for (let j = i + 1; j < patterns.length; j++) {
      const pattern1 = patterns[i];
      const pattern2 = patterns[j];
      
      if (pattern1 && pattern2) {
        if (pattern1 === pattern2) {
          score += 2; // Same pattern
        } else if (patternRules[pattern1]?.includes(pattern2)) {
          score += 4; // Compatible patterns
        }
      }
    }
  }
  
  return Math.min(score, 15); // Cap pattern mixing score at 15
};

// Enhanced outfit scoring
export const calculateOutfitScore = (outfit: Outfit): number => {
  let score = 0;
  
  // Get style and season from metadata
  const style = outfit.metadata?.style?.toLowerCase() || '';
  const season = outfit.metadata?.season?.toLowerCase() || '';
  
  // Define piece count ranges based on style and season
  let minPieces = 2;
  let maxPieces = 6;
  
  // Adjust for summer styles
  if (season === 'summer' || style.includes('summer')) {
    minPieces = 2;
    maxPieces = 4;
  }
  
  // Adjust for winter styles
  if (season === 'winter' || style.includes('winter')) {
    minPieces = 3;
    maxPieces = 6;
  }
  
  // Adjust for specific styles
  if (style.includes('minimalist')) {
    minPieces = 2;
    maxPieces = 4;
  } else if (style.includes('layered')) {
    minPieces = 4;
    maxPieces = 6;
  }
  
  // Basic scoring
  if (outfit.items.length > 0) {
    score += 10;
  }

  // Score based on piece count within the appropriate range
  if (outfit.items.length >= minPieces && outfit.items.length <= maxPieces) {
    score += 15; // Higher score for being within the style-appropriate range
  } else if (outfit.items.length > 0) {
    score += 5; // Lower score for having items but not in the right range
  }

  if (outfit.occasion.length > 0) score += 5;
  if (outfit.season.length > 0) score += 5;

  // Add sophisticated scoring
  score += calculateColorHarmony(outfit);
  score += calculateMaterialCompatibility(outfit);
  score += calculatePatternMixing(outfit);
  
  // Add pairability score
  score += averagePairability(outfit.items) * 20; // Add up to 20 new points
  
  // Validate formality consistency
  const formalityLevels = outfit.items.map(item => 
    item.metadata?.visualAttributes?.formalLevel
  ).filter(Boolean);
  
  if (formalityLevels.length > 0) {
    const isFormalConsistent = formalityLevels.every(level => level === formalityLevels[0]);
    if (isFormalConsistent) {
      score += 10;
    }
  }

  // Add bonus points for metadata completeness
  if (outfit.metadata?.colorHarmony) {
    score += 10; // Required metadata
  }
  
  if (outfit.metadata?.styleNotes) {
    score += 5; // Optional metadata bonus
  }
  
  return Math.min(score, 100); // Cap total score at 100
};

export const getColorContrast = (hexColor: string): 'light' | 'dark' => {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? 'dark' : 'light';
};

export const groupClothingByType = (items: ClothingItem[]): Record<string, ClothingItem[]> => {
  return items.reduce((acc, item) => {
    const type = item.type.toLowerCase();
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(item);
    return acc;
  }, {} as Record<string, ClothingItem[]>);
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const generateUniqueId = (): string => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
};

export const validateOpenAIAnalysis = (data: any): OpenAIClothingAnalysis => {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid analysis data');
  }

  const requiredFields = ['type'];
  for (const field of requiredFields) {
    if (!data[field]) {
      throw new Error(`Missing required field: ${field}`);
    }
  }

  return {
    type: data.type,
    subType: data.subType || null,
    brand: data.brand || null,
    dominantColors: data.dominantColors || [],
    matchingColors: data.matchingColors || [],
    season: data.season || [],
    style: data.style || [],
    occasion: data.occasion || [],
    metadata: data.metadata || {
      imageHash: null,
      basicMetadata: {
        width: null,
        height: null,
        orientation: null,
        dateTaken: null,
        deviceModel: null,
        gps: null,
        flashUsed: null
      },
      visualAttributes: {
        material: null,
        pattern: null,
        textureStyle: null,
        fabricWeight: null,
        fit: null,
        silhouette: null,
        length: null,
        genderTarget: null,
        sleeveLength: null,
        hangerPresent: null,
        backgroundRemoved: null,
        wearLayer: null,
        formalLevel: null
      },
      itemMetadata: {
        priceEstimate: null,
        careInstructions: null,
        tags: []
      }
    }
  };
};

export * from './dom';
export * from './formatting';
export * from './validation'; 