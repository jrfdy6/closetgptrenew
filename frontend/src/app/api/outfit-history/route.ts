import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  console.log('🔍 DEBUG: Frontend outfit-history route called!');
  console.log('🔍 DEBUG: Request headers:', Object.fromEntries(req.headers.entries()));
  
  try {
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      console.log('❌ Frontend API: No valid authorization header found');
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'No authorization token provided'
        },
        { status: 401 }
      );
    }

    console.log('🔍 DEBUG: Authorization header found, forwarding to backend...');

    // Get query parameters
    const { searchParams } = new URL(req.url);
    const startDate = searchParams.get('start_date');
    const endDate = searchParams.get('end_date');
    const limit = searchParams.get('limit');

    // Build backend URL with query parameters
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-backend-production.up.railway.app';
    const backendUrl = new URL(`${baseUrl}/api/outfit-history/`);
    if (startDate) backendUrl.searchParams.set('start_date', startDate);
    if (endDate) backendUrl.searchParams.set('end_date', endDate);
    if (limit) backendUrl.searchParams.set('limit', limit);

    console.log('🔍 DEBUG: Backend URL:', backendUrl.toString());

    // Forward request to backend
    const response = await fetch(backendUrl.toString(), {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    console.log('🔍 DEBUG: Backend response status:', response.status);

    const data = await response.json();

    if (!response.ok) {
      console.log('❌ Frontend API: Backend error:', data);
      return NextResponse.json(
        { 
          success: false,
          error: data.detail || 'Failed to fetch outfit history',
          details: data.detail || 'Backend request failed'
        },
        { status: response.status }
      );
    }

    console.log('🔍 DEBUG: Backend data received:', data);
    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Frontend API: Error in outfit-history route:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch outfit history',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 