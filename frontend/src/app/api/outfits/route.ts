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
    
    // Ensure the URL has a protocol
    const fullApiUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
    
    console.log('🔍 DEBUG: Calling backend outfits endpoint:', `${fullApiUrl}/api/outfits/`);
    console.log('🔍 DEBUG: Headers:', headers);
    
    const response = await fetch(`${fullApiUrl}/api/outfits/`, {
      method: 'GET',
      headers,
    });

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
    console.error('🔍 DEBUG: Error fetching outfits:', error);
    return NextResponse.json(
      { error: 'Failed to fetch outfits', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 