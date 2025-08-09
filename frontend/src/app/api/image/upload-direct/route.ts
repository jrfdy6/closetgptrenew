import { NextResponse } from 'next/server';
import { getApps, initializeApp, cert } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getStorage } from 'firebase-admin/storage';
import { v4 as uuidv4 } from 'uuid';

function initAdmin() {
  if (!getApps().length) {
    const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n');
    if (!privateKey) throw new Error('FIREBASE_PRIVATE_KEY not set');
    initializeApp({
      credential: cert({
        projectId: process.env.FIREBASE_PROJECT_ID,
        clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
        privateKey,
      }),
      storageBucket: `${process.env.FIREBASE_PROJECT_ID}.appspot.com`,
    });
  }
}

export async function POST(request: Request) {
  try {
    initAdmin();

    const authHeader = request.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    const idToken = authHeader.split('Bearer ')[1];
    const decoded = await getAuth().verifyIdToken(idToken);
    const userId = decoded.uid;

    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const category = (formData.get('category') as string) || 'clothing';
    const name = (formData.get('name') as string) || 'upload';
    if (!file) return NextResponse.json({ error: 'No file' }, { status: 400 });

    const buffer = Buffer.from(await file.arrayBuffer());
    const ext = file.name?.split('.').pop() || 'jpg';
    const objectPath = `wardrobe/${userId}/${uuidv4()}.${ext}`;

    const bucket = getStorage().bucket();
    const blob = bucket.file(objectPath);
    const downloadToken = uuidv4();

    await blob.save(buffer, {
      metadata: {
        contentType: file.type || 'image/jpeg',
        metadata: { firebaseStorageDownloadTokens: downloadToken },
      },
      resumable: false,
    });

    const imageUrl = `https://firebasestorage.googleapis.com/v0/b/${bucket.name}/o/${encodeURIComponent(objectPath)}?alt=media&token=${downloadToken}`;

    return NextResponse.json({
      message: 'Image uploaded successfully',
      image_url: imageUrl,
      path: objectPath,
      item_id: uuidv4(),
      name,
      category,
    });
  } catch (e: any) {
    return NextResponse.json({ error: 'Upload failed', details: String(e?.message || e) }, { status: 500 });
  }
}


