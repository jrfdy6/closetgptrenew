import * as tf from '@tensorflow/tfjs';
import * as bodyPix from '@tensorflow-models/body-pix';
import { 
  PhotoAnalysis, 
  BodyMeasurements, 
  ColorAnalysis, 
  OutfitAnalysis,
  BodyType,
  GarmentType,
  GarmentStyle,
  GarmentPattern,
  GarmentFit,
  GarmentMaterial,
  OutfitFormality,
  OutfitOccasion,
  OutfitSeason,
  Garment,
  GarmentDetails
} from '@/types/photo-analysis';

// Initialize TensorFlow.js
const initTensorFlow = async () => {
  await tf.ready();
};

// Load BodyPix model
let net: bodyPix.BodyPix | null = null;
const loadModel = async () => {
  if (!net) {
    net = await bodyPix.load({
      architecture: 'MobileNetV1',
      outputStride: 16,
      multiplier: 0.75,
      quantBytes: 2,
    });
  }
  return net;
};

// Convert image to tensor
const imageToTensor = async (imageData: ImageData): Promise<tf.Tensor3D> => {
  return tf.browser.fromPixels(imageData);
};

// Calculate body measurements from segmentation
const calculateBodyMeasurements = (
  segmentation: bodyPix.SemanticPersonSegmentation,
  imageWidth: number,
  imageHeight: number
): BodyMeasurements => {
  const { data } = segmentation;
  const pixels = new Uint8Array(data.buffer);
  
  // Find body boundaries
  let minX = imageWidth;
  let maxX = 0;
  let minY = imageHeight;
  let maxY = 0;
  
  for (let y = 0; y < imageHeight; y++) {
    for (let x = 0; x < imageWidth; x++) {
      if (pixels[y * imageWidth + x] === 1) {
        minX = Math.min(minX, x);
        maxX = Math.max(maxX, x);
        minY = Math.min(minY, y);
        maxY = Math.max(maxY, y);
      }
    }
  }

  // Calculate measurements (in pixels)
  const height = maxY - minY;
  const shoulderWidth = (maxX - minX) * 0.3; // Approximate shoulder width
  const waistWidth = (maxX - minX) * 0.25; // Approximate waist width
  const hipWidth = (maxX - minX) * 0.3; // Approximate hip width
  const inseam = height * 0.45; // Approximate inseam

  // Convert to centimeters (assuming average height of 170cm)
  const scaleFactor = 170 / height;
  
  return {
    height: Math.round(height * scaleFactor),
    shoulderWidth: Math.round(shoulderWidth * scaleFactor),
    waistWidth: Math.round(waistWidth * scaleFactor),
    hipWidth: Math.round(hipWidth * scaleFactor),
    inseam: Math.round(inseam * scaleFactor),
    bodyType: determineBodyType(shoulderWidth, waistWidth, hipWidth),
  };
};

// Determine body type based on measurements
const determineBodyType = (
  shoulderWidth: number,
  waistWidth: number,
  hipWidth: number
): BodyType => {
  const shoulderToWaistRatio = shoulderWidth / waistWidth;
  const waistToHipRatio = waistWidth / hipWidth;

  if (Math.abs(shoulderToWaistRatio - 1) < 0.1 && Math.abs(waistToHipRatio - 1) < 0.1) {
    return 'rectangle';
  } else if (shoulderToWaistRatio > 1.1 && waistToHipRatio < 0.9) {
    return 'hourglass';
  } else if (shoulderToWaistRatio < 0.9) {
    return 'triangle';
  } else if (shoulderToWaistRatio > 1.1) {
    return 'inverted-triangle';
  } else {
    return 'oval';
  }
};

// Extract colors from image
const extractColors = async (imageData: ImageData): Promise<ColorAnalysis> => {
  // Simple color extraction without ColorThief
  const data = imageData.data;
  const colors: { [key: string]: number } = {};
  
  // Sample colors from the image
  for (let i = 0; i < data.length; i += 16) { // Sample every 4th pixel
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const hex = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    colors[hex] = (colors[hex] || 0) + 1;
  }
  
  // Get most common colors
  const sortedColors = Object.entries(colors)
    .sort(([,a], [,b]) => b - a)
    .map(([color]) => color);
  
  const primaryColors = sortedColors.slice(0, 2);
  const secondaryColors = sortedColors.slice(2, 5);

  // Get skin tone (simplified)
  const skinTone = {
    undertone: 'neutral' as const,
    shade: primaryColors[0] || '#000000',
  };

  return {
    primaryColors,
    secondaryColors,
    dominantColors: primaryColors,
    matchingColors: secondaryColors,
    skinTone,
  };
};

// Helper function to detect garment patterns
const detectPattern = (inputImageData: ImageData, region: { x: number; y: number; width: number; height: number }): GarmentPattern => {
  const canvas = document.createElement('canvas');
  canvas.width = region.width;
  canvas.height = region.height;
  const ctx = canvas.getContext('2d');
  if (!ctx) return 'solid';

  // Extract region
  const regionData = ctx.getImageData(region.x, region.y, region.width, region.height);
  ctx.putImageData(regionData, 0, 0);

  // Convert to grayscale for pattern analysis
  const patternImageData = ctx.getImageData(0, 0, region.width, region.height);
  const grayscaleData = new Uint8Array(region.width * region.height);
  
  for (let i = 0; i < patternImageData.data.length; i += 4) {
    const r = patternImageData.data[i];
    const g = patternImageData.data[i + 1];
    const b = patternImageData.data[i + 2];
    grayscaleData[i / 4] = Math.round((r + g + b) / 3);
  }

  // Calculate pattern metrics
  const metrics = calculatePatternMetrics(grayscaleData, region.width, region.height);
  
  // Determine pattern type based on metrics
  if (metrics.regularity > 0.8 && metrics.contrast > 0.6) {
    if (metrics.horizontalLines > 0.7) return 'striped';
    if (metrics.verticalLines > 0.7) return 'striped';
    if (metrics.checkeredPattern > 0.7) return 'checkered';
    if (metrics.dots > 0.7) return 'polka-dot';
  }
  
  if (metrics.irregularity > 0.7) {
    if (metrics.organicShapes > 0.6) return 'floral';
    if (metrics.geometricShapes > 0.6) return 'geometric';
    if (metrics.abstractShapes > 0.6) return 'abstract';
  }

  if (metrics.animalPattern > 0.7) return 'animal-print';
  if (metrics.tieDyePattern > 0.7) return 'tie-dye';
  
  return 'solid';
};

