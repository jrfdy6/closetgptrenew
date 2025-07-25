import { NextResponse } from 'next/server';
import { auth } from '@/lib/firebase/admin';
import { db } from '@/lib/firebase/admin';

export async function POST(request: Request) {
  try {
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Unauthorized - No token provided' },
        { status: 401 }
      );
    }

    // Verify the token
    const token = authHeader.split('Bearer ')[1];
    const decodedToken = await auth.verifyIdToken(token);
    const userId = decodedToken.uid;

    // Get the request body
    const body = await request.json();
    
    // Verify that the user ID in the request matches the authenticated user
    if (body.user_id !== userId) {
      return NextResponse.json(
        { error: 'Unauthorized - User ID mismatch' },
        { status: 401 }
      );
    }

    // Prepare the profile data with optional fields
    const profileData = {
      name: body.name || '',
      gender: body.gender || '',
      avatarUrl: body.avatarUrl || '',
      bodyType: body.bodyType || '',
      height: body.height || '',
      weight: body.weight || '',
      skinTone: body.skinTone || null,
      topSize: body.topSize || '',
      bottomSize: body.bottomSize || '',
      shoeSize: body.shoeSize || '',
      chest: body.chest || '',
      waist: body.waist || '',
      inseam: body.inseam || '',
      stylePreferences: body.stylePreferences || [],
      occasions: body.occasions || [],
      preferredColors: body.preferredColors || [],
      formality: body.formality || 'casual',
      budget: body.budget || 'mid-range',
      preferredBrands: body.preferredBrands || [],
      fitPreference: body.fitPreference || '',
      sizePreference: body.sizePreference || '',
      seasonalPreferences: body.seasonality || ['spring', 'summer', 'fall', 'winter'],
      updatedAt: new Date().toISOString(),
    };

    // Save to Firestore in the profiles collection
    await db.collection('profiles').doc(userId).set(profileData, { merge: true });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error saving profile:', error);
    return NextResponse.json(
      { error: 'Failed to save profile', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 