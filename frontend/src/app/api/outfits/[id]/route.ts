import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

export const dynamic = 'force-dynamic';

function buildBackendUrl(path: string) {
  return `${getBackendUrl().replace(/\/$/, '')}${path}`;
}

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const headers = { 'Cache-Control': 'private, no-store' };
  const authorization = request.headers.get('authorization');
  if (!authorization || !/^Bearer \S+$/.test(authorization)) return NextResponse.json({ error: 'Sign in to view this outfit.' }, { status: 401, headers });
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(buildBackendUrl('/api/outfits/' + encodeURIComponent(params.id)), {
      headers: { Authorization: authorization }, cache: 'no-store', signal: controller.signal,
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) return NextResponse.json({ error: response.status === 404 || response.status === 403 ? 'This saved outfit is unavailable.' : 'We could not load your saved outfit. Please try again.' }, { status: response.status, headers });
    if (data?.id !== params.id || !Array.isArray(data?.items)) return NextResponse.json({ error: 'The saved outfit response could not be confirmed.' }, { status: 502, headers });
    return NextResponse.json(data, { headers });
  } catch {
    return NextResponse.json({ error: 'We could not load your saved outfit. Please try again.' }, { status: 503, headers });
  } finally { clearTimeout(timer); }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Handle the special case where id is "generate"
    if (params.id === 'generate') {
      serverDebugLog('🔍 DEBUG: Outfits POST API route called for generate - CONNECTING TO BACKEND');
      
      // Get the authorization header
      const authHeader = request.headers.get('authorization');
      serverDebugLog('🔍 DEBUG: Authorization header present:', !!authHeader);
      
      // Get backend URL from environment variables
      const backendUrl = getBackendUrl();
      serverDebugLog('🔍 DEBUG: Backend URL:', backendUrl);
      
      // Get request body
      const body = await request.json();
      serverDebugLog('🔍 DEBUG: Request body:', body);
      
      // Call the real backend to generate outfit using robust service
      const fullBackendUrl = `${backendUrl}/api/outfits/generate`;
      serverDebugLog('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
      
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
      
      serverDebugLog('🔍 DEBUG: Backend response received:', {
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
      serverDebugLog('✅ Successfully generated outfit from backend:', {
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
    serverDebugLog('🔍 DEBUG: Outfits PUT API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    serverDebugLog('🔍 DEBUG: Authorization header present:', !!authHeader);
    
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
    serverDebugLog('🔍 DEBUG: Updating outfit:', outfitId, 'with data:', body);
    
    // Call the production backend
    const fullBackendUrl = buildBackendUrl(`/api/outfits/${outfitId}`);
    serverDebugLog('🔍 DEBUG: About to call backend PUT:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'PUT',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    serverDebugLog('🔍 DEBUG: Backend PUT response status:', response.status);
    serverDebugLog('🔍 DEBUG: Backend PUT response ok:', response.ok);
    
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
    serverDebugLog('🔍 DEBUG: Backend PUT response received:', {
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
    serverDebugLog('🔍 DEBUG: Outfits DELETE API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    serverDebugLog('🔍 DEBUG: Authorization header present:', !!authHeader);
    
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
    
    serverDebugLog('🔍 DEBUG: Deleting outfit:', outfitId);
    
    // Call the production backend
    const fullBackendUrl = buildBackendUrl(`/api/outfits/${outfitId}`);
    serverDebugLog('🔍 DEBUG: About to call backend DELETE:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'DELETE',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    serverDebugLog('🔍 DEBUG: Backend DELETE response status:', response.status);
    serverDebugLog('🔍 DEBUG: Backend DELETE response ok:', response.ok);
    
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
    serverDebugLog('🔍 DEBUG: Backend DELETE response received:', {
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
