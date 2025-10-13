import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
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

    // Forward request to backend
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-production.up.railway.app';
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

    try {
      const response = await fetch(`${baseUrl}/api/outfits-fast/filter-options`, {
        method: 'GET',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Backend filter options error: ${response.status} ${errorText}`);
        return NextResponse.json(
          { 
            success: false,
            error: 'Backend request failed',
            details: errorText
          },
          { status: response.status }
        );
      }

      const data = await response.json();
      return NextResponse.json(data);

    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      
      if (fetchError.name === 'AbortError') {
        return NextResponse.json(
          { 
            success: false,
            error: 'Backend request timeout',
            details: 'Backend took too long to respond'
          },
          { status: 504 }
        );
      }

      throw fetchError;
    }

  } catch (error) {
    console.error('Error fetching filter options:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch filter options',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
