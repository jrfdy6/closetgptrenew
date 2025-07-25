import { ClothingItem, Color, VisualAttributes, Metadata, BasicMetadata } from '@/types/wardrobe';
import { db } from './firebase/config';
import { collection, doc, setDoc, getDocs, query, where } from 'firebase/firestore';
import { validateClothingItem } from '@/lib/utils/validation';
import { Garment, GarmentStyle, GarmentPattern, GarmentFit, GarmentMaterial } from '@/types/photo-analysis';

interface ItemComparison {
  id: string;
  name: string;
  differences: {
    field: string;
    original: any;
    cleaned: any;
  }[];
  improvements: {
    field: string;
    value: any;
    description: string;
  }[];
}

interface EnhancementSummary {
  timestamp: number;
  userId: string;
  statistics: {
    totalItems: number;
    itemsWithEnhancements: number;
    totalEnhancements: number;
  };
  enhancements: {
    byField: Record<string, {
      count: number;
      examples: Array<{
        itemId: string;
        itemName: string;
        original: any;
        enhanced: any;
      }>;
    }>;
  };
  items: Array<{
    id: string;
    name: string;
    enhancements: Array<{
      field: string;
      original: any;
      enhanced: any;
      description: string;
    }>;
  }>;
}

interface DataQualityMetrics {
  completeness: {
    requiredFields: {
      field: string;
      original: number;
      transformed: number;
      improvement: number;
    }[];
    totalRequiredFields: number;
    originalCompleteness: number;
    transformedCompleteness: number;
    overallImprovement: number;
  };
  consistency: {
    field: string;
    original: any;
    transformed: any;
    isValid: boolean;
    issues: string[];
  }[];
  enrichment: {
    field: string;
    originalValue: any;
    transformedValue: any;
    confidence: number;
    source: 'analyzed' | 'default' | 'derived';
  }[];
  reliability: {
    field: string;
    confidence: number;
    validationPassed: boolean;
    potentialIssues: string[];
  }[];
}

// Helper function to convert GarmentFit to VisualAttributes fit
function convertGarmentFitToVisualAttributesFit(fit: GarmentFit): "slim" | "loose" | "oversized" | null {
  switch (fit) {
    case 'slim':
    case 'fitted':
      return 'slim';
    case 'loose':
    case 'relaxed':
      return 'loose';
    case 'oversized':
      return 'oversized';
    case 'regular':
      return 'slim'; // Default to slim for regular fit
    default:
      return null;
  }
}

// Helper function to convert string to fabric weight
function convertToFabricWeight(weight: string | null): "light" | "medium" | "heavy" | null {
  if (!weight) return null;
  const weightLower = weight.toLowerCase();
  if (weightLower === 'light' || weightLower === 'medium' || weightLower === 'heavy') {
    return weightLower;
  }
  return null;
}

// Helper function to convert string to wear layer
function convertToWearLayer(layer: string): "inner" | "outer" | "base" | null {
  const layerLower = layer.toLowerCase();
  if (layerLower === 'inner' || layerLower === 'outer' || layerLower === 'base') {
    return layerLower;
  }
  return null;
}

// Helper function to convert string to formal level
function convertToFormalLevel(level: string): "casual" | "semi-formal" | "formal" | null {
  const levelLower = level.toLowerCase();
  if (levelLower === 'casual' || levelLower === 'semi-formal' || levelLower === 'formal') {
    return levelLower;
  }
  return null;
}

// Helper function to convert BasicMetadata from photo-analysis to shared/types
function convertBasicMetadata(metadata: BasicMetadata): BasicMetadata {
  return {
    ...metadata,
    gps: metadata.gps ? {
      latitude: 0, // Default values since we don't have the actual coordinates
      longitude: 0
    } : null
  };
}

