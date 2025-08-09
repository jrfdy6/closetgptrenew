import { NextResponse } from 'next/server';
import { uploadImage } from '@/lib/firebase/storageService';

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    const { imageUrl } = await request.json();

    if (!imageUrl) {
      return NextResponse.json(
        { error: 'Image URL is required' },
        { status: 400 }
      );
    }

    // If we have a file path, we need to upload it first
    let imageUrlToAnalyze = imageUrl;
    if (typeof imageUrl === 'object' && imageUrl.path) {
      try {
        // Create a File object from the path
        const file = new File([imageUrl.path], imageUrl.path.split('/').pop() || 'image.jpg', {
          type: 'image/jpeg',
        });

        // Upload to Firebase Storage
        const uploadedImage = await uploadImage(file, 'temp'); // Using 'temp' as userId for analysis
        imageUrlToAnalyze = uploadedImage.url;
      } catch (error) {
        console.error('Error uploading image:', error);
        return NextResponse.json(
          { error: 'Failed to upload image' },
          { status: 500 }
        );
      }
    }

    // Forward the request to the real backend
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-backend-production.up.railway.app';
    const response = await fetch(`${baseUrl}/api/analyze-image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: imageUrlToAnalyze }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || 'Failed to analyze image' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in analyze route:', error);
    return NextResponse.json(
      { error: 'Failed to analyze image' },
      { status: 500 }
    );
  }
} 