// Helper function to calculate pattern metrics
const calculatePatternMetrics = (
  grayscaleData: Uint8Array,
  width: number,
  height: number
): {
  regularity: number;
  contrast: number;
  horizontalLines: number;
  verticalLines: number;
  checkeredPattern: number;
  dots: number;
  irregularity: number;
  organicShapes: number;
  geometricShapes: number;
  abstractShapes: number;
  animalPattern: number;
  tieDyePattern: number;
} => {
  // Calculate basic metrics
  const contrast = calculateContrast(grayscaleData);
  const regularity = calculateRegularity(grayscaleData, width, height);
  
  // Detect lines
  const horizontalLines = detectHorizontalLines(grayscaleData, width, height);
  const verticalLines = detectVerticalLines(grayscaleData, width, height);
  
  // Detect patterns
  const checkeredPattern = detectCheckeredPattern(grayscaleData, width, height);
  const dots = detectDots(grayscaleData, width, height);
  
  // Detect shapes
  const { organicShapes, geometricShapes, abstractShapes } = detectShapes(grayscaleData, width, height);
  
  // Detect special patterns
  const animalPattern = detectAnimalPattern(grayscaleData, width, height);
  const tieDyePattern = detectTieDyePattern(grayscaleData, width, height);
  
  return {
    regularity,
    contrast,
    horizontalLines,
    verticalLines,
    checkeredPattern,
    dots,
    irregularity: 1 - regularity,
    organicShapes,
    geometricShapes,
    abstractShapes,
    animalPattern,
    tieDyePattern,
  };
};

// Helper functions for pattern detection
const calculateContrast = (data: Uint8Array): number => {
  let min = 255;
  let max = 0;
  for (const value of data) {
    min = Math.min(min, value);
    max = Math.max(max, value);
  }
  return (max - min) / 255;
};

const calculateRegularity = (data: Uint8Array, width: number, height: number): number => {
  // Calculate the standard deviation of pixel values
  const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
  const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length;
  return 1 - Math.min(1, Math.sqrt(variance) / 128);
};

const detectHorizontalLines = (data: Uint8Array, width: number, height: number): number => {
  let lineCount = 0;
  for (let y = 1; y < height - 1; y++) {
    let isLine = true;
    for (let x = 0; x < width; x++) {
      const idx = y * width + x;
      if (Math.abs(data[idx] - data[idx - width]) > 30) {
        isLine = false;
        break;
      }
    }
    if (isLine) lineCount++;
  }
  return lineCount / height;
};

const detectVerticalLines = (data: Uint8Array, width: number, height: number): number => {
  let lineCount = 0;
  for (let x = 1; x < width - 1; x++) {
    let isLine = true;
    for (let y = 0; y < height; y++) {
      const idx = y * width + x;
      if (Math.abs(data[idx] - data[idx - 1]) > 30) {
        isLine = false;
        break;
      }
    }
    if (isLine) lineCount++;
  }
  return lineCount / width;
};

const detectCheckeredPattern = (data: Uint8Array, width: number, height: number): number => {
  let checkCount = 0;
  const blockSize = Math.min(width, height) / 8;
  
  for (let y = 0; y < height - blockSize; y += blockSize) {
    for (let x = 0; x < width - blockSize; x += blockSize) {
      const block1 = getBlockAverage(data, width, x, y, blockSize);
      const block2 = getBlockAverage(data, width, x + blockSize, y, blockSize);
      const block3 = getBlockAverage(data, width, x, y + blockSize, blockSize);
      const block4 = getBlockAverage(data, width, x + blockSize, y + blockSize, blockSize);
      
      if (Math.abs(block1 - block2) > 30 && Math.abs(block3 - block4) > 30 &&
          Math.abs(block1 - block3) > 30 && Math.abs(block2 - block4) > 30) {
        checkCount++;
      }
    }
  }
  
  return checkCount / ((width / blockSize) * (height / blockSize));
};

const detectDots = (data: Uint8Array, width: number, height: number): number => {
  let dotCount = 0;
  const threshold = 30;
  
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const idx = y * width + x;
      const center = data[idx];
      const neighbors = [
        data[idx - width - 1], data[idx - width], data[idx - width + 1],
        data[idx - 1], data[idx + 1],
        data[idx + width - 1], data[idx + width], data[idx + width + 1]
      ];
      
      if (neighbors.every(n => Math.abs(n - center) > threshold)) {
        dotCount++;
      }
    }
  }
  
  return dotCount / (width * height);
};

const detectShapes = (
  data: Uint8Array,
  width: number,
  height: number
): { organicShapes: number; geometricShapes: number; abstractShapes: number } => {
  // Simplified shape detection using edge detection and contour analysis
  const edges = detectEdges(data, width, height);
  const contours = findContours(edges, width, height);
  
  let organicShapes = 0;
  let geometricShapes = 0;
  let abstractShapes = 0;
  
  for (const contour of contours) {
    const complexity = calculateContourComplexity(contour);
    if (complexity > 0.8) {
      organicShapes++;
    } else if (complexity > 0.5) {
      geometricShapes++;
    } else {
      abstractShapes++;
    }
  }
  
  const total = organicShapes + geometricShapes + abstractShapes;
  return {
    organicShapes: total > 0 ? organicShapes / total : 0,
    geometricShapes: total > 0 ? geometricShapes / total : 0,
    abstractShapes: total > 0 ? abstractShapes / total : 0,
  };
};

const detectAnimalPattern = (data: Uint8Array, width: number, height: number): number => {
  // Simplified animal print detection using texture analysis
  const textureFeatures = analyzeTexture(data, width, height);
  return textureFeatures.irregularity * textureFeatures.contrast;
};

const detectTieDyePattern = (data: Uint8Array, width: number, height: number): number => {
  // Simplified tie-dye detection using color gradient analysis
  const gradients = analyzeColorGradients(data, width, height);
  return gradients.radial * gradients.contrast;
};

// Helper functions for shape detection
const detectEdges = (data: Uint8Array, width: number, height: number): Uint8Array => {
  const edges = new Uint8Array(data.length);
  const sobelX = [-1, 0, 1, -2, 0, 2, -1, 0, 1];
  const sobelY = [-1, -2, -1, 0, 0, 0, 1, 2, 1];
  
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      let gx = 0;
      let gy = 0;
      
      for (let ky = -1; ky <= 1; ky++) {
        for (let kx = -1; kx <= 1; kx++) {
          const idx = (y + ky) * width + (x + kx);
          const weight = sobelX[(ky + 1) * 3 + (kx + 1)];
          gx += data[idx] * weight;
          gy += data[idx] * sobelY[(ky + 1) * 3 + (kx + 1)];
        }
      }
      
      const idx = y * width + x;
      edges[idx] = Math.min(255, Math.sqrt(gx * gx + gy * gy));
    }
  }
  
  return edges;
};

