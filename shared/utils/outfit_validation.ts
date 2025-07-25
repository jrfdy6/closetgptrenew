import { ClothingItem, UserProfile, Season } from '../types/wardrobe';

// Material compatibility rules
const COMPATIBLE_MATERIALS: Record<string, string[]> = {
  'cotton': ['denim', 'linen', 'wool', 'silk'],
  'denim': ['cotton', 'leather', 'wool'],
  'wool': ['cotton', 'silk', 'cashmere'],
  'silk': ['cotton', 'wool', 'cashmere'],
  'leather': ['denim', 'cotton', 'wool'],
  'linen': ['cotton', 'silk'],
  'cashmere': ['wool', 'silk', 'cotton']
};

// Weather-appropriate materials
const WEATHER_MATERIALS: Record<string, string[]> = {
  'winter': ['wool', 'cashmere', 'leather', 'thick_cotton'],
  'summer': ['cotton', 'linen', 'silk', 'light_wool'],
  'spring': ['cotton', 'linen', 'light_wool'],
  'fall': ['wool', 'cotton', 'denim', 'leather']
};

// Skin tone color compatibility
const SKIN_TONE_COLORS: Record<string, string[]> = {
  'warm': ['coral', 'peach', 'gold', 'olive', 'terracotta', 'warm_red'],
  'cool': ['blue', 'purple', 'pink', 'silver', 'cool_red', 'emerald'],
  'neutral': ['navy', 'gray', 'white', 'black', 'beige', 'mauve']
};

// Body type fit recommendations
const BODY_TYPE_FITS: Record<string, string[]> = {
  'hourglass': ['fitted', 'relaxed'],
  'pear': ['fitted_top', 'relaxed_bottom'],
  'apple': ['relaxed_top', 'fitted_bottom'],
  'rectangle': ['fitted', 'oversized'],
  'inverted_triangle': ['relaxed_top', 'fitted_bottom']
};

export interface ValidationResult {
  isValid: boolean;
  warnings: string[];
}

export function validateMaterialCompatibility(items: ClothingItem[]): ValidationResult {
  const warnings: string[] = [];
  const materials = items.map(item => item.metadata?.visualAttributes?.material?.toLowerCase() || 'unknown');

  for (let i = 0; i < materials.length; i++) {
    for (let j = i + 1; j < materials.length; j++) {
      const material1 = materials[i];
      const material2 = materials[j];

      if (material1 === 'unknown' || material2 === 'unknown') continue;

      const compatibleWith1 = COMPATIBLE_MATERIALS[material1] || [];
      const compatibleWith2 = COMPATIBLE_MATERIALS[material2] || [];

      if (!compatibleWith1.includes(material2) && !compatibleWith2.includes(material1)) {
        warnings.push(`Material compatibility warning: ${material1} and ${material2} may not work well together`);
      }
    }
  }

  return {
    isValid: warnings.length === 0,
    warnings
  };
}

export function validateWeatherAppropriateness(items: ClothingItem[], season: Season): ValidationResult {
  const warnings: string[] = [];
  const seasonMaterials = WEATHER_MATERIALS[season.toLowerCase()] || [];

  for (const item of items) {
    const material = item.metadata?.visualAttributes?.material?.toLowerCase();
    if (material && !seasonMaterials.includes(material)) {
      warnings.push(`${item.name} (${material}) may not be appropriate for ${season} weather`);
    }
  }

  return {
    isValid: warnings.length === 0,
    warnings
  };
}

export function validateSkinToneCompatibility(items: ClothingItem[], userProfile: UserProfile): ValidationResult {
  const warnings: string[] = [];
  const skinTone = userProfile.skinTone?.toLowerCase();

  if (!skinTone) return { isValid: true, warnings: [] };

  const recommendedColors = SKIN_TONE_COLORS[skinTone] || [];
  
  for (const item of items) {
    const color = item.color.toLowerCase();
    if (!recommendedColors.some(recColor => color.includes(recColor))) {
      warnings.push(`${item.name} (${color}) may not complement your ${skinTone} skin tone`);
    }
  }

  return {
    isValid: warnings.length === 0,
    warnings
  };
}

export function validateBodyTypeFit(items: ClothingItem[], userProfile: UserProfile): ValidationResult {
  const warnings: string[] = [];
  const bodyType = userProfile.bodyType?.toLowerCase();
  const fitPreference = userProfile.fitPreference?.toLowerCase();

  if (!bodyType) return { isValid: true, warnings: [] };

  const recommendedFits = BODY_TYPE_FITS[bodyType] || [];

  for (const item of items) {
    const itemFit = item.metadata?.visualAttributes?.fit?.toLowerCase();
    if (itemFit && !recommendedFits.includes(itemFit)) {
      warnings.push(`${item.name} (${itemFit} fit) may not be ideal for your ${bodyType} body type`);
    }

    if (fitPreference && itemFit && itemFit !== fitPreference) {
      warnings.push(`${item.name} (${itemFit} fit) doesn't match your preferred ${fitPreference} fit`);
    }
  }

  return {
    isValid: warnings.length === 0,
    warnings
  };
}

export function validateGenderAppropriateness(items: ClothingItem[], userProfile: UserProfile): ValidationResult {
  const warnings: string[] = [];
  const gender = userProfile.gender?.toLowerCase();

  if (!gender) return { isValid: true, warnings: [] };

  for (const item of items) {
    const itemGender = item.metadata?.visualAttributes?.genderTarget?.toLowerCase();
    if (itemGender && itemGender !== 'unisex' && itemGender !== gender) {
      warnings.push(`${item.name} is targeted for ${itemGender} but your preference is ${gender}`);
    }
  }

  return {
    isValid: warnings.length === 0,
    warnings
  };
}

export function validateOutfitCompatibility(
  items: ClothingItem[],
  userProfile: UserProfile,
  season: Season
): ValidationResult {
  const results = [
    validateMaterialCompatibility(items),
    validateWeatherAppropriateness(items, season),
    validateSkinToneCompatibility(items, userProfile),
    validateBodyTypeFit(items, userProfile),
    validateGenderAppropriateness(items, userProfile)
  ];

  const allWarnings = results.flatMap(result => result.warnings);
  const isValid = results.every(result => result.isValid);

  return {
    isValid,
    warnings: allWarnings
  };
} 