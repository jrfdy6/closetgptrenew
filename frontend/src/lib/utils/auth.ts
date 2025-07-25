import { getAuth } from 'firebase/auth';

/**
 * Get the current Firebase ID token for authentication
 * @returns Promise<string> - The Firebase ID token
 */
export async function getFirebaseIdToken(): Promise<string | null> {
  try {
    const auth = getAuth();
    const user = auth.currentUser;
    
    if (!user) {
      console.warn('No authenticated user found');
      return null;
    }
    
    const token = await user.getIdToken();
    return token;
  } catch (error) {
    console.error('Error getting Firebase ID token:', error);
    return null;
  }
}

/**
 * Create headers with Firebase authentication token
 * @returns Promise<Headers> - Headers object with authorization
 */
export async function createAuthHeaders(): Promise<Headers> {
  const headers = new Headers({
    'Content-Type': 'application/json',
  });
  
  const token = await getFirebaseIdToken();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  return headers;
}

/**
 * Make an authenticated API request
 * @param url - The API endpoint URL
 * @param options - Fetch options
 * @returns Promise<Response> - The fetch response
 */
export async function authenticatedFetch(
  url: string, 
  options: RequestInit = {}
): Promise<Response> {
  const token = await getFirebaseIdToken();
  
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  return fetch(url, {
    ...options,
    headers,
  });
} 