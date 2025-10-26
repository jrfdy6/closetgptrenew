import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    // Get authorization header
    const authHeader = request.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          outfits_worn_this_week: 0
        },
        { status: 401 }
      );
    }

    // Get backend URL
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.NEXT_PUBLIC_BACKEND_URL ||
                      'https://closetgptrenew-production.up.railway.app';
    
    const fullUrl = `${backendUrl}/api/simple-analytics/outfits-worn-this-week`;
    
    // Forward request to backend
    const response = await fetch(fullUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Return fallback data if backend fails
      console.log(`⚠️ Backend analytics unavailable (${response.status}), using fallback`);
      return NextResponse.json({
        success: true,
        outfits_worn_this_week: 0,
        message: 'Backend analytics unavailable, using fallback data'
      });
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error fetching analytics:', error);
    // Return fallback data on error
    return NextResponse.json({
      success: true,
      outfits_worn_this_week: 0,
      message: 'Analytics service unavailable'
    });
  }
}

