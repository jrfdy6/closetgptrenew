import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  console.log('🔍 DEBUG: Frontend trending-styles route called!');
  console.log('🔍 DEBUG: Request headers:', Object.fromEntries(request.headers.entries()));
  
  try {
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-backend-production.up.railway.app';
    
    console.log('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Check for authorization header first
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      console.log('❌ Frontend API: No authorization header found');
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    console.log('🔍 DEBUG: Authorization header found, forwarding to backend...');
    
    // Forward request directly to backend
    const response = await fetch(`${backendUrl}/api/wardrobe/trending-styles`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    console.log('🔍 DEBUG: Backend response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.log('❌ Frontend API: Backend error:', errorText);
      return NextResponse.json(
        { error: 'Backend error', status: response.status, details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('🔍 DEBUG: Backend data received:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ Frontend API: Error in trending-styles route:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch trending styles' },
      { status: 500 }
    );
  }
} 