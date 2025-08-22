import { NextRequest, NextResponse } from 'next/server';

// ===== FRONTEND API ROUTE FOR OUTFIT STATS =====
// This route forwards outfit statistics requests to the backend

export async function GET(req: NextRequest) {
  try {
    console.log('🔍 [Frontend API] Outfit stats route called');
    
    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL;
    
    if (!backendUrl) {
      console.error('❌ [Frontend API] NEXT_PUBLIC_API_URL not configured');
      return NextResponse.json(
        { error: 'Backend URL not configured' },
        { status: 500 }
      );
    }
    
    console.log(`🔗 [Frontend API] Forwarding stats request to backend: ${backendUrl}/api/outfits/stats/summary`);
    
    // Forward the request to the backend outfit service
    const response = await fetch(`${backendUrl}/api/outfits/stats/summary`, {
      method: "GET",
      headers: { 
        "Content-Type": "application/json",
        // Forward any authorization headers
        ...(req.headers.get('authorization') && {
          'Authorization': req.headers.get('authorization')!
        })
      },
      cache: "no-store",
    });
    
    if (!response.ok) {
      console.error(`❌ [Frontend API] Backend responded with status: ${response.status}`);
      const errorData = await response.json().catch(() => ({}));
      
      return NextResponse.json(
        { 
          error: 'Backend service error', 
          details: errorData.detail || errorData.error || 'Unknown error',
          status: response.status 
        },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log(`✅ [Frontend API] Successfully forwarded stats request to backend`);
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ [Frontend API] Error in outfit stats route:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: 'Failed to process outfit stats request'
      },
      { status: 500 }
    );
  }
}

// ===== OPTIONS HANDLER FOR CORS =====
export async function OPTIONS(req: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
