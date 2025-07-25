import { z } from 'zod';
import { ClothingTypeEnum, CoreCategoryEnum, LayerLevelEnum, WarmthFactorEnum } from '../types';
import { ClothingItem, UserProfile } from '../types/wardrobe';

type ClothingType = z.infer<typeof ClothingTypeEnum>;
type CoreCategory = z.infer<typeof CoreCategoryEnum>;
type LayerLevel = z.infer<typeof LayerLevelEnum>;
type WarmthFactor = z.infer<typeof WarmthFactorEnum>;

// Core category mapping for layering logic
export const CORE_CATEGORY_MAPPING: Record<ClothingType, CoreCategory> = {
  // Tops
  'shirt': 'top',
  'dress_shirt': 'top',
  't-shirt': 'top',
  'blouse': 'top',
  'tank_top': 'top',
  'crop_top': 'top',
  'polo': 'top',
  'sweater': 'top',
  'hoodie': 'top',
  'cardigan': 'top',
  
  // Bottoms
  'pants': 'bottom',
  'shorts': 'bottom',
  'jeans': 'bottom',
  'chinos': 'bottom',
  'slacks': 'bottom',
  'joggers': 'bottom',
  'sweatpants': 'bottom',
  'skirt': 'bottom',
  'mini_skirt': 'bottom',
  'midi_skirt': 'bottom',
  'maxi_skirt': 'bottom',
  'pencil_skirt': 'bottom',
  
  // Dresses
  'dress': 'dress',
  'sundress': 'dress',
  'cocktail_dress': 'dress',
  'maxi_dress': 'dress',
  'mini_dress': 'dress',
  
  // Outerwear
  'jacket': 'outerwear',
  'blazer': 'outerwear',
  'coat': 'outerwear',
  'vest': 'outerwear',
  
  // Shoes
  'shoes': 'shoes',
  'dress_shoes': 'shoes',
  'loafers': 'shoes',
  'sneakers': 'shoes',
  'boots': 'shoes',
  'sandals': 'shoes',
  'heels': 'shoes',
  'flats': 'shoes',
  
  // Accessories
  'accessory': 'accessory',
  'hat': 'accessory',
  'scarf': 'accessory',
  'belt': 'accessory',
  'jewelry': 'accessory',
  'bag': 'accessory',
  'watch': 'accessory',
  
  // Other
  'other': 'accessory'
};

// Layer level mapping for layering logic
export const LAYER_LEVEL_MAPPING: Record<ClothingType, LayerLevel> = {
  // Base/Inner layers
  't-shirt': 'base',
  'tank_top': 'base',
  'crop_top': 'base',
  
  // Inner layers
  'shirt': 'inner',
  'dress_shirt': 'inner',
  'blouse': 'inner',
  'polo': 'inner',
  
  // Middle layers
  'sweater': 'middle',
  'hoodie': 'middle',
  'cardigan': 'middle',
  'vest': 'middle',
  
  // Outer layers
  'jacket': 'outer',
  'blazer': 'outer',
  'coat': 'outer',
  
  // Non-layering items
  'pants': 'base',
  'shorts': 'base',
  'jeans': 'base',
  'chinos': 'base',
  'slacks': 'base',
  'joggers': 'base',
  'sweatpants': 'base',
  'skirt': 'base',
  'mini_skirt': 'base',
  'midi_skirt': 'base',
  'maxi_skirt': 'base',
  'pencil_skirt': 'base',
  'dress': 'base',
  'sundress': 'base',
  'cocktail_dress': 'base',
  'maxi_dress': 'base',
  'mini_dress': 'base',
  'shoes': 'base',
  'dress_shoes': 'base',
  'loafers': 'base',
  'sneakers': 'base',
  'boots': 'base',
  'sandals': 'base',
  'heels': 'base',
  'flats': 'base',
  'accessory': 'base',
  'hat': 'base',
  'scarf': 'base',
  'belt': 'base',
  'jewelry': 'base',
  'bag': 'base',
  'watch': 'base',
  'other': 'base'
};

