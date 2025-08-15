import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  console.log('🔍 DEBUG: Frontend wardrobe-stats route called!');
  console.log('🔍 DEBUG: Request headers:', Object.fromEntries(request.headers.entries()));
  
  try {
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
      console.log('❌ Frontend API: No authorization header found');
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }

    console.log('🔍 DEBUG: Authorization header found, returning fallback data...');
    
    // Return fallback data since production backend endpoint is not working properly
    const fallbackData = {
      success: true,
      data: {
        total_items: 0,
        categories: {},
        colors: {},
        user_id: "fallback-user"
      },
      message: "Fallback wardrobe stats (production backend setup in progress)"
    };
    
    console.log('🔍 DEBUG: Returning fallback wardrobe stats data');
    return NextResponse.json(fallbackData);
    
  } catch (error) {
    console.error('❌ Frontend API: Error in wardrobe-stats route:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch wardrobe statistics',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 