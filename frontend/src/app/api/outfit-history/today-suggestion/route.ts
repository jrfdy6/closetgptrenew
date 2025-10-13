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
    const response = await fetch(`${baseUrl}/api/outfit-history/today-suggestion`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { 
          success: false,
          error: data.detail || 'Failed to fetch today\'s outfit suggestion',
          details: data.detail || 'Backend request failed'
        },
        { status: response.status }
      );
    }

    return NextResponse.json(data);

  } catch (error) {
    console.error('Error fetching today\'s outfit suggestion:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch today\'s outfit suggestion',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
