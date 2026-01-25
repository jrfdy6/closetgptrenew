import { NextRequest, NextResponse } from "next/server";

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 Frontend API: Wardrobe gaps endpoint called');
    console.log('🔍 DEBUG: All headers:', Object.fromEntries(request.headers.entries()));
    
    // Get the authorization header - try multiple variations
    const authHeader = request.headers.get('authorization') || 
                      request.headers.get('Authorization') ||
                      request.headers.get('AUTHORIZATION');
    console.log('🔍 Frontend API: Authorization header present:', !!authHeader);
    console.log('🔍 DEBUG: Authorization header value:', authHeader ? authHeader.substring(0, 20) + '...' : 'null');

    // Require auth; callers are authenticated and this avoids sending null Authorization upstream.
    if (!authHeader) {
      return NextResponse.json(
        { success: false, error: 'Authorization header required', data: { gaps: [] } },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
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
    const fullBackendUrl = `${backendUrl}/api/wardrobe-analysis/gaps${queryString ? `?${queryString}` : ''}`;
    console.log('🔍 Frontend API: Full backend URL:', fullBackendUrl);
    
    // Call the backend with a short timeout (this is non-critical; UI should proceed without it).
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);

    const backendResponse = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    }).finally(() => clearTimeout(timeoutId));
    
    console.log('🔍 Frontend API: Backend response status:', backendResponse.status);
    
    if (!backendResponse.ok) {
      console.log('❌ Frontend API: Backend call failed:', backendResponse.status, backendResponse.statusText);
      const errorText = await backendResponse.text();
      console.log('❌ Frontend API: Backend error response:', errorText);
      // IMPORTANT: return 200 with safe empty data so dashboard/profile pages don't throw and
      // users don't get blocked by a "nice-to-have" endpoint.
      return NextResponse.json({
        success: true,
        data: { gaps: [] },
        debug: {
          backendStatus: backendResponse.status,
          backendStatusText: backendResponse.statusText,
          backendError: errorText?.substring?.(0, 500) || null,
          backendUnavailable: true,
        },
      });
    }
    
    const data = await backendResponse.json();
    console.log('🔍 Frontend API: Backend data received successfully');
    return NextResponse.json(data);
    
  } catch (error) {
    console.error("❌ Frontend API: Error:", error);
    // Same rationale: do not break the page for optional gaps.
    return NextResponse.json({
      success: true,
      data: { gaps: [] },
      debug: {
        backendUnavailable: true,
        error: error instanceof Error ? error.message : "Unknown error",
      },
    });
  }
} 