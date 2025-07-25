import { ClothingItem } from '../types';

/**
 * Computes the cosine similarity between two embedding vectors
 * @param vec1 First embedding vector
 * @param vec2 Second embedding vector
 * @returns Cosine similarity score between -1 and 1
 */
export function cosineSimilarity(vec1: number[], vec2: number[]): number {
  if (vec1.length !== vec2.length) {
    throw new Error('Vectors must have the same length');
  }

  const dotProduct = vec1.reduce((sum, val, i) => sum + val * vec2[i], 0);
  const magnitude1 = Math.sqrt(vec1.reduce((sum, val) => sum + val * val, 0));
  const magnitude2 = Math.sqrt(vec2.reduce((sum, val) => sum + val * val, 0));

  return dotProduct / (magnitude1 * magnitude2);
}

/**
 * Finds the most similar items to a given item based on embedding similarity
 * @param targetItem The item to find similar items for
 * @param items Array of items to search through
 * @param limit Maximum number of similar items to return
 * @returns Array of items sorted by similarity
 */
export function findSimilarItems(
  targetItem: ClothingItem,
  items: ClothingItem[],
  limit: number = 5
): ClothingItem[] {
  if (!targetItem.embedding) {
    throw new Error('Target item must have an embedding');
  }

  return items
    .filter(item => item.id !== targetItem.id && item.embedding)
    .map(item => ({
      item,
      similarity: cosineSimilarity(targetItem.embedding!, item.embedding!)
    }))
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, limit)
    .map(({ item }) => item);
} 