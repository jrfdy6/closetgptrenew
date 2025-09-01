import { NextResponse } from 'next/server';

// Mock profile endpoint - returns data directly without calling backend
export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: User profile API route called - MOCK VERSION');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
      console.log('🔍 DEBUG: No auth header - returning 401');
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    // Return mock profile data directly
    const mockProfile = {
      id: 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
      userId: 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
      name: 'Johnnie Fields',
      email: 'johnnie@example.com',
      gender: 'male',
      onboardingCompleted: true,
      
      // Style Preferences
      stylePreferences: ['Dark Academia', 'Old Money', 'Minimalist'],
      preferences: {
        gender: 'male',
        style: ['dark-academia', 'old-money', 'minimalist'],
        colors: ['black', 'navy', 'gray', 'brown'],
        brands: []
      },
      
      // Measurements & Sizes
      measurements: {
        height: 180,
        heightFeetInches: '5\'11"',
        weight: '170 lbs',
        bodyType: 'Athletic',
        skinTone: 'Medium',
        topSize: 'M',
        bottomSize: '32x32',
        shoeSize: '10',
        dressSize: 'M',
        jeanWaist: '32',
        braSize: 'N/A',
        inseam: '32',
        waist: '32',
        chest: '40'
      },
      
      // Fit Preferences
      fitPreference: 'Slim Fit',
      fitPreferences: {
        tops: 'slim',
        bottoms: 'slim',
        shoes: 'comfortable'
      },
      
      // Color Palette
      colorPalette: {
        primary: ['black', 'navy', 'gray'],
        secondary: ['brown', 'white'],
        accent: ['gold', 'silver']
      },
      
      // Quiz Responses
      quizResponses: [
        { question: 'style', answer: 'Dark Academia' },
        { question: 'occasion', answer: 'Casual' },
        { question: 'mood', answer: 'Confident' }
      ],
      
      // Additional Info
      budget: 'Mid-range',
      hybridStyleName: 'Dark Academia Minimalist',
      alignmentScore: 85,
      wardrobeCount: 114,
      
      // Timestamps
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      
      // Backend-specific fields
      avatarUrl: '',
    };
    
    return NextResponse.json({
      success: true,
      profile: mockProfile
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in mock profile route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch user profile' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Creating/updating user profile - MOCK VERSION');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    const body = await request.json();
    console.log('🔍 DEBUG: Profile data:', body);
    
    // Return success with updated profile
    return NextResponse.json({
      success: true,
      profile: {
        id: 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
        userId: 'dANqjiI0CKgaitxzYtw1bhtvQrG3',
        name: body.name || 'Johnnie Fields',
        email: body.email || 'johnnie@example.com',
        onboardingCompleted: true,
        stylePreferences: body.stylePreferences || ['Dark Academia'],
        createdAt: body.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        avatarUrl: '',
      }
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in mock profile POST:', error);
    return NextResponse.json(
      { error: 'Failed to create/update user profile', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 