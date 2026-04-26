import { NextResponse } from "next/server";
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

export async function GET(
  request: Request,
  context: { params: Promise<{ type: string }> }
) {
  try {
    const { type } = await context.params;
    serverDebugLog(`🔍 API Route: Fetching favorites for type: ${type}`);
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    serverDebugLog(`🔍 API Route: Auth header present: ${!!authHeader}`);
    
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
      serverDebugLog(`🔍 API Route: Forwarding auth header to backend`);
    } else {
      serverDebugLog(`⚠️ API Route: No auth header found`);
    }
    
    const backendUrl = `${getBackendUrl()}/api/item-analytics/favorites/${type}`;
    serverDebugLog(`🔍 API Route: Calling backend: ${backendUrl}`);
    
    // Forward the request to the backend
    const response = await fetch(backendUrl, {
      headers,
    });

    serverDebugLog(`🔍 API Route: Backend response status: ${response.status}`);

    if (!response.ok) {
      const errorData = await response.json();
      serverDebugLog(`❌ API Route: Backend error:`, errorData);
      return NextResponse.json(
        { error: errorData.error || "Failed to fetch favorites" },
        { status: response.status }
      );
    }

    const data = await response.json();
    serverDebugLog(`✅ API Route: Backend success, data:`, data);
    return NextResponse.json(data);
  } catch (error) {
    console.error("❌ API Route: Error fetching favorites:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
} 
