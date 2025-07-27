import { NextResponse } from "next/server";

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    // Forward the request to the backend server
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://acceptable-wisdom-production-ac06.up.railway.app'}/api/user/profile`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Backend error:", errorData);
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch user profile');
    }

    const profileData = await response.json();
    return NextResponse.json(profileData);
  } catch (error) {
    console.error("Error fetching profile:", error);
    return NextResponse.json(
      { 
        error: "Failed to fetch user profile", 
        details: error instanceof Error ? error.message : "Unknown error",
        stack: process.env.NODE_ENV === 'development' ? error instanceof Error ? error.stack : undefined : undefined
      },
      { status: 500 }
    );
  }
} 