const findContours = (edges: Uint8Array, width: number, height: number): number[][] => {
  const contours: number[][] = [];
  const visited = new Set<number>();
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = y * width + x;
      if (edges[idx] > 128 && !visited.has(idx)) {
        const contour = traceContour(edges, width, height, x, y, visited);
        if (contour.length > 10) {
          contours.push(contour);
        }
      }
    }
  }
  
  return contours;
};

const traceContour = (
  edges: Uint8Array,
  width: number,
  height: number,
  startX: number,
  startY: number,
  visited: Set<number>
): number[] => {
  const contour: number[] = [];
  let currentX = startX;
  let currentY = startY;
  
  do {
    const idx = currentY * width + currentX;
    contour.push(idx);
    visited.add(idx);
    
    // Find next edge pixel
    const neighbors = [
      { x: currentX + 1, y: currentY },
      { x: currentX + 1, y: currentY + 1 },
      { x: currentX, y: currentY + 1 },
      { x: currentX - 1, y: currentY + 1 },
      { x: currentX - 1, y: currentY },
      { x: currentX - 1, y: currentY - 1 },
      { x: currentX, y: currentY - 1 },
      { x: currentX + 1, y: currentY - 1 }
    ];
    
    let found = false;
    for (const { x: nx, y: ny } of neighbors) {
      if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
        const nidx = ny * width + nx;
        if (edges[nidx] > 128 && !visited.has(nidx)) {
          currentX = nx;
          currentY = ny;
          found = true;
          break;
        }
      }
    }
    
    if (!found) break;
  } while (currentX !== startX || currentY !== startY);
  
  return contour;
};

const calculateContourComplexity = (contour: number[]): number => {
  // Calculate contour complexity using perimeter and area
  const perimeter = contour.length;
  const area = calculateContourArea(contour);
  return perimeter / (4 * Math.sqrt(area));
};

const calculateContourArea = (contour: number[]): number => {
  // Calculate contour area using shoelace formula
  let area = 0;
  for (let i = 0; i < contour.length; i++) {
    const j = (i + 1) % contour.length;
    area += contour[i] * contour[j];
    area -= contour[j] * contour[i];
  }
  return Math.abs(area) / 2;
};

// Helper functions for texture analysis
const analyzeTexture = (
  data: Uint8Array,
  width: number,
  height: number
): { irregularity: number; contrast: number; thickness: number; elasticity: number; denim: number } => {
  const irregularity = calculateRegularity(data, width, height);
  const contrast = calculateContrast(data);
  const thickness = calculateThickness(data, width, height);
  const elasticity = calculateElasticity(data, width, height);
  const denim = calculateDenimScore(data, width, height);
  
  return {
    irregularity,
    contrast,
    thickness,
    elasticity,
    denim,
  };
};

const analyzeColorGradients = (
  data: Uint8Array,
  width: number,
  height: number
): { radial: number; contrast: number } => {
  let radial = 0;
  const centerX = width / 2;
  const centerY = height / 2;
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const dx = x - centerX;
      const dy = y - centerY;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const idx = y * width + x;
      radial += data[idx] * distance;
    }
  }
  
  radial /= (width * height * Math.sqrt(width * width + height * height));
  const contrast = calculateContrast(data);
  
  return { radial, contrast };
};

const getBlockAverage = (
  data: Uint8Array,
  width: number,
  x: number,
  y: number,
  blockSize: number
): number => {
  let sum = 0;
  let count = 0;
  
  for (let dy = 0; dy < blockSize; dy++) {
    for (let dx = 0; dx < blockSize; dx++) {
      const idx = (y + dy) * width + (x + dx);
      if (idx >= 0 && idx < data.length) {
        sum += data[idx];
        count++;
      }
    }
  }
  
  return count > 0 ? sum / count : 0;
};

// Helper function to detect garment material
const detectMaterial = (inputImageData: ImageData, region: { x: number; y: number; width: number; height: number }): GarmentMaterial => {
  const canvas = document.createElement('canvas');
  canvas.width = region.width;
  canvas.height = region.height;
  const ctx = canvas.getContext('2d');
  if (!ctx) return 'cotton';

  // Extract region
  const regionData = ctx.getImageData(region.x, region.y, region.width, region.height);
  ctx.putImageData(regionData, 0, 0);

  // Convert to grayscale for texture analysis
  const materialImageData = ctx.getImageData(0, 0, region.width, region.height);
  const grayscaleData = new Uint8Array(region.width * region.height);
  
  for (let i = 0; i < materialImageData.data.length; i += 4) {
    const r = materialImageData.data[i];
    const g = materialImageData.data[i + 1];
    const b = materialImageData.data[i + 2];
    grayscaleData[i / 4] = Math.round((r + g + b) / 3);
  }

  // Calculate material features
  const features = calculateMaterialFeatures(grayscaleData, region.width, region.height);
  
  // Determine material type based on features
  if (features.smoothness > 0.8 && features.reflectivity > 0.7) {
    return 'silk';
  }
  
  if (features.texture > 0.7 && features.thickness > 0.6) {
    if (features.elasticity > 0.7) return 'knit';
    if (features.durability > 0.7) return 'denim';
    return 'wool';
  }
  
  if (features.smoothness > 0.6 && features.breathability > 0.7) {
    return 'cotton';
  }
  
  if (features.waterproof > 0.7) {
    return 'leather';
  }
  
  if (features.softness > 0.7) {
    return 'fleece';
  }
  
  if (features.luxury > 0.7) {
    return 'velvet';
  }
  
  if (features.durability > 0.6) {
    return 'suede';
  }
  
  return 'synthetic';
};

// Helper function to calculate material features
const calculateMaterialFeatures = (
  data: Uint8Array,
  width: number,
  height: number
): {
  smoothness: number;
  texture: number;
  reflectivity: number;
  thickness: number;
  elasticity: number;
  durability: number;
  breathability: number;
  waterproof: number;
  softness: number;
  luxury: number;
} => {
  // Calculate basic texture features
  const contrast = calculateContrast(data);
  const regularity = calculateRegularity(data, width, height);
  const edges = detectEdges(data, width, height);
  
  // Calculate advanced features
  const smoothness = 1 - (edges.reduce((sum, val) => sum + val, 0) / (255 * edges.length));
  const texture = 1 - regularity;
  const reflectivity = calculateReflectivity(data, width, height);
  const thickness = calculateThickness(data, width, height);
  const elasticity = calculateElasticity(data, width, height);
  const durability = calculateDurability(data, width, height);
  const breathability = calculateBreathability(data, width, height);
  const waterproof = calculateWaterproof(data, width, height);
  const softness = calculateSoftness(data, width, height);
  const luxury = calculateLuxury(data, width, height);
  
  return {
    smoothness,
    texture,
    reflectivity,
    thickness,
    elasticity,
    durability,
    breathability,
    waterproof,
    softness,
    luxury,
  };
};

