import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Outfits API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://acceptable-wisdom-production-ac06.up.railway.app';
    console.log('🔍 DEBUG: NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
    console.log('🔍 DEBUG: Using apiUrl:', apiUrl);
    
    // Ensure the URL has a protocol
    const fullApiUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;
    console.log('🔍 DEBUG: Full API URL:', fullApiUrl);
    
    // First, let's test if the backend is reachable
    try {
      console.log('🔍 DEBUG: Testing backend connectivity...');
      const healthResponse = await fetch(`${fullApiUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });
      console.log('🔍 DEBUG: Backend health check status:', healthResponse.status);
    } catch (healthError) {
      console.error('🔍 DEBUG: Backend health check failed:', healthError);
      return NextResponse.json(
        { error: 'Backend not reachable', details: 'Health check failed' },
        { status: 503 }
      );
    }
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
    
    console.log('🔍 DEBUG: Calling backend outfits endpoint:', `${fullApiUrl}/api/outfits/`);
    console.log('🔍 DEBUG: Headers:', headers);
    
    // Create an AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    try {
      const response = await fetch(`${fullApiUrl}/api/outfits/`, {
        method: 'GET',
        headers,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      console.log('🔍 DEBUG: Backend response status:', response.status);
      console.log('🔍 DEBUG: Backend response headers:', Object.fromEntries(response.headers.entries()));

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
        console.error('🔍 DEBUG: Request timed out after 10 seconds');
        return NextResponse.json(
          { error: 'Request timed out', details: 'Backend did not respond within 10 seconds' },
          { status: 504 }
        );
      }
      throw error;
    }
  } catch (error) {
    console.error('🔍 DEBUG: Error fetching outfits:', error);
    return NextResponse.json(
      { error: 'Failed to fetch outfits', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 