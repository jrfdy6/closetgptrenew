// Validation utilities
export const validateImageFile = (file: File): boolean => {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  return validTypes.includes(file.type)
}

export const validateFileSize = (file: File, maxSizeMB: number = 10): boolean => {
  return file.size <= maxSizeMB * 1024 * 1024
}

// Convert OpenAI analysis to clothing item
export const convertOpenAIAnalysisToClothingItem = (analysis: any, userId: string, imageUrl: string) => {
  console.log('🔄 Converting AI analysis to clothing item:', analysis);
  
  // Extract basic information
  const name = analysis.name || analysis.subType || 'Unnamed Item';
  const type = analysis.type || 'other';
  const subType = analysis.subType || '';
  
  // Extract colors
  const dominantColors = analysis.dominantColors || [];
  const primaryColor = dominantColors.length > 0 ? dominantColors[0].name : 'unknown';
  
  // Extract arrays
  const styles = analysis.style || [];
  const occasions = analysis.occasion || [];
  const seasons = analysis.season || [];
  
  // Extract metadata
  const metadata = analysis.metadata || {};
  const visualAttributes = metadata.visualAttributes || {};
  const itemMetadata = metadata.itemMetadata || {};
  
  const clothingItem = {
    // Basic fields
    name,
    type,
    subType,
    color: primaryColor,
    imageUrl,
    userId,
    
    // Arrays
    style: styles,
    occasion: occasions,
    season: seasons,
    tags: itemMetadata.tags || [],
    
    // Colors
    dominantColors,
    matchingColors: analysis.matchingColors || [],
    
    // Visual attributes
    material: visualAttributes.material || '',
    pattern: visualAttributes.pattern || '',
    textureStyle: visualAttributes.textureStyle || '',
    fabricWeight: visualAttributes.fabricWeight || '',
    fit: visualAttributes.fit || '',
    silhouette: visualAttributes.silhouette || '',
    length: visualAttributes.length || '',
    genderTarget: visualAttributes.genderTarget || '',
    sleeveLength: visualAttributes.sleeveLength || '',
    formalLevel: visualAttributes.formalLevel || '',
    
    // Phase 1 new attributes for gender-inclusive outfit generation
    neckline: visualAttributes.neckline || '',
    transparency: visualAttributes.transparency || 'opaque',
    collarType: visualAttributes.collarType || '',
    embellishments: visualAttributes.embellishments || 'none',
    printSpecificity: visualAttributes.printSpecificity || 'none',
    rise: visualAttributes.rise || '',
    legOpening: visualAttributes.legOpening || '',
    heelHeight: visualAttributes.heelHeight || '',
    statementLevel: visualAttributes.statementLevel || 0,
    waistbandType: visualAttributes.waistbandType || '',
    
    // Brand and description
    brand: analysis.brand || '',
    description: metadata.naturalDescription || `${type} ${subType ? `(${subType})` : ''} in ${primaryColor}`,
    
    // CRITICAL: Send the complete analysis object so backend can extract all metadata
    analysis: analysis,
    
    // Metadata
    metadata: {
      ...metadata,
      aiGenerated: true,
      analysisTimestamp: new Date().toISOString(),
      confidence: metadata.confidenceScores?.overallConfidence || 0.8
    },
    
    // Compatibility data
    temperatureCompatibility: visualAttributes.temperatureCompatibility || {},
    materialCompatibility: visualAttributes.materialCompatibility || {},
    bodyTypeCompatibility: visualAttributes.bodyTypeCompatibility || {},
    skinToneCompatibility: visualAttributes.skinToneCompatibility || {},
    
    // Item metadata
    priceEstimate: itemMetadata.priceEstimate || '',
    careInstructions: itemMetadata.careInstructions || '',
    outfitScoring: itemMetadata.outfitScoring || {},
    
    // Status fields
    wearCount: 0,
    favorite: false,
    lastWorn: null,
    
    // Timestamps
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  console.log('✅ Converted clothing item:', clothingItem);
  return clothingItem;
};