// Helper functions for material feature calculation
const calculateReflectivity = (data: Uint8Array, width: number, height: number): number => {
  // Calculate light reflection based on pixel intensity distribution
  const histogram = new Array(256).fill(0);
  for (const value of data) {
    histogram[value]++;
  }
  
  const total = data.length;
  const highIntensity = histogram.slice(200).reduce((sum, count) => sum + count, 0);
  return highIntensity / total;
};

const calculateThickness = (data: Uint8Array, width: number, height: number): number => {
  // Calculate thickness based on edge density and contrast
  const edges = detectEdges(data, width, height);
  const edgeDensity = edges.reduce((sum, val) => sum + (val > 128 ? 1 : 0), 0) / edges.length;
  const contrast = calculateContrast(data);
  return (edgeDensity + contrast) / 2;
};

const calculateElasticity = (data: Uint8Array, width: number, height: number): number => {
  // Calculate elasticity based on texture patterns and deformation
  const texture = calculateRegularity(data, width, height);
  const deformation = calculateDeformation(data, width, height);
  return (texture + deformation) / 2;
};

const calculateDurability = (data: Uint8Array, width: number, height: number): number => {
  // Calculate durability based on texture strength and consistency
  const texture = calculateRegularity(data, width, height);
  const consistency = calculateConsistency(data, width, height);
  return (texture + consistency) / 2;
};

const calculateBreathability = (data: Uint8Array, width: number, height: number): number => {
  // Calculate breathability based on texture porosity
  const porosity = calculatePorosity(data, width, height);
  const texture = calculateRegularity(data, width, height);
  return (porosity + texture) / 2;
};

const calculateWaterproof = (data: Uint8Array, width: number, height: number): number => {
  // Calculate waterproofness based on surface smoothness and reflectivity
  const smoothness = calculateSmoothness(data, width, height);
  const reflectivity = calculateReflectivity(data, width, height);
  return (smoothness + reflectivity) / 2;
};

const calculateSoftness = (data: Uint8Array, width: number, height: number): number => {
  // Calculate softness based on texture smoothness and uniformity
  const smoothness = calculateSmoothness(data, width, height);
  const uniformity = calculateUniformity(data, width, height);
  return (smoothness + uniformity) / 2;
};

const calculateLuxury = (data: Uint8Array, width: number, height: number): number => {
  // Calculate luxury based on texture quality and visual appeal
  const quality = calculateTextureQuality(data, width, height);
  const appeal = calculateVisualAppeal(data, width, height);
  return (quality + appeal) / 2;
};

// Additional helper functions for material analysis
const calculateDeformation = (data: Uint8Array, width: number, height: number): number => {
  // Calculate deformation based on texture distortion
  const edges = detectEdges(data, width, height);
  const distortion = calculateDistortion(edges, width, height);
  return 1 - distortion;
};

const calculateConsistency = (data: Uint8Array, width: number, height: number): number => {
  // Calculate consistency based on texture uniformity
  const uniformity = calculateUniformity(data, width, height);
  const regularity = calculateRegularity(data, width, height);
  return (uniformity + regularity) / 2;
};

const calculatePorosity = (data: Uint8Array, width: number, height: number): number => {
  // Calculate porosity based on texture gaps
  const gaps = detectGaps(data, width, height);
  return gaps / (width * height);
};

const calculateSmoothness = (data: Uint8Array, width: number, height: number): number => {
  // Calculate smoothness based on texture variation
  const variation = calculateVariation(data, width, height);
  return 1 - variation;
};

const calculateUniformity = (data: Uint8Array, width: number, height: number): number => {
  // Calculate uniformity based on pixel distribution
  const histogram = new Array(256).fill(0);
  for (const value of data) {
    histogram[value]++;
  }
  
  const total = data.length;
  const expected = total / 256;
  const chiSquare = histogram.reduce((sum, count) => {
    const diff = count - expected;
    return sum + (diff * diff) / expected;
  }, 0);
  
  return 1 - Math.min(1, chiSquare / total);
};

const calculateTextureQuality = (data: Uint8Array, width: number, height: number): number => {
  // Calculate texture quality based on multiple factors
  const smoothness = calculateSmoothness(data, width, height);
  const uniformity = calculateUniformity(data, width, height);
  const contrast = calculateContrast(data);
  return (smoothness + uniformity + contrast) / 3;
};

const calculateVisualAppeal = (data: Uint8Array, width: number, height: number): number => {
  // Calculate visual appeal based on aesthetic factors
  const contrast = calculateContrast(data);
  const balance = calculateBalance(data, width, height);
  const harmony = calculateHarmony(data, width, height);
  return (contrast + balance + harmony) / 3;
};

const calculateDistortion = (edges: Uint8Array, width: number, height: number): number => {
  // Calculate distortion based on edge irregularity
  let distortion = 0;
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const idx = y * width + x;
      if (edges[idx] > 128) {
        const neighbors = [
          edges[idx - width - 1], edges[idx - width], edges[idx - width + 1],
          edges[idx - 1], edges[idx + 1],
          edges[idx + width - 1], edges[idx + width], edges[idx + width + 1]
        ];
        const maxDiff = Math.max(...neighbors.map(n => Math.abs(n - edges[idx])));
        distortion += maxDiff / 255;
      }
    }
  }
  return distortion / (width * height);
};

const detectGaps = (data: Uint8Array, width: number, height: number): number => {
  // Detect gaps in the texture
  let gaps = 0;
  const threshold = 30;
  
  for (let y = 1; y < height - 1; y++) {
    for (let x = 1; x < width - 1; x++) {
      const idx = y * width + x;
      const center = data[idx];
      const neighbors = [
        data[idx - width - 1], data[idx - width], data[idx - width + 1],
        data[idx - 1], data[idx + 1],
        data[idx + width - 1], data[idx + width], data[idx + width + 1]
      ];
      
      if (neighbors.every(n => Math.abs(n - center) > threshold)) {
        gaps++;
      }
    }
  }
  
  return gaps;
};

const calculateVariation = (data: Uint8Array, width: number, height: number): number => {
  // Calculate texture variation
  const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
  const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length;
  return Math.min(1, Math.sqrt(variance) / 128);
};

