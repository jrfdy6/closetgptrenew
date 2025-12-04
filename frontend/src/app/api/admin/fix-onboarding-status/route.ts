import { NextRequest, NextResponse } from 'next/server';
import { getAuth } from 'firebase/auth';

export async function POST(req: NextRequest) {
  try {
    // Get auth header
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Decode token to get user ID
    const token = authHeader.replace('Bearer ', '');
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
      return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
    }

    const base64Payload = tokenParts[1].replace(/-/g, '+').replace(/_/g, '/');
    const paddedPayload = base64Payload + '='.repeat((4 - base64Payload.length % 4) % 4);
    const payload = JSON.parse(atob(paddedPayload));
    const userId = payload.user_id || payload.sub;

    if (!userId) {
      return NextResponse.json({ error: 'No user ID in token' }, { status: 401 });
    }

    // Import Firebase
    const { db } = await import('@/lib/firebase/config');
    const { doc, getDoc, updateDoc } = await import('firebase/firestore');

    // Get user document
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);

    if (!userDoc.exists()) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const userData = userDoc.data();
    const wasOnboardingComplete = userData.onboarding_completed || userData.onboardingCompleted;

    // Set onboarding_completed to true
    await updateDoc(userRef, {
      onboarding_completed: true,
      onboardingCompleted: true,
      updatedAt: Date.now()
    });

    return NextResponse.json({
      success: true,
      message: 'Onboarding status updated',
      userId,
      wasComplete: wasOnboardingComplete,
      nowComplete: true
    });

  } catch (error) {
    console.error('Error fixing onboarding status:', error);
    return NextResponse.json(
      { 
        error: 'Failed to update onboarding status',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

