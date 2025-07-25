/**
 * Converts an image file to WebP format if supported, otherwise returns the original file
 * @param file The input image file
 * @returns Promise<Blob> A blob containing the image data
 */
export const convertToWebP = async (file: File): Promise<Blob> => {
  // For now, just return the original file
  // TODO: Implement proper WebP conversion when needed
  return file;
}; 