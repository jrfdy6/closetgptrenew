import { NextResponse } from 'next/server';
import { getApps, initializeApp, cert } from 'firebase-admin/app';
import { getStorage } from 'firebase-admin/storage';
import { v4 as uuidv4 } from 'uuid';

// Initialize Firebase Admin SDK
function initAdmin() {
  if (!getApps().length) {
    // Use environment variables for Firebase Admin SDK
    const serviceAccount = {
      type: "service_account",
      project_id: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      private_key_id: process.env.FIREBASE_PRIVATE_KEY_ID,
      private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      client_email: process.env.FIREBASE_CLIENT_EMAIL,
      client_id: process.env.FIREBASE_CLIENT_ID,
      auth_uri: "https://accounts.google.com/o/oauth2/auth",
      token_uri: "https://oauth2.googleapis.com/token",
      auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs",
      client_x509_cert_url: `https://www.googleapis.com/robot/v1/metadata/x509/${encodeURIComponent(process.env.FIREBASE_CLIENT_EMAIL || '')}`
    };

    return initializeApp({
      credential: cert(serviceAccount),
      storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || 'closetgptrenew.appspot.com',
    });
  }
  return getApps()[0];
}

export async function POST(request: Request) {
  try {
    console.log('🚀 Starting Firebase Storage upload...');
    
    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const userId = formData.get('userId') as string;
    const category = (formData.get('category') as string) || 'clothing';
    const name = (formData.get('name') as string) || 'upload';

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    if (!userId) {
      return NextResponse.json({ error: 'No user ID provided' }, { status: 400 });
    }

    // Check if required environment variables are present
    if (!process.env.FIREBASE_PRIVATE_KEY || !process.env.FIREBASE_CLIENT_EMAIL) {
      console.warn('⚠️ Firebase Admin SDK environment variables not set, falling back to placeholder URLs');
      console.log('Available env vars:', {
        hasProjectId: !!process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
        hasStorageBucket: !!process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
        hasPrivateKey: !!process.env.FIREBASE_PRIVATE_KEY,
        hasClientEmail: !!process.env.FIREBASE_CLIENT_EMAIL
      });
      
      // Fall back to placeholder URLs if Firebase Admin SDK is not configured
      const placeholderUrl = `https://picsum.photos/400/400?random=${Date.now()}`;
      
      return NextResponse.json({
        success: true,
        image_url: placeholderUrl,
        path: `wardrobe/${userId}/${uuidv4()}`,
        item_id: uuidv4(),
        name,
        category,
      });
    }
    
    // Initialize Firebase Admin
    const app = initAdmin();
    console.log('✅ Firebase Admin initialized');
    
    const bucket = getStorage().bucket();
    console.log('✅ Firebase Storage bucket initialized:', bucket.name);

    console.log('📁 File details:', {
      name: file.name,
      size: file.size,
      type: file.type
    });

    // Create a reference to the file
    const ext = file.name?.split('.').pop() || 'jpg';
    const fileName = `${uuidv4()}.${ext}`;
    const fileRef = bucket.file(`wardrobe/${userId}/${fileName}`);
    
    console.log('📂 File reference created:', fileRef.name);

    // Convert file to buffer
    const buffer = Buffer.from(await file.arrayBuffer());
    console.log('📦 Buffer created, size:', buffer.length);

    // Upload the file
    console.log('⬆️ Starting file upload...');
    await fileRef.save(buffer, {
      metadata: {
        contentType: file.type || 'image/jpeg',
        metadata: {
          uploadedBy: userId,
          category: category,
          originalName: file.name || 'upload',
          firebaseStorageDownloadTokens: uuidv4()
        }
      },
      resumable: false,
    });
    
    console.log('✅ File uploaded successfully');

    // Get the download URL
    const downloadURL = `https://firebasestorage.googleapis.com/v0/b/${bucket.name}/o/${encodeURIComponent(fileRef.name)}?alt=media&token=${uuidv4()}`;
    
    console.log('🔗 Download URL generated:', downloadURL);

    return NextResponse.json({
      success: true,
      image_url: downloadURL,
      path: `wardrobe/${userId}/${fileName}`,
      item_id: uuidv4(),
      name,
      category,
    });

  } catch (error) {
    console.error('❌ Image upload error:', error);
    return NextResponse.json(
      { error: 'Upload failed', details: String(error) },
      { status: 500 }
    );
  }
}
