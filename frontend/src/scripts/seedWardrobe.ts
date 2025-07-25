import { ClothingItem } from "../../../shared/types";

const sampleItems: Omit<ClothingItem, 'id'>[] = [
  {
    type: "pants",
    subType: "Blue Denim Jeans",
    userId: "user123",
    dominantColors: [
      {
        name: "blue",
        hex: "#1E90FF",
        rgb: [30, 144, 255]
      }
    ],
    matchingColors: [
      {
        name: "white",
        hex: "#FFFFFF",
        rgb: [255, 255, 255]
      },
      {
        name: "black",
        hex: "#000000",
        rgb: [0, 0, 0]
      }
    ],
    style: ["casual", "streetwear"],
    season: ["spring", "summer", "fall"],
    occasion: ["casual", "everyday"],
    imageUrl: "https://via.placeholder.com/400x600/1E90FF/FFFFFF?text=Jeans",
    createdAt: Date.now(),
    updatedAt: Date.now(),
    metadata: {}
  },
  {
    type: "shirt",
    subType: "White T-Shirt",
    userId: "user123",
    dominantColors: [
      {
        name: "white",
        hex: "#FFFFFF",
        rgb: [255, 255, 255]
      }
    ],
    matchingColors: [
      {
        name: "blue",
        hex: "#1E90FF",
        rgb: [30, 144, 255]
      },
      {
        name: "black",
        hex: "#000000",
        rgb: [0, 0, 0]
      }
    ],
    style: ["casual", "minimalist"],
    season: ["spring", "summer"],
    occasion: ["casual", "everyday"],
    imageUrl: "https://via.placeholder.com/400x600/FFFFFF/000000?text=T-Shirt",
    createdAt: Date.now(),
    updatedAt: Date.now(),
    metadata: {}
  }
];

export async function seedWardrobe(userId: string) {
  try {
    const { addMultipleWardrobeItems } = await import("@/lib/firebase/wardrobeService");
    const response = await addMultipleWardrobeItems(userId, sampleItems);
    if (!response.success) {
      throw new Error(response.error);
    }
    console.log("Successfully seeded wardrobe with sample items");
    return response.data;
  } catch (error) {
    console.error("Failed to seed wardrobe:", error);
    throw error;
  }
}

// Add a CLI command to run the seeding script
if (require.main === module) {
  const userId = process.argv[2];
  if (!userId) {
    console.error("Please provide a userId as an argument.");
    process.exit(1);
  }
  seedWardrobe(userId).catch(console.error);
} 