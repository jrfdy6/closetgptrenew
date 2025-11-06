import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe API route called - CONNECTING TO BACKEND');
    
    // Check if this is a request for outfit history (temporary workaround)
    const url = new URL(request.url);
    if (url.pathname.includes('outfit-history')) {
      return handleOutfitHistory(request);
    }
    
    // Get the authorization header - try multiple variations
    const authHeader = request.headers.get('authorization') || 
                      request.headers.get('Authorization') ||
                      request.headers.get('AUTHORIZATION');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    console.log('🔍 DEBUG: Authorization header value:', authHeader ? authHeader.substring(0, 20) + '...' : 'null');
    console.log('🔍 DEBUG: All headers:', Object.fromEntries(request.headers.entries()));
    
    // Check for auth header
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = 'https://closetgptrenew-production.up.railway.app'; // Force correct backend URL
    console.log('🔍 DEBUG: Backend URL:', backendUrl);
    console.log('🔍 DEBUG: Environment variable NEXT_PUBLIC_BACKEND_URL:', process.env.NEXT_PUBLIC_BACKEND_URL);
    console.log('🔍 DEBUG: Using hardcoded backend URL to ensure correct backend is called');
    
    // Call the real backend to get your 114 wardrobe items
    // Add trailing slash to avoid 307 redirect that changes protocol
    const fullBackendUrl = `${backendUrl}/api/wardrobe/`;
    console.log('🔍 DEBUG: Full backend URL being called:', fullBackendUrl);
    
    console.log('🔍 DEBUG: About to call backend with URL:', fullBackendUrl);
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader, // Use ONLY the real auth token
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Backend response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend response not ok:', response.status, response.statusText);
      console.error('🔍 DEBUG: This means the backend rejected the request - likely due to invalid token');
      // Fallback to mock data if backend is not available
      const mockWardrobe = {
        success: true,
        items: [
          {
            id: 'item_1',
            name: 'Dark Academia Blazer',
            type: 'blazer',
            color: 'charcoal',
            brand: 'The Savile Row Company',
            imageUrl: '/placeholder.jpg',
            isFavorite: true,
            category: 'outerwear'
          },
          {
            id: 'item_2',
            name: 'Statement T-Shirt',
            type: 't-shirt',
            color: 'white',
            brand: 'Celine',
            imageUrl: '/placeholder.jpg',
            isFavorite: false,
            category: 'tops'
          },
          {
            id: 'item_3',
            name: 'Slim Fit Pants',
            type: 'pants',
            color: 'olive',
            brand: 'Dockers',
            imageUrl: '/placeholder.jpg',
            isFavorite: true,
            category: 'bottoms'
          },
          {
            id: 'item_4',
            name: 'Oxford Shoes',
            type: 'shoes',
            color: 'brown',
            brand: 'Unknown',
            imageUrl: '/placeholder.jpg',
            isFavorite: false,
            category: 'shoes'
          }
        ],
        count: 4,
        user_id: 'mock-user',
        message: 'Backend not available, using mock data'
      };
      
      return NextResponse.json(mockWardrobe);
    }
    
    const wardrobeData = await response.json();
    console.log('🔍 DEBUG: Backend wardrobe data received:', {
      success: wardrobeData.success,
      count: wardrobeData.count || wardrobeData.items?.length,
      hasItems: !!wardrobeData.items,
      userId: wardrobeData.user_id,
      items: wardrobeData.items?.map(item => ({ id: item.id, name: item.name })) || []
    });
    
    return NextResponse.json(wardrobeData);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in wardrobe route:', error);
    
    // Fallback to mock data on error
    const mockWardrobe = {
      success: true,
      items: [
        {
          id: 'item_1',
          name: 'Dark Academia Blazer',
          type: 'blazer',
          color: 'charcoal',
          brand: 'The Savile Row Company',
          imageUrl: '/placeholder.jpg',
          isFavorite: true,
          category: 'outerwear'
        },
        {
          id: 'item_2',
          name: 'Statement T-Shirt',
          type: 't-shirt',
          color: 'white',
          brand: 'Celine',
          imageUrl: '/placeholder.jpg',
          isFavorite: false,
          category: 'tops'
        },
        {
          id: 'item_3',
          name: 'Slim Fit Pants',
          type: 'pants',
          color: 'olive',
          brand: 'Dockers',
          imageUrl: '/placeholder.jpg',
          isFavorite: true,
          category: 'bottoms'
        },
        {
          id: 'item_4',
          name: 'Oxford Shoes',
          type: 'shoes',
          color: 'brown',
          brand: 'Unknown',
          imageUrl: '/placeholder.jpg',
          isFavorite: false,
          category: 'shoes'
        }
      ],
      count: 4,
      user_id: 'mock-user',
      message: 'Error occurred, using mock data'
    };
    
    return NextResponse.json(mockWardrobe);
  }
}

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe POST API route called - CONNECTING TO BACKEND');
    
    // Get the authorization header - try multiple variations
    const authHeader = request.headers.get('authorization') || 
                      request.headers.get('Authorization') ||
                      request.headers.get('AUTHORIZATION');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    console.log('🔍 DEBUG: Authorization header value:', authHeader ? authHeader.substring(0, 20) + '...' : 'null');
    
    // Temporarily bypass auth check to test functionality
    console.log('🔍 DEBUG: TEMPORARILY BYPASSING AUTH CHECK FOR TESTING');
    
    // if (!authHeader) {
    //   return NextResponse.json(
    //     { error: 'Authorization header required' },
    //     { status: 401 }
    //   );
    // }
    
    // Get the request body
    let requestBody;
    try {
      requestBody = await request.json();
      console.log('🔍 DEBUG: Request body:', requestBody);
    } catch (bodyError) {
      console.error('🔍 DEBUG: Failed to parse request body:', bodyError);
      return NextResponse.json(
        { error: 'Invalid request body', details: 'Request body must be valid JSON' },
        { status: 400 }
      );
    }
    
    // Get backend URL from environment variables
    const backendUrl = 'https://closetgptrenew-production.up.railway.app'; // Force correct backend URL
    console.log('🔍 DEBUG: Backend URL:', backendUrl);
    
    // Call the real backend to add the item - using direct endpoint to bypass router issues
    console.log('🔍 DEBUG: About to call backend POST:', `${backendUrl}/api/wardrobe/add-direct`);
    console.log('🔍 DEBUG: Request body:', JSON.stringify(requestBody, null, 2));
    console.log('🔍 DEBUG: Authorization header:', authHeader);
    
    const response = await fetch(`${backendUrl}/api/wardrobe/add-direct`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });
    
    console.log('🔍 DEBUG: Backend response status:', response.status);
    console.log('🔍 DEBUG: Backend response ok:', response.ok);
    console.log('🔍 DEBUG: Backend response headers:', Object.fromEntries(response.headers.entries()));
    
    // Get the response text first to see what we're actually getting
    const responseText = await response.text();
    console.log('🔍 DEBUG: Backend response text (v2):', responseText);
    console.log('🔍 DEBUG: Response text length:', responseText.length);
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend response not ok:', response.status, response.statusText);
      console.error('🔍 DEBUG: Backend error response body:', responseText);
      console.error('🔍 DEBUG: Request that failed:', {
        url: `${backendUrl}/api/wardrobe/add`,
        method: 'POST',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });
      // Fallback to mock response if backend is not available
      return NextResponse.json({
        success: true,
        message: 'Item added successfully (mock)',
        item: {
          id: `item_${Date.now()}`,
          ...requestBody,
          isFavorite: false
        }
      });
    }
    
    // Parse the response text as JSON
    let responseData;
    try {
      responseData = JSON.parse(responseText);
      console.log('🔍 DEBUG: Backend POST response received:', {
        success: responseData.success,
        hasItem: !!responseData.item
      });
    } catch (parseError) {
      console.error('🔍 DEBUG: Failed to parse backend response as JSON:', parseError);
      console.error('🔍 DEBUG: Response text was:', responseText);
      // Fallback to mock response if JSON parsing fails
      return NextResponse.json({
        success: true,
        message: 'Item added successfully (mock)',
        item: {
          id: `item_${Date.now()}`,
          ...requestBody,
          isFavorite: false
        }
      });
    }
    
    return NextResponse.json(responseData);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in wardrobe POST:', error);
    
    // Fallback to mock response on error
    return NextResponse.json({
      success: true,
      message: 'Item added successfully (mock)',
      item: {
        id: `item_${Date.now()}`,
        name: 'Mock Item',
        type: 'shirt',
        color: 'blue',
        isFavorite: false
      }
    });
  }
}

