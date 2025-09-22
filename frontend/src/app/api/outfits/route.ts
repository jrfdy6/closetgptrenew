import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

// Test route to verify deployment - URGENT DEPLOYMENT FORCE
export async function OPTIONS(req: NextRequest) {
  console.log("🔍 DEBUG: OPTIONS request received - API route is deployed [URGENT v3.0]");
  return new NextResponse(null, { 
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

export async function GET(req: NextRequest) {
  console.log("🚀 FORCE DEPLOYMENT: Outfits GET route called - CONNECTING TO PRODUCTION BACKEND [VERCEL FORCE DEPLOY v5.0]");
  
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
      isArray: Array.isArray(outfitsData),
      count: Array.isArray(outfitsData) ? outfitsData.length : (outfitsData.outfits?.length || 0),
      hasOutfits: Array.isArray(outfitsData) ? outfitsData.length > 0 : !!outfitsData.outfits
    });
    
    // Handle both array response (from backend) and structured response
    const normalizedResponse = Array.isArray(outfitsData) 
      ? {
          success: true,
          outfits: outfitsData,
          total: outfitsData.length,
          limit: parseInt(limit),
          offset: parseInt(offset)
        }
      : outfitsData;
    
    const response_obj = NextResponse.json(normalizedResponse);
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

export async function POST(req: NextRequest) {
  const timestamp = new Date().toISOString();
  console.log(`🚀 FORCE DEPLOYMENT: Outfits POST route called - CONNECTING TO PRODUCTION BACKEND [VERCEL FORCE DEPLOY v5.0] [${timestamp}]`);
    console.log(`🔍 DEBUG: API ROUTE IS BEING CALLED! - COHESIVE COMPOSITION ENABLED [URGENT v3.0]`);
  
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
    
    // Call the production backend - Updated to use cohesive composition service
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const backendEndpoint = isCreation ? '/api/outfits' : '/api/outfit/generate';
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

