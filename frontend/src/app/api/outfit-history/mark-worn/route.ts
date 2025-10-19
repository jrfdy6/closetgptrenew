import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'No authorization token provided'
        },
        { status: 401 }
      );
    }

    // Get request body
    const body = await req.json();
    console.log('🔍 DEBUG: Mark worn request body:', body);

    // Forward request to backend
    const baseUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-production.up.railway.app';
    
    const backendUrl = `${baseUrl}/api/outfit-history/mark-worn`;
    console.log('🔍 DEBUG: Calling backend URL:', backendUrl);
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    console.log('🔍 DEBUG: Backend response status:', response.status);
    
    const data = await response.json();
    console.log('🔍 DEBUG: Backend response data:', data);

    if (!response.ok) {
      console.error('❌ Backend returned error:', {
        status: response.status,
        detail: data.detail,
        fullError: data
      });
      return NextResponse.json(
        { 
          success: false,
          error: data.detail || 'Failed to mark outfit as worn',
          details: data.detail || 'Backend request failed',
          backendError: data
        },
        { status: response.status }
      );
    }

    return NextResponse.json(data);

  } catch (error) {
    console.error('Error marking outfit as worn:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to mark outfit as worn',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 