import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  console.log("💎 Forgotten Gems API route called");
  
  try {
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    console.log("🔍 Authorization header:", authHeader ? 'Present' : 'Missing');
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    // Call the backend forgotten gems endpoint
    const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app'}/api/wardrobe-insights/insights/forgotten-gems`;
    console.log("🔗 Proxying to backend URL:", backendUrl);
    
    const res = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
    });

    if (!res.ok) {
      console.error(`❌ Backend error: ${res.status} ${res.statusText}`);
      const errorText = await res.text().catch(() => 'Unable to read error');
      console.error('❌ Backend error details:', errorText);
      
      // Return graceful fallback instead of propagating error
      return NextResponse.json({ 
        success: true,
        data: {
          forgottenItems: [],
          totalUnwornItems: 0,
          potentialSavings: 0,
          rediscoveryOpportunities: 0,
          analysis_timestamp: new Date().toISOString()
        },
        message: `Backend temporarily unavailable (${res.status})`
      }, { status: 200 });
    }

    const data = await res.json();
    console.log("✅ Successfully fetched forgotten gems from backend");
    return NextResponse.json(data);

  } catch (error) {
    console.error('❌ Error in forgotten gems API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch forgotten gems' },
      { status: 500 }
    );
  }
}