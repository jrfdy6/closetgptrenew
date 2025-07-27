import { NextRequest, NextResponse } from "next/server";
import { getUserIdFromRequest } from '@/lib/utils/server-auth';

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    // Verify user authentication
    const userId = await getUserIdFromRequest(request);
    if (!userId) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Get the authorization header from the request
    const authHeader = request.headers.get('authorization');
    
    // For now, return mock data since the backend endpoint doesn't exist yet
    console.log("📊 Returning mock wardrobe coverage data");
    return NextResponse.json({
      success: true,
      coverage: {
        occasion: {
          casual: 75,
          formal: 60,
          business: 45,
          athletic: 80,
          evening: 30
        },
        seasonal: {
          spring: 70,
          summer: 85,
          fall: 65,
          winter: 55
        },
        category: {
          tops: 90,
          bottoms: 75,
          dresses: 40,
          outerwear: 60,
          shoes: 70,
          accessories: 50
        }
      },
      message: "Mock wardrobe coverage data (backend endpoint not yet implemented)"
    });
  } catch (error) {
    console.error("Error fetching wardrobe coverage:", error);
    return NextResponse.json(
      { 
        error: "Failed to fetch wardrobe coverage",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
} 