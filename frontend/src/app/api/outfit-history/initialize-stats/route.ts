import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: NextRequest) {
  try {
    // Get the backend URL with fallbacks
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.NEXT_PUBLIC_BACKEND_URL || 
                      'https://closetgptrenew-backend-production.up.railway.app';
    
    // Get authentication token from cookies
    const cookieStore = cookies();
    const authToken = cookieStore.get('auth_token')?.value;
    
    if (!authToken) {
      return NextResponse.json(
        { success: false, error: 'Not authenticated' },
        { status: 401 }
      );
    }

    // Forward request to backend with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout for initialization

    try {
      const backendResponse = await fetch(`${backendUrl}/api/outfit-history/initialize-stats`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!backendResponse.ok) {
        const errorText = await backendResponse.text();
        console.error(`Backend initialization error: ${backendResponse.status} ${errorText}`);
        return NextResponse.json(
          { 
            success: false, 
            error: 'Backend initialization failed',
            details: errorText 
          },
          { status: backendResponse.status }
        );
      }

      const data = await backendResponse.json();
      return NextResponse.json(data);

    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      
      if (fetchError.name === 'AbortError') {
        return NextResponse.json(
          { 
            success: false, 
            error: 'Initialization timeout',
            details: 'Backend took too long to initialize stats' 
          },
          { status: 504 }
        );
      }

      throw fetchError;
    }

  } catch (error: any) {
    console.error('Initialize stats API error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to initialize user stats',
        details: error.message 
      },
      { status: 500 }
    );
  }
}
