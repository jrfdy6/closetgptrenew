import { NextResponse } from 'next/server';
import { NextRequest } from 'next/server';
import { getAuth } from '@clerk/nextjs/server';
import { adminDb } from '@/lib/firebase-admin';
import { getStorage } from 'firebase-admin/storage';
import { Firestore } from 'firebase-admin/firestore';
import { UserPhotos } from '@/types/photo-analysis';

export async function DELETE(req: NextRequest) {
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

    const { searchParams } = new URL(req.url);
    const photoUrl = searchParams.get('url');
    const type = searchParams.get('type') as 'fullBody' | 'outfit';

    if (!photoUrl || !type) {
      return new NextResponse('Missing required parameters', { status: 400 });
    }

    // Extract filename from URL
    const filename = photoUrl.split('/').pop();
    if (!filename) {
      return new NextResponse('Invalid photo URL', { status: 400 });
    }

    // Delete from Firebase Storage
    const bucket = getStorage().bucket();
    const fileRef = bucket.file(`${userId}/${type}/${filename}`);
    await fileRef.delete();

    // Update user's photos in Firestore
    const userRef = (adminDb as Firestore).collection('users').doc(userId);
    const userDoc = await userRef.get();
    const userData = userDoc.data() as { photos?: UserPhotos };

    if (!userData?.photos) {
      return new NextResponse('No photos found', { status: 404 });
    }

    const photos = userData.photos;
    const updatedPhotos: UserPhotos = {
      ...photos,
      [type === 'fullBody' ? 'fullBodyPhoto' : 'outfitPhotos']: type === 'fullBody'
        ? ''
        : photos.outfitPhotos.filter(url => url !== photoUrl),
      analyses: {
        ...photos.analyses,
        [type === 'fullBody' ? 'fullBody' : 'outfits']: type === 'fullBody'
          ? undefined
          : photos.analyses.outfits.filter((_, index) => 
              photos.outfitPhotos[index] !== photoUrl
            ),
      },
      lastUpdated: new Date().toISOString(),
    };

    await userRef.set({ photos: updatedPhotos }, { merge: true });

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error('Error deleting photo:', error);
    return new NextResponse(
      JSON.stringify({
        error: 'Failed to delete photo',
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