export function compareItems(original: ClothingItem, cleaned: ClothingItem): ItemComparison {
  const differences: ItemComparison['differences'] = [];
  const improvements: ItemComparison['improvements'] = [];

  // Compare basic fields
  const fieldsToCompare = [
    'name', 'type', 'color', 'season', 'tags', 'style', 'occasion',
    'brand', 'subType', 'colorName', 'backgroundRemoved'
  ];

  fieldsToCompare.forEach(field => {
    const originalValue = original[field as keyof ClothingItem];
    const cleanedValue = cleaned[field as keyof ClothingItem];
    
    if (JSON.stringify(originalValue) !== JSON.stringify(cleanedValue)) {
      differences.push({
        field,
        original: originalValue,
        cleaned: cleanedValue
      });

      // Check if the cleaned value is an improvement
      if (cleanedValue && !originalValue) {
        improvements.push({
          field,
          value: cleanedValue,
          description: `Added missing ${field}`
        });
      } else if (Array.isArray(cleanedValue) && Array.isArray(originalValue) && cleanedValue.length > originalValue.length) {
        improvements.push({
          field,
          value: cleanedValue,
          description: `Enhanced ${field} with additional values`
        });
      }
    }
  });

  // Compare metadata
  if (original.metadata && cleaned.metadata) {
    // Compare visual attributes
    const originalVisual = original.metadata.visualAttributes;
    const cleanedVisual = cleaned.metadata.visualAttributes;
    if (originalVisual && cleanedVisual) {
      Object.keys(cleanedVisual).forEach(key => {
        const originalValue = originalVisual[key as keyof typeof originalVisual];
        const cleanedValue = cleanedVisual[key as keyof typeof cleanedVisual];
        
        if (JSON.stringify(originalValue) !== JSON.stringify(cleanedValue)) {
          differences.push({
            field: `metadata.visualAttributes.${key}`,
            original: originalValue,
            cleaned: cleanedValue
          });

          if (cleanedValue && !originalValue) {
            improvements.push({
              field: `metadata.visualAttributes.${key}`,
              value: cleanedValue,
              description: `Added missing visual attribute: ${key}`
            });
          }
        }
      });
    }

    // Compare item metadata
    const originalItemMeta = original.metadata.itemMetadata;
    const cleanedItemMeta = cleaned.metadata.itemMetadata;
    if (originalItemMeta && cleanedItemMeta) {
      Object.keys(cleanedItemMeta).forEach(key => {
        const originalValue = originalItemMeta[key as keyof typeof originalItemMeta];
        const cleanedValue = cleanedItemMeta[key as keyof typeof cleanedItemMeta];
        
        if (JSON.stringify(originalValue) !== JSON.stringify(cleanedValue)) {
          differences.push({
            field: `metadata.itemMetadata.${key}`,
            original: originalValue,
            cleaned: cleanedValue
          });

          if (cleanedValue && !originalValue) {
            improvements.push({
              field: `metadata.itemMetadata.${key}`,
              value: cleanedValue,
              description: `Added missing item metadata: ${key}`
            });
          }
        }
      });
    }
  }

  return {
    id: original.id,
    name: original.name,
    differences,
    improvements
  };
}

export function generateEnhancementSummary(
  userId: string,
  comparisons: ItemComparison[]
): EnhancementSummary {
  const summary: EnhancementSummary = {
    timestamp: Date.now(),
    userId,
    statistics: {
      totalItems: comparisons.length,
      itemsWithEnhancements: 0,
      totalEnhancements: 0
    },
    enhancements: {
      byField: {}
    },
    items: []
  };

  comparisons.forEach(comparison => {
    const itemEnhancements = comparison.improvements.map(improvement => {
      const diff = comparison.differences.find(d => d.field === improvement.field);
      return {
        field: improvement.field,
        original: diff?.original,
        enhanced: diff?.cleaned,
        description: improvement.description
      };
    });

    if (itemEnhancements.length > 0) {
      summary.statistics.itemsWithEnhancements++;
      summary.statistics.totalEnhancements += itemEnhancements.length;

      // Add to items list
      summary.items.push({
        id: comparison.id,
        name: comparison.name,
        enhancements: itemEnhancements
      });

      // Track by field
      itemEnhancements.forEach(enhancement => {
        if (!summary.enhancements.byField[enhancement.field]) {
          summary.enhancements.byField[enhancement.field] = {
            count: 0,
            examples: []
          };
        }
        summary.enhancements.byField[enhancement.field].count++;
        summary.enhancements.byField[enhancement.field].examples.push({
          itemId: comparison.id,
          itemName: comparison.name,
          original: enhancement.original,
          enhanced: enhancement.enhanced
        });
      });
    }
  });

  // Sort items by number of enhancements
  summary.items.sort((a, b) => b.enhancements.length - a.enhancements.length);

  return summary;
}

