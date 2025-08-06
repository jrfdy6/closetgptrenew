import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 Frontend API: Forgotten gems endpoint called');
    
    const backendUrl = process.env.BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
    
    // Get query parameters
    const { searchParams } = new URL(request.url);
    const daysThreshold = searchParams.get('days_threshold');
    const minRediscoveryPotential = searchParams.get('min_rediscovery_potential');
    
    // Build backend URL with query parameters
    const backendApiUrl = new URL(`${backendUrl}/api/wardrobe/forgotten-gems`);
    if (daysThreshold) backendApiUrl.searchParams.set('days_threshold', daysThreshold);
    if (minRediscoveryPotential) backendApiUrl.searchParams.set('min_rediscovery_potential', minRediscoveryPotential);
    
    // Get authentication header from the request
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      console.log('❌ Frontend API: No authorization header or invalid format');
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    
    console.log('🔍 Frontend API: Calling backend with auth header from request');
    
    // Forward request to backend
    const response = await fetch(backendApiUrl.toString(), {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 Frontend API: Backend response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.log('❌ Frontend API: Backend error response:', errorText);
      
      // Handle authentication errors properly
      if (response.status === 401 || response.status === 403) {
        return NextResponse.json(
          { error: 'Authentication required' },
          { status: 401 }
        );
      }
      
      // If backend returns 405 (Method Not Allowed) or 404 (Not Found), provide fallback data
      if (response.status === 405 || response.status === 404) {
        console.log('🔍 Forgotten gems endpoint not available, providing fallback data');
        return NextResponse.json({
          success: true,
          data: {
            forgottenItems: [],
            totalUnwornItems: 0,
            potentialSavings: 0,
            rediscoveryOpportunities: 0,
            analysis_timestamp: new Date().toISOString()
          },
          message: "Forgotten gems feature not available yet"
        });
      }
      
      // Handle other errors
      return NextResponse.json(
        { error: 'Backend service unavailable' },
        { status: 500 }
      );
    }
    
    const data = await response.json();
    console.log('✅ Frontend API: Backend data received successfully');
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Frontend API: Error:', error);
    return NextResponse.json(
      { 
        error: "Failed to fetch forgotten gems",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log('🔍 Frontend API: Forgotten gems POST endpoint called');
    
    const backendUrl = process.env.BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
    
    // Get the request body
    const body = await request.json();
    const { item_id, action } = body;
    
    if (!item_id || !action) {
      return NextResponse.json(
        { error: 'item_id and action are required' },
        { status: 400 }
      );
    }
    
    // Get authentication header from the request
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      console.log('❌ Frontend API: No authorization header or invalid format');
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    
    // Determine which endpoint to call based on action
    let endpoint = '';
    if (action === 'rediscover') {
      endpoint = 'rediscover';
    } else if (action === 'declutter') {
      endpoint = 'declutter';
    } else {
      return NextResponse.json(
        { error: 'Invalid action. Must be "rediscover" or "declutter"' },
        { status: 400 }
      );
    }
    
    const backendApiUrl = `${backendUrl}/api/wardrobe/forgotten-gems/${endpoint}`;
    
    console.log(`🔍 Frontend API: Calling backend ${endpoint} endpoint`);
    
    // Forward request to backend
    const response = await fetch(backendApiUrl, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ item_id }),
    });
    
    console.log('🔍 Frontend API: Backend response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.log('❌ Frontend API: Backend error response:', errorText);
      
      // Handle authentication errors properly
      if (response.status === 401 || response.status === 403) {
        return NextResponse.json(
          { error: 'Authentication required' },
          { status: 401 }
        );
      }
      
      // Handle other errors
      return NextResponse.json(
        { error: 'Backend service unavailable' },
        { status: 500 }
      );
    }
    
    const data = await response.json();
    console.log('✅ Frontend API: Backend data received successfully');
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('❌ Frontend API: Error:', error);
    return NextResponse.json(
      { 
        error: "Failed to process forgotten gems action",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
} 