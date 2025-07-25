import { ClothingItem } from '@shared/types';

/**
 * Generates a CLIP embedding for a clothing item image
 * @param itemId The ID of the clothing item
 * @param imageFile The image file to generate embedding for
 * @returns The updated clothing item with embedding
 */
export async function generateEmbedding(itemId: string, imageFile: File): Promise<ClothingItem> {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('item_id', itemId);

    const response = await fetch('/api/embed', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to generate embedding');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating embedding:', error);
    throw error;
  }
} 