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
    
    // Forward the request to the backend server
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://acceptable-wisdom-production-ac06.up.railway.app'}/api/wardrobe/coverage`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader || '',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Backend error:", errorData);
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch wardrobe coverage');
    }

    const coverageData = await response.json();
    return NextResponse.json(coverageData);
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