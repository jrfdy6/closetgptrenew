// Validation utilities
export const validateImageFile = (file: File): boolean => {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  return validTypes.includes(file.type)
}

export const validateFileSize = (file: File, maxSizeMB: number = 10): boolean => {
  return file.size <= maxSizeMB * 1024 * 1024
}

// Placeholder function for converting OpenAI analysis to clothing item
export const convertOpenAIAnalysisToClothingItem = (analysis: any) => {
  // This is a placeholder - implement based on your analysis structure
  return {
    id: '',
    type: '',
    color: '',
    style: '',
    occasion: '',
    season: '',
    // Add other fields as needed
  };
};