// Warmth factor mapping for temperature-based layering
export const WARMTH_FACTOR_MAPPING: Record<ClothingType, WarmthFactor> = {
  // Light items
  't-shirt': 'light',
  'tank_top': 'light',
  'crop_top': 'light',
  'blouse': 'light',
  'polo': 'light',
  'shorts': 'light',
  'mini_skirt': 'light',
  'sundress': 'light',
  'mini_dress': 'light',
  'sandals': 'light',
  'flats': 'light',
  'accessory': 'light',
  'hat': 'light',
  'belt': 'light',
  'jewelry': 'light',
  'watch': 'light',
  
  // Medium items
  'shirt': 'medium',
  'dress_shirt': 'medium',
  'pants': 'medium',
  'jeans': 'medium',
  'chinos': 'medium',
  'slacks': 'medium',
  'joggers': 'medium',
  'sweatpants': 'medium',
  'skirt': 'medium',
  'midi_skirt': 'medium',
  'maxi_skirt': 'medium',
  'pencil_skirt': 'medium',
  'dress': 'medium',
  'cocktail_dress': 'medium',
  'maxi_dress': 'medium',
  'sweater': 'medium',
  'hoodie': 'medium',
  'cardigan': 'medium',
  'vest': 'medium',
  'shoes': 'medium',
  'dress_shoes': 'medium',
  'loafers': 'medium',
  'sneakers': 'medium',
  'boots': 'medium',
  'heels': 'medium',
  'scarf': 'medium',
  'bag': 'medium',
  
  // Heavy items
  'jacket': 'heavy',
  'blazer': 'heavy',
  'coat': 'heavy',
  'other': 'medium'
};

// Can layer mapping - which items can be layered
export const CAN_LAYER_MAPPING: Record<ClothingType, boolean> = {
  // Items that can be layered
  'shirt': true,
  'dress_shirt': true,
  't-shirt': true,
  'blouse': true,
  'tank_top': true,
  'crop_top': true,
  'polo': true,
  'sweater': true,
  'hoodie': true,
  'cardigan': true,
  'jacket': true,
  'blazer': true,
  'coat': true,
  'vest': true,
  'scarf': true,
  
  // Items that cannot be layered
  'pants': false,
  'shorts': false,
  'jeans': false,
  'chinos': false,
  'slacks': false,
  'joggers': false,
  'sweatpants': false,
  'skirt': false,
  'mini_skirt': false,
  'midi_skirt': false,
  'maxi_skirt': false,
  'pencil_skirt': false,
  'dress': false,
  'sundress': false,
  'cocktail_dress': false,
  'maxi_dress': false,
  'mini_dress': false,
  'shoes': false,
  'dress_shoes': false,
  'loafers': false,
  'sneakers': false,
  'boots': false,
  'sandals': false,
  'heels': false,
  'flats': false,
  'accessory': false,
  'hat': false,
  'belt': false,
  'jewelry': false,
  'bag': false,
  'watch': false,
  'other': false
};

// Maximum layers mapping - how many layers an item can support
export const MAX_LAYERS_MAPPING: Record<ClothingType, number> = {
  // Items that can support multiple layers
  'jacket': 4,
  'coat': 4,
  'blazer': 3,
  'cardigan': 3,
  'vest': 3,
  'sweater': 2,
  'hoodie': 2,
  'shirt': 2,
  'dress_shirt': 2,
  'blouse': 2,
  'polo': 2,
  't-shirt': 1,
  'tank_top': 1,
  'crop_top': 1,
  
  // Non-layering items
  'pants': 1,
  'shorts': 1,
  'jeans': 1,
  'chinos': 1,
  'slacks': 1,
  'joggers': 1,
  'sweatpants': 1,
  'skirt': 1,
  'mini_skirt': 1,
  'midi_skirt': 1,
  'maxi_skirt': 1,
  'pencil_skirt': 1,
  'dress': 1,
  'sundress': 1,
  'cocktail_dress': 1,
  'maxi_dress': 1,
  'mini_dress': 1,
  'shoes': 1,
  'dress_shoes': 1,
  'loafers': 1,
  'sneakers': 1,
  'boots': 1,
  'sandals': 1,
  'heels': 1,
  'flats': 1,
  'accessory': 1,
  'hat': 1,
  'scarf': 1,
  'belt': 1,
  'jewelry': 1,
  'bag': 1,
  'watch': 1,
  'other': 1
};

