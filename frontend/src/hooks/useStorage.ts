import { useState, useCallback } from "react";
import type { ClothingItem } from "@/lib/utils/outfitGenerator";

export function useStorage() {
  const [items, setItems] = useState<ClothingItem[]>([]);

  // Get all items
  const getItems = useCallback(async (): Promise<ClothingItem[]> => {
    try {
      // TODO: Replace with actual API call
      // For now, return sample data
      return [
        {
          id: "1",
          name: "White T-Shirt",
          type: "Top",
          color: "White",
          season: ["Spring", "Summer"],
          imageUrl: "/placeholder.jpg",
          tags: ["Casual", "Basic"],
          style: ["Minimal", "Streetwear"],
        },
        {
          id: "2",
          name: "Blue Jeans",
          type: "Bottom",
          color: "Blue",
          season: ["Spring", "Summer", "Fall"],
          imageUrl: "/placeholder.jpg",
          tags: ["Casual", "Denim"],
          style: ["Streetwear", "Classic"],
        },
      ];
    } catch (error) {
      console.error("Error fetching items:", error);
      return [];
    }
  }, []);

  // Add new item
  const addItem = useCallback(async (item: Omit<ClothingItem, "id">): Promise<ClothingItem> => {
    try {
      // TODO: Replace with actual API call
      const newItem = {
        ...item,
        id: Math.random().toString(36).substr(2, 9),
      };
      setItems((prev) => [...prev, newItem]);
      return newItem;
    } catch (error) {
      console.error("Error adding item:", error);
      throw error;
    }
  }, []);

  // Update item
  const updateItem = useCallback(async (id: string, updates: Partial<ClothingItem>): Promise<ClothingItem> => {
    try {
      // TODO: Replace with actual API call
      setItems((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, ...updates } : item
        )
      );
      const updatedItem = items.find((item) => item.id === id);
      if (!updatedItem) throw new Error("Item not found");
      return updatedItem;
    } catch (error) {
      console.error("Error updating item:", error);
      throw error;
    }
  }, [items]);

  // Delete item
  const deleteItem = useCallback(async (id: string): Promise<void> => {
    try {
      // TODO: Replace with actual API call
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (error) {
      console.error("Error deleting item:", error);
      throw error;
    }
  }, []);

  return {
    items,
    getItems,
    addItem,
    updateItem,
    deleteItem,
  };
} 