const calculateBalance = (data: Uint8Array, width: number, height: number): number => {
  // Calculate visual balance
  const leftHalf = data.slice(0, width * height / 2);
  const rightHalf = data.slice(width * height / 2);
  
  const leftMean = leftHalf.reduce((sum, val) => sum + val, 0) / leftHalf.length;
  const rightMean = rightHalf.reduce((sum, val) => sum + val, 0) / rightHalf.length;
  
  return 1 - Math.abs(leftMean - rightMean) / 255;
};

const calculateHarmony = (data: Uint8Array, width: number, height: number): number => {
  // Calculate color harmony
  const histogram = new Array(256).fill(0);
  for (const value of data) {
    histogram[value]++;
  }
  
  const total = data.length;
  const peaks = findPeaks(histogram);
  const peakDistances = calculatePeakDistances(peaks);
  
  return 1 - Math.min(1, peakDistances.reduce((sum, dist) => sum + dist, 0) / (peaks.length * 128));
};

const findPeaks = (histogram: number[]): number[] => {
  const peaks: number[] = [];
  const threshold = Math.max(...histogram) * 0.1;
  
  for (let i = 1; i < histogram.length - 1; i++) {
    if (histogram[i] > threshold && histogram[i] > histogram[i - 1] && histogram[i] > histogram[i + 1]) {
      peaks.push(i);
    }
  }
  
  return peaks;
};

const calculatePeakDistances = (peaks: number[]): number[] => {
  const distances: number[] = [];
  
  for (let i = 1; i < peaks.length; i++) {
    distances.push(Math.abs(peaks[i] - peaks[i - 1]) / 255);
  }
  
  return distances;
};

// Helper function to detect garment fit
const detectFit = (segmentation: bodyPix.SemanticPersonSegmentation, region: { x: number; y: number; width: number; height: number }): GarmentFit => {
  // TODO: Implement fit detection by analyzing the relationship between body and garment
  // For now, return a default value
  return 'regular';
};

// Helper function to determine color harmony
const determineColorHarmony = (colors: string[]): OutfitAnalysis['colorHarmony'] => {
  // Sort colors by frequency and brightness
  const sortedColors = [...colors].sort((a, b) => {
    const brightnessA = getBrightness(a);
    const brightnessB = getBrightness(b);
    return brightnessB - brightnessA;
  });

  return {
    primary: sortedColors[0] || '#000000',
    secondary: sortedColors[1] || '#FFFFFF',
    accent: sortedColors[2] || '#808080',
    complementary: getComplementaryColors(sortedColors[0] || '#000000'),
  };
};

// Helper function to calculate color brightness
const getBrightness = (hex: string): number => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return (r * 299 + g * 587 + b * 114) / 1000;
};

// Helper function to get complementary colors
const getComplementaryColors = (hex: string): string[] => {
  // TODO: Implement proper color theory calculations
  // For now, return a simple complementary color
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const complementary = `#${(255 - r).toString(16).padStart(2, '0')}${(255 - g).toString(16).padStart(2, '0')}${(255 - b).toString(16).padStart(2, '0')}`;
  return [complementary];
};

// Helper function to determine outfit occasion
const determineOccasion = (garments: Garment[], formality: OutfitFormality): OutfitOccasion => {
  // TODO: Implement more sophisticated occasion detection
  if (formality === 'very-formal' || formality === 'formal') {
    return 'formal-event';
  } else if (formality === 'business' || formality === 'business-casual') {
    return 'business';
  } else if (garments.some(g => g.type === 'sneakers' || g.type === 'shorts')) {
    return 'athletic';
  }
  return 'everyday';
};

// Helper function to determine outfit season
const determineSeason = (garments: Garment[]): OutfitSeason => {
  // TODO: Implement more sophisticated season detection
  const hasHeavyLayers = garments.some(g => 
    ['coat', 'sweater', 'hoodie'].includes(g.type) || 
    ['wool', 'fleece'].includes(g.material)
  );
  const hasLightLayers = garments.some(g => 
    ['t-shirt', 'shorts'].includes(g.type) || 
    ['linen', 'cotton'].includes(g.material)
  );

  if (hasHeavyLayers && !hasLightLayers) return 'winter';
  if (!hasHeavyLayers && hasLightLayers) return 'summer';
  if (hasHeavyLayers && hasLightLayers) return 'fall';
  return 'all-season';
};

// Helper function to calculate style coherence
const calculateStyleCoherence = (garments: Garment[]): number => {
  // TODO: Implement more sophisticated style coherence calculation
  const styleCounts: Record<GarmentStyle, number> = {} as Record<GarmentStyle, number>;
  let totalStyles = 0;

  garments.forEach(garment => {
    garment.style.forEach(style => {
      styleCounts[style] = (styleCounts[style] || 0) + 1;
      totalStyles++;
    });
  });

  // Calculate entropy of style distribution
  const entropy = Object.values(styleCounts).reduce((sum, count) => {
    const p = count / totalStyles;
    return sum - p * Math.log2(p);
  }, 0);

  // Convert entropy to coherence score (0-1)
  return Math.max(0, 1 - entropy / Math.log2(Object.keys(styleCounts).length));
};

// Enhanced outfit analysis
const analyzeOutfit = async (imageData: ImageData, segmentation: bodyPix.SemanticPersonSegmentation): Promise<OutfitAnalysis> => {
  // Detect garments using segmentation
  const garments: Garment[] = [];
  const regions = detectGarmentRegions(segmentation);

  for (const region of regions) {
    const type = detectGarmentType(segmentation, region);
    const pattern = detectPattern(imageData, region);
    const material = detectMaterial(imageData, region);
    const fit = detectFit(segmentation, region);
    const color = await extractRegionColor(imageData, region);
    const style = detectGarmentStyle(type, pattern, material, fit);

    garments.push({
      type,
      color,
      style,
      pattern,
      fit,
      material,
      confidence: calculateConfidence(type, pattern, material, fit, style),
    });
  }

  // Extract overall color palette
  const colorPalette = await extractColors(imageData);
  const colorHarmony = determineColorHarmony(colorPalette.primaryColors.concat(colorPalette.secondaryColors));

  // Determine formality based on garments
  const formality = determineFormality(garments);
  const occasion = determineOccasion(garments, formality);
  const season = determineSeason(garments);

  // Calculate style coherence
  const styleCoherence = calculateStyleCoherence(garments);

  return {
    garments,
    overallStyle: determineOverallStyle(garments),
    colorPalette: colorPalette.primaryColors.concat(colorPalette.secondaryColors),
    formality,
    occasion,
    season,
    colorHarmony,
    styleCoherence,
    confidence: calculateOverallConfidence(garments, colorHarmony, styleCoherence),
  };
};

