import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    // Use the correct backend URL
    const apiUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'http://localhost:3001';
    console.log('🔍 DEBUG: Using apiUrl:', apiUrl);
    
    // Ensure the URL has a protocol
    const fullApiUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;
    console.log('🔍 DEBUG: Full API URL:', fullApiUrl);
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    } else {
      console.warn('🔍 DEBUG: No authorization header provided');
    }
    
    console.log('🔍 DEBUG: Calling backend wardrobe endpoint:', `${fullApiUrl}/api/wardrobe`);
    console.log('🔍 DEBUG: Headers:', headers);
    
    // Create an AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // Increased to 15 seconds
    
    try {
      console.log('🔍 DEBUG: Starting fetch request to backend...');
      const response = await fetch(`${fullApiUrl}/api/wardrobe`, {
        method: 'GET',
        headers,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      console.log('🔍 DEBUG: Backend response received!');
      console.log('🔍 DEBUG: Backend response status:', response.status);

      if (!response.ok) {
        console.error('🔍 DEBUG: Backend response not OK:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('🔍 DEBUG: Backend error response:', errorText);
        
        // Handle specific error cases
        if (response.status === 401) {
          return NextResponse.json(
            { error: 'Authentication required', details: 'Please sign in to access your wardrobe' },
            { status: 401 }
          );
        }
        
        if (response.status === 403) {
          return NextResponse.json(
            { error: 'Access denied', details: 'You do not have permission to access this resource' },
            { status: 403 }
          );
        }
        
        throw new Error(`Backend responded with ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('🔍 DEBUG: Backend response data:', data);
      return NextResponse.json(data);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('🔍 DEBUG: Request timed out after 15 seconds');
        return NextResponse.json(
          { error: 'Request timed out', details: 'Backend did not respond within 15 seconds' },
          { status: 504 }
        );
      }
      throw error;
    }
  } catch (error) {
    console.error('🔍 DEBUG: Error fetching wardrobe:', error);
    return NextResponse.json(
      { error: 'Failed to fetch wardrobe', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe POST API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    // Use the correct backend URL
    const apiUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'http://localhost:3001';
    console.log('🔍 DEBUG: Using apiUrl:', apiUrl);
    
    // Ensure the URL has a protocol
    const fullApiUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;
    console.log('🔍 DEBUG: Full API URL:', fullApiUrl);
    
    // Get the request body
    const requestBody = await request.json();
    console.log('🔍 DEBUG: Request body:', requestBody);
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    } else {
      console.warn('🔍 DEBUG: No authorization header provided');
    }
    
    console.log('🔍 DEBUG: Calling backend wardrobe endpoint:', `${fullApiUrl}/api/wardrobe`);
    console.log('🔍 DEBUG: Headers:', headers);
    
    // Create an AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000); // Increased to 20 seconds for POST
    
    try {
      console.log('🔍 DEBUG: Starting fetch request to backend...');
      const response = await fetch(`${fullApiUrl}/api/wardrobe`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      console.log('🔍 DEBUG: Backend response received!');
      console.log('🔍 DEBUG: Backend response status:', response.status);

      if (!response.ok) {
        console.error('🔍 DEBUG: Backend response not OK:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('🔍 DEBUG: Backend error response:', errorText);
        
        // Handle specific error cases
        if (response.status === 401) {
          return NextResponse.json(
            { error: 'Authentication required', details: 'Please sign in to add items to your wardrobe' },
            { status: 401 }
          );
        }
        
        if (response.status === 403) {
          return NextResponse.json(
            { error: 'Access denied', details: 'You do not have permission to add items' },
            { status: 403 }
          );
        }
        
        if (response.status === 400) {
          return NextResponse.json(
            { error: 'Invalid request', details: errorText },
            { status: 400 }
          );
        }
        
        throw new Error(`Backend responded with ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('🔍 DEBUG: Backend response data:', data);
      return NextResponse.json(data);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('🔍 DEBUG: Request timed out after 20 seconds');
        return NextResponse.json(
          { error: 'Request timed out', details: 'Backend did not respond within 20 seconds' },
          { status: 504 }
        );
      }
      throw error;
    }
  } catch (error) {
    console.error('🔍 DEBUG: Error creating wardrobe item:', error);
    return NextResponse.json(
      { error: 'Failed to create wardrobe item', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 