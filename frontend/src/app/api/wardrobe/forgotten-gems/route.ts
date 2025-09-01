import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Forgotten gems API route called - MOCK VERSION');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
      console.log('🔍 DEBUG: No auth header - returning 401');
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    // Return mock forgotten gems data
    const mockForgottenGems = [
      {
        id: 'item_5',
        name: 'Vintage Denim Jacket',
        type: 'jacket',
        color: 'blue',
        brand: 'Levi\'s',
        lastWorn: '2023-12-01T00:00:00Z',
        daysSinceLastWorn: 45,
        imageUrl: '/images/placeholder.jpg',
        reason: 'Perfect for layering in spring'
      },
      {
        id: 'item_6',
        name: 'Silk Scarf',
        type: 'accessory',
        color: 'burgundy',
        brand: 'Hermès',
        lastWorn: '2023-11-15T00:00:00Z',
        daysSinceLastWorn: 60,
        imageUrl: '/images/placeholder.jpg',
        reason: 'Great for adding color to neutral outfits'
      },
      {
        id: 'item_7',
        name: 'Leather Belt',
        type: 'accessory',
        color: 'brown',
        brand: 'Unknown',
        lastWorn: '2023-10-20T00:00:00Z',
        daysSinceLastWorn: 85,
        imageUrl: '/images/placeholder.jpg',
        reason: 'Essential for formal occasions'
      }
    ];
    
    return NextResponse.json({
      success: true,
      data: mockForgottenGems,
      count: mockForgottenGems.length,
      message: 'Found items you haven\'t worn in a while'
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in mock forgotten gems route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch forgotten gems' },
      { status: 500 }
    );
  }
}