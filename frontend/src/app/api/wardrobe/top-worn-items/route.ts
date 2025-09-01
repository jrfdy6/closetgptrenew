import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
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

    const { searchParams } = new URL(req.url);
    const limit = searchParams.get('limit') || '10';

    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgpt-backend-production.up.railway.app';
    
    console.log(`🔍 Fetching top worn items from: ${baseUrl}/api/wardrobe/top-worn-items?limit=${limit}`);
    
    const response = await fetch(`${baseUrl}/api/wardrobe/top-worn-items?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (!response.ok) {
      console.error(`❌ Backend error fetching top worn items: ${response.status} ${response.statusText}`);
      console.error('❌ Backend error details:', data);
      return NextResponse.json(
        { 
          success: false,
          error: data.detail || 'Failed to fetch top worn items',
          details: data.detail || 'Backend request failed'
        },
        { status: response.status }
      );
    }

    console.log("✅ Successfully fetched top worn items from backend");
    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Error in top worn items API route:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch top worn items',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
