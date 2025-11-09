import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'https://closetgptrenew-production.up.railway.app';

function buildBackendUrl(path: string) {
  return `${BACKEND_URL.replace(/\/$/, '')}${path}`;
}

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }

    const outfitId = params.id;
    const response = await fetch(
      buildBackendUrl(`/api/outfits/${outfitId}`),
      {
        method: 'GET',
        headers: {
          Authorization: authHeader
        }
      }
    );

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: data.detail || 'Failed to fetch outfit'
        },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ Error in outfits GET API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch outfit' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Handle the special case where id is "generate"
    if (params.id === 'generate') {
      console.log('🔍 DEBUG: Outfits POST API route called for generate - CONNECTING TO BACKEND');
      
      // Get the authorization header
      const authHeader = request.headers.get('authorization');
      console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
      
      // Get backend URL from environment variables
      const backendUrl = 'https://closetgptrenew-production.up.railway.app';
      console.log('🔍 DEBUG: Backend URL:', backendUrl);
      
      // Get request body
      const body = await request.json();
      console.log('🔍 DEBUG: Request body:', body);
      
      // Call the real backend to generate outfit using robust service
      const fullBackendUrl = `${backendUrl}/api/outfits/generate`;
      console.log('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
      
      if (!authHeader) {
        console.error('❌ No Authorization header provided');
        return NextResponse.json(
          { error: 'Authorization header required' },
          { status: 401 }
        );
      }

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
          { error: `Backend error: ${response.status} ${response.statusText}`, details: errorText },
          { status: response.status }
        );
      }
      
      const data = await response.json();
      console.log('✅ Successfully generated outfit from backend:', {
        hasItems: data.items ? data.items.length : 'unknown',
        occasion: data.occasion,
        style: data.style
      });
      
      return NextResponse.json(data);
    }
    
    // For other IDs, return method not allowed
    return NextResponse.json(
      { error: 'POST method not supported for outfit ID operations' },
      { status: 405 }
    );
    
  } catch (error) {
    console.error('❌ Error in outfits POST API route:', error);
    return NextResponse.json(
      { error: 'Failed to generate outfit' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    console.log('🔍 DEBUG: Outfits PUT API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    const outfitId = params.id;
    
    if (!outfitId) {
      return NextResponse.json(
        { error: 'Outfit ID is required' },
        { status: 400 }
      );
    }
    
    // Get the request body
    const body = await request.json();
    console.log('🔍 DEBUG: Updating outfit:', outfitId, 'with data:', body);
    
    // Call the production backend
      const fullBackendUrl = buildBackendUrl(`/api/outfits/${outfitId}`);
    const fullBackendUrl = buildBackendUrl(`/api/outfits/${outfitId}`);
    console.log('🔍 DEBUG: About to call backend PUT:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'PUT',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    console.log('🔍 DEBUG: Backend PUT response status:', response.status);
    console.log('🔍 DEBUG: Backend PUT response ok:', response.ok);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('🔍 DEBUG: Backend PUT response not ok:', response.status, response.statusText);
      console.error('🔍 DEBUG: Backend PUT error response body:', errorText);
      
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Outfit not found' },
          { status: 404 }
        );
      } else if (response.status === 403) {
        return NextResponse.json(
          { error: 'Not authorized to update this outfit' },
          { status: 403 }
        );
      } else {
        return NextResponse.json(
          { error: 'Failed to update outfit' },
          { status: response.status }
        );
      }
    }
    
    const responseData = await response.json();
    console.log('🔍 DEBUG: Backend PUT response received:', {
      success: responseData.success,
      message: responseData.message
    });
    
    return NextResponse.json(responseData);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in outfits PUT:', error);
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    console.log('🔍 DEBUG: Outfits DELETE API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    const outfitId = params.id;
    
    if (!outfitId) {
      return NextResponse.json(
        { error: 'Outfit ID is required' },
        { status: 400 }
      );
    }
    
    console.log('🔍 DEBUG: Deleting outfit:', outfitId);
    
    // Call the production backend
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
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