function summarizeSkippedItems(skippedItems: Array<{ id: string; reason: string; details?: any }>) {
  const summary = {
    total: skippedItems.length,
    byReason: {} as Record<string, { count: number; items: Array<{ id: string; details?: any }> }>
  };

  skippedItems.forEach(item => {
    if (!summary.byReason[item.reason]) {
      summary.byReason[item.reason] = {
        count: 0,
        items: []
      };
    }
    summary.byReason[item.reason].count++;
    summary.byReason[item.reason].items.push({
      id: item.id,
      details: item.details
    });
  });

  return summary;
}

export async function processAllWardrobeItems(
  userId: string,
  analyzedDataMap: Map<string, Garment>
): Promise<{
  processed: number;
  skipped: number;
  comparisons: ItemComparison[];
  summary: EnhancementSummary;
  skippedItems: Array<{ id: string; reason: string; details?: any }>;
}> {
  const comparisons: ItemComparison[] = [];
  const skippedItems: Array<{ id: string; reason: string; details?: any }> = [];
  let processed = 0;
  let skipped = 0;

  try {
    console.log(`Starting wardrobe processing for user ${userId}`);
    console.log(`Analyzed data available for ${analyzedDataMap.size} items`);

    // Get all items from the user's wardrobe
    const wardrobeRef = collection(db, 'wardrobe');
    const wardrobeSnapshot = await getDocs(wardrobeRef);
    
    console.log(`Found ${wardrobeSnapshot.size} total items in wardrobe`);

    // Process each item
    for (const doc of wardrobeSnapshot.docs) {
      const originalItem = doc.data() as ClothingItem;
      
      // Skip items that don't belong to the current user
      if (originalItem.userId !== userId) {
        console.log(`Skipping item ${originalItem.id}: Wrong user (${originalItem.userId} vs ${userId})`);
        skippedItems.push({
          id: originalItem.id,
          reason: 'wrong_user',
          details: { itemUserId: originalItem.userId, currentUserId: userId }
        });
        skipped++;
        continue;
      }
      
      const analyzedData = analyzedDataMap.get(originalItem.id);

      if (!analyzedData) {
        console.warn(`No analyzed data found for item ${originalItem.id} (${originalItem.name || 'unnamed'})`);
        skippedItems.push({
          id: originalItem.id,
          reason: 'no_analyzed_data',
          details: { itemName: originalItem.name }
        });
        skipped++;
        continue;
      }

      try {
        console.log(`Processing item ${originalItem.id} (${originalItem.name || 'unnamed'})`);
        const { item: cleanedItem, quality } = await cleanAndStoreWardrobeItem(userId, originalItem, analyzedData);
        
        // Log data quality metrics
        console.log(`Data quality for item ${originalItem.id}:`, {
          completeness: quality.completeness.overallImprovement,
          consistency: quality.consistency.filter(c => !c.isValid).length,
          enrichment: quality.enrichment.length,
          reliability: quality.reliability.filter(r => !r.validationPassed).length
        });

        const comparison = compareItems(originalItem, cleanedItem);
        comparisons.push(comparison);
        processed++;
        
        console.log(`Successfully processed item ${originalItem.id} with ${comparison.improvements.length} improvements`);
      } catch (error) {
        console.error(`Error processing item ${originalItem.id}:`, error);
        skippedItems.push({
          id: originalItem.id,
          reason: 'processing_error',
          details: { error: error instanceof Error ? error.message : String(error) }
        });
        skipped++;
      }
    }

    // Generate summary
    const summary = generateEnhancementSummary(userId, comparisons);

    // Log detailed skipped items summary
    const skippedSummary = summarizeSkippedItems(skippedItems);
    console.log('Skipped Items Summary:', {
      total: skippedSummary.total,
      byReason: Object.entries(skippedSummary.byReason).map(([reason, data]) => ({
        reason,
        count: data.count,
        examples: data.items.slice(0, 3) // Show up to 3 examples per reason
      }))
    });

    console.log('Processing complete:', {
      processed,
      skipped,
      totalItems: processed + skipped,
      itemsWithEnhancements: summary.statistics.itemsWithEnhancements,
      totalEnhancements: summary.statistics.totalEnhancements
    });

    return {
      processed,
      skipped,
      comparisons,
      summary,
      skippedItems
    };
  } catch (error) {
    console.error('Error processing wardrobe items:', error);
    throw error;
  }
}

