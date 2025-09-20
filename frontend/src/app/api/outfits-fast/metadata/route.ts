import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers and search params
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

    // Get query parameters
    const searchParams = req.nextUrl.searchParams;
    const limit = searchParams.get('limit') || '100';
    const offset = searchParams.get('offset') || '0';
    const occasion = searchParams.get('occasion');
    const style = searchParams.get('style');
    const is_favorite = searchParams.get('is_favorite');
    const sort_by = searchParams.get('sort_by') || 'date-newest';

    // Build query string
    const queryParams = new URLSearchParams({
      limit,
      offset,
      sort_by
    });
    
    if (occasion) queryParams.append('occasion', occasion);
    if (style) queryParams.append('style', style);
    if (is_favorite !== null) queryParams.append('is_favorite', is_favorite);

    // Forward request to backend
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-backend-production.up.railway.app';
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

    try {
      const response = await fetch(`${baseUrl}/api/outfits-fast/metadata?${queryParams.toString()}`, {
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
        console.error(`Backend outfits metadata error: ${response.status} ${errorText}`);
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
    console.error('Error fetching outfit metadata:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch outfit metadata',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
