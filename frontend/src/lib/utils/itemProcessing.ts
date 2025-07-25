import { ClothingItem, ClothingType } from '@/types/wardrobe';
import { OpenAIClothingAnalysis } from '@shared/types/wardrobe';
import { z } from "zod";
import { v4 as uuidv4 } from 'uuid';

// --- Robust metadata types and constants (TODO: Move to shared/constants file) ---
type Material = 'cotton' | 'wool' | 'silk' | 'linen' | 'denim' | 'leather' | 'synthetic' | 'knit' | 'fleece' | 'other';
type Season = 'winter' | 'summer' | 'spring' | 'fall';
type BodyType = 'hourglass' | 'pear' | 'apple' | 'rectangle' | 'inverted_triangle';
type SkinTone = 'warm' | 'cool' | 'neutral';

const TEMPERATURE_RANGES: Record<string, { min: number; max: number; layers: Material[] }> = {
  FREEZING: { min: -Infinity, max: 32, layers: ['wool', 'fleece', 'knit'] },
  COLD: { min: 32, max: 50, layers: ['wool', 'knit'] },
  CHILLY: { min: 50, max: 65, layers: ['cotton'] },
  MILD: { min: 65, max: 75, layers: ['cotton', 'linen'] },
  WARM: { min: 75, max: 85, layers: ['cotton', 'linen', 'silk'] },
  HOT: { min: 85, max: Infinity, layers: ['cotton', 'linen'] }
};
const MATERIAL_COMPATIBILITY: Record<Material, Material[]> = {
  cotton: ['denim', 'linen', 'wool', 'silk'],
  denim: ['cotton', 'leather', 'wool'],
  wool: ['cotton', 'silk', 'knit'],
  silk: ['cotton', 'wool', 'knit'],
  leather: ['denim', 'cotton', 'wool'],
  linen: ['cotton', 'silk'],
  synthetic: ['cotton', 'denim'],
  knit: ['wool', 'silk', 'cotton'],
  fleece: ['cotton', 'wool'],
  other: ['cotton', 'denim']
};
const WEATHER_MATERIALS: Record<Season, Material[]> = {
  winter: ['wool', 'knit', 'leather', 'fleece'],
  summer: ['cotton', 'linen', 'silk'],
  spring: ['cotton', 'linen', 'knit'],
  fall: ['wool', 'cotton', 'denim', 'leather']
};
const SKIN_TONE_COLORS: Record<SkinTone, string[]> = {
  warm: ['coral', 'peach', 'gold', 'olive', 'terracotta', 'warm_red'],
  cool: ['blue', 'purple', 'pink', 'silver', 'cool_red', 'emerald'],
  neutral: ['navy', 'gray', 'white', 'black', 'beige', 'mauve']
};
const BODY_TYPE_FITS = {
  recommendedFits: {
    hourglass: ['fitted', 'relaxed'],
    pear: ['fitted_top', 'relaxed_bottom'],
    apple: ['relaxed_top', 'fitted_bottom'],
    rectangle: ['fitted', 'oversized'],
    inverted_triangle: ['relaxed_top', 'fitted_bottom']
  } as Record<BodyType, string[]>,
  styleRecommendations: {
    hourglass: ['balanced', 'defined_waist'],
    pear: ['balance_top', 'accentuate_waist'],
    apple: ['elongate', 'define_waist'],
    rectangle: ['create_curves', 'add_dimension'],
    inverted_triangle: ['balance_shoulders', 'create_waist']
  } as Record<BodyType, string[]>
};

interface ProcessedItemName {
  name: string;
  type: string;
  color: string;
  seasons: string[];
  tags: string[];
}

function getColorAdjective(color: string): string {
  const colorMap: Record<string, string> = {
    'black': 'Ebony',
    'white': 'Ivory',
    'red': 'Crimson',
    'blue': 'Azure',
    'green': 'Emerald',
    'yellow': 'Amber',
    'purple': 'Royal',
    'pink': 'Rose',
    'brown': 'Mahogany',
    'gray': 'Silver',
    'grey': 'Silver',
    'orange': 'Amber',
    'beige': 'Cream',
    'navy': 'Navy',
    'burgundy': 'Burgundy',
    'maroon': 'Maroon',
    'teal': 'Teal',
    'olive': 'Olive',
    'tan': 'Tan',
    'gold': 'Golden',
    'silver': 'Silver'
  };
  return colorMap[color.toLowerCase()] || color;
}

