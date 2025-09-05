import { NextResponse } from 'next/server';
import { getApps, initializeApp, cert } from 'firebase-admin/app';
import { getStorage } from 'firebase-admin/storage';
import { v4 as uuidv4 } from 'uuid';

// Initialize Firebase Admin SDK
function initAdmin() {
  if (!getApps().length) {
    // Use the service account key from the file system
    const serviceAccount = {
      type: "service_account",
      project_id: "closetgptrenew",
      private_key_id: "9709cc91e142842bd54fb0d2905566f67f7f6ba8",
      private_key: "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC4LpUEnmYkjEVd\nEEcL87HfGsFRk8NQKic1nk2KYT4PBhh/GcmXnTo1ULIQrwTRXgbxnTiQkJwGv59u\naOBl/aesFfqzwU79ohewhqXgSSz8V8vs54RuNC5mKGHANOD/B2KXt9tmb+noPtio\nAxI3rnf/bI56mVHVCxxoIX5QES+3VmZY4nHCcCj0QjNpsor5/umRVnYOeqUOC56k\nW7qk3UjhISZe16jx7TLbvc+Qb91uL08lFyuCkSlBOON4eLr8FNGoi5DcE7igJkj0\ni7m4yHKPC6W0WA6xI5mdAlY21BGAAL8AjUtLdQtYJlUUMMaaWJYRZntqpfxVlV6d\nAcbj4tddAgMBAAECggEANBWQNIcqsWktcFzbCok2orXpN02G7ROOlP4YRWqsZwk9\nQiwjswlWXZ9dS5SC00Y4xnjEdzU9ujbUOh/UXWM22FY62DxxPw5ojpX1MJDg9NdL\nJspty9Bb0q3Wvsj1W4lWGzt2AujhB7lGAXUk4LQo4QVs4UScPJfwx425L6E8kiaU\ngbZD3o+NFR1n3THYNS1Wjhs+9/HswYQ4ZKoLzbz59TCMtAtw12Daz6VYj3lrGmPu\na6FibJeA8voxX3y2Og6+QzhCCWadjxjVduq8QHpM/fmFVG3A5Fbje4Q9U6eGU3Fp\nEyAVarVHPrFMqQacUm0cIwBWt2FAC4b0fDHFMFc/jQKBgQDreVg4ghX1KbqAU37q\neduXKUhlGYGr16zI/uw/gtES0j5SL8hz9wWg2YX76R3s0dMnbVFHJSIvr5EH0d5Y\nG2znhLug7C8FxGyApy/lsJ1tOytUCNJxTqljVmf+dT5UYUZEK7qKj9ibilq/nx05\nPlMDIaZfDFNumZW7H/ph6IiNFwKBgQDIPKTgBUDxYcOYCD2UqY5kRkxZUlZh6Qtj\n6PLE22VvT8J3S7EyJqCmmOPoo2lGtgnKJz+LTDyv9zHOOpGh86nNdtYRF+3GRRLU\nD4cvf/1qvYa8eW8i41DtRHc3zsdQiPEXDRwe/zscDgv2Vq8ASOX5tIbU1XKtYive\nSgNiIoHPqwKBgDvtcvVWrg3p48wa89bq0mcDG6iXODgquI+iyS9UtK7skO3LuWFC\nAc2w7ndxGauWrv1+xcuseKnYLbnmwIZ93FaDoljPIxx9o/uOEROMwlP1Vg6Z/CzY\nDyX37JmG7yj8ZKye0GfJOiBDstrHvOE/qlLGspfIBEfGkKPB/LAERRRbAoGBAINu\nUuZ8bFFEU4dSOWGAHeexwOGMSwj/V6uftuICBEWY+9MkCs4ZTq+rgUUtJaf1St22\n/12mj9sMjVOJXBgKgPVNQFt98mOG6UHqY1iJUUSj3HGP36PtwyvKGdq2zlsNV/pC\nb6fk7d6PVci+wyWTs+hAV5QR+rDV1GeW+zuJ3Nz7AoGACM2BkbrxzjOJrqYoPvXl\nq8eNGxZHMNAuGuiYqlfFeKaNnLnTZuQQdPVEispU/2NdB214VQXykNPQ5iWX+EwG\nQe2utYI88H1JVqDE6hgLSzf5lKd59mv24qhfQvFS3ktNeahneIaTGgrz7uaNdZlH\nHYnyWzl+BDDH0rCIeruTIks=\n-----END PRIVATE KEY-----\n",
      client_email: "firebase-adminsdk-fbsvc@closetgptrenew.iam.gserviceaccount.com",
      client_id: "110004373816846158464",
      auth_uri: "https://accounts.google.com/o/oauth2/auth",
      token_uri: "https://oauth2.googleapis.com/token",
      auth_provider_x509_cert_url: "https://www.googleapis.com/oauth2/v1/certs",
      client_x509_cert_url: "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40closetgptrenew.iam.gserviceaccount.com"
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
    
    // Initialize Firebase Admin
    const app = initAdmin();
    console.log('✅ Firebase Admin initialized');
    
    const bucket = getStorage().bucket();
    console.log('✅ Firebase Storage bucket initialized:', bucket.name);

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
