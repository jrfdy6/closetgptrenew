import { NextResponse } from "next/server";

export async function GET(request: Request) {
  try {
    // Forward the request to the backend server
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgpt-clean-production.up.railway.app'}/api/wardrobe/coverage`, {
      method: 'GET',
      headers: {
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