// Utility functions for layering logic
export const getCoreCategory = (clothingType: ClothingType): CoreCategory => {
  return CORE_CATEGORY_MAPPING[clothingType] || 'accessory';
};

export const getLayerLevel = (clothingType: ClothingType): LayerLevel => {
  return LAYER_LEVEL_MAPPING[clothingType] || 'base';
};

export const getWarmthFactor = (clothingType: ClothingType): WarmthFactor => {
  return WARMTH_FACTOR_MAPPING[clothingType] || 'medium';
};

export const canLayer = (clothingType: ClothingType): boolean => {
  return CAN_LAYER_MAPPING[clothingType] || false;
};

export const getMaxLayers = (clothingType: ClothingType): number => {
  return MAX_LAYERS_MAPPING[clothingType] || 1;
};

// Temperature-based layering rules
export const getLayeringRule = (temperature: number) => {
  if (temperature < 32) {
    return {
      minLayers: 3,
      maxLayers: 5,
      requiredCategories: ['top', 'outerwear'],
      preferredWarmth: ['medium', 'heavy'] as WarmthFactor[],
      notes: 'Heavy layering required with thermal base layer'
    };
  } else if (temperature < 50) {
    return {
      minLayers: 2,
      maxLayers: 4,
      requiredCategories: ['top'],
      preferredWarmth: ['medium', 'heavy'] as WarmthFactor[],
      notes: 'Medium layering with warm materials'
    };
  } else if (temperature < 65) {
    return {
      minLayers: 1,
      maxLayers: 3,
      requiredCategories: ['top'],
      preferredWarmth: ['light', 'medium'] as WarmthFactor[],
      notes: 'Light layering with breathable materials'
    };
  } else if (temperature < 75) {
    return {
      minLayers: 1,
      maxLayers: 2,
      requiredCategories: ['top'],
      preferredWarmth: ['light', 'medium'] as WarmthFactor[],
      notes: 'Single layer with light materials'
    };
  } else if (temperature < 85) {
    return {
      minLayers: 1,
      maxLayers: 2,
      requiredCategories: ['top'],
      preferredWarmth: ['light'] as WarmthFactor[],
      notes: 'Light, breathable single layer'
    };
  } else {
    return {
      minLayers: 1,
      maxLayers: 1,
      requiredCategories: ['top'],
      preferredWarmth: ['light'] as WarmthFactor[],
      notes: 'Minimal, breathable clothing'
    };
  }
};

// Validate layering compatibility
export const validateLayeringCompatibility = (
  items: Array<{ type: ClothingType; layerLevel?: LayerLevel; warmthFactor?: WarmthFactor }>,
  temperature: number
) => {
  const rule = getLayeringRule(temperature);
  const errors: string[] = [];
  const warnings: string[] = [];
  
  // Count layers by category
  const layersByCategory = new Map<CoreCategory, number>();
  const layersByLevel = new Map<LayerLevel, number>();
  
  items.forEach(item => {
    const category = getCoreCategory(item.type);
    const layerLevel = item.layerLevel || getLayerLevel(item.type);
    const warmthFactor = item.warmthFactor || getWarmthFactor(item.type);
    
    layersByCategory.set(category, (layersByCategory.get(category) || 0) + 1);
    layersByLevel.set(layerLevel, (layersByLevel.get(layerLevel) || 0) + 1);
    
    // Check warmth appropriateness
    if (!rule.preferredWarmth.includes(warmthFactor)) {
      warnings.push(`${item.type} may be too ${warmthFactor} for ${temperature}°F weather`);
    }
  });
  
  // Check minimum layers
  const totalLayers = items.filter(item => canLayer(item.type)).length;
  if (totalLayers < rule.minLayers) {
    errors.push(`Insufficient layering for ${temperature}°F weather. Need at least ${rule.minLayers} layers.`);
  }
  
  // Check maximum layers
  if (totalLayers > rule.maxLayers) {
    warnings.push(`Too many layers for ${temperature}°F weather. Consider removing some items.`);
  }
  
  // Check required categories
  rule.requiredCategories.forEach(category => {
    if (!layersByCategory.has(category as CoreCategory)) {
      errors.push(`Missing required category: ${category}`);
    }
  });
  
  return { errors, warnings, isValid: errors.length === 0 };
};

