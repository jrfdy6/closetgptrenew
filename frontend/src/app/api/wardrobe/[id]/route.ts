import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request headers
export const dynamic = 'force-dynamic';

export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    console.log('🔍 DEBUG: Wardrobe DELETE API route called for item:', id);
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
    console.log('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Call the real backend to delete the item
    const fullBackendUrl = `${backendUrl}/api/wardrobe/${id}`;
    console.log('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'DELETE',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Backend DELETE response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('🔍 DEBUG: Backend DELETE response not ok:', response.status, response.statusText);
      console.error('🔍 DEBUG: Backend error response body:', errorText);
      
      return NextResponse.json(
        { 
          error: `Failed to delete wardrobe item`, 
          details: errorText,
          status: response.status 
        },
        { status: response.status }
      );
    }
    
    const responseData = await response.json();
    console.log('🔍 DEBUG: Backend DELETE response data:', responseData);
    
    return NextResponse.json({
      success: true,
      message: 'Wardrobe item deleted successfully',
      deletedItemId: id
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in wardrobe DELETE:', error);
    
    return NextResponse.json(
      { 
        error: 'Wardrobe delete failed', 
        details: String(error) 
      },
      { status: 500 }
    );
  }
}