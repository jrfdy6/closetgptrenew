import { ClothingItem } from '../../../../shared/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export const wardrobeApi = {
  async addItem(item: Omit<ClothingItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<ClothingItem> {
    const response = await fetch(`${API_BASE_URL}/api/wardrobe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(item),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add item');
    }

    return response.json();
  },

  async updateItem(itemId: string, updates: Partial<ClothingItem>): Promise<ClothingItem> {
    const response = await fetch(`${API_BASE_URL}/api/wardrobe/${itemId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update item');
    }

    return response.json();
  },

  async deleteItem(itemId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/wardrobe/${itemId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete item');
    }
  },

  async getItems(userId: string): Promise<ClothingItem[]> {
    const response = await fetch(`${API_BASE_URL}/api/wardrobe?user_id=${userId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get items');
    }

    return response.json();
  },

  async getItem(itemId: string): Promise<ClothingItem> {
    const response = await fetch(`${API_BASE_URL}/api/wardrobe/${itemId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get item');
    }

    return response.json();
  },
}; 