// Get layering suggestions
export const getLayeringSuggestions = (
  items: Array<{ type: ClothingType; layerLevel?: LayerLevel; warmthFactor?: WarmthFactor }>,
  temperature: number
) => {
  const rule = getLayeringRule(temperature);
  const suggestions: string[] = [];
  
  const currentLayers = items.filter(item => canLayer(item.type)).length;
  const currentCategories = new Set(items.map(item => getCoreCategory(item.type)));
  
  if (currentLayers < rule.minLayers) {
    suggestions.push(`Add ${rule.minLayers - currentLayers} more layer(s) for ${temperature}°F weather`);
  }
  
  rule.requiredCategories.forEach(category => {
    if (!currentCategories.has(category as CoreCategory)) {
      suggestions.push(`Add a ${category} item for complete outfit`);
    }
  });
  
  return suggestions;
};

// Enhanced color compatibility for different skin tones
export const SKIN_TONE_COLOR_COMPATIBILITY: Record<string, Record<string, string[]>> = {
  'warm': {
    'flattering_colors': ['coral', 'peach', 'gold', 'olive', 'terracotta', 'warm_red', 'orange', 'yellow', 'brown'],
    'avoid_colors': ['cool_blue', 'silver', 'cool_pink', 'purple'],
    'neutral_colors': ['cream', 'beige', 'warm_white', 'camel', 'tan']
  },
  'cool': {
    'flattering_colors': ['blue', 'purple', 'pink', 'silver', 'cool_red', 'emerald', 'teal', 'navy'],
    'avoid_colors': ['orange', 'yellow', 'warm_red', 'gold'],
    'neutral_colors': ['white', 'cool_gray', 'navy', 'charcoal']
  },
  'neutral': {
    'flattering_colors': ['navy', 'gray', 'white', 'black', 'beige', 'mauve', 'rose', 'sage'],
    'avoid_colors': ['bright_orange', 'neon_yellow', 'electric_pink'],
    'neutral_colors': ['white', 'black', 'gray', 'beige', 'navy']
  },
  'olive': {
    'flattering_colors': ['olive', 'sage', 'mauve', 'rose', 'camel', 'brown', 'cream'],
    'avoid_colors': ['bright_orange', 'neon_yellow', 'electric_pink'],
    'neutral_colors': ['cream', 'beige', 'warm_white', 'camel', 'tan']
  },
  'deep': {
    'flattering_colors': ['deep_red', 'purple', 'emerald', 'navy', 'gold', 'cream', 'white'],
    'avoid_colors': ['pastel_pink', 'light_yellow', 'mint'],
    'neutral_colors': ['white', 'cream', 'beige', 'navy', 'charcoal']
  },
  'medium': {
    'flattering_colors': ['blue', 'green', 'purple', 'pink', 'coral', 'navy', 'gray'],
    'avoid_colors': ['neon_colors', 'very_pale_pastels'],
    'neutral_colors': ['white', 'black', 'gray', 'beige', 'navy']
  },
  'fair': {
    'flattering_colors': ['navy', 'gray', 'rose', 'sage', 'cream', 'soft_pink'],
    'avoid_colors': ['bright_orange', 'neon_yellow', 'electric_pink'],
    'neutral_colors': ['white', 'cream', 'beige', 'navy', 'charcoal']
  }
};

