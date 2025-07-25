import { ClothingItem, OpenAIClothingAnalysis } from "@shared/types";
import { validateOpenAIAnalysis, createSuccessResponse, createErrorResponse } from "@shared/utils/validation";

export const analyzeImage = async (imageFile: File): Promise<OpenAIClothingAnalysis> => {
  try {
    // Convert image to base64
    const base64Image = await new Promise<string>((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        resolve(base64);
      };
      reader.readAsDataURL(imageFile);
    });

    // Call the API endpoint
    const response = await fetch('/api/analyze-image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: base64Image,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || 'Failed to analyze image');
    }

    const data = await response.json();
    const validatedData = validateOpenAIAnalysis(data);
    return validatedData;
  } catch (error) {
    console.error('Error analyzing image:', error);
    throw error;
  }
}; 