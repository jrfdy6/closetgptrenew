import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Outfits API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://closetgptrenew-backend-production.up.railway.app';
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
    
    // Call the backend outfits endpoint
    console.log('🔍 DEBUG: Calling backend outfits endpoint...');
    const outfitsResponse = await fetch(`${fullApiUrl}/api/outfits/`, {
      method: 'GET',
      headers,
      signal: AbortSignal.timeout(10000), // 10 second timeout
    });
    
    console.log('🔍 DEBUG: Backend outfits response status:', outfitsResponse.status);
    
    if (!outfitsResponse.ok) {
      console.error('🔍 DEBUG: Backend outfits endpoint failed:', outfitsResponse.status, outfitsResponse.statusText);
      return NextResponse.json(
        { 
          error: 'Backend outfits endpoint failed', 
          status: outfitsResponse.status,
          message: `Backend returned ${outfitsResponse.status}: ${outfitsResponse.statusText}`
        },
        { status: outfitsResponse.status }
      );
    }
    
    const outfitsData = await outfitsResponse.json();
    console.log('🔍 DEBUG: Backend outfits data received:', outfitsData);
    
    return NextResponse.json(outfitsData);
  } catch (error) {
    console.error('🔍 DEBUG: Error in outfits route:', error);
    return NextResponse.json(
      { error: 'Failed to process request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 