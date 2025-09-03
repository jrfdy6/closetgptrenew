import { getApps, initializeApp, cert } from 'firebase-admin/app';
import { getStorage } from 'firebase-admin/storage';
import { v4 as uuidv4 } from 'uuid';

// Initialize Firebase Admin if not already initialized
function initAdmin() {
  if (!getApps().length) {
    const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n');
    if (!privateKey) {
      throw new Error('FIREBASE_PRIVATE_KEY not set');
    }

    initializeApp({
      credential: cert({
        projectId: process.env.FIREBASE_PROJECT_ID,
        clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
        privateKey,
      }),
    });
  }
}

export const uploadImage = async (file: File, userId: string): Promise<{ url: string; path: string }> => {
  try {
    initAdmin();

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

    return {
      url: imageUrl,
      path: objectPath
    };
  } catch (error) {
    console.error('Error uploading image to Firebase Storage:', error);
    throw new Error(`Failed to upload image: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

export const deleteImage = async (url: string): Promise<void> => {
  try {
    initAdmin();
    
    // Extract the file path from the URL
    const urlParts = url.split('/o/');
    if (urlParts.length < 2) {
      throw new Error('Invalid Firebase Storage URL');
    }
    
    const pathWithParams = urlParts[1].split('?')[0];
    const filePath = decodeURIComponent(pathWithParams);
    
    const bucket = getStorage().bucket();
    const file = bucket.file(filePath);
    
    await file.delete();
  } catch (error) {
    console.error('Error deleting image from Firebase Storage:', error);
    throw new Error(`Failed to delete image: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}
