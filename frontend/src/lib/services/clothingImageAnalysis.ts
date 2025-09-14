// Clothing image analysis service
export const analyzeClothingImage = async (imageUrl: string) => {
  try {
    console.log('🔍 analyzeClothingImage called with URL length:', imageUrl.length);
    console.log('🔍 Image URL starts with:', imageUrl.substring(0, 50) + '...');
    
    // Get the current user's ID token for authentication
    const { auth } = await import('@/lib/firebase/config');
    const user = auth.currentUser;
    
    if (!user) {
      throw new Error('User not authenticated');
    }
    
    const token = await user.getIdToken();
    
    const response = await fetch('/api/analyze-image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ image: imageUrl }),
    });

    console.log('📡 Response status:', response.status, response.statusText);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ API Error:', errorData);
      throw new Error(errorData.error || 'Failed to analyze image');
    }

    const data = await response.json();
    console.log('✅ Analysis completed:', data);
    return data.analysis || data;
  } catch (error) {
    console.error('❌ Error analyzing clothing image:', error);
    throw error;
  }
}

export const processImageForAnalysis = async (file: File) => {
  try {
    console.log('🔄 processImageForAnalysis called with file:', file.name, file.size);
    
    // Convert file to base64 for analysis
    const base64 = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        console.log('📸 File converted to base64, length:', reader.result?.toString().length);
        resolve(reader.result as string);
      };
      reader.onerror = (error) => {
        console.error('❌ FileReader error:', error);
        reject(error);
      };
      reader.readAsDataURL(file);
    });

    console.log('🔄 Calling analyzeClothingImage with base64...');
    const result = await analyzeClothingImage(base64);
    console.log('✅ processImageForAnalysis completed:', result);
    return result;
  } catch (error) {
    console.error('❌ Error processing image for analysis:', error);
    throw error;
  }
}
