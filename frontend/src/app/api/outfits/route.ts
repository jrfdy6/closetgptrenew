import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  console.log("🔍 DEBUG: Outfits GET route called - CONNECTING TO PRODUCTION BACKEND");
  
  try {
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get query parameters
    const { searchParams } = new URL(req.url);
    const limit = searchParams.get('limit') || '50';
    const offset = searchParams.get('offset') || '0';
    
    console.log('🔍 DEBUG: Query params:', { limit, offset });
    
    // Call the production backend
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/outfits/?limit=${limit}&offset=${offset}`;
    console.log('🔍 DEBUG: Calling backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Backend response status:', response.status);
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend response not ok:', response.status, response.statusText);
      return NextResponse.json({ 
        error: 'Backend request failed', 
        details: `Status: ${response.status} ${response.statusText}`
      }, { status: response.status });
    }
    
    const outfitsData = await response.json();
    console.log('🔍 DEBUG: Backend outfits data received:', {
      success: outfitsData.success,
      count: outfitsData.outfits?.length || 0,
      total: outfitsData.total,
      hasOutfits: !!outfitsData.outfits
    });
    
    const response_obj = NextResponse.json(outfitsData);
    response_obj.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    response_obj.headers.set('Pragma', 'no-cache');
    response_obj.headers.set('Expires', '0');
    response_obj.headers.set('Surrogate-Control', 'no-store');
    
    return response_obj;
  } catch (err) {
    console.error('❌ PRODUCTION: /api/outfits GET failed:', err);
    return NextResponse.json({ 
      error: 'Failed to fetch outfits', 
      details: err instanceof Error ? err.message : 'Unknown error'
    }, { status: 500 });
  }
}

export const runtime = 'edge';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  const timestamp = new Date().toISOString();
  console.log(`🔍 DEBUG: Outfits POST route called - CONNECTING TO PRODUCTION BACKEND [${timestamp}]`);
  console.log(`🔍 DEBUG: API ROUTE IS BEING CALLED!`);
  
  try {
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    const body = await req.text();
    console.log("🔍 DEBUG: Request body length:", body.length);
    console.log("🔍 DEBUG: Request body preview:", body.substring(0, 200) + "...");
    
    // Parse and log the request data to check for baseItemId
    try {
      const requestData = JSON.parse(body);
      console.log("🔍 DEBUG: Parsed request data keys:", Object.keys(requestData));
      console.log("🔍 DEBUG: baseItemId in request:", requestData.baseItemId);
      console.log("🔍 DEBUG: baseItem in request:", requestData.baseItem);
    } catch (e) {
      console.log("🔍 DEBUG: Error parsing request body:", e);
    }
    
    const requestData = JSON.parse(body);
    
    // Determine if this is outfit creation (has 'items' field) or generation (has 'mood' field)
    const isCreation = requestData.items && Array.isArray(requestData.items);
    console.log("🔍 DEBUG: Request type detected:", isCreation ? "outfit creation" : "outfit generation");
    
    // Call the production backend
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const backendEndpoint = isCreation ? '/api/outfits' : '/api/outfits/generate';
    const fullBackendUrl = `${backendUrl}${backendEndpoint}`;
    console.log('🔍 DEBUG: Calling backend URL:', fullBackendUrl);
    
    // Log what we're sending to the backend
    console.log('🔍 DEBUG: Sending to backend:', {
      url: fullBackendUrl,
      bodyLength: body.length,
      bodyPreview: body.substring(0, 200) + '...',
      hasBaseItemId: requestData.baseItemId ? 'YES' : 'NO',
      baseItemId: requestData.baseItemId
    });
    
    const response = await fetch(fullBackendUrl, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: body,
    });
    
    console.log('🔍 DEBUG: Backend response status:', response.status);
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend response not ok:', response.status, response.statusText);
      return NextResponse.json({ 
        error: 'Backend request failed', 
        details: `Status: ${response.status} ${response.statusText}`
      }, { status: response.status });
    }
    
    const outfitData = await response.json();
    console.log('🔍 DEBUG: Backend outfit data received:', {
      success: outfitData.success,
      hasOutfit: !!outfitData.outfit,
      hasItems: !!outfitData.items,
      outfitId: outfitData.id || outfitData.outfit?.id
    });
    
    return NextResponse.json(outfitData);
  } catch (err) {
    console.error('❌ PRODUCTION: /api/outfits POST failed:', err);
    return NextResponse.json({ 
      error: 'Failed to process outfit request', 
      details: err instanceof Error ? err.message : 'Unknown error' 
    }, { status: 500 });
  }
}

export async function DELETE(req: NextRequest) {
  try {
    console.log('🔍 DEBUG: Outfits DELETE API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get the outfit ID from the URL
    const { searchParams } = new URL(req.url);
    const outfitId = searchParams.get('outfitId');
    
    if (!outfitId) {
      return NextResponse.json(
        { error: 'Outfit ID is required' },
        { status: 400 }
      );
    }
    
    console.log('🔍 DEBUG: Deleting outfit:', outfitId);
    
    // Call the production backend
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/outfits/${outfitId}`;
    console.log('🔍 DEBUG: About to call backend DELETE:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'DELETE',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Backend DELETE response status:', response.status);
    console.log('🔍 DEBUG: Backend DELETE response ok:', response.ok);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('🔍 DEBUG: Backend DELETE response not ok:', response.status, response.statusText);
      console.error('🔍 DEBUG: Backend DELETE error response body:', errorText);
      
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Outfit not found' },
          { status: 404 }
        );
      } else if (response.status === 403) {
        return NextResponse.json(
          { error: 'Not authorized to delete this outfit' },
          { status: 403 }
        );
      } else {
        return NextResponse.json(
          { error: 'Failed to delete outfit' },
          { status: response.status }
        );
      }
    }
    
    const responseData = await response.json();
    console.log('🔍 DEBUG: Backend DELETE response received:', {
      success: responseData.success,
      message: responseData.message
    });
    
    return NextResponse.json(responseData);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in outfits DELETE:', error);
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
