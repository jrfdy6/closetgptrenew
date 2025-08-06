import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Outfits API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    // Check if the API URL is set
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    console.log('🔍 DEBUG: NEXT_PUBLIC_API_URL:', apiUrl);
    
    if (!apiUrl) {
      console.error('🔍 DEBUG: NEXT_PUBLIC_API_URL environment variable is not set');
      return NextResponse.json(
        { 
          error: 'Configuration error', 
          details: 'Backend URL not configured. Please check environment variables.'
        },
        { status: 500 }
      );
    }
    
    // Ensure the URL has a protocol
    const fullApiUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;
    console.log('🔍 DEBUG: Full API URL:', fullApiUrl);
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
      console.log('🔍 DEBUG: Forwarding authorization header');
    } else {
      console.log('🔍 DEBUG: No authorization header present');
    }
    
    // Call the backend outfits endpoint with increased timeout
    console.log('🔍 DEBUG: Calling backend outfits endpoint...');
    const outfitsResponse = await fetch(`${fullApiUrl}/api/outfits/`, {
      method: 'GET',
      headers,
      signal: AbortSignal.timeout(30000), // 30 second timeout (increased from 10)
    });
    
    console.log('🔍 DEBUG: Backend outfits response status:', outfitsResponse.status);
    
    if (!outfitsResponse.ok) {
      console.error('🔍 DEBUG: Backend outfits endpoint failed:', outfitsResponse.status, outfitsResponse.statusText);
      
      // If it's a 403, return a more specific error
      if (outfitsResponse.status === 403) {
        return NextResponse.json(
          { 
            error: 'Authentication required', 
            status: 403,
            message: 'Please log in to view your outfits'
          },
          { status: 403 }
        );
      }
      
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
    
    // Provide more specific error messages
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        console.error('🔍 DEBUG: Request timed out after 30 seconds');
        return NextResponse.json(
          { 
            error: 'Request timeout', 
            details: 'Backend did not respond within 30 seconds. The server may be experiencing high load.'
          },
          { status: 504 }
        );
      }
      
      if (error.message.includes('fetch')) {
        return NextResponse.json(
          { error: 'Backend not reachable', details: 'Unable to connect to backend service' },
          { status: 503 }
        );
      }
    }
    
    return NextResponse.json(
      { error: 'Failed to process request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 