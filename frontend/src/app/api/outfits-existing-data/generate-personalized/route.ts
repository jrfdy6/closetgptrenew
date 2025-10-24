import { NextRequest, NextResponse } from 'next/server';

// DEPLOYMENT VERSION: 2025-10-11-v4-working-endpoint
// Force this route to be treated as a dynamic server route
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';
export const revalidate = 0;

// Handle CORS preflight requests
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

export async function POST(request: NextRequest) {
  try {
    console.log('🔍 DEBUG v4: Existing-data generate API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      console.error('❌ No Authorization header provided');
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
    console.log('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Get request body
    const body = await request.json();
    console.log('🔍 DEBUG: Request body keys:', Object.keys(body));
    
    // DEBUG: Check if wardrobe has metadata
    if (body.wardrobe && body.wardrobe.length > 0) {
      const firstItem = body.wardrobe[0];
      console.log('🔍 VERCEL PROXY: First wardrobe item keys:', Object.keys(firstItem));
      console.log('🔍 VERCEL PROXY: metadata field present?', 'metadata' in firstItem);
      if ('metadata' in firstItem) {
        console.log('🔍 VERCEL PROXY: metadata value:', JSON.stringify(firstItem.metadata).substring(0, 200));
      }
    }
    
    // Call the real backend generate endpoint (the one that actually exists!)
    const fullBackendUrl = `${backendUrl}/api/outfits-existing-data/generate-personalized`;
    console.log('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    console.log('🔍 DEBUG: Backend response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Backend error response:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.statusText}`, details: errorText },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('✅ DEBUG: Generated outfit received successfully');
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Error in generate outfit route:', error);
    return NextResponse.json(
      { error: 'Outfit generation failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
