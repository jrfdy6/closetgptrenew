import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  console.log('🔍 DEBUG: Frontend trending-styles route called!');
  
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
    
    // Return fallback data since production backend doesn't have trending styles yet
    const fallbackData = {
      success: true,
      data: {
        trending_styles: [
          {
            name: "Classic Denim",
            popularity: 85,
            category: "bottoms",
            description: "Timeless denim styles"
          },
          {
            name: "Minimalist Basics",
            popularity: 78,
            category: "tops",
            description: "Essential wardrobe staples"
          },
          {
            name: "Athleisure",
            popularity: 72,
            category: "activewear",
            description: "Comfort meets style"
          }
        ],
        total_trends: 3,
        most_popular: {
          name: "Classic Denim",
          popularity: 85,
          category: "bottoms"
        }
      },
      message: "Fallback trending styles data (production backend setup in progress)"
    };
    
    console.log('🔍 DEBUG: Returning fallback trending styles data');
    return NextResponse.json(fallbackData);
    
  } catch (error) {
    console.error('❌ Frontend API: Error in trending-styles route:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch trending styles',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 