function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((current, key) => current?.[key], obj);
}

export function analyzeDataQuality(original: ClothingItem, transformed: ClothingItem): DataQualityMetrics {
  const metrics: DataQualityMetrics = {
    completeness: {
      requiredFields: [],
      totalRequiredFields: 0,
      originalCompleteness: 0,
      transformedCompleteness: 0,
      overallImprovement: 0
    },
    consistency: [],
    enrichment: [],
    reliability: []
  };

  // Required fields for outfit generation
  const requiredFields = [
    'type',
    'color',
    'season',
    'style',
    'occasion',
    'dominantColors',
    'matchingColors',
    'metadata.visualAttributes.material',
    'metadata.visualAttributes.pattern',
    'metadata.visualAttributes.fit',
    'metadata.visualAttributes.wearLayer',
    'metadata.visualAttributes.formalLevel'
  ];

  metrics.completeness.totalRequiredFields = requiredFields.length;

  // Analyze completeness
  requiredFields.forEach(field => {
    const originalValue = getNestedValue(original, field);
    const transformedValue = getNestedValue(transformed, field);
    
    const originalScore = originalValue ? 1 : 0;
    const transformedScore = transformedValue ? 1 : 0;
    
    metrics.completeness.requiredFields.push({
      field,
      original: originalScore,
      transformed: transformedScore,
      improvement: transformedScore - originalScore
    });
  });

  // Calculate completeness scores
  metrics.completeness.originalCompleteness = 
    metrics.completeness.requiredFields.reduce((sum, field) => sum + field.original, 0) / 
    metrics.completeness.totalRequiredFields * 100;

  metrics.completeness.transformedCompleteness = 
    metrics.completeness.requiredFields.reduce((sum, field) => sum + field.transformed, 0) / 
    metrics.completeness.totalRequiredFields * 100;

  metrics.completeness.overallImprovement = 
    metrics.completeness.transformedCompleteness - metrics.completeness.originalCompleteness;

  // Analyze consistency
  const consistencyChecks = [
    {
      field: 'color',
      validator: (value: any) => typeof value === 'string' && value.startsWith('#'),
      issues: ['Invalid color format']
    },
    {
      field: 'season',
      validator: (value: any) => Array.isArray(value) && value.every(s => ['spring', 'summer', 'fall', 'winter'].includes(s)),
      issues: ['Invalid season values']
    },
    {
      field: 'dominantColors',
      validator: (value: any) => Array.isArray(value) && value.every(c => c.name && c.hex && Array.isArray(c.rgb)),
      issues: ['Invalid color object structure']
    }
  ];

  consistencyChecks.forEach(check => {
    const originalValue = getNestedValue(original, check.field);
    const transformedValue = getNestedValue(transformed, check.field);
    
    metrics.consistency.push({
      field: check.field,
      original: originalValue,
      transformed: transformedValue,
      isValid: check.validator(transformedValue),
      issues: check.validator(transformedValue) ? [] : check.issues
    });
  });

  // Analyze enrichment
  const enrichmentFields = [
    {
      field: 'style',
      confidence: 0.9,
      source: 'analyzed' as const
    },
    {
      field: 'metadata.visualAttributes.wearLayer',
      confidence: 0.8,
      source: 'derived' as const
    },
    {
      field: 'metadata.visualAttributes.formalLevel',
      confidence: 0.7,
      source: 'default' as const
    }
  ];

  enrichmentFields.forEach(field => {
    const originalValue = getNestedValue(original, field.field);
    const transformedValue = getNestedValue(transformed, field.field);
    
    if (originalValue !== transformedValue) {
      metrics.enrichment.push({
        field: field.field,
        originalValue,
        transformedValue,
        confidence: field.confidence,
        source: field.source
      });
    }
  });

  // Analyze reliability
  const reliabilityChecks = [
    {
      field: 'metadata.visualAttributes.material',
      confidence: 0.85,
      validator: (value: any) => typeof value === 'string' && value.length > 0
    },
    {
      field: 'metadata.visualAttributes.pattern',
      confidence: 0.8,
      validator: (value: any) => typeof value === 'string' && value.length > 0
    },
    {
      field: 'metadata.visualAttributes.fit',
      confidence: 0.9,
      validator: (value: any) => typeof value === 'string' && value.length > 0
    }
  ];

  reliabilityChecks.forEach(check => {
    const value = getNestedValue(transformed, check.field);
    const validationPassed = check.validator(value);
    
    metrics.reliability.push({
      field: check.field,
      confidence: check.confidence,
      validationPassed,
      potentialIssues: validationPassed ? [] : ['Value may not be accurate']
    });
  });

  return metrics;
}

