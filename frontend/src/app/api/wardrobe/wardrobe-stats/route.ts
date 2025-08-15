import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  console.log('🔍 DEBUG: Frontend wardrobe-stats route called!');
  console.log('🔍 DEBUG: Request headers:', Object.fromEntries(request.headers.entries()));
  
  try {
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
      console.log('❌ Frontend API: No authorization header found');
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }

    console.log('🔍 DEBUG: Authorization header found, forwarding to backend...');

    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-backend-production.up.railway.app';
    
    console.log('🔍 DEBUG: Backend URL:', baseUrl);
    console.log('🔍 DEBUG: Full endpoint URL:', `${baseUrl}/api/analytics/wardrobe-stats`);
    
    const response = await fetch(`${baseUrl}/api/analytics/wardrobe-stats`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    console.log('🔍 DEBUG: Backend response status:', response.status);
    console.log('🔍 DEBUG: Backend response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text();
      console.log('❌ Frontend API: Backend error:', errorText);
      console.log('❌ Frontend API: Response status:', response.status);
      console.log('❌ Frontend API: Response status text:', response.statusText);
      
      return NextResponse.json(
        { 
          error: 'Backend error', 
          status: response.status, 
          statusText: response.statusText,
          details: errorText 
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('🔍 DEBUG: Backend data received:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ Frontend API: Error in wardrobe-stats route:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch wardrobe statistics',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 