function getMaterialAdjective(material: string): string {
  const materialMap: Record<string, string> = {
    'leather': 'Leather',
    'cotton': 'Cotton',
    'denim': 'Denim',
    'silk': 'Silk',
    'wool': 'Wool',
    'linen': 'Linen',
    'polyester': 'Polyester',
    'nylon': 'Nylon',
    'velvet': 'Velvet',
    'suede': 'Suede',
    'cashmere': 'Cashmere',
    'fleece': 'Fleece',
    'canvas': 'Canvas',
    'tweed': 'Tweed',
    'lace': 'Lace',
    'satin': 'Satin',
    'chiffon': 'Chiffon',
    'knit': 'Knit',
    'mesh': 'Mesh',
    'vinyl': 'Vinyl'
  };
  return materialMap[material.toLowerCase()] || material;
}

// Keep track of item names to ensure uniqueness
const itemNameCounts = new Map<string, number>();

function generateDescriptiveName(analysis: OpenAIClothingAnalysis): string {
  const parts: string[] = [];
  
  // Add color with fancy adjective
  if (analysis.dominantColors?.[0]?.name) {
    parts.push(getColorAdjective(analysis.dominantColors[0].name));
  }
  
  // Add material with fancy adjective
  if (analysis.metadata?.visualAttributes?.material) {
    parts.push(getMaterialAdjective(analysis.metadata.visualAttributes.material));
  }
  
  // Add subType if available, otherwise use type
  if (analysis.subType) {
    parts.push(analysis.subType);
  } else {
    parts.push(analysis.type);
  }
  
  // Add brand if available
  if (analysis.brand) {
    parts.push(`by ${analysis.brand}`);
  }
  
  // Join all parts with spaces and capitalize first letter
  let name = parts.join(' ');
  name = name.charAt(0).toUpperCase() + name.slice(1);

  // Check if this name already exists
  const count = itemNameCounts.get(name) || 0;
  if (count > 0) {
    // Add a subtle numeric suffix
    name = `${name} (${count + 1})`;
  }
  
  // Increment the count for this base name
  itemNameCounts.set(name.split(' (')[0], count + 1);
  
  return name;
}

export function processItemName(name: string): string {
  return name.trim();
}

function normalizeFabricWeight(weight: string | null): 'light' | 'medium' | 'heavy' | null {
  if (!weight) return null;
  const normalized = weight.toLowerCase();
  if (normalized.includes('light')) return 'light';
  if (normalized.includes('medium')) return 'medium';
  if (normalized.includes('heavy')) return 'heavy';
  return null;
}

function normalizeFit(fit: string | null): 'slim' | 'loose' | 'oversized' | null {
  if (!fit) return null;
  const normalized = fit.toLowerCase();
  if (normalized.includes('slim') || normalized.includes('regular')) return 'slim';
  if (normalized.includes('loose')) return 'loose';
  if (normalized.includes('oversized')) return 'oversized';
  return null;
}

function normalizeWearLayer(layer: string | null): 'base' | 'outer' | 'inner' | null {
  if (!layer) return null;
  const normalized = layer.toLowerCase();
  if (normalized.includes('base')) return 'base';
  if (normalized.includes('outer')) return 'outer';
  if (normalized.includes('inner')) return 'inner';
  return null;
}

function normalizeFormalLevel(level: string | null): 'casual' | 'semi-formal' | 'formal' | null {
  if (!level) return null;
  const normalized = level.toLowerCase();
  if (normalized.includes('casual')) return 'casual';
  if (normalized.includes('semi-formal')) return 'semi-formal';
  if (normalized.includes('formal')) return 'formal';
  return null;
}

function normalizeSeason(season: string): 'spring' | 'summer' | 'fall' | 'winter' {
  const normalized = season.toLowerCase();
  if (normalized.includes('spring')) return 'spring';
  if (normalized.includes('summer')) return 'summer';
  if (normalized.includes('fall') || normalized.includes('autumn')) return 'fall';
  if (normalized.includes('winter')) return 'winter';
  return 'spring'; // default to spring if no match
}

