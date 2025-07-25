import { NextResponse } from 'next/server';
import { NextRequest } from 'next/server';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import { initializeApp, getApps, cert } from 'firebase-admin/app';

// Lazy initialization function
function initializeFirebaseAdmin() {
  const apps = getApps();
  if (!apps.length) {
    try {
      // Get the service account credentials from environment variables
      const projectId = process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID;
      const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;
      const privateKey = process.env.FIREBASE_PRIVATE_KEY;

      if (!projectId || !clientEmail || !privateKey) {
        throw new Error('Missing Firebase Admin credentials');
      }

      // Initialize the app with the service account credentials
      initializeApp({
        credential: cert({
          projectId,
          clientEmail,
          privateKey: privateKey.replace(/\\n/g, '\n'),
        }),
      });
      console.log('Firebase Admin initialized successfully');
    } catch (error) {
      console.error('Error initializing Firebase Admin:', error);
      throw error;
    }
  }
}

export async function POST(req: NextRequest) {
  // Initialize Firebase Admin only when needed
  initializeFirebaseAdmin();
  
  try {
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'No authorization token provided'
        },
        { status: 401 }
      );
    }

    // Get the ID token from the header
    const idToken = authHeader.split('Bearer ')[1];
    
    // Verify the token using Firebase Admin
    let decodedToken;
    try {
      const adminAuth = getAuth();
      if (!adminAuth) {
        throw new Error('Firebase Admin Auth not initialized');
      }
      decodedToken = await adminAuth.verifyIdToken(idToken);
    } catch (error) {
      console.error('Error verifying token:', error);
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'Invalid token'
        },
        { status: 401 }
      );
    }

    const submission = await req.json();
    const userId = submission.user_id;

    // Verify that the user ID in the submission matches the authenticated user
    if (userId !== decodedToken.uid) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'User ID mismatch'
        },
        { status: 401 }
      );
    }

    // Get Firestore instance
    const db = getFirestore();
    if (!db) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Database Error',
          details: 'Firestore is not initialized'
        },
        { status: 500 }
      );
    }

    // Save the style profile to Firestore
    const profileRef = db.collection('style_discovery_profiles').doc(userId);
    await profileRef.set({
      user_id: userId,
      answers: submission.answers,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }, { merge: true });

    return NextResponse.json({ 
      success: true,
      message: 'Style profile saved successfully'
    });
  } catch (error) {
    console.error('Error saving style profile:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to save style profile',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 