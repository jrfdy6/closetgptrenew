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
    
    // Extract user info from Firebase token
    let userEmail = 'johnnie@example.com'; // fallback
    let userName = 'Johnnie Fields'; // fallback
    let userId = 'dANqjiI0CKgaitxzYtw1bhtvQrG3'; // fallback
    
    try {
      // Decode the JWT token to get user info
      const token = authHeader.replace('Bearer ', '');
      console.log('🔍 DEBUG: Token length:', token.length);
      console.log('🔍 DEBUG: Token starts with:', token.substring(0, 20) + '...');
      
      const tokenParts = token.split('.');
      console.log('🔍 DEBUG: Token parts count:', tokenParts.length);
      
      if (tokenParts.length === 3) {
        const payload = JSON.parse(atob(tokenParts[1]));
        console.log('🔍 DEBUG: Token payload:', payload);
        console.log('🔍 DEBUG: Available payload keys:', Object.keys(payload));
        
        userEmail = payload.email || userEmail;
        userName = payload.name || payload.email?.split('@')[0] || userName;
        userId = payload.user_id || payload.sub || userId;
        console.log('🔍 DEBUG: Extracted user info from token:', { userEmail, userName, userId });
      } else {
        console.log('🔍 DEBUG: Invalid token format, expected 3 parts, got:', tokenParts.length);
      }
    } catch (tokenError) {
      console.log('🔍 DEBUG: Could not decode token, using fallback values:', tokenError);
    }
    
    // Return mock profile data with actual user info
    const mockProfile = {
      id: userId,
      userId: userId,
      name: userName,
      email: userEmail,
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
    
    // Extract user info from Firebase token
    let userEmail = 'johnnie@example.com'; // fallback
    let userName = 'Johnnie Fields'; // fallback
    let userId = 'dANqjiI0CKgaitxzYtw1bhtvQrG3'; // fallback
    
    try {
      // Decode the JWT token to get user info
      const token = authHeader.replace('Bearer ', '');
      console.log('🔍 DEBUG: POST - Token length:', token.length);
      console.log('🔍 DEBUG: POST - Token starts with:', token.substring(0, 20) + '...');
      
      const tokenParts = token.split('.');
      console.log('🔍 DEBUG: POST - Token parts count:', tokenParts.length);
      
      if (tokenParts.length === 3) {
        const payload = JSON.parse(atob(tokenParts[1]));
        console.log('🔍 DEBUG: POST - Token payload:', payload);
        console.log('🔍 DEBUG: POST - Available payload keys:', Object.keys(payload));
        
        userEmail = payload.email || userEmail;
        userName = payload.name || payload.email?.split('@')[0] || userName;
        userId = payload.user_id || payload.sub || userId;
        console.log('🔍 DEBUG: POST - Extracted user info from token:', { userEmail, userName, userId });
      } else {
        console.log('🔍 DEBUG: POST - Invalid token format, expected 3 parts, got:', tokenParts.length);
      }
    } catch (tokenError) {
      console.log('🔍 DEBUG: POST - Could not decode token, using fallback values:', tokenError);
    }
    
    const body = await request.json();
    console.log('🔍 DEBUG: Profile data:', body);
    
    // Return success with updated profile
    return NextResponse.json({
      success: true,
      profile: {
        id: userId,
        userId: userId,
        name: body.name || userName,
        email: body.email || userEmail,
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