// Body type layering recommendations
export const BODY_TYPE_LAYERING_RECOMMENDATIONS: Record<string, Record<string, string[]>> = {
  'hourglass': {
    'flattering_layers': ['fitted_tops', 'belted_waist', 'structured_jackets', 'wrap_styles'],
    'avoid_layers': ['boxy_shapes', 'oversized_tops', 'baggy_layers'],
    'layer_priorities': ['define_waist', 'balance_proportions', 'show_curves']
  },
  'pear': {
    'flattering_layers': ['fitted_tops', 'structured_jackets', 'longer_tops', 'dark_bottoms'],
    'avoid_layers': ['short_tops', 'light_bottoms', 'tight_bottoms'],
    'layer_priorities': ['draw_attention_up', 'balance_lower_body', 'create_length']
  },
  'apple': {
    'flattering_layers': ['longer_tops', 'structured_jackets', 'dark_colors', 'v_necks'],
    'avoid_layers': ['crop_tops', 'tight_tops', 'short_jackets'],
    'layer_priorities': ['create_length', 'define_waist', 'draw_attention_down']
  },
  'rectangle': {
    'flattering_layers': ['layered_looks', 'belts', 'structured_pieces', 'textured_layers'],
    'avoid_layers': ['boxy_shapes', 'single_layer_looks'],
    'layer_priorities': ['create_curves', 'add_dimension', 'define_waist']
  },
  'inverted_triangle': {
    'flattering_layers': ['darker_tops', 'lighter_bottoms', 'v_necks', 'longer_tops'],
    'avoid_layers': ['wide_shoulders', 'bright_tops', 'short_jackets'],
    'layer_priorities': ['balance_shoulders', 'draw_attention_down', 'create_waist']
  },
  'athletic': {
    'flattering_layers': ['fitted_pieces', 'structured_layers', 'textured_fabrics', 'belts'],
    'avoid_layers': ['baggy_layers', 'oversized_pieces'],
    'layer_priorities': ['create_curves', 'add_dimension', 'define_shape']
  },
  'curvy': {
    'flattering_layers': ['fitted_tops', 'structured_jackets', 'wrap_styles', 'belted_waist'],
    'avoid_layers': ['boxy_shapes', 'oversized_pieces', 'baggy_layers'],
    'layer_priorities': ['define_waist', 'show_curves', 'balance_proportions']
  }
};

