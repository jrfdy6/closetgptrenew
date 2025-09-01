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
    const daysThreshold = searchParams.get('days_threshold') || '30';
    const minRediscoveryPotential = searchParams.get('min_rediscovery_potential') || '20.0';

    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgpt-backend-production.up.railway.app';
    
    console.log(`🔍 Fetching forgotten gems from: ${baseUrl}/api/wardrobe/insights/forgotten-gems`);
    
    const response = await fetch(`${baseUrl}/api/wardrobe/insights/forgotten-gems?days_threshold=${daysThreshold}&min_rediscovery_potential=${minRediscoveryPotential}`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (!response.ok) {
      console.error(`❌ Backend error fetching forgotten gems: ${response.status} ${response.statusText}`);
      console.error('❌ Backend error details:', data);
      return NextResponse.json(
        { 
          success: false,
          error: data.detail || 'Failed to fetch forgotten gems',
          details: data.detail || 'Backend request failed'
        },
        { status: response.status }
      );
    }

    console.log("✅ Successfully fetched forgotten gems from backend");
    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Error in forgotten gems API route:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch forgotten gems',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}