import { NextResponse } from 'next/server';
import { NextRequest } from 'next/server';
import { getAuth } from '@clerk/nextjs/server';
import { adminDb } from '@/lib/firebase-admin';
import { getStorage } from 'firebase-admin/storage';
import { PhotoAnalysis, UserPhotos, OutfitAnalysis } from '@/types/photo-analysis';
import { Firestore } from 'firebase-admin/firestore';
import { analyzePhoto } from '@/services/photoAnalysis';

// Cache for analysis results
const analysisCache = new Map<string, PhotoAnalysis>();

export async function POST(req: NextRequest) {
  try {
    // Check if Firebase Admin is initialized
    if (!adminDb) {
      return new NextResponse(
        JSON.stringify({ error: 'Firebase Admin not initialized' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const { userId } = getAuth(req);
    if (!userId) {
      return new NextResponse('Unauthorized', { status: 401 });
    }

    const formData = await req.formData();
    const file = formData.get('file') as File;
    const type = formData.get('type') as 'fullBody' | 'outfit';

    if (!file) {
      return new NextResponse('No file provided', { status: 400 });
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      return new NextResponse('Invalid file type. Only images are allowed.', { status: 400 });
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      return new NextResponse('File too large. Maximum size is 5MB.', { status: 400 });
    }

    // Convert File to Buffer for Firebase Storage
    const buffer = Buffer.from(await file.arrayBuffer());
    const filename = `${userId}/${type}/${Date.now()}-${file.name}`;

    // Upload to Firebase Storage
    const bucket = getStorage().bucket();
    const fileRef = bucket.file(filename);
    await fileRef.save(buffer, {
      metadata: {
        contentType: file.type,
      },
    });

    // Get the public URL
    const [url] = await fileRef.getSignedUrl({
      action: 'read',
      expires: '03-01-2500', // Far future expiration
    });

    // Check cache for existing analysis
    const cacheKey = `${userId}-${type}-${file.name}`;
    let analysis = analysisCache.get(cacheKey);

    if (!analysis) {
      // Convert buffer to ImageData for analysis
      const imageData = await bufferToImageData(buffer);
      analysis = await analyzePhoto(imageData, type);
      analysisCache.set(cacheKey, analysis);
    }

    // Update user's photos in Firestore
    const userRef = (adminDb as Firestore).collection('users').doc(userId);
    const userDoc = await userRef.get();
    const userData = userDoc.data() as { photos?: UserPhotos };

    // Initialize default values for UserPhotos
    const defaultPhotos: UserPhotos = {
      fullBodyPhoto: '',
      outfitPhotos: [],
      analyses: {
        fullBody: undefined,
        outfits: [],
      },
      lastUpdated: new Date().toISOString(),
    };

    const existingPhotos = userData?.photos || defaultPhotos;

    const updatedPhotos: UserPhotos = {
      ...existingPhotos,
      [type === 'fullBody' ? 'fullBodyPhoto' : 'outfitPhotos']: type === 'fullBody'
        ? url
        : [...existingPhotos.outfitPhotos, url],
      analyses: {
        ...existingPhotos.analyses,
        [type === 'fullBody' ? 'fullBody' : 'outfits']: type === 'fullBody'
          ? analysis
          : [...existingPhotos.analyses.outfits, analysis.outfitAnalysis as OutfitAnalysis],
      },
      lastUpdated: new Date().toISOString(),
    };

    await userRef.set({ photos: updatedPhotos }, { merge: true });

    return NextResponse.json({ photoUrl: url, analysis });
  } catch (error) {
    console.error('Error uploading photo:', error);
    return new NextResponse(
      JSON.stringify({
        error: 'Failed to upload photo',
        details: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
}

// Helper function to convert buffer to ImageData
async function bufferToImageData(buffer: Buffer): Promise<ImageData> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }
      ctx.drawImage(img, 0, 0);
      resolve(ctx.getImageData(0, 0, img.width, img.height));
    };
    img.onerror = () => reject(new Error('Failed to load image'));
    img.src = `data:image/jpeg;base64,${buffer.toString('base64')}`;
  });
} 