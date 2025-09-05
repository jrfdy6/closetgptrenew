import { NextResponse } from 'next/server';
import { getApps, initializeApp, cert } from 'firebase-admin/app';
import { getStorage } from 'firebase-admin/storage';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';
import path from 'path';

// Initialize Firebase Admin SDK
function initAdmin() {
  if (!getApps().length) {
    // Try to load service account key from file
    const serviceAccountPath = path.join(process.cwd(), 'serviceAccountKey.json');
    
    let serviceAccount;
    try {
      if (fs.existsSync(serviceAccountPath)) {
        serviceAccount = JSON.parse(fs.readFileSync(serviceAccountPath, 'utf8'));
      } else {
        throw new Error('Service account key file not found');
      }
    } catch (error) {
      console.error('Error loading service account key:', error);
      throw new Error('Failed to load Firebase service account key');
    }

    return initializeApp({
      credential: cert(serviceAccount),
      storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || 'closetgptrenew.appspot.com',
    });
  }
  return getApps()[0];
}

export async function POST(request: Request) {
  try {
    // Initialize Firebase Admin
    const app = initAdmin();
    const bucket = getStorage().bucket();

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

    // Create a reference to the file
    const ext = file.name?.split('.').pop() || 'jpg';
    const fileName = `${uuidv4()}.${ext}`;
    const fileRef = bucket.file(`wardrobe/${userId}/${fileName}`);

    // Convert file to buffer
    const buffer = Buffer.from(await file.arrayBuffer());

    // Upload the file
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

    // Get the download URL
    const downloadURL = `https://firebasestorage.googleapis.com/v0/b/${bucket.name}/o/${encodeURIComponent(fileRef.name)}?alt=media&token=${uuidv4()}`;

    return NextResponse.json({
      success: true,
      image_url: downloadURL,
      path: `wardrobe/${userId}/${fileName}`,
      item_id: uuidv4(),
      name,
      category,
    });

  } catch (error) {
    console.error('Image upload error:', error);
    return NextResponse.json(
      { error: 'Upload failed', details: String(error) },
      { status: 500 }
    );
  }
}
