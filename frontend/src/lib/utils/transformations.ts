import { ClothingItem } from '@/types/wardrobe';

export interface ColorObject {
  hex: string;
  name: string;
  rgb: [number, number, number];
}

export interface ColorAnalysis {
  dominant: ColorObject[];
  matching: ColorObject[];
}

export interface ItemMetadata {
  analysisTimestamp?: number | null;
  originalType?: string | null;
  styleTags?: string[] | null;
  occasionTags?: string[] | null;
  colorAnalysis?: ColorAnalysis;
  basicMetadata?: {
    width?: number | null;
    height?: number | null;
    orientation?: string | null;
    dateTaken?: string | null;
    deviceModel?: string | null;
    gps?: {
      latitude: number;
      longitude: number;
    } | null;
    flashUsed?: boolean | null;
  } | null;
  visualAttributes?: {
    material?: string | null;
    pattern?: string | null;
    textureStyle?: string | null;
    fabricWeight?: string | null;
    fit?: string | null;
    silhouette?: string | null;
    length?: string | null;
    genderTarget?: string | null;
    sleeveLength?: string | null;
    hangerPresent?: boolean | null;
    backgroundRemoved?: boolean | null;
    wearLayer?: string | null;
    formalLevel?: string | null;
  } | null;
  itemMetadata?: {
    priceEstimate?: string | null;
    careInstructions?: string | null;
    tags?: string[] | null;
  } | null;
  naturalDescription?: string | null;
  [key: string]: any;
}

export type TransformedClothingItem = ClothingItem;

/**
 * Transforms an array of colors (strings or objects) into an array of color objects
 */
export function transformColorArray(colors: (string | { name?: string; hex?: string; rgb?: number[] })[]): Array<{ hex: string; name: string; rgb: [number, number, number] }> {
  if (!Array.isArray(colors)) return [];
  
  return colors
    .map(color => {
      if (typeof color === 'string') {
        // Map common color names to hex and RGB values
        const colorMap: { [key: string]: { hex: string; rgb: [number, number, number] } } = {
          'Dark Gray': { hex: '#404040', rgb: [64, 64, 64] },
          'Black': { hex: '#000000', rgb: [0, 0, 0] },
          'Navy': { hex: '#000080', rgb: [0, 0, 128] },
          'Blue': { hex: '#0000FF', rgb: [0, 0, 255] },
          'Light Blue': { hex: '#ADD8E6', rgb: [173, 216, 230] },
          'Gray': { hex: '#808080', rgb: [128, 128, 128] },
          'White': { hex: '#FFFFFF', rgb: [255, 255, 255] },
          'Red': { hex: '#FF0000', rgb: [255, 0, 0] },
          'Green': { hex: '#008000', rgb: [0, 128, 0] },
          'Brown': { hex: '#A52A2A', rgb: [165, 42, 42] },
          'Tan': { hex: '#D2B48C', rgb: [210, 180, 140] },
          'Beige': { hex: '#F5F5DC', rgb: [245, 245, 220] },
          'Olive Green': { hex: '#808000', rgb: [128, 128, 0] },
          'Gold': { hex: '#FFD700', rgb: [255, 215, 0] },
          'Crimson': { hex: '#DC143C', rgb: [220, 20, 60] },
          'Burnt Orange': { hex: '#CC5500', rgb: [204, 85, 0] }
        };

        const colorInfo = colorMap[color] || { hex: '#000000', rgb: [0, 0, 0] as [number, number, number] };
        return {
          hex: colorInfo.hex,
          name: color,
          rgb: colorInfo.rgb
        };
      }
      if (typeof color === 'object' && color !== null) {
        const hex = color.hex || '#000000';
        const name = color.name || '';
        let rgb: [number, number, number] = [0, 0, 0];

        if (Array.isArray(color.rgb) && color.rgb.length === 3) {
          rgb = [
            Number(color.rgb[0]) || 0,
            Number(color.rgb[1]) || 0,
            Number(color.rgb[2]) || 0
          ] as [number, number, number];
        }

        return { hex, name, rgb };
      }
      return null;
    })
    .filter((color): color is { hex: string; name: string; rgb: [number, number, number] } => 
      color !== null && color.name !== ''
    );
}