// Helper function to detect garment regions
const detectGarmentRegions = (segmentation: bodyPix.SemanticPersonSegmentation): Array<{ x: number; y: number; width: number; height: number }> => {
  const regions: Array<{ x: number; y: number; width: number; height: number }> = [];
  const visited = new Set<number>();
  
  // Define body regions for garment detection
  const bodyRegions = [
    { name: 'top', yStart: 0.1, yEnd: 0.4 },
    { name: 'bottom', yStart: 0.4, yEnd: 0.7 },
    { name: 'outerwear', yStart: 0.1, yEnd: 0.7 },
    { name: 'footwear', yStart: 0.7, yEnd: 0.9 },
  ];
  
  for (const region of bodyRegions) {
    const yStart = Math.floor(segmentation.height * region.yStart);
    const yEnd = Math.floor(segmentation.height * region.yEnd);
    
    for (let y = yStart; y < yEnd; y++) {
      for (let x = 0; x < segmentation.width; x++) {
        const idx = y * segmentation.width + x;
        if (segmentation.data[idx] === 1 && !visited.has(idx)) {
          const { x: regionX, y: regionY, width, height } = findConnectedRegion(segmentation, x, y, visited);
          if (width > 20 && height > 20) { // Filter out small regions
            regions.push({ x: regionX, y: regionY, width, height });
          }
        }
      }
    }
  }
  
  return regions;
};

// Helper function to find connected region
const findConnectedRegion = (
  segmentation: bodyPix.SemanticPersonSegmentation,
  startX: number,
  startY: number,
  visited: Set<number>
): { x: number; y: number; width: number; height: number } => {
  let minX = startX;
  let maxX = startX;
  let minY = startY;
  let maxY = startY;
  
  const queue = [{ x: startX, y: startY }];
  visited.add(startY * segmentation.width + startX);
  
  while (queue.length > 0) {
    const { x, y } = queue.shift()!;
    
    // Check neighbors
    const neighbors = [
      { x: x + 1, y },
      { x: x - 1, y },
      { x, y: y + 1 },
      { x, y: y - 1 },
    ];
    
    for (const { x: nx, y: ny } of neighbors) {
      if (nx >= 0 && nx < segmentation.width && ny >= 0 && ny < segmentation.height) {
        const idx = ny * segmentation.width + nx;
        if (segmentation.data[idx] === 1 && !visited.has(idx)) {
          visited.add(idx);
          queue.push({ x: nx, y: ny });
          minX = Math.min(minX, nx);
          maxX = Math.max(maxX, nx);
          minY = Math.min(minY, ny);
          maxY = Math.max(maxY, ny);
        }
      }
    }
  }
  
  return {
    x: minX,
    y: minY,
    width: maxX - minX + 1,
    height: maxY - minY + 1,
  };
};

// Helper function to detect garment style
const detectGarmentStyle = (
  type: GarmentType,
  pattern: GarmentPattern,
  material: GarmentMaterial,
  fit: GarmentFit
): GarmentStyle[] => {
  const styles: GarmentStyle[] = [];
  
  // Determine style based on garment type
  switch (type) {
    case 't-shirt':
    case 'hoodie':
      styles.push('casual');
      break;
    case 'shirt':
    case 'blouse':
      styles.push('business');
      break;
    case 'dress':
      styles.push('elegant');
      break;
    case 'sweater':
      styles.push('classic');
      break;
    case 'jacket':
    case 'coat':
      styles.push('modern');
      break;
  }
  
  // Add styles based on pattern
  switch (pattern) {
    case 'floral':
      styles.push('bohemian');
      break;
    case 'plaid':
      styles.push('preppy');
      break;
    case 'animal-print':
      styles.push('bold');
      break;
    case 'geometric':
      styles.push('modern');
      break;
  }
  
  // Add styles based on material
  switch (material) {
    case 'leather':
      styles.push('bold');
      break;
    case 'silk':
      styles.push('elegant');
      break;
    case 'denim':
      styles.push('casual');
      break;
    case 'wool':
      styles.push('classic');
      break;
  }
  
  // Add styles based on fit
  switch (fit) {
    case 'oversized':
      styles.push('streetwear');
      break;
    case 'slim':
      styles.push('modern');
      break;
    case 'loose':
      styles.push('bohemian');
      break;
  }
  
  return [...new Set(styles)]; // Remove duplicates
};

// Helper function to calculate confidence score
const calculateConfidence = (
  type: GarmentType,
  pattern: GarmentPattern,
  material: GarmentMaterial,
  fit: GarmentFit,
  style: GarmentStyle[]
): number => {
  // Calculate confidence based on feature detection results
  const typeConfidence = 0.8; // Placeholder for type detection confidence
  const patternConfidence = 0.7; // Placeholder for pattern detection confidence
  const materialConfidence = 0.7; // Placeholder for material detection confidence
  const fitConfidence = 0.8; // Placeholder for fit detection confidence
  const styleConfidence = style.length > 0 ? 0.8 : 0.5; // Placeholder for style detection confidence
  
  return (typeConfidence + patternConfidence + materialConfidence + fitConfidence + styleConfidence) / 5;
};

// Helper function to determine overall style
const determineOverallStyle = (garments: Garment[]): GarmentStyle[] => {
  const styleCounts: Record<GarmentStyle, number> = {} as Record<GarmentStyle, number>;
  
  garments.forEach(garment => {
    garment.style.forEach(style => {
      styleCounts[style] = (styleCounts[style] || 0) + 1;
    });
  });
  
  return Object.entries(styleCounts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)
    .map(([style]) => style as GarmentStyle);
};

// Helper function to calculate overall confidence
const calculateOverallConfidence = (
  garments: Garment[],
  colorHarmony: OutfitAnalysis['colorHarmony'],
  styleCoherence: number
): number => {
  const garmentConfidence = garments.reduce((sum, garment) => sum + garment.confidence, 0) / garments.length;
  const colorConfidence = 0.8; // Placeholder for color harmony confidence
  return (garmentConfidence + colorConfidence + styleCoherence) / 3;
};