// Style preference layering patterns
export const STYLE_PREFERENCE_LAYERING: Record<string, Record<string, string[]>> = {
  'minimalist': {
    'layer_approach': ['clean_lines', 'monochromatic', 'simple_layers', 'structured_pieces'],
    'preferred_layers': ['blazer', 'sweater', 'structured_jacket'],
    'avoid_layers': ['busy_patterns', 'multiple_accessories', 'complex_layering']
  },
  'bohemian': {
    'layer_approach': ['flowy_layers', 'textured_fabrics', 'mixed_patterns', 'natural_materials'],
    'preferred_layers': ['cardigan', 'vest', 'flowy_jacket', 'scarf'],
    'avoid_layers': ['structured_blazers', 'formal_coats']
  },
  'streetwear': {
    'layer_approach': ['oversized_layers', 'sporty_pieces', 'mixed_styles', 'bold_statements'],
    'preferred_layers': ['hoodie', 'oversized_jacket', 'vest', 'sports_jacket'],
    'avoid_layers': ['formal_blazers', 'structured_coats']
  },
  'classic': {
    'layer_approach': ['timeless_layers', 'structured_pieces', 'quality_fabrics', 'refined_looks'],
    'preferred_layers': ['blazer', 'structured_jacket', 'cardigan', 'coat'],
    'avoid_layers': ['trendy_pieces', 'oversized_layers', 'casual_layers']
  },
  'romantic': {
    'layer_approach': ['soft_layers', 'flowy_fabrics', 'feminine_details', 'delicate_layers'],
    'preferred_layers': ['cardigan', 'flowy_jacket', 'scarf', 'vest'],
    'avoid_layers': ['structured_blazers', 'sporty_jackets']
  },
  'edgy': {
    'layer_approach': ['bold_layers', 'contrasting_pieces', 'mixed_materials', 'statement_layers'],
    'preferred_layers': ['leather_jacket', 'structured_blazer', 'vest', 'bold_jacket'],
    'avoid_layers': ['soft_layers', 'delicate_pieces']
  },
  'casual': {
    'layer_approach': ['comfortable_layers', 'easy_pieces', 'practical_layers', 'relaxed_fits'],
    'preferred_layers': ['hoodie', 'cardigan', 'casual_jacket', 'vest'],
    'avoid_layers': ['formal_blazers', 'structured_coats']
  },
  'formal': {
    'layer_approach': ['structured_layers', 'quality_fabrics', 'refined_details', 'professional_looks'],
    'preferred_layers': ['blazer', 'structured_jacket', 'coat', 'vest'],
    'avoid_layers': ['casual_layers', 'sporty_pieces']
  }
};

export const getSkinToneColorRecommendations = (skinTone: string) => {
  return SKIN_TONE_COLOR_COMPATIBILITY[skinTone.toLowerCase()] || {
    flattering_colors: [],
    avoid_colors: [],
    neutral_colors: []
  };
};

export const getBodyTypeLayeringRecommendations = (bodyType: string) => {
  return BODY_TYPE_LAYERING_RECOMMENDATIONS[bodyType.toLowerCase()] || {
    flattering_layers: [],
    avoid_layers: [],
    layer_priorities: []
  };
};

export const getStylePreferenceLayering = (stylePreference: string) => {
  return STYLE_PREFERENCE_LAYERING[stylePreference.toLowerCase()] || {
    layer_approach: [],
    preferred_layers: [],
    avoid_layers: []
  };
};

export const validateColorSkinToneCompatibility = (itemColor: string, skinTone: string) => {
  if (!skinTone || !itemColor) {
    return { compatible: true, score: 0.5, reason: 'Missing skin tone or color information' };
  }

  const recommendations = getSkinToneColorRecommendations(skinTone);
  const colorLower = itemColor.toLowerCase();

  // Check if color is flattering
  if (recommendations.flattering_colors.includes(colorLower)) {
    return { compatible: true, score: 1.0, reason: `${itemColor} is flattering for ${skinTone} skin tone` };
  }

  // Check if color should be avoided
  if (recommendations.avoid_colors.includes(colorLower)) {
    return { compatible: false, score: 0.0, reason: `${itemColor} may not be ideal for ${skinTone} skin tone` };
  }

  // Check if color is neutral
  if (recommendations.neutral_colors.includes(colorLower)) {
    return { compatible: true, score: 0.8, reason: `${itemColor} is a neutral color for ${skinTone} skin tone` };
  }

  // Default to moderate compatibility
  return { compatible: true, score: 0.6, reason: `${itemColor} has moderate compatibility with ${skinTone} skin tone` };
};

