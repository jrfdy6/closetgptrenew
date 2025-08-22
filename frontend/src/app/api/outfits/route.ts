import { NextRequest, NextResponse } from 'next/server';

// ===== FRONTEND API ROUTE =====
// This route follows the established wardrobe service architecture pattern:
// - Routes: Handle HTTP requests/responses and basic validation
// - Services: Backend outfit service handles business logic
// - Types: Proper TypeScript interfaces for data contracts

export async function GET(req: NextRequest) {
  try {
    console.log('🔍 [Frontend API] Outfits route called');
    
    // Get the backend URL from environment
    const backendUrl = process.env.NEXT_PUBLIC_API_URL;
    
    if (!backendUrl) {
      console.error('❌ [Frontend API] NEXT_PUBLIC_API_URL not configured');
      return NextResponse.json(
        { error: 'Backend URL not configured' },
        { status: 500 }
      );
    }
    
    console.log(`🔗 [Frontend API] Forwarding to backend: ${backendUrl}/api/outfits`);
    
    // Forward the request to the backend outfit service
    // This follows the established wardrobe service pattern
    const response = await fetch(`${backendUrl}/api/outfits`, {
      method: "GET",
      headers: { 
        "Content-Type": "application/json",
        // Forward any authorization headers
        ...(req.headers.get('authorization') && {
          'Authorization': req.headers.get('authorization')!
        })
      },
      cache: "no-store",
    });
    
    if (!response.ok) {
      console.error(`❌ [Frontend API] Backend responded with status: ${response.status}`);
      const errorData = await response.json().catch(() => ({}));
      
      return NextResponse.json(
        { 
          error: 'Backend service error', 
          details: errorData.detail || errorData.error || 'Unknown error',
          status: response.status 
        },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log(`✅ [Frontend API] Successfully forwarded request to backend`);
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ [Frontend API] Error in outfits route:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: 'Failed to process outfits request'
      },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    console.log('🔍 [Frontend API] Creating outfit via backend');
    
    const backendUrl = process.env.NEXT_PUBLIC_API_URL;
    
    if (!backendUrl) {
      console.error('❌ [Frontend API] NEXT_PUBLIC_API_URL not configured');
      return NextResponse.json(
        { error: 'Backend URL not configured' },
        { status: 500 }
      );
    }
    
    // Get the request body
    const body = await req.json();
    
    console.log(`🔗 [Frontend API] Forwarding POST to backend: ${backendUrl}/api/outfits`);
    
    // Forward the request to the backend outfit service
    const response = await fetch(`${backendUrl}/api/outfits`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        ...(req.headers.get('authorization') && {
          'Authorization': req.headers.get('authorization')!
        })
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      console.error(`❌ [Frontend API] Backend responded with status: ${response.status}`);
      const errorData = await response.json().catch(() => ({}));
      
      return NextResponse.json(
        { 
          error: 'Backend service error', 
          details: errorData.detail || errorData.error || 'Unknown error',
          status: response.status 
        },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log(`✅ [Frontend API] Successfully created outfit via backend`);
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ [Frontend API] Error creating outfit:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: 'Failed to create outfit'
      },
      { status: 500 }
    );
  }
}

// ===== OPTIONS HANDLER FOR CORS =====
export async function OPTIONS(req: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
} 