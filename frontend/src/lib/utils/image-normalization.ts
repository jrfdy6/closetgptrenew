import { ref, uploadString, getDownloadURL } from "firebase/storage";
import { storage } from "@/lib/firebase";

/**
 * Normalizes image data by uploading base64 images to Firebase Storage
 * and returning the download URL. If the image is already a valid URL,
 * it returns the URL as-is.
 */
export async function normalizeImage(
  imageUrl: string, 
  userId: string, 
  itemId: string
): Promise<string> {
  // If it's already a valid HTTPS URL, return it
  if (imageUrl.startsWith("https://")) {
    return imageUrl;
  }

  // If it's a base64 data URL, upload to Firebase Storage
  if (imageUrl.startsWith("data:image")) {
    try {
      const storageRef = ref(storage, `users/${userId}/wardrobe/${itemId}.jpg`);
      await uploadString(storageRef, imageUrl, "data_url");
      const downloadURL = await getDownloadURL(storageRef);
      console.log(`✅ Image uploaded to Firebase Storage: ${downloadURL}`);
      return downloadURL;
    } catch (error) {
      console.error("❌ Failed to upload image to Firebase Storage:", error);
      throw new Error("Failed to upload image to storage");
    }
  }

  // If it's an invalid format, throw an error
  throw new Error(`Invalid image URL format: ${imageUrl}`);
}

/**
 * Normalizes all images in a wardrobe item object
 */
export async function normalizeWardrobeItemImages(
  item: any,
  userId: string
): Promise<any> {
  const normalizedItem = { ...item };

  // Normalize the main image
  if (normalizedItem.imageUrl) {
    normalizedItem.imageUrl = await normalizeImage(
      normalizedItem.imageUrl,
      userId,
      normalizedItem.id || `temp_${Date.now()}`
    );
  }

  // Normalize any additional images in metadata
  if (normalizedItem.metadata?.additionalImages) {
    const normalizedAdditionalImages = [];
    for (let i = 0; i < normalizedItem.metadata.additionalImages.length; i++) {
      const imageUrl = normalizedItem.metadata.additionalImages[i];
      const normalizedUrl = await normalizeImage(
        imageUrl,
        userId,
        `${normalizedItem.id || `temp_${Date.now()}`}_additional_${i}`
      );
      normalizedAdditionalImages.push(normalizedUrl);
    }
    normalizedItem.metadata.additionalImages = normalizedAdditionalImages;
  }

  return normalizedItem;
}
