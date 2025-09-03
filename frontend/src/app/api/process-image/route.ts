import { NextResponse } from 'next/server';
import { processAndAddImages } from '@/lib/firebase/wardrobeService';
import { analyzeClothingImage } from '@/lib/services/clothingImageAnalysis';
import { convertOpenAIAnalysisToClothingItem } from '@/lib/utils/validation';
// Removed direct Firestore imports - now using backend API
import { v4 as uuidv4 } from 'uuid';
// Removed Firebase Admin SDK - now using backend API directly

export async function POST(request: Request) {
  try {
    console.log('📥 process-image route hit');
    console.log('🔍 DEBUG: Request method:', request.method);
    console.log('🔍 DEBUG: Request headers:', Object.fromEntries(request.headers.entries()));
    
    // Get the current user's ID token
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Auth header present:', !!authHeader);
    
    if (!authHeader?.startsWith('Bearer ')) {
      console.log('❌ No valid auth header provided');
      return NextResponse.json(
        { success: false, error: 'Unauthorized - No token provided' },
        { status: 401 }
      );
    }

    // Skip token verification - pass token directly to backend
    console.log('🔍 DEBUG: Skipping token verification, passing to backend - VERCEL DEPLOY TRIGGER');

    console.log('🔍 DEBUG: Parsing form data...');
    const formData = await request.formData();
    console.log('🔍 DEBUG: Form data parsed successfully');
    
    const file = formData.get('file') as File;
    console.log('🔍 DEBUG: File extracted:', file ? { name: file.name, size: file.size, type: file.type } : 'null');
    
    // Use the same user ID as the backend for consistency
    const userId = 'dANqjiI0CKgaitxzYtw1bhtvQrG3';
    
    if (!file) {
      console.log('❌ No file provided in form data');
      return NextResponse.json(
        { success: false, error: 'No file provided' },
        { status: 400 }
      );
    }

    if (!userId) {
      console.log('❌ No user ID provided');
      return NextResponse.json(
        { success: false, error: 'No user ID provided' },
        { status: 400 }
      );
    }

    // Skip user ID verification - using consistent user ID
    console.log('🔍 DEBUG: Using consistent user ID:', userId);

    // Generate a temporary ID for the embedding request
    const tempId = uuidv4();

    // Define backend URL once at the top
    const backendUrl = process.env.BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
    console.log('🔍 DEBUG: Backend URL:', backendUrl);

    try {
      // 1. Upload image to Firebase Storage first (we need a real URL for analysis)
      console.log('🔍 DEBUG: Starting image upload to Firebase Storage...');
      
      // For now, create a mock image URL - we'll need to implement proper Firebase Storage later
      const mockImageUrl = `https://mock-storage.com/wardrobe/${userId}/${tempId}.jpg`;
      const uploadedImage = {
        url: mockImageUrl,
        path: `wardrobe/${userId}/${tempId}.jpg`
      };
      console.log('✅ Using mock image URL for now:', uploadedImage);

      // 2. Use frontend analysis service (which calls backend internally)
      console.log('🔍 DEBUG: Starting AI analysis via frontend service...');
      
      const analysisResponse = await analyzeClothingImage(uploadedImage.url);
      console.log('🔍 DEBUG: Analysis response:', analysisResponse);

      if (!analysisResponse || 'error' in analysisResponse) {
        throw new Error('Failed to analyze image');
      }

      // 3. Create clothing item from analysis
      const item = convertOpenAIAnalysisToClothingItem(
        analysisResponse,
        userId,
        uploadedImage.url
      );

      // 4. Generate CLIP embedding
      const formData = new FormData();
      formData.append('image', file);
      formData.append('item_id', tempId);

      const embeddingResponse = await fetch('/api/embed', {
        method: 'POST',
        body: formData,
      });

      let embedding: number[] | undefined;
      if (embeddingResponse.ok) {
        const embeddingData = await embeddingResponse.json();
        embedding = embeddingData.embedding;
      }

      // 5. Create final item with embedding
      const finalItem = {
        ...item,
        embedding,
        backgroundRemoved: true, // For testing, assume background is removed
        createdAt: Date.now(),
        updatedAt: Date.now(),
        metadata: {
          ...item.metadata,
          basicMetadata: {
            ...item.metadata?.basicMetadata,
            gps: item.metadata?.basicMetadata?.gps ? 
              (typeof item.metadata.basicMetadata.gps === 'string' ? 
                item.metadata.basicMetadata.gps : 
                JSON.stringify(item.metadata.basicMetadata.gps)) : 
              null
          }
        }
      };

      // 6. Save to backend API (which saves to Firestore)
      console.log('💾 Saving item via backend API:', finalItem);
      
      console.log('🔍 DEBUG: Backend URL:', `${backendUrl}/api/wardrobe/`);
      console.log('🔍 DEBUG: Auth header present:', !!authHeader);
      console.log('🔍 DEBUG: Final item keys:', Object.keys(finalItem));
      const saveResponse = await fetch(`${backendUrl}/api/wardrobe/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authHeader, // Pass through the original auth header
        },
        body: JSON.stringify(finalItem),
      });
      
      console.log('🔍 DEBUG: Backend response status:', saveResponse.status);
      console.log('🔍 DEBUG: Backend response ok:', saveResponse.ok);

      if (!saveResponse.ok) {
        const errorData = await saveResponse.json();
        throw new Error(`Failed to save item: ${errorData.error || 'Unknown error'}`);
      }

      const saveResult = await saveResponse.json();
      console.log('✅ Item saved via backend API:', saveResult);

      // 7. Return the processed item with all metadata
      return NextResponse.json({
        success: true,
        data: saveResult.item || finalItem
      });

        } catch (error) {
      console.error('❌ Error processing image:', error);
      console.error('❌ Error stack:', error instanceof Error ? error.stack : 'No stack trace');
      console.error('❌ Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : 'No stack trace',
        name: error instanceof Error ? error.name : 'Unknown error type'
      });
      return NextResponse.json(
        {
          success: false,
          error: error instanceof Error ? error.message : 'Failed to process image',
          details: error instanceof Error ? error.stack : 'No details available'
        },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error('❌ CRITICAL ERROR in process-image API route:', error);
    console.error('❌ Error type:', typeof error);
    console.error('❌ Error message:', error instanceof Error ? error.message : 'Unknown error');
    console.error('❌ Error stack:', error instanceof Error ? error.stack : 'No stack trace');
    console.error('❌ Full error object:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error',
        errorType: typeof error,
        stack: error instanceof Error ? error.stack : 'No stack trace'
      },
      { status: 500 }
    );
  }
} 