export const validateBodyTypeLayeringCompatibility = (items: ClothingItem[], bodyType: string) => {
  if (!bodyType) {
    return { compatible: true, score: 0.5, warnings: [], suggestions: [] };
  }

  const recommendations = getBodyTypeLayeringRecommendations(bodyType);
  const warnings: string[] = [];
  const suggestions: string[] = [];
  let score = 1.0;

  // Analyze the layering approach
  const topItems = items.filter(item => getCoreCategory(item.type) === 'top');
  const outerwearItems = items.filter(item => getCoreCategory(item.type) === 'outerwear');

  // Check for body type specific recommendations
  if (bodyType.toLowerCase() === 'pear') {
    if (topItems.length === 0) {
      warnings.push('Pear body types benefit from fitted tops to balance proportions');
      score -= 0.2;
    }
    if (outerwearItems.length === 0) {
      suggestions.push('Consider adding a structured jacket to draw attention upward');
    }
  } else if (bodyType.toLowerCase() === 'apple') {
    if (topItems.some(item => item.type.toLowerCase().includes('crop'))) {
      warnings.push('Crop tops may not be ideal for apple body types');
      score -= 0.3;
    }
    if (outerwearItems.length === 0) {
      suggestions.push('Consider adding a longer jacket to create length');
    }
  } else if (bodyType.toLowerCase() === 'rectangle') {
    if (items.length < 3) {
      suggestions.push('Rectangle body types benefit from layered looks to create curves');
      score -= 0.1;
    }
  } else if (bodyType.toLowerCase() === 'hourglass') {
    if (topItems.length === 0) {
      warnings.push('Hourglass body types benefit from fitted tops to show curves');
      score -= 0.2;
    }
  }

  return {
    compatible: score > 0.5,
    score: Math.max(0.0, score),
    warnings,
    suggestions
  };
};

export const validateStylePreferenceCompatibility = (items: ClothingItem[], stylePreferences: string[]) => {
  if (!stylePreferences || stylePreferences.length === 0) {
    return { compatible: true, score: 0.5, warnings: [], suggestions: [] };
  }

  const warnings: string[] = [];
  const suggestions: string[] = [];
  let score = 1.0;

  for (const style of stylePreferences) {
    const styleRec = getStylePreferenceLayering(style);

    // Check if items match preferred layers
    const itemTypes = items.map(item => item.type.toLowerCase());
    const preferredLayers = styleRec.preferred_layers.map(layer => layer.toLowerCase());

    // Calculate how many preferred layers are present
    const matchingLayers = preferredLayers.filter(layer => 
      itemTypes.some(itemType => itemType.includes(layer))
    ).length;

    if (matchingLayers === 0) {
      warnings.push(`No preferred ${style} layering pieces found`);
      score -= 0.2;
    } else if (matchingLayers < 2) {
      suggestions.push(`Consider adding more ${style} layering pieces`);
      score -= 0.1;
    }
  }

  return {
    compatible: score > 0.5,
    score: Math.max(0.0, score),
    warnings,
    suggestions
  };
};

export const getPersonalizedLayeringSuggestions = (
  items: ClothingItem[],
  temperature: number,
  skinTone?: string,
  bodyType?: string,
  stylePreferences?: string[]
) => {
  const suggestions: string[] = [];
  const warnings: string[] = [];
  const recommendations: string[] = [];

  // Basic temperature-based suggestions
  const tempSuggestions = getLayeringSuggestions(items, temperature);
  suggestions.push(...tempSuggestions);

  // Skin tone color suggestions
  if (skinTone) {
    const colorRec = getSkinToneColorRecommendations(skinTone);
    if (colorRec.flattering_colors.length > 0) {
      recommendations.push(`Consider colors like ${colorRec.flattering_colors.slice(0, 3).join(', ')} for your ${skinTone} skin tone`);
    }
  }

  // Body type suggestions
  if (bodyType) {
    const bodyRec = getBodyTypeLayeringRecommendations(bodyType);
    if (bodyRec.layer_priorities.length > 0) {
      recommendations.push(`For your ${bodyType} body type, focus on: ${bodyRec.layer_priorities.slice(0, 2).join(', ')}`);
    }
  }

  // Style preference suggestions
  if (stylePreferences) {
    for (const style of stylePreferences.slice(0, 2)) { // Limit to top 2 preferences
      const styleRec = getStylePreferenceLayering(style);
      if (styleRec.preferred_layers.length > 0) {
        recommendations.push(`For ${style} style, try: ${styleRec.preferred_layers.slice(0, 2).join(', ')}`);
      }
    }
  }

  return {
    suggestions,
    warnings,
    recommendations,
    temperature_based: tempSuggestions,
    personalized: recommendations
  };
};

