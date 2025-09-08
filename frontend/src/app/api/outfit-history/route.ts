import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Outfit history API route called - MOCK VERSION');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
      console.log('🔍 DEBUG: No auth header - returning 401');
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }

    // Return mock outfit history data in the format the frontend expects
    const mockOutfitHistory = [
      {
        id: 'outfit_1',
        outfitName: 'Dark Academia Confident Look',
        occasion: 'Casual',
        style: 'Dark Academia',
        mood: 'Confident',
        dateWorn: '2024-01-15T00:00:00Z',
        tags: ['blazer', 'pants', 'shoes', 'dark-academia'],
        items: [
          {
            id: 'item_1',
            name: 'Dark Academia Blazer',
            type: 'blazer',
            color: 'charcoal'
          },
          {
            id: 'item_3',
            name: 'Slim Fit Pants',
            type: 'pants',
            color: 'olive'
          },
          {
            id: 'item_4',
            name: 'Oxford Shoes',
            type: 'shoes',
            color: 'brown'
          }
        ],
        createdAt: '2024-01-15T00:00:00Z',
        matchScore: 86,
        isFavorite: true
      },
      {
        id: 'outfit_2',
        outfitName: 'Old Money Dynamic Interview',
        occasion: 'Interview',
        style: 'Old Money',
        mood: 'Dynamic',
        dateWorn: '2024-01-14T00:00:00Z',
        tags: ['t-shirt', 'pants', 'shoes', 'old-money'],
        items: [
          {
            id: 'item_2',
            name: 'Statement T-Shirt',
            type: 't-shirt',
            color: 'white'
          },
          {
            id: 'item_3',
            name: 'Slim Fit Pants',
            type: 'pants',
            color: 'olive'
          },
          {
            id: 'item_4',
            name: 'Oxford Shoes',
            type: 'shoes',
            color: 'brown'
          }
        ],
        createdAt: '2024-01-14T00:00:00Z',
        matchScore: 82,
        isFavorite: false
      },
      {
        id: 'outfit_3',
        outfitName: 'Minimalist Clean Look',
        occasion: 'Casual',
        style: 'Minimalist',
        mood: 'Clean',
        dateWorn: '2024-01-13T00:00:00Z',
        tags: ['t-shirt', 'pants', 'minimalist'],
        items: [
          {
            id: 'item_2',
            name: 'Statement T-Shirt',
            type: 't-shirt',
            color: 'white'
          },
          {
            id: 'item_3',
            name: 'Slim Fit Pants',
            type: 'pants',
            color: 'olive'
          }
        ],
        createdAt: '2024-01-13T00:00:00Z',
        matchScore: 78,
        isFavorite: true
      }
    ];
    
    return NextResponse.json({
      success: true,
      data: mockOutfitHistory,
      count: mockOutfitHistory.length,
      totalPages: 1,
      currentPage: 1
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in mock outfit history route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch outfit history' },
      { status: 500 }
    );
  }
} 