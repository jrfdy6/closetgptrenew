import { OpenAIClothingAnalysis } from '@shared/types/wardrobe';

export const analyzeClothingImage = async (imageUrl: string): Promise<OpenAIClothingAnalysis> => {
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ imageUrl }),
    });

    if (!response.ok) {
      throw new Error('Failed to analyze image');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error analyzing image:', error);
    throw error;
  }
}; 