export async function cleanAndStoreWardrobeItem(
  userId: string,
  originalItem: ClothingItem,
  analyzedData: Garment
): Promise<{ item: ClothingItem; quality: DataQualityMetrics }> {
  // Create a cleaned version of the item
  const cleanedItem: ClothingItem = {
    id: originalItem.id,
    userId,
    name: originalItem.name || analyzedData.name || 'Unnamed Item',
    type: originalItem.type,
    color: analyzedData.color,
    season: analyzedData.season.filter(s => s !== 'all-season') as ('spring' | 'summer' | 'fall' | 'winter')[],
    imageUrl: originalItem.imageUrl,
    tags: [...new Set([...(originalItem.tags || []), ...(analyzedData.tags || [])])],
    style: analyzedData.style,
    dominantColors: analyzedData.dominantColors.map(color => ({
      name: color.name || 'unknown',
      hex: color.hex || '#000000',
      rgb: Array.isArray(color.rgb) && color.rgb.length === 3 ? color.rgb : [0, 0, 0]
    })),
    matchingColors: analyzedData.matchingColors.map(color => ({
      name: color.name || 'unknown',
      hex: color.hex || '#000000',
      rgb: Array.isArray(color.rgb) && color.rgb.length === 3 ? color.rgb : [0, 0, 0]
    })),
    occasion: analyzedData.occasion,
    brand: analyzedData.brand || originalItem.brand,
    createdAt: originalItem.createdAt,
    updatedAt: Date.now(),
    subType: analyzedData.subType || originalItem.subType,
    colorName: analyzedData.colorName || originalItem.colorName || null,
    backgroundRemoved: analyzedData.backgroundRemoved || originalItem.backgroundRemoved || false,
    metadata: {
      brand: analyzedData.brand || originalItem.brand || null,
      analysisTimestamp: Date.now(),
      originalType: originalItem.type,
      originalSubType: originalItem.subType,
      styleTags: analyzedData.style || [],
      occasionTags: analyzedData.occasion || [],
      imageHash: originalItem.metadata?.imageHash || null,
      colorAnalysis: {
        dominant: analyzedData.dominantColors.map(color => ({
          name: color.name || 'unknown',
          hex: color.hex || '#000000',
          rgb: Array.isArray(color.rgb) && color.rgb.length === 3 ? color.rgb : [0, 0, 0]
        })),
        matching: analyzedData.matchingColors.map(color => ({
          name: color.name || 'unknown',
          hex: color.hex || '#000000',
          rgb: Array.isArray(color.rgb) && color.rgb.length === 3 ? color.rgb : [0, 0, 0]
        }))
      },
      basicMetadata: analyzedData.metadata?.basicMetadata || {},
      visualAttributes: {
        material: analyzedData.material || null,
        pattern: analyzedData.pattern || null,
        textureStyle: analyzedData.metadata?.visualAttributes?.textureStyle || null,
        fabricWeight: analyzedData.metadata?.visualAttributes?.fabricWeight || null,
        fit: analyzedData.fit || null,
        silhouette: analyzedData.metadata?.visualAttributes?.silhouette || null,
        length: analyzedData.metadata?.visualAttributes?.length || null,
        genderTarget: analyzedData.metadata?.visualAttributes?.genderTarget || 'unisex',
        sleeveLength: analyzedData.metadata?.visualAttributes?.sleeveLength || null,
        hangerPresent: analyzedData.metadata?.visualAttributes?.hangerPresent || false,
        backgroundRemoved: analyzedData.backgroundRemoved || false,
        wearLayer: analyzedData.metadata?.visualAttributes?.wearLayer || 'outer',
        formalLevel: analyzedData.metadata?.visualAttributes?.formalLevel || 'casual'
      },
      itemMetadata: {
        ...(analyzedData.metadata?.itemMetadata || {}),
        tags: [...new Set([
          ...(analyzedData.metadata?.itemMetadata?.tags || []),
          ...(originalItem.metadata?.itemMetadata?.tags || [])
        ])]
      },
      naturalDescription: originalItem.metadata?.naturalDescription || null
    }
  };

  // Remove any undefined values from the cleaned item
  const removeUndefined = (obj: any): any => {
    if (Array.isArray(obj)) {
      return obj.map(item => removeUndefined(item));
    }
    if (obj !== null && typeof obj === 'object') {
      return Object.fromEntries(
        Object.entries(obj)
          .filter(([_, v]) => v !== undefined)
          .map(([k, v]) => [k, removeUndefined(v)])
      );
    }
    return obj;
  };

  const cleanedItemWithoutUndefined = removeUndefined(cleanedItem);

  // Validate the cleaned item
  const validatedItem = validateClothingItem(cleanedItemWithoutUndefined);

  // Analyze data quality
  const quality = analyzeDataQuality(originalItem, validatedItem);

  // Store in Firebase under the wardrobe collection
  const docRef = doc(collection(db, 'wardrobe'), validatedItem.id);
  await setDoc(docRef, {
    ...validatedItem,
    qualityMetrics: quality // Store quality metrics as a separate field
  });

  return { item: validatedItem, quality };
}

