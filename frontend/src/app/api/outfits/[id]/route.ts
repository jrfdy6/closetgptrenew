import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

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
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/outfits/${outfitId}`;
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
