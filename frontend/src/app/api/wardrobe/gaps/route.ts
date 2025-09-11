import { NextRequest, NextResponse } from "next/server";

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 Frontend API: Wardrobe gaps endpoint called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 Frontend API: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    console.log('🔍 Frontend API: Backend URL:', backendUrl);
    
    // Get query parameters
    const { searchParams } = new URL(request.url);
    const budgetRange = searchParams.get('budget_range');
    const preferredStores = searchParams.get('preferred_stores');
    
    // Build query string
    const queryParams = new URLSearchParams();
    if (budgetRange) queryParams.append('budget_range', budgetRange);
    if (preferredStores) queryParams.append('preferred_stores', preferredStores);
    
    const queryString = queryParams.toString();
    const fullBackendUrl = `${backendUrl}/api/wardrobe/gaps${queryString ? `?${queryString}` : ''}`;
    console.log('🔍 Frontend API: Full backend URL:', fullBackendUrl);
    
    // Call the backend
    const backendResponse = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 Frontend API: Backend response status:', backendResponse.status);
    
    if (!backendResponse.ok) {
      console.log('❌ Frontend API: Backend call failed:', backendResponse.status, backendResponse.statusText);
      const errorText = await backendResponse.text();
      console.log('❌ Frontend API: Backend error response:', errorText);
      return NextResponse.json(
        { error: 'Backend service unavailable' },
        { status: backendResponse.status }
      );
    }
    
    const data = await backendResponse.json();
    console.log('🔍 Frontend API: Backend data received successfully');
    return NextResponse.json(data);
    
  } catch (error) {
    console.error("❌ Frontend API: Error:", error);
    return NextResponse.json(
      { 
        error: "Failed to fetch wardrobe gaps",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
} 