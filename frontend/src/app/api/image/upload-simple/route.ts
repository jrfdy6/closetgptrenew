import { NextResponse } from 'next/server';
import { initializeApp } from 'firebase/app';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { v4 as uuidv4 } from 'uuid';

// Firebase configuration
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || '',
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || '',
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || '',
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || ''
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const storage = getStorage(app);

export async function POST(request: Request) {
  try {
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
    const storageRef = ref(storage, `wardrobe/${userId}/${fileName}`);

    // Convert file to buffer
    const buffer = Buffer.from(await file.arrayBuffer());

    // Upload the file
    const snapshot = await uploadBytes(storageRef, buffer, {
      contentType: file.type || 'image/jpeg',
    });

    // Get the download URL
    const downloadURL = await getDownloadURL(snapshot.ref);

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
