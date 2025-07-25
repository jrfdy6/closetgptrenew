/**
 * Authentication utilities for API requests
 */

export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  // Get the auth token from localStorage or cookies
  let token: string | null = null;
  
  if (typeof window !== 'undefined') {
    // Client-side: try to get from localStorage
    token = localStorage.getItem('authToken') || 
            localStorage.getItem('firebaseToken') ||
            localStorage.getItem('accessToken');
  }
  
  // Create headers
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  // Make the request
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  return response;
}

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  
  return localStorage.getItem('authToken') || 
         localStorage.getItem('firebaseToken') ||
         localStorage.getItem('accessToken');
}

export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  
  localStorage.setItem('authToken', token);
}

export function clearAuthToken(): void {
  if (typeof window === 'undefined') {
    return;
  }
  
  localStorage.removeItem('authToken');
  localStorage.removeItem('firebaseToken');
  localStorage.removeItem('accessToken');
} 