import { ref, uploadBytes, getDownloadURL, deleteObject } from "firebase/storage";
import { v4 as uuidv4 } from "uuid";
import { storage } from "./config";
import { getAuthToken } from "@/lib/auth";
import { auth } from "./config";
import { useFirebase } from "@/lib/firebase-context";

export interface UploadedImage {
  url: string;
  path: string;
  item_id?: string;
}

export interface BackendUploadResponse {
  message: string;
  item_id: string;
  image_url: string;
  item: any;
}

/**
 * Upload image through backend API to avoid CORS issues
 */
export async function uploadImage(file: File, userId: string, category: string = "clothing", name?: string): Promise<UploadedImage> {
  try {
    // Debug authentication state
    console.log('🔍 Debug uploadImage authentication:');
    console.log('  - auth object:', !!auth);
    console.log('  - auth.currentUser:', auth?.currentUser);
    console.log('  - userId parameter:', userId);
    
    // Get Firebase ID token for authentication
    let authToken = '';
    if (auth && auth.currentUser) {
      try {
        console.log('  - Getting ID token from current user...');
        authToken = await auth.currentUser.getIdToken();
        console.log('  - ID token obtained:', !!authToken);
      } catch (error) {
        console.error("Error getting Firebase ID token:", error);
        authToken = '';
      }
    } else {
      console.log('  - No current user found');
      authToken = '';
    }

    // Create FormData for the upload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    formData.append('name', name || file.name);

    // Upload through backend API
    console.log('  - Using endpoint: /api/image/upload');
    console.log('  - Auth token present:', !!authToken);
    console.log('  - Auth token preview:', authToken ? authToken.substring(0, 20) + '...' : 'none');
    
    // Use Next.js API route to avoid CORS and keep credentials secure
    let response: Response;
    try {
      response = await fetch(`/api/image/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          // Don't set Content-Type, let browser set it with boundary
          'Authorization': `Bearer ${authToken}`,
        },
      });
    } catch (proxyErr) {
      // If the proxy route is not available on this preview, fallback to backend directly
      console.warn('⚠️ Proxy upload failed, falling back to backend:', proxyErr);
      response = new Response(null, { status: 404 });
    }

    if (!response.ok && (response.status === 404 || response.status === 405)) {
      const baseUrl =
        process.env.NEXT_PUBLIC_API_URL ||
        process.env.NEXT_PUBLIC_BACKEND_URL ||
        'https://closetgptrenew-backend-production.up.railway.app';
      console.log('↪️ Falling back to backend upload:', `${baseUrl}/api/image/upload`);
      response = await fetch(`${baseUrl}/api/image/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      // If backend CORS blocks or still missing, final fallback to server-side direct upload
      if (!response.ok) {
        console.log('↪️ Final fallback to server-side direct upload');
        response = await fetch('/api/image/upload-direct', {
          method: 'POST',
          body: formData,
          headers: {
            'Authorization': `Bearer ${authToken}`,
          },
        });
      }
    }

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Upload failed: ${response.status} - ${errorData}`);
    }

    const data: BackendUploadResponse = await response.json();
    
    return {
      url: data.image_url,
      path: `users/${userId}/wardrobe/${data.item_id}`,
      item_id: data.item_id
    };
  } catch (error) {
    console.error("Error uploading image through backend:", error);
    throw error;
  }
}

/**
 * Fallback: Direct Firebase Storage upload (for when backend is not available)
 */
export async function uploadImageDirect(file: File, userId: string): Promise<UploadedImage> {
  const fileExtension = file.name.split('.').pop();
  const fileName = `${uuidv4()}.${fileExtension}`;
  const path = `users/${userId}/wardrobe/${fileName}`;
  const storageRef = ref(storage, path);

  try {
    await uploadBytes(storageRef, file);
    const url = await getDownloadURL(storageRef);
    return { url, path };
  } catch (error) {
    console.error("Error uploading image directly:", error);
    throw error;
  }
}

export async function uploadMultipleImages(files: File[], userId: string, category: string = "clothing"): Promise<UploadedImage[]> {
  const uploadPromises = files.map(file => uploadImage(file, userId, category));
  return Promise.all(uploadPromises);
}

export async function deleteImage(path: string): Promise<void> {
  const storageRef = ref(storage, path);
  try {
    await deleteObject(storageRef);
  } catch (error) {
    console.error("Error deleting image:", error);
    throw error;
  }
}

export async function deleteMultipleImages(paths: string[]): Promise<void> {
  const deletePromises = paths.map(path => deleteImage(path));
  await Promise.all(deletePromises);
} 