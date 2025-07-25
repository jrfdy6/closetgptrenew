import { NextResponse } from 'next/server';
import { NextRequest } from 'next/server';
import { StyleProfile } from '@/types/style-quiz';
import { getAuth } from '@clerk/nextjs/server';
import { adminDb } from '@/lib/firebase-admin';

export async function POST(req: NextRequest) {
  try {
    const { userId } = getAuth(req);
    if (!userId) {
      console.error('No user ID found in request');
      return new NextResponse('Unauthorized', { status: 401 });
    }

    const styleProfile: StyleProfile = await req.json();
    console.log('Received style profile:', { userId, styleProfile });

    if (!adminDb) {
      throw new Error('Firebase Admin DB not initialized');
    }

    // Save the style profile to Firestore using admin SDK
    await adminDb.collection('users').doc(userId).set({
      styleProfile: {
        preferredColors: styleProfile.preferredColors,
        preferredPatterns: styleProfile.preferredPatterns,
        preferredStyles: styleProfile.preferredStyles,
        formality: styleProfile.formality,
        seasonality: styleProfile.seasonality,
        confidence: styleProfile.confidence,
        updatedAt: new Date().toISOString()
      }
    }, { merge: true });

    console.log('Successfully saved style profile for user:', userId);
    return new NextResponse('Style profile saved successfully', { status: 200 });
  } catch (error) {
    console.error('Error saving style profile:', error);
    return new NextResponse(
      JSON.stringify({ 
        error: 'Failed to save style profile',
        details: error instanceof Error ? error.message : 'Unknown error'
      }), 
      { 
        status: 500,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
} 