// Add a test function for processing a single item
export async function testProcessWardrobeItem(
  userId: string,
  itemId: string,
  analyzedData: Garment
): Promise<{
  success: boolean;
  item?: ClothingItem;
  quality?: DataQualityMetrics;
  error?: string;
}> {
  try {
    console.log(`Testing processing for item ${itemId}`);
    
    // Get the original item
    const wardrobeRef = collection(db, 'wardrobe');
    const itemDoc = await getDocs(query(wardrobeRef, where('id', '==', itemId)));
    
    if (itemDoc.empty) {
      return {
        success: false,
        error: 'Item not found'
      };
    }

    const originalItem = itemDoc.docs[0].data() as ClothingItem;
    
    // Process the item
    const { item: cleanedItem, quality } = await cleanAndStoreWardrobeItem(userId, originalItem, analyzedData);
    
    // Log detailed quality metrics
    console.log('Data quality metrics:', {
      completeness: {
        original: quality.completeness.originalCompleteness,
        transformed: quality.completeness.transformedCompleteness,
        improvement: quality.completeness.overallImprovement
      },
      consistency: quality.consistency.map(c => ({
        field: c.field,
        isValid: c.isValid,
        issues: c.issues
      })),
      enrichment: quality.enrichment.map(e => ({
        field: e.field,
        confidence: e.confidence,
        source: e.source
      })),
      reliability: quality.reliability.map(r => ({
        field: r.field,
        confidence: r.confidence,
        validationPassed: r.validationPassed
      }))
    });

    return {
      success: true,
      item: cleanedItem,
      quality
    };
  } catch (error) {
    console.error('Error in test processing:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
} 