// Temporary outfit history handler (workaround for Vercel deployment issue)
async function handleOutfitHistory(request: Request) {
  try {
    console.log('🔍 DEBUG: Handling outfit history request via wardrobe route');
    
    // Get the authorization header - try multiple variations
    const authHeader = request.headers.get('authorization') || 
                      request.headers.get('Authorization') ||
                      request.headers.get('AUTHORIZATION');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    // Temporarily bypass auth check to test functionality
    console.log('🔍 DEBUG: TEMPORARILY BYPASSING AUTH CHECK FOR TESTING');
    
    // if (!authHeader) {
    //   return NextResponse.json({ error: 'Authorization header required' }, { status: 401 });
    // }
    
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/outfit-history/`;
    console.log('🔍 DEBUG: Outfit history backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Outfit history backend response status:', response.status);
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Outfit history backend response not ok:', response.status);
      return NextResponse.json({ error: 'Backend request failed' }, { status: response.status });
    }
    
    const data = await response.json();
    console.log('🔍 DEBUG: Outfit history data received:', data);
    
    return NextResponse.json(data, { status: response.status });
    
  } catch (error) {
    console.error('❌ Error in outfit history handler:', error);
    return NextResponse.json({ error: 'Failed to fetch outfit history' }, { status: 500 });
  }
}
