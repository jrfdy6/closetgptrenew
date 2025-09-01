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
    
    // Return mock top worn items data
    const mockTopWornItems = [
      {
        id: 'item_1',
        name: 'Dark Academia Blazer',
        type: 'blazer',
        color: 'charcoal',
        brand: 'The Savile Row Company',
        wearCount: 12,
        lastWorn: '2024-01-15T00:00:00Z',
        imageUrl: '/images/placeholder.jpg'
      },
      {
        id: 'item_3',
        name: 'Slim Fit Pants',
        type: 'pants',
        color: 'olive',
        brand: 'Dockers',
        wearCount: 8,
        lastWorn: '2024-01-14T00:00:00Z',
        imageUrl: '/images/placeholder.jpg'
      },
      {
        id: 'item_4',
        name: 'Oxford Shoes',
        type: 'shoes',
        color: 'brown',
        brand: 'Unknown',
        wearCount: 6,
        lastWorn: '2024-01-13T00:00:00Z',
        imageUrl: '/images/placeholder.jpg'
      },
      {
        id: 'item_2',
        name: 'Statement T-Shirt',
        type: 't-shirt',
        color: 'white',
        brand: 'Celine',
        wearCount: 4,
        lastWorn: '2024-01-12T00:00:00Z',
        imageUrl: '/images/placeholder.jpg'
      }
    ].slice(0, limit);
    
    return NextResponse.json({
      success: true,
      data: mockTopWornItems,
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
