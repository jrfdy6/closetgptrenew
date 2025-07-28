import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
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
    
    console.log('🔍 Calling backend outfits endpoint:', `${fullApiUrl}/api/outfits`);
    console.log('🔍 Headers:', headers);
    
    const response = await fetch(`${fullApiUrl}/api/outfits/`, {
      method: 'GET',
      headers,
    });

    console.log('🔍 Backend response status:', response.status);
    console.log('🔍 Backend response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      console.error('Backend response not OK:', response.status, response.statusText);
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      throw new Error(`Backend responded with ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log('🔍 Backend response data:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching outfits:', error);
    return NextResponse.json(
      { error: 'Failed to fetch outfits', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 