// Helper function to detect garment type
const detectGarmentType = (
  segmentation: bodyPix.SemanticPersonSegmentation,
  region: { x: number; y: number; width: number; height: number }
): GarmentType => {
  // Extract region from segmentation
  const regionData = new Uint8Array(region.width * region.height);
  for (let y = 0; y < region.height; y++) {
    for (let x = 0; x < region.width; x++) {
      const segIdx = (region.y + y) * segmentation.width + (region.x + x);
      const regionIdx = y * region.width + x;
      regionData[regionIdx] = segmentation.data[segIdx];
    }
  }

  // Calculate garment features
  const features = calculateGarmentFeatures(regionData, region.width, region.height);
  
  // Determine garment type based on features
  if (features.isTop) {
    if (features.hasCollar && features.hasButtons) {
      return 'shirt';
    }
    if (features.hasHood) {
      return 'hoodie';
    }
    if (features.isThick) {
      return 'sweater';
    }
    if (features.isLight) {
      return 'blouse';
    }
    return 't-shirt';
  }
  
  if (features.isBottom) {
    if (features.isDenim) {
      return 'jeans';
    }
    if (features.isShort) {
      return 'shorts';
    }
    if (features.isSkirt) {
      return 'skirt';
    }
    return 'pants';
  }
  
  if (features.isDress) {
    return 'dress';
  }
  
  if (features.isOuterwear) {
    if (features.isHeavy) {
      return 'coat';
    }
    return 'jacket';
  }
  
  if (features.isFootwear) {
    if (features.hasHeel) {
      return 'heels';
    }
    if (features.isBoot) {
      return 'boots';
    }
    if (features.isOpen) {
      return 'sandals';
    }
    if (features.isAthletic) {
      return 'sneakers';
    }
    return 'shoes';
  }
  
  return 't-shirt'; // Default fallback
};

// Helper function to calculate garment features
const calculateGarmentFeatures = (
  data: Uint8Array,
  width: number,
  height: number
): {
  isTop: boolean;
  isBottom: boolean;
  isDress: boolean;
  isOuterwear: boolean;
  isFootwear: boolean;
  hasCollar: boolean;
  hasButtons: boolean;
  hasHood: boolean;
  isThick: boolean;
  isLight: boolean;
  isDenim: boolean;
  isShort: boolean;
  isSkirt: boolean;
  isHeavy: boolean;
  hasHeel: boolean;
  isBoot: boolean;
  isOpen: boolean;
  isAthletic: boolean;
} => {
  // Calculate basic shape features
  const shape = analyzeShape(data, width, height);
  const texture = analyzeTexture(data, width, height);
  const details = detectDetails(data, width, height);
  
  // Determine garment category
  const isTop = shape.aspectRatio > 1.2 && shape.topHeavy;
  const isBottom = shape.aspectRatio > 1.2 && shape.bottomHeavy;
  const isDress = shape.aspectRatio > 2 && shape.uniform;
  const isOuterwear = shape.aspectRatio > 1.5 && shape.bulky;
  const isFootwear = shape.aspectRatio < 0.8 && shape.compact;
  
  // Determine specific features
  const hasCollar = details.hasCollar;
  const hasButtons = details.hasButtons;
  const hasHood = details.hasHood;
  const isThick = texture.thickness > 0.7;
  const isLight = texture.thickness < 0.3;
  const isDenim = texture.denim > 0.7;
  const isShort = shape.garmentHeight < height * 0.4;
  const isSkirt = shape.flare > 0.7;
  const isHeavy = texture.thickness > 0.8;
  const hasHeel = details.hasHeel;
  const isBoot = shape.garmentHeight > height * 0.6;
  const isOpen = details.isOpen;
  const isAthletic = details.isAthletic;
  
  return {
    isTop,
    isBottom,
    isDress,
    isOuterwear,
    isFootwear,
    hasCollar,
    hasButtons,
    hasHood,
    isThick,
    isLight,
    isDenim,
    isShort,
    isSkirt,
    isHeavy,
    hasHeel,
    isBoot,
    isOpen,
    isAthletic,
  };
};

// Helper function to analyze garment shape
const analyzeShape = (
  data: Uint8Array,
  width: number,
  height: number
): {
  aspectRatio: number;
  topHeavy: boolean;
  bottomHeavy: boolean;
  uniform: boolean;
  bulky: boolean;
  compact: boolean;
  garmentHeight: number;
  flare: number;
} => {
  // Calculate basic shape metrics
  const aspectRatio = width / height;
  
  // Calculate vertical distribution
  const topHalf = data.slice(0, width * height / 2);
  const bottomHalf = data.slice(width * height / 2);
  const topDensity = topHalf.reduce((sum, val) => sum + val, 0) / topHalf.length;
  const bottomDensity = bottomHalf.reduce((sum, val) => sum + val, 0) / bottomHalf.length;
  
  const topHeavy = topDensity > bottomDensity * 1.2;
  const bottomHeavy = bottomDensity > topDensity * 1.2;
  
  // Calculate uniformity
  const uniform = Math.abs(topDensity - bottomDensity) < 0.1;
  
  // Calculate bulkiness
  const edges = detectEdges(data, width, height);
  const edgeDensity = edges.reduce((sum, val) => sum + (val > 128 ? 1 : 0), 0) / edges.length;
  const bulky = edgeDensity > 0.3;
  
  // Calculate compactness
  const compact = aspectRatio < 0.8;
  
  // Calculate height
  const garmentHeight = calculateGarmentHeight(data, width, height);
  
  // Calculate flare
  const flare = calculateFlare(data, width, height);
  
  return {
    aspectRatio,
    topHeavy,
    bottomHeavy,
    uniform,
    bulky,
    compact,
    garmentHeight,
    flare,
  };
};

// Helper function to detect garment details
const detectDetails = (
  data: Uint8Array,
  width: number,
  height: number
): GarmentDetails => {
  // Detect collar
  const hasCollar = detectCollar(data, width, height);
  
  // Detect buttons
  const hasButtons = detectButtons(data, width, height);
  
  // Detect hood
  const hasHood = detectHood(data, width, height);
  
  // Detect heel
  const hasHeel = detectHeel(data, width, height);
  
  // Detect open areas
  const isOpen = detectOpenAreas(data, width, height);
  
  // Detect athletic features
  const isAthletic = detectAthleticFeatures(data, width, height);
  
  // Detect stripes and mesh
  const hasStripes = detectStripes(data, width, height);
  const hasMesh = detectMesh(data, width, height);
  
  return {
    hasCollar,
    hasButtons,
    hasHood,
    hasHeel,
    isOpen,
    isAthletic,
    hasStripes,
    hasMesh,
  };
};

// Helper functions for detail detection
const detectCollar = (data: Uint8Array, width: number, height: number): boolean => {
  // Look for collar-like patterns in the upper region
  const upperRegion = data.slice(0, width * height * 0.2);
  const edges = detectEdges(upperRegion, width, height * 0.2);
  const horizontalLines = detectHorizontalLines(edges, width, height * 0.2);
  return horizontalLines > 0.3;
};

const detectButtons = (data: Uint8Array, width: number, height: number): boolean => {
  // Look for button-like patterns
  const dots = detectDots(data, width, height);
  const verticalAlignment = detectVerticalAlignment(data, width, height);
  return dots > 0.1 && verticalAlignment > 0.7;
};