/**
 * Transforms a clothing item's colors into the expected format
 */
export function transformItemColors(item: ClothingItem): TransformedClothingItem {
  const { dominantColors, matchingColors, ...rest } = item;
  const metadata = item.metadata ? JSON.parse(JSON.stringify(item.metadata)) : {};

  // Ensure required metadata fields are present
  metadata.originalType = item.type;
  metadata.analysisTimestamp = item.createdAt || Date.now();

  // Transform color arrays to objects
  const transformedColors: ColorAnalysis = {
    dominant: [],
    matching: []
  };

  // Process dominant colors - check root level first, then metadata
  if (Array.isArray(dominantColors) && dominantColors.length > 0) {
    transformedColors.dominant = transformColorArray(dominantColors);
  } else if (metadata.colorAnalysis?.dominant) {
    transformedColors.dominant = transformColorArray(metadata.colorAnalysis.dominant);
  }

  // Process matching colors - check root level first, then metadata
  if (Array.isArray(matchingColors) && matchingColors.length > 0) {
    transformedColors.matching = transformColorArray(matchingColors);
  } else if (metadata.colorAnalysis?.matching) {
    transformedColors.matching = transformColorArray(metadata.colorAnalysis.matching);
  }

  // Transform visual attributes
  if (metadata.visualAttributes) {
    // Transform fit values
    if (metadata.visualAttributes.fit) {
      const fit = metadata.visualAttributes.fit.toLowerCase();
      if (fit === 'regular' || fit === 'standard') {
        metadata.visualAttributes.fit = 'slim';
      } else if (!['slim', 'loose', 'oversized'].includes(fit)) {
        metadata.visualAttributes.fit = null;
      } else {
        metadata.visualAttributes.fit = fit;
      }
    } else {
      metadata.visualAttributes.fit = null;
    }

    // Transform fabric weight
    if (metadata.visualAttributes.fabricWeight) {
      const weight = metadata.visualAttributes.fabricWeight.toLowerCase();
      if (['light', 'medium', 'heavy'].includes(weight)) {
        metadata.visualAttributes.fabricWeight = weight;
      } else {
        metadata.visualAttributes.fabricWeight = null;
      }
    } else {
      metadata.visualAttributes.fabricWeight = null;
    }

    // Transform wear layer
    if (metadata.visualAttributes.wearLayer) {
      const layer = metadata.visualAttributes.wearLayer.toLowerCase();
      if (['inner', 'outer', 'base'].includes(layer)) {
        metadata.visualAttributes.wearLayer = layer;
      } else {
        metadata.visualAttributes.wearLayer = null;
      }
    } else {
      metadata.visualAttributes.wearLayer = null;
    }

    // Transform formal level
    if (metadata.visualAttributes.formalLevel) {
      const level = metadata.visualAttributes.formalLevel.toLowerCase();
      if (['casual', 'semi-formal', 'formal'].includes(level)) {
        metadata.visualAttributes.formalLevel = level;
      } else {
        metadata.visualAttributes.formalLevel = null;
      }
    } else {
      metadata.visualAttributes.formalLevel = null;
    }
  }

  // Update metadata with transformed colors
  metadata.colorAnalysis = transformedColors;

  // Remove undefined fields
  Object.keys(metadata).forEach(key => {
    if (metadata[key] === undefined) {
      delete metadata[key];
    }
  });

  // Ensure all required fields are present
  return {
    ...rest,
    dominantColors: transformedColors.dominant,
    matchingColors: transformedColors.matching,
    metadata
  };
}

/**
 * Transforms an array of clothing items
 */
export function transformWardrobe(wardrobe: ClothingItem[]): TransformedClothingItem[] {
  if (!wardrobe || !Array.isArray(wardrobe)) return [];
  return wardrobe.map(transformItemColors);
} 