export const calculatePersonalizedLayeringScore = (
  items: ClothingItem[],
  temperature: number,
  skinTone?: string,
  bodyType?: string,
  stylePreferences?: string[]
) => {
  let baseScore = 0.5;

  // Temperature compatibility (30% weight)
  const tempValidation = validateLayeringCompatibility(items, temperature);
  baseScore += (tempValidation.isValid ? 0.8 : 0.3) * 0.3;

  // Skin tone compatibility (20% weight)
  if (skinTone) {
    const colorScores: number[] = [];
    for (const item of items) {
      const color = item.color || '';
      if (color) {
        const colorValidation = validateColorSkinToneCompatibility(color, skinTone);
        colorScores.push(colorValidation.score);
      }
    }

    if (colorScores.length > 0) {
      const avgColorScore = colorScores.reduce((a, b) => a + b, 0) / colorScores.length;
      baseScore += avgColorScore * 0.2;
    }
  }

  // Body type compatibility (25% weight)
  if (bodyType) {
    const bodyValidation = validateBodyTypeLayeringCompatibility(items, bodyType);
    baseScore += bodyValidation.score * 0.25;
  }

  // Style preference compatibility (25% weight)
  if (stylePreferences) {
    const styleValidation = validateStylePreferenceCompatibility(items, stylePreferences);
    baseScore += styleValidation.score * 0.25;
  }

  return Math.min(1.0, Math.max(0.0, baseScore));
};

export const getEnhancedLayeringValidation = (
  items: ClothingItem[],
  temperature: number,
  userProfile?: UserProfile
) => {
  if (!userProfile) {
    return validateLayeringCompatibility(items, temperature);
  }

  const skinTone = userProfile.skinTone || userProfile.measurements?.skinTone;
  const bodyType = userProfile.bodyType || userProfile.measurements?.bodyType;
  const stylePreferences = userProfile.stylePreferences || [];

  // Get all validation results
  const tempValidation = validateLayeringCompatibility(items, temperature);
  const colorValidation = skinTone ? validateColorSkinToneCompatibility('', skinTone) : { compatible: true, score: 0.5 };
  const bodyValidation = bodyType ? validateBodyTypeLayeringCompatibility(items, bodyType) : { compatible: true, score: 0.5 };
  const styleValidation = stylePreferences.length > 0 ? validateStylePreferenceCompatibility(items, stylePreferences) : { compatible: true, score: 0.5 };

  // Calculate overall score
  const overallScore = calculatePersonalizedLayeringScore(
    items, temperature, skinTone, bodyType, stylePreferences
  );

  // Combine all suggestions and warnings
  const allSuggestions: string[] = [];
  const allWarnings: string[] = [];

  if ('suggestions' in bodyValidation && bodyValidation.suggestions) {
    allSuggestions.push(...bodyValidation.suggestions);
  }

  if ('suggestions' in styleValidation && styleValidation.suggestions) {
    allSuggestions.push(...styleValidation.suggestions);
  }

  if ('warnings' in bodyValidation && bodyValidation.warnings) {
    allWarnings.push(...bodyValidation.warnings);
  }

  if ('warnings' in styleValidation && styleValidation.warnings) {
    allWarnings.push(...styleValidation.warnings);
  }

  return {
    isValid: overallScore > 0.6,
    overallScore,
    temperatureScore: tempValidation.isValid ? 0.8 : 0.3,
    colorScore: colorValidation.score || 0.5,
    bodyTypeScore: bodyValidation.score || 0.5,
    styleScore: styleValidation.score || 0.5,
    suggestions: allSuggestions,
    warnings: allWarnings,
    personalizedRecommendations: getPersonalizedLayeringSuggestions(
      items, temperature, skinTone, bodyType, stylePreferences
    )
  };
}; 