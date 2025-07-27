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
    console.log("💡 Returning mock wardrobe recommendations data");
    return NextResponse.json({
      success: true,
      recommendations: [
        {
          priority: "high",
          category: "outerwear",
          item: "Lightweight blazer",
          reason: "Improve business casual coverage",
          estimated_cost: "$80-120"
        },
        {
          priority: "medium",
          category: "dresses",
          item: "Cocktail dress",
          reason: "Enhance evening wear options",
          estimated_cost: "$60-100"
        },
        {
          priority: "low",
          category: "accessories",
          item: "Statement necklace",
          reason: "Add versatility to existing outfits",
          estimated_cost: "$30-50"
        }
      ],
      message: "Mock wardrobe recommendations (backend endpoint not yet implemented)"
    });
  } catch (error) {
    console.error("Error fetching wardrobe recommendations:", error);
    return NextResponse.json(
      { 
        error: "Failed to fetch wardrobe recommendations",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
} 