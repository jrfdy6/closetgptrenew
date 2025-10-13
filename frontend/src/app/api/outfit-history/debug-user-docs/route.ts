import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
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

    // Get user_id from query params
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('user_id');
    
    if (!userId) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Missing user_id parameter',
          details: 'user_id query parameter is required'
        },
        { status: 400 }
      );
    }

    // Get the backend URL with fallbacks
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.NEXT_PUBLIC_BACKEND_URL || 
                      'https://closetgptrenew-production.up.railway.app';

    // Forward request to backend with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

    try {
      const backendResponse = await fetch(`${backendUrl}/api/outfit-history/debug-user-docs?user_id=${encodeURIComponent(userId)}`, {
        method: 'GET',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await backendResponse.json();

      if (!backendResponse.ok) {
        return NextResponse.json(
          { 
            success: false,
            error: data.detail || 'Backend request failed',
            details: data.detail || 'Unknown backend error'
          },
          { status: backendResponse.status }
        );
      }

      return NextResponse.json(data);

    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        return NextResponse.json(
          { 
            success: false,
            error: 'Backend request timeout',
            details: 'Backend took too long to respond to debug request'
          },
          { status: 504 }
        );
      }
      console.error('Error forwarding debug request:', fetchError);
      return NextResponse.json(
        { 
          success: false,
          error: 'Failed to forward debug request',
          details: fetchError.message
        },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error('Error in debug-user-docs API route:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to debug user docs',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
