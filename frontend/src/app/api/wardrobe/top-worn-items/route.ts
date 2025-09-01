import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Top worn items API route called - MOCK VERSION');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
      console.log('🔍 DEBUG: No auth header - returning 401');
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    // Get limit from query params
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '5');
    
    // Return mock top worn items data in the format the frontend expects
    const mockTopWornItems = [
      {
        id: 'item_1',
        name: 'Dark Academia Blazer',
        type: 'blazer',
        color: 'charcoal',
        brand: 'The Savile Row Company',
        wear_count: 12,
        last_worn: '2024-01-15T00:00:00Z',
        image_url: '/images/placeholder.jpg',
        is_favorite: true
      },
      {
        id: 'item_3',
        name: 'Slim Fit Pants',
        type: 'pants',
        color: 'olive',
        brand: 'Dockers',
        wear_count: 8,
        last_worn: '2024-01-14T00:00:00Z',
        image_url: '/images/placeholder.jpg',
        is_favorite: true
      },
      {
        id: 'item_4',
        name: 'Oxford Shoes',
        type: 'shoes',
        color: 'brown',
        brand: 'Unknown',
        wear_count: 6,
        last_worn: '2024-01-13T00:00:00Z',
        image_url: '/images/placeholder.jpg',
        is_favorite: false
      },
      {
        id: 'item_2',
        name: 'Statement T-Shirt',
        type: 't-shirt',
        color: 'white',
        brand: 'Celine',
        wear_count: 4,
        last_worn: '2024-01-12T00:00:00Z',
        image_url: '/images/placeholder.jpg',
        is_favorite: false
      }
    ].slice(0, limit);
    
    return NextResponse.json({
      success: true,
      top_worn_items: mockTopWornItems,
      count: mockTopWornItems.length
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in mock top worn items route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch top worn items' },
      { status: 500 }
    );
  }
}
