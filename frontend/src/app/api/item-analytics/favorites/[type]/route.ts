import { NextResponse } from "next/server";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://acceptable-wisdom-production-ac06.up.railway.app";

export async function GET(
  request: Request,
  context: { params: Promise<{ type: string }> }
) {
  try {
    const { type } = await context.params;
    console.log(`🔍 API Route: Fetching favorites for type: ${type}`);
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log(`🔍 API Route: Auth header present: ${!!authHeader}`);
    
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
      console.log(`🔍 API Route: Forwarding auth header to backend`);
    } else {
      console.log(`⚠️ API Route: No auth header found`);
    }
    
    const backendUrl = `${API_URL}/api/item-analytics/favorites/${type}`;
    console.log(`🔍 API Route: Calling backend: ${backendUrl}`);
    
    // Forward the request to the backend
    const response = await fetch(backendUrl, {
      headers,
    });

    console.log(`🔍 API Route: Backend response status: ${response.status}`);

    if (!response.ok) {
      const errorData = await response.json();
      console.log(`❌ API Route: Backend error:`, errorData);
      return NextResponse.json(
        { error: errorData.error || "Failed to fetch favorites" },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log(`✅ API Route: Backend success, data:`, data);
    return NextResponse.json(data);
  } catch (error) {
    console.error("❌ API Route: Error fetching favorites:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
} 