import { NextResponse } from "next/server";
import { cookies } from 'next/headers';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    console.log("✨ Frontend style-inspiration API route called");
    const requestBody = await request.json();
    console.log("✨ Style inspiration request:", requestBody);

    // Get authorization header from request
    const authHeader = request.headers.get('authorization') || 
                      request.headers.get('Authorization');
    
    console.log("✨ Authorization header present:", !!authHeader);

    // Check for auth header
    if (!authHeader) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Authorization header required',
          message: 'Please log in to get style inspiration'
        },
        { status: 401 }
      );
    }

    // Forward the request to the backend server
    const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app'}/api/style-inspiration/get-inspiration`;
    console.log("✨ Forwarding to backend:", backendUrl);
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': authHeader, // Forward the auth header
    };

    const response = await fetch(backendUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody),
      signal: AbortSignal.timeout(15000), // 15 second timeout
    });

    console.log("✨ Backend response status:", response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error("✨ Backend error:", errorData);
      
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch style inspiration');
    }

    const inspirationData = await response.json();
    console.log("✨ Backend inspiration data received");
    
    // Return with CORS headers
    return NextResponse.json(inspirationData, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  } catch (error) {
    console.error("✨ Error fetching style inspiration:", error);
    
    return NextResponse.json(
      { 
        success: false,
        error: "Failed to fetch style inspiration", 
        message: error instanceof Error ? error.message : "Unknown error",
        details: process.env.NODE_ENV === 'development' ? error instanceof Error ? error.stack : undefined : undefined
      },
      { 
        status: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      }
    );
  }
}

// Handle OPTIONS requests for CORS
export async function OPTIONS(request: Request) {
  return NextResponse.json({}, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

