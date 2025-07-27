import type { OpenAIClothingAnalysis } from "@shared/types";

export async function analyzeClothingImage(imageUrl: string): Promise<OpenAIClothingAnalysis> {
  try {
    console.log("Sending image for enhanced analysis:", imageUrl);
    
    // Call the frontend API route instead of backend directly
    const response = await fetch('/api/analyze-image', {
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
        dominantColors: analysis.dominantColors || [],
        matchingColors: analysis.matchingColors || [],
        style: analysis.style || [],
        brand: analysis.brand || '',
        season: analysis.season || [],
        occasion: analysis.occasion || []
      };

      return transformedAnalysis;
    } catch (parseError) {
      console.error("Error parsing analysis response:", parseError);
      throw new Error('Failed to parse analysis response');
    }
  } catch (error) {
    console.error("Error in analyzeClothingImage:", error);
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