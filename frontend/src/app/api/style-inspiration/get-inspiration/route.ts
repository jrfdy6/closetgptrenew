import { NextResponse } from "next/server";
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    serverDebugLog("✨ Frontend style-inspiration API route called");
    const requestBody = await request.json();
    serverDebugLog("✨ Style inspiration request:", requestBody);

    // Get authorization header from request
    const authHeader = request.headers.get('authorization') || 
                      request.headers.get('Authorization');
    
    serverDebugLog("✨ Authorization header present:", !!authHeader);

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
    const backendUrl = `${getBackendUrl()}/api/style-inspiration/get-inspiration`;
    serverDebugLog("✨ Forwarding to backend:", backendUrl);
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': authHeader, // Forward the auth header
    };

    // Longer timeout for mobile networks
    const userAgent = request.headers.get('user-agent') || '';
    const isMobile = /Mobile|Android|iPhone|iPad/i.test(userAgent);
    const timeout = isMobile ? 30000 : 15000; // 30s on mobile, 15s on desktop
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);

    serverDebugLog("✨ Backend response status:", response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error("✨ Backend error:", errorData);
      
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch style inspiration');
    }

    const inspirationData = await response.json();
    serverDebugLog("✨ Backend inspiration data received");
    
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
