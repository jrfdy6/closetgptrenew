import { ApiResponse } from '@shared/types/responses';
import { OpenAIClothingAnalysis } from '@/types/wardrobe';

export async function analyzeClothingImage(imageUrl: string): Promise<ApiResponse<OpenAIClothingAnalysis>> {
  try {
    const response = await fetch('/api/analyze-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ imageUrl })
    });

    if (!response.ok) {
      const errorData = await response.json();
      return {
        success: false,
        error: errorData.error || 'Failed to analyze image',
        data: null
      };
    }

    const data = await response.json();
    return {
      success: true,
      data
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to analyze image',
      data: null
    };
  }
} 