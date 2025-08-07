import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Outfit generation API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-backend-production.up.railway.app';
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
    }
    
    console.log('🔍 DEBUG: Calling backend outfit generation endpoint:', `${fullApiUrl}/api/outfits/generate`);
    console.log('🔍 DEBUG: Headers:', headers);
    
    // Create an AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout for AI generation
    
    try {
      console.log('🔍 DEBUG: Starting fetch request to backend...');
      const response = await fetch(`${fullApiUrl}/api/outfits/generate`, {
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
        throw new Error(`Backend responded with ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('🔍 DEBUG: Backend response data:', data);
      return NextResponse.json(data);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('🔍 DEBUG: Request timed out after 30 seconds');
        return NextResponse.json(
          { error: 'Request timed out', details: 'Backend did not respond within 30 seconds' },
          { status: 504 }
        );
      }
      throw error;
    }
  } catch (error) {
    console.error('🔍 DEBUG: Error generating outfit:', error);
    return NextResponse.json(
      { error: 'Failed to generate outfit', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 