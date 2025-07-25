import { ClothingItem } from '../types/wardrobe';

// Helper function to analyze color harmony between two colors
const analyzeColorHarmony = (color1: string, color2: string): number => {
  // Convert colors to RGB for comparison
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);
  
  if (!rgb1 || !rgb2) return 0;
  
  // Calculate color difference using a simple Euclidean distance
  const diff = Math.sqrt(
    Math.pow(rgb1.r - rgb2.r, 2) +
    Math.pow(rgb1.g - rgb2.g, 2) +
    Math.pow(rgb1.b - rgb2.b, 2)
  );
  
  // Normalize to 0-1 range (max distance is sqrt(255^2 * 3))
  const maxDiff = Math.sqrt(255 * 255 * 3);
  return 1 - (diff / maxDiff);
};

// Helper function to convert hex color to RGB
const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
};

// Helper function to check material compatibility
const areMaterialsCompatible = (material1: string, material2: string): boolean => {
  const compatibleMaterials: Record<string, string[]> = {
    'cotton': ['denim', 'linen', 'wool', 'silk'],
    'denim': ['cotton', 'leather', 'wool'],
    'wool': ['cotton', 'silk', 'cashmere'],
    'silk': ['cotton', 'wool', 'cashmere'],
    'leather': ['denim', 'cotton', 'wool'],
    'linen': ['cotton', 'silk'],
    'cashmere': ['wool', 'silk', 'cotton']
  };

  const m1 = material1.toLowerCase();
  const m2 = material2.toLowerCase();

  return m1 === m2 || 
         (compatibleMaterials[m1]?.includes(m2) || 
          compatibleMaterials[m2]?.includes(m1));
};

// Calculate pairability score between two items
const calculatePairScore = (item1: ClothingItem, item2: ClothingItem): number => {
  let score = 0;
  
  // Color harmony
  if (item1.color && item2.color) {
    const colorHarmony = analyzeColorHarmony(item1.color, item2.color);
    score += colorHarmony * 0.4; // 40% weight
  }
  
  // Style compatibility
  const commonStyles = item1.style.filter(s => item2.style.includes(s));
  const styleScore = commonStyles.length / Math.max(item1.style.length, item2.style.length);
  score += styleScore * 0.3; // 30% weight
  
  // Material compatibility
  if (item1.material && item2.material) {
    const materialScore = areMaterialsCompatible(item1.material, item2.material) ? 1 : 0;
    score += materialScore * 0.2; // 20% weight
  }
  
  // Occasion compatibility
  const commonOccasions = item1.occasion.filter(o => item2.occasion.includes(o));
  const occasionScore = commonOccasions.length / Math.max(item1.occasion.length, item2.occasion.length);
  score += occasionScore * 0.1; // 10% weight
  
  return score;
};

// Calculate average pairability score for all items in an outfit
export const averagePairability = (items: ClothingItem[]): number => {
  if (items.length < 2) return 1; // Single item is perfectly pairable
  
  let totalScore = 0;
  let pairCount = 0;
  
  // Calculate pairability for each unique pair
  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      totalScore += calculatePairScore(items[i], items[j]);
      pairCount++;
    }
  }
  
  return pairCount > 0 ? totalScore / pairCount : 0;
}; 