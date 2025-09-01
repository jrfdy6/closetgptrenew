import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe API route called - MOCK VERSION');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    // Return mock wardrobe data directly
    const mockWardrobe = {
      success: true,
      items: [
        {
          id: 'item_1',
          name: 'Dark Academia Blazer',
          type: 'blazer',
          color: 'charcoal',
          brand: 'The Savile Row Company',
          imageUrl: '/images/placeholder.jpg',
          isFavorite: true,
          category: 'outerwear'
        },
        {
          id: 'item_2',
          name: 'Statement T-Shirt',
          type: 't-shirt',
          color: 'white',
          brand: 'Celine',
          imageUrl: '/images/placeholder.jpg',
          isFavorite: false,
          category: 'tops'
        },
        {
          id: 'item_3',
          name: 'Slim Fit Pants',
          type: 'pants',
          color: 'olive',
          brand: 'Dockers',
          imageUrl: '/images/placeholder.jpg',
          isFavorite: true,
          category: 'bottoms'
        },
        {
          id: 'item_4',
          name: 'Oxford Shoes',
          type: 'shoes',
          color: 'brown',
          brand: 'Unknown',
          imageUrl: '/images/placeholder.jpg',
          isFavorite: false,
          category: 'shoes'
        }
      ],
      count: 4,
      user_id: 'dANqjiI0CKgaitxzYtw1bhtvQrG3'
    };
    
    return NextResponse.json(mockWardrobe);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in mock wardrobe route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch wardrobe' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe POST API route called - MOCK VERSION');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
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
    
    // Return success response
    return NextResponse.json({
      success: true,
      message: 'Item added successfully',
      item: {
        id: `item_${Date.now()}`,
        ...requestBody,
        isFavorite: false
      }
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in mock wardrobe POST:', error);
    return NextResponse.json(
      { error: 'Failed to add item to wardrobe' },
      { status: 500 }
    );
  }
} 