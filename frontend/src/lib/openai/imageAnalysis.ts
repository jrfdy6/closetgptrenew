import { OpenAIClothingAnalysis } from '@shared/types/wardrobe';

export const analyzeImage = async (imageUrl: string): Promise<OpenAIClothingAnalysis> => {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-backend-production.up.railway.app'}/api/analyze-image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: imageUrl }),
    });

    if (!response.ok) {
      throw new Error('Failed to analyze image');
    }

    const data = await response.json();
    return data as OpenAIClothingAnalysis;
  } catch (error) {
    console.error('Error analyzing image:', error);
    throw error;
  }
}; 