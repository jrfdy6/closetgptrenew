import { NextRequest, NextResponse } from 'next/server';

// FORCE REBUILD: Timestamp 2025-08-24 21:00:00
// Main /api/outfits route
export async function GET(req: NextRequest) {
  console.log("🚀 FORCE REBUILD: /api/outfits GET route HIT:", req.method);
  console.log("🔍 DEBUG: Environment variables:", {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL
  });
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/outfits/${req.nextUrl.search}`;
    console.log("🚀 FORCE REBUILD: Backend URL:", backendUrl);
    console.log("🔍 DEBUG: Request URL search params:", req.nextUrl.search);
    const authHeader = req.headers.get('authorization');
    console.log("🔍 DEBUG: Authorization header:", authHeader ? `Present (${authHeader.substring(0, 20)}...)` : 'Missing');
    
    const res = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.get('authorization') && {
          Authorization: req.headers.get('authorization')!,
        }),
      },
    });

    if (!res.ok) {
      console.error('❌ FORCE REBUILD: Backend responded with:', res.status, res.statusText);
      const errorText = await res.text().catch(() => 'Unable to read error response');
      console.error('❌ FORCE REBUILD: Backend error details:', errorText);
      
      // Special handling for auth errors
      if (res.status === 403 || res.status === 401) {
        console.error('🔐 AUTH ERROR: Token may be invalid or expired');
        console.error('🔐 AUTH DEBUG: Auth header sent:', authHeader ? 'Yes' : 'No');
      }
      
      return NextResponse.json({ 
        error: `Backend error: ${res.status} ${res.statusText}`, 
        details: errorText,
        authHeaderSent: !!authHeader
      }, { status: res.status });
    }

    const data = await res.json();
    console.log("🚀 FORCE REBUILD: Successfully fetched data from backend");
    console.log("🔍 DEBUG: First 3 outfits from backend:", data.slice(0, 3).map((o: any) => `${o.name}: ${o.createdAt}`));
    
    const response = NextResponse.json(data, { status: res.status });
    // Add cache-busting headers to prevent browser caching
    response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    response.headers.set('Pragma', 'no-cache');
    response.headers.set('Expires', '0');
    response.headers.set('Surrogate-Control', 'no-store');
    
    return response;
  } catch (err) {
    console.error('❌ FORCE REBUILD: /api/outfits proxy failed:', err);
    console.error('❌ FORCE REBUILD: Error type:', typeof err);
    console.error('❌ FORCE REBUILD: Error details:', {
      message: err instanceof Error ? err.message : String(err),
      stack: err instanceof Error ? err.stack : undefined,
      cause: err instanceof Error ? err.cause : undefined
    });
    return NextResponse.json({ 
      error: 'Proxy failed', 
      details: err instanceof Error ? err.message : 'Unknown error',
      type: typeof err
    }, { status: 500 });
  }
}

// FORCE REBUILD: August 31 2025 15:10 - Aggressive cache bust
export const runtime = 'edge';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  const timestamp = new Date().toISOString();
  console.log(`🚀 UNIFIED v3 [${timestamp}]: /api/outfits POST route HIT:`, req.method);
  console.log("🚀 UNIFIED v2: Request URL:", req.url);
  console.log("🚀 UNIFIED v2: Request headers:", Object.fromEntries(req.headers.entries()));
  
  try {
    const body = await req.text();
    console.log("🚀 UNIFIED: Request body length:", body.length);
    console.log("🚀 UNIFIED: Request body preview:", body.substring(0, 200) + "...");
    
    const requestData = JSON.parse(body);
    
    // Determine if this is outfit creation (has 'items' field) or generation (has 'mood' field)
    const isCreation = requestData.items && Array.isArray(requestData.items);
    const backendEndpoint = isCreation ? '/api/outfits' : '/api/outfits/generate';
    const backendUrl = `https://closetgpt-backend-production.up.railway.app${backendEndpoint}`; // Temporarily use local backend for testing
    
    console.log(`🚀 UNIFIED: ${isCreation ? 'CREATION' : 'GENERATION'} request to:`, backendUrl);
    console.log("🔍 Request type detected:", isCreation ? "outfit creation" : "outfit generation");
    
    if (isCreation) {
      console.log("🔍 CREATION DEBUG: Outfit data being sent:", {
        name: requestData.name,
        occasion: requestData.occasion,
        style: requestData.style,
        itemsCount: requestData.items?.length,
        createdAt: requestData.createdAt,
        createdAtType: typeof requestData.createdAt
      });
    }
    
    const res = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.get('authorization') && {
          Authorization: req.headers.get('authorization')!,
        }),
      },
      body: body,
    });

    if (!res.ok) {
      console.error(`❌ UNIFIED: Backend ${isCreation ? 'creation' : 'generation'} responded with:`, res.status);
      const errorText = await res.text().catch(() => 'Unable to read error response');
      console.error('❌ UNIFIED: Backend error details:', errorText);
      return NextResponse.json({ 
        error: `Backend error: ${res.status}`, 
        details: errorText,
        requestType: isCreation ? "creation" : "generation"
      }, { status: res.status });
    }

    const data = await res.json();
    console.log(`🚀 UNIFIED: Successfully ${isCreation ? 'created' : 'generated'} outfit`);
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ UNIFIED: /api/outfits POST proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}