export function createClothingItemFromAnalysis(
  analysis: OpenAIClothingAnalysis,
  userId: string,
  imageUrl: string
): ClothingItem {
  // --- Determine robust metadata values ---
  const material = (analysis.metadata?.visualAttributes?.material?.toLowerCase() as Material) || 'cotton';
  const type = (analysis.type || '').toLowerCase();
  let minTemp = 32;
  let maxTemp = 75;
  let recommendedLayers: Material[] = ['cotton'];
  if (type.includes('jacket') || type.includes('coat')) {
    minTemp = -Infinity;
    maxTemp = 50;
    recommendedLayers = ['wool', 'fleece', 'knit'];
  } else if (type.includes('sweater')) {
    minTemp = 32;
    maxTemp = 65;
    recommendedLayers = ['wool', 'knit'];
  }
  const materialPreferences: Material[] = Object.entries(TEMPERATURE_RANGES)
    .filter(([_, range]) => minTemp <= range.max && maxTemp >= range.min)
    .flatMap(([_, range]) => range.layers);

  // --- Build ClothingItem ---
  const item: ClothingItem = {
    id: uuidv4(),
    userId,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    name: analysis.name || generateDescriptiveName(analysis),
    type: analysis.type as ClothingType || 'other',
    subType: analysis.subType,
    color: analysis.dominantColors?.[0]?.name || 'Unknown',
    season: (analysis.season || []).map(normalizeSeason),
    imageUrl,
    style: analysis.style || [],
    occasion: analysis.occasion || [],
    brand: analysis.brand || undefined,
    dominantColors: analysis.dominantColors || [],
    matchingColors: analysis.matchingColors || [],
    tags: analysis.style || [],
    metadata: {
      analysisTimestamp: Date.now(),
      originalType: analysis.type,
      colorAnalysis: {
        dominant: analysis.dominantColors || [],
        matching: analysis.matchingColors || []
      },
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
        material: analysis.metadata?.visualAttributes?.material || null,
        pattern: analysis.metadata?.visualAttributes?.pattern || null,
        textureStyle: analysis.metadata?.visualAttributes?.textureStyle || null,
        fabricWeight: normalizeFabricWeight(analysis.metadata?.visualAttributes?.fabricWeight || null),
        fit: normalizeFit(analysis.metadata?.visualAttributes?.fit || null),
        silhouette: analysis.metadata?.visualAttributes?.silhouette || null,
        length: analysis.metadata?.visualAttributes?.length || null,
        genderTarget: analysis.metadata?.visualAttributes?.genderTarget || 'unisex',
        sleeveLength: analysis.metadata?.visualAttributes?.sleeveLength || null,
        hangerPresent: analysis.metadata?.visualAttributes?.hangerPresent || null,
        backgroundRemoved: analysis.metadata?.visualAttributes?.backgroundRemoved || false,
        wearLayer: normalizeWearLayer(analysis.metadata?.visualAttributes?.wearLayer || null) || 'outer',
        formalLevel: normalizeFormalLevel(analysis.metadata?.visualAttributes?.formalLevel || null) || 'casual',
        // --- Robust metadata fields ---
        temperatureCompatibility: {
          minTemp,
          maxTemp,
          recommendedLayers,
          materialPreferences
        },
        materialCompatibility: {
          compatibleMaterials: MATERIAL_COMPATIBILITY[material] || [],
          weatherAppropriate: WEATHER_MATERIALS
        },
        bodyTypeCompatibility: BODY_TYPE_FITS,
        skinToneCompatibility: {
          compatibleColors: SKIN_TONE_COLORS,
          recommendedPalettes: {
            warm: ['warm_autumn', 'warm_spring'],
            cool: ['cool_winter', 'cool_summer'],
            neutral: ['neutral_autumn', 'neutral_spring']
          }
        },
        outfitScoring: {
          versatility: 5,
          seasonality: 5,
          formality: 5,
          trendiness: 5,
          quality: 5
        }
      },
      itemMetadata: {
        priceEstimate: null,
        careInstructions: null,
        tags: []
      },
      naturalDescription: null
    }
  };
  console.log('Item before validation:', item);
  return item;
} 