const detectHood = (data: Uint8Array, width: number, height: number): boolean => {
  // Look for hood-like shape in the upper region
  const upperRegion = data.slice(0, width * height * 0.3);
  const shape = analyzeShape(upperRegion, width, height * 0.3);
  return shape.aspectRatio > 1.5 && shape.topHeavy;
};

const detectHeel = (data: Uint8Array, width: number, height: number): boolean => {
  // Look for heel-like shape in the lower region
  const lowerRegion = data.slice(width * height * 0.7);
  const shape = analyzeShape(lowerRegion, width, height * 0.3);
  return shape.aspectRatio < 0.5 && shape.bottomHeavy;
};

const detectOpenAreas = (data: Uint8Array, width: number, height: number): boolean => {
  // Look for open areas in the garment
  const gaps = detectGaps(data, width, height);
  return gaps / (width * height) > 0.1;
};

const detectAthleticFeatures = (data: Uint8Array, width: number, height: number): boolean => {
  const texture = analyzeTexture(data, width, height);
  const details = detectDetails(data, width, height);
  return texture.elasticity > 0.7 || details.hasStripes || details.hasMesh;
};

const calculateGarmentHeight = (data: Uint8Array, width: number, height: number): number => {
  let top = height;
  let bottom = 0;
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = y * width + x;
      if (data[idx] > 0) {
        top = Math.min(top, y);
        bottom = Math.max(bottom, y);
      }
    }
  }
  
  return (bottom - top) / height;
};

const calculateFlare = (data: Uint8Array, width: number, height: number): number => {
  // Calculate the flare of the garment
  const bottomRegion = data.slice(width * height * 0.7);
  const bottomWidth = calculateWidth(bottomRegion, width, height * 0.3);
  const topWidth = calculateWidth(data.slice(0, width * height * 0.3), width, height * 0.3);
  return bottomWidth / topWidth;
};

const calculateWidth = (data: Uint8Array, width: number, height: number): number => {
  // Calculate the width of the garment at a specific height
  let left = width;
  let right = 0;
  
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = y * width + x;
      if (data[idx] > 0) {
        left = Math.min(left, x);
        right = Math.max(right, x);
      }
    }
  }
  
  return (right - left) / width;
};

const detectVerticalAlignment = (data: Uint8Array, width: number, height: number): number => {
  // Calculate the vertical alignment of features
  let alignment = 0;
  const threshold = 30;
  
  for (let x = 0; x < width; x++) {
    let verticalLine = true;
    for (let y = 1; y < height - 1; y++) {
      const idx = y * width + x;
      if (Math.abs(data[idx] - data[idx - width]) > threshold) {
        verticalLine = false;
        break;
      }
    }
    if (verticalLine) alignment++;
  }
  
  return alignment / width;
};

// Helper function to extract color from a specific region
const extractRegionColor = async (imageData: ImageData, region: { x: number; y: number; width: number; height: number }): Promise<string> => {
  const canvas = document.createElement('canvas');
  canvas.width = region.width;
  canvas.height = region.height;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Failed to get canvas context');

  // Extract region
  const regionData = ctx.getImageData(region.x, region.y, region.width, region.height);
  ctx.putImageData(regionData, 0, 0);

  // Get dominant color (simple average)
  const regionImageData = ctx.getImageData(0, 0, region.width, region.height);
  const data = regionImageData.data;
  let r = 0, g = 0, b = 0, count = 0;
  
  for (let i = 0; i < data.length; i += 4) {
    r += data[i];
    g += data[i + 1];
    b += data[i + 2];
    count++;
  }
  
  const avgR = Math.round(r / count);
  const avgG = Math.round(g / count);
  const avgB = Math.round(b / count);
  
  return `#${avgR.toString(16).padStart(2, '0')}${avgG.toString(16).padStart(2, '0')}${avgB.toString(16).padStart(2, '0')}`;
};

// Helper function to determine formality
const determineFormality = (garments: Garment[]): OutfitFormality => {
  const hasFormalItems = garments.some(g => 
    ['shirt', 'blouse', 'dress'].includes(g.type) || 
    ['formal', 'business'].includes(g.style[0])
  );
  const hasCasualItems = garments.some(g => 
    ['t-shirt', 'hoodie', 'sneakers'].includes(g.type) || 
    ['casual', 'sporty'].includes(g.style[0])
  );

  if (hasFormalItems && !hasCasualItems) return 'formal';
  if (hasFormalItems && hasCasualItems) return 'business-casual';
  return 'casual';
};

// Main analysis function
export const analyzePhoto = async (
  imageData: ImageData,
  type: 'fullBody' | 'outfit'
): Promise<PhotoAnalysis> => {
  try {
    await initTensorFlow();
    const net = await loadModel();
    const tensor = await imageToTensor(imageData);
    
    // Get body segmentation
    const segmentation = await net.segmentPerson(tensor);
    
    // Calculate measurements for full body photos
    const bodyMeasurements = type === 'fullBody'
      ? calculateBodyMeasurements(segmentation, imageData.width, imageData.height)
      : {
          height: 0,
          shoulderWidth: 0,
          waistWidth: 0,
          hipWidth: 0,
          inseam: 0,
          bodyType: 'rectangle' as BodyType,
        };

    // Extract colors
    const colorAnalysis = await extractColors(imageData);

    // Analyze outfit if needed
    const outfitAnalysis = type === 'outfit' ? await analyzeOutfit(imageData, segmentation) : undefined;

    // Clean up tensors
    tensor.dispose();

    return {
      bodyMeasurements,
      colorAnalysis,
      outfitAnalysis,
      confidence: 0.85, // TODO: Implement actual confidence calculation
    };
  } catch (error) {
    console.error('Error analyzing photo:', error);
    throw new Error('Failed to analyze photo');
  }
};

// Add missing calculateDenimScore function
const calculateDenimScore = (data: Uint8Array, width: number, height: number): number => {
  const edges = detectEdges(data, width, height);
  const edgeDensity = edges.reduce((sum, val) => sum + (val > 128 ? 1 : 0), 0) / edges.length;
  const contrast = calculateContrast(data);
  const texture = calculateRegularity(data, width, height);
  
  // Denim typically has high edge density, contrast, and regular texture
  return (edgeDensity + contrast + texture) / 3;
};

// Helper functions for detail detection
const detectStripes = (data: Uint8Array, width: number, height: number): boolean => {
  const horizontalLines = detectHorizontalLines(data, width, height);
  const verticalLines = detectVerticalLines(data, width, height);
  return horizontalLines > 0.3 || verticalLines > 0.3;
};

const detectMesh = (data: Uint8Array, width: number, height: number): boolean => {
  const gaps = detectGaps(data, width, height);
  const porosity = gaps / (width * height);
  return porosity > 0.2;
}; 