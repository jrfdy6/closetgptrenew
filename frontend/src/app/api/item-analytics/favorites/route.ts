import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Item analytics favorites API route called');
    
    // For now, return empty data since this is a new user
    return NextResponse.json({
      success: true,
      favorites: [],
      totalFavorites: 0
    });
  } catch (error) {
    console.error('🔍 DEBUG: Error in item analytics favorites:', error);
    return NextResponse.json(
      { error: 'Failed to fetch favorites', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 