import type { OpenAIClothingAnalysis } from "@shared/types";

export async function analyzeClothingImage(imageUrl: string): Promise<OpenAIClothingAnalysis> {
  try {
    console.log("Sending image for enhanced analysis:", imageUrl);
    
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgpt-clean-production.up.railway.app';
    const response = await fetch(`${backendUrl}/api/analyze-image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: { url: imageUrl } }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("API Error Response:", {
        status: response.status,
        statusText: response.statusText,
        data: errorData
      });
      throw new Error(errorData.error || errorData.details || 'Failed to analyze image');
    }

    const data = await response.json();

    // Log the raw response for debugging
    console.log("Raw enhanced API response:", data);

    // Parse the analysis from the response
    let analysis;
    try {
      // The backend returns { analysis: {...} }
      analysis = data.analysis;
      
      // Transform enhanced analysis to match expected format
      const transformedAnalysis: OpenAIClothingAnalysis = {
        type: analysis.type || 'other',
        subType: analysis.subType || 'Unnamed Item',
        name: analysis.name || `${analysis.type}${analysis.subType ? ` - ${analysis.subType}` : ''}`,
        dominantColors: analysis.dominantColors || [],
        matchingColors: analysis.matchingColors || [],
        style: analysis.style || [],
        brand: analysis.brand || '',
        season: analysis.season || [],
        occasion: analysis.occasion || [],
        metadata: {
          analysisTimestamp: Date.now(),
          originalType: analysis.type || 'other',
          originalSubType: analysis.subType,
          styleTags: analysis.style || [],
          occasionTags: analysis.occasion || [],
          colorAnalysis: {
            dominant: analysis.dominantColors || [],
            matching: analysis.matchingColors || []
          },
          basicMetadata: analysis.metadata?.basicMetadata || {},
          visualAttributes: {
            material: analysis.metadata?.visualAttributes?.material || null,
            pattern: analysis.metadata?.visualAttributes?.pattern || null,
            textureStyle: analysis.metadata?.visualAttributes?.textureStyle || null,
            fabricWeight: analysis.metadata?.visualAttributes?.fabricWeight || null,
            fit: analysis.metadata?.visualAttributes?.fit || null,
            silhouette: analysis.metadata?.visualAttributes?.silhouette || null,
            length: analysis.metadata?.visualAttributes?.length || null,
            genderTarget: analysis.metadata?.visualAttributes?.genderTarget || 'unisex',
            sleeveLength: analysis.metadata?.visualAttributes?.sleeveLength || null,
            hangerPresent: analysis.metadata?.visualAttributes?.hangerPresent || null,
            backgroundRemoved: analysis.metadata?.visualAttributes?.backgroundRemoved || false,
            wearLayer: analysis.metadata?.visualAttributes?.wearLayer || 'outer',
            formalLevel: analysis.metadata?.visualAttributes?.formalLevel || 'casual',
            // Enhanced analysis fields
            temperatureCompatibility: analysis.metadata?.visualAttributes?.temperatureCompatibility || {
              minTemp: 32,
              maxTemp: 75,
              recommendedLayers: [],
              materialPreferences: []
            },
            materialCompatibility: analysis.metadata?.visualAttributes?.materialCompatibility || {
              compatibleMaterials: [],
              weatherAppropriate: {
                spring: [],
                summer: [],
                fall: [],
                winter: []
              }
            },
            bodyTypeCompatibility: analysis.metadata?.visualAttributes?.bodyTypeCompatibility || {
              hourglass: {"recommendedFits": [], "styleRecommendations": []},
              pear: {"recommendedFits": [], "styleRecommendations": []},
              apple: {"recommendedFits": [], "styleRecommendations": []},
              rectangle: {"recommendedFits": [], "styleRecommendations": []},
              inverted_triangle: {"recommendedFits": [], "styleRecommendations": []}
            },
            skinToneCompatibility: analysis.metadata?.visualAttributes?.skinToneCompatibility || {
              warm: {"compatibleColors": [], "recommendedColorPalette": []},
              cool: {"compatibleColors": [], "recommendedColorPalette": []},
              neutral: {"compatibleColors": [], "recommendedColorPalette": []}
            }
          },
          itemMetadata: {
            priceEstimate: analysis.metadata?.itemMetadata?.priceEstimate || null,
            careInstructions: analysis.metadata?.itemMetadata?.careInstructions || null,
            tags: analysis.metadata?.itemMetadata?.tags || []
          },
          naturalDescription: analysis.metadata?.naturalDescription || null,
          // Enhanced analysis metadata
          clipAnalysis: analysis.metadata?.clipAnalysis || null,
          confidenceScores: analysis.metadata?.confidenceScores || {
            styleAnalysis: 0,
            gptAnalysis: 0.85,
            overallConfidence: 0.425
          },
          styleCompatibility: analysis.metadata?.styleCompatibility || {
            primaryStyle: null,
            compatibleStyles: [],
            avoidStyles: [],
            styleNotes: ""
          },
          enhancedStyles: analysis.style || [],
          enhancedOccasions: analysis.occasion || [],
          enhancedColorAnalysis: {
            dominant: analysis.dominantColors || [],
            matching: analysis.matchingColors || []
          }
        }
      };

      console.log("Successfully received and transformed enhanced analysis:", transformedAnalysis);
      return transformedAnalysis;
    } catch (parseError) {
      console.error("Failed to parse enhanced analysis:", {
        rawData: data,
        error: parseError
      });
      throw new Error('Invalid enhanced analysis response format');
    }
  } catch (error) {
    console.error("Error analyzing image with enhanced analysis:", error);
    if (error instanceof Error) {
      console.error("Error details:", {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
    }
    throw error;
  }
}

export async function analyzeClothingImageLegacy(imageUrl: string): Promise<OpenAIClothingAnalysis> {
  try {
    console.log("Sending image for legacy analysis:", imageUrl);
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://closetgpt-clean-production.up.railway.app'}/api/analyze-image-legacy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: { url: imageUrl } }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || errorData.details || 'Failed to analyze image');
    }

    const data = await response.json();
    return data.analysis;
  } catch (error) {
    console.error("Error analyzing image with legacy analysis:", error);
    throw error;
  }
}

export async function analyzeClothingImageClipOnly(imageUrl: string): Promise<any> {
  try {
    console.log("Sending image for CLIP-only analysis:", imageUrl);
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://closetgpt-clean-production.up.railway.app'}/api/analyze-image-clip-only`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: { url: imageUrl } }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || errorData.details || 'Failed to analyze image');
    }

    const data = await response.json();
    return data.analysis;
  } catch (error) {
    console.error("Error analyzing image with CLIP-only analysis:", error);
    throw error;
  }
}

export async function analyzeMultipleImages(imageUrls: string[]): Promise<OpenAIClothingAnalysis[]> {
  console.log("Analyzing multiple images with enhanced analysis:", imageUrls);
  const analysisPromises = imageUrls.map(url => analyzeClothingImage(url));
  return Promise.all(analysisPromises);
}

export async function analyzeMultipleImagesLegacy(imageUrls: string[]): Promise<OpenAIClothingAnalysis[]> {
  console.log("Analyzing multiple images with legacy analysis:", imageUrls);
  const analysisPromises = imageUrls.map(url => analyzeClothingImageLegacy(url));
  return Promise.all(analysisPromises);
}

export async function analyzeMultipleImagesClipOnly(imageUrls: string[]): Promise<any[]> {
  console.log("Analyzing multiple images with CLIP-only analysis:", imageUrls);
  const analysisPromises = imageUrls.map(url => analyzeClothingImageClipOnly(url));
  return